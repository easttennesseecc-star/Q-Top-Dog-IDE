"""
Email Inbound API

Accepts inbound email webhooks and processes simple commands so users can reply
with ACCEPT/DECLINE/MODIFY even if buttons/links fail.

POST /api/email/inbound
Body (JSON suggested): {
  "from": "user@example.com",
  "to": "qide@example.com",
  "subject": "Re: UI Draft ...",
  "text": "ACCEPT <token>" | "DECLINE <token>" | "MODIFY <token>: notes",
  "html": "..." (optional)
}

For production, wire this endpoint to your email provider's inbound webhook.
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any
import re
import logging

router = APIRouter(prefix="/email", tags=["email-inbound"])
logger = logging.getLogger(__name__)


def _extract_text(payload: Dict[str, Any]) -> str:
    txt = payload.get("text") or ""
    if not txt:
        # Fallback: strip tags from html rudimentarily
        html = payload.get("html") or ""
        if html:
            try:
                txt = re.sub(r"<[^>]+>", " ", html)
            except Exception:
                txt = html
    subj = payload.get("subject") or ""
    return f"{subj}\n{txt}".strip()


def _extract_tokens(text: str) -> Dict[str, str]:
    tokens: Dict[str, str] = {}
    # Approve-email links
    for m in re.findall(r"/api/assistant/approve-email\?token=([A-Za-z0-9._\-~]+)", text):
        tokens.setdefault("approve", m)
    # Modify-email links
    for m in re.findall(r"/api/assistant/modify-email\?token=([A-Za-z0-9._\-~]+)", text):
        tokens.setdefault("modify", m)
    # Generic token pattern when included as plain text: "token: <abc>" or "ACCEPT <abc>"
    for m in re.findall(r"(?:token[:\s]+|ACCEPT\s+|APPROVE\s+|DECLINE\s+|REJECT\s+|MODIFY\s+)([A-Za-z0-9._\-~]{16,})", text, flags=re.IGNORECASE):
        tokens.setdefault("generic", m)
    return tokens


@router.post("/inbound")
async def email_inbound(req: Request):
    try:
        payload = await req.json()
    except Exception:
        try:
            # Fallback for form-encoded providers
            form = await req.form()
            payload = dict(form)
        except Exception:
            return JSONResponse(status_code=400, content={"error": "Invalid body"})
    text = _extract_text(payload)
    upper = text.upper()
    tokens = _extract_tokens(text)
    sender = payload.get("from") or payload.get("sender") or "unknown"

    # Helper to process approval token similar to /approve-email
    async def _process_approval_token(tok: str) -> Dict[str, Any]:
        from backend.services.email_token_service import consume_token
        from backend.services.build_plan_approval_service import get_plan_approval_service, PlanStep
        p = consume_token(tok)
        if not p:
            return {"status": "error", "message": "invalid_or_expired_token"}
        kind = p.get("kind")
        if kind == "ui_draft_approval":
            svc = get_plan_approval_service()
            import uuid
            workflow_id = f"wf-mail-{uuid.uuid4().hex[:8]}"
            desc = p.get("description") or "User-approved UI draft"
            steps = [
                PlanStep(step_id="step-1", order=1, description="Finalize UI assets and constraints", estimated_duration="1h", files_affected=[], dependencies=[], risk_level="low", verification_criteria="UI snapshot matches draft"),
                PlanStep(step_id="step-2", order=2, description="Implement features and tests per draft", estimated_duration="2h", files_affected=[], dependencies=[], risk_level="low", verification_criteria="Unit/integration tests pass"),
            ]
            generated_plan = svc.generate_plan(workflow_id=workflow_id, generated_by="email-reply", objective="Approved UI draft → build", scope=desc, steps=steps, risks=[], dependencies_to_install=[], files_to_create=[], files_to_modify=[], files_to_delete=[], estimated_total_duration=None)
            svc.approve_plan(generated_plan.plan_id, approved_by="email-reply")
            svc.start_execution(generated_plan.plan_id)
            return {"status": "ok", "action": "approved", "plan_id": generated_plan.plan_id}
        elif kind == "plan_approval":
            from backend.services.build_plan_approval_service import get_plan_approval_service
            svc = get_plan_approval_service()
            plan_id = p.get("plan_id")
            if not plan_id:
                return {"status": "error", "message": "missing_plan_id"}
            plan = svc.approve_plan(plan_id, approved_by="email-reply")
            if not plan:
                return {"status": "error", "message": "plan_not_found"}
            if p.get("start_execution", True):
                svc.start_execution(plan_id)
            return {"status": "ok", "action": "approved", "plan_id": plan_id}
        else:
            return {"status": "error", "message": "unsupported_token_kind"}

    # ACCEPT/APPROVE
    if "ACCEPT" in upper or "APPROVE" in upper:
        tok = tokens.get("approve") or tokens.get("generic")
        if not tok:
            return {"status": "error", "message": "no_token_found", "hint": "Reply with: ACCEPT <token>"}
        res = await _process_approval_token(tok)
        # Mark pending resolved
        try:
            from backend.services.pending_action_store import mark_resolved_by_token
            mark_resolved_by_token(tok)
        except Exception:
            pass
        return res

    # DECLINE/REJECT/DENY — acknowledge and (optionally) send modify link back
    if any(w in upper for w in ("DECLINE", "REJECT", "DENY")):
        # If we can, issue a modify token from context contained in token payload
        try:
            tok = tokens.get("approve") or tokens.get("generic")
            modify_link = None
            if tok:
                from backend.services.email_token_service import consume_token, register_token
                p = consume_token(tok)
                if p and p.get("kind") in ("ui_draft_approval",):
                    import os
                    backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
                    mod = register_token({
                        "kind": "ui_draft_modify",
                        "project_id": p.get("project_id"),
                        "description": p.get("description"),
                    }, expires_seconds=24*3600)
                    modify_link = f"{backend_url.rstrip('/')}/api/assistant/modify-email?token={mod}"
                    # Resolve the original approval token to stop reminders
                    try:
                        from backend.services.pending_action_store import mark_resolved_by_token
                        mark_resolved_by_token(tok)
                    except Exception:
                        pass
            return {"status": "ok", "action": "declined", "modify_link": modify_link}
        except Exception as e:
            logger.warning(f"Decline handling failed: {e}")
            return {"status": "ok", "action": "declined"}

    # MODIFY: capture notes and create revised plan + approval link
    if "MODIFY" in upper or "CHANGE" in upper or "REVISE" in upper:
        # Extract notes after the keyword
        m = re.search(r"(?:MODIFY|CHANGE|REVISE)[:\s]+(.+)", text, flags=re.IGNORECASE | re.DOTALL)
        notes = (m.group(1).strip() if m else "").strip()
        try:
            from backend.services.build_plan_approval_service import get_plan_approval_service, PlanStep
            from backend.services.email_token_service import register_token
            import uuid
            import os
            plan_svc = get_plan_approval_service()
            workflow_id = f"wf-mailmod-{uuid.uuid4().hex[:8]}"
            steps = [
                PlanStep(step_id="step-1", order=1, description=f"Apply requested changes: {notes[:200]}" if notes else "Apply requested changes", estimated_duration="1-2h", files_affected=[], dependencies=[], risk_level="low", verification_criteria="Updated UI reflects requested changes"),
                PlanStep(step_id="step-2", order=2, description="Regenerate UI draft and confirm", estimated_duration="1h", files_affected=[], dependencies=["step-1"], risk_level="low", verification_criteria="New draft approved"),
            ]
            plan = plan_svc.generate_plan(workflow_id=workflow_id, generated_by="email-reply-modify", objective="Revise UI per email reply", scope=notes or "Email change request", steps=steps, risks=[], dependencies_to_install=[], files_to_create=[], files_to_modify=[], files_to_delete=[], estimated_total_duration=None)
            backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
            approve = register_token({"kind": "plan_approval", "plan_id": plan.plan_id, "start_execution": True}, expires_seconds=7*24*3600)
            approve_link = f"{backend_url.rstrip('/')}/api/assistant/approve-email?token={approve}"
            return {"status": "ok", "action": "modify_plan_created", "plan_id": plan.plan_id, "approve_link": approve_link}
        except Exception as e:
            logger.error(f"Modify via email failed: {e}")
            return JSONResponse(status_code=500, content={"error": "modify_failed"})

    # No explicit command matched — new behavior: direct Todo / Note ingestion (assistant inbox deprecated)
    try:
        from backend.services.tasks_service import get_tasks_service, TasksService
        from backend.services.user_notes_service import get_notes_service, NoteType
        user_id = payload.get("user_id") or "__global__"
        content = text.strip()
        tasks_svc: TasksService = get_tasks_service()

        # Preserve NOTE/NOTES prefix even if it's not at the very start (subject may precede body)
        # Scan lines for a line beginning with NOTE: or NOTES:
        lines = [l.strip() for l in content.splitlines() if l is not None]
        note_line = None
        for l in lines:
            ll = l.lower().lstrip()
            if ll.startswith("note:") or ll.startswith("notes:"):
                note_line = l
                break

        if note_line is not None:
            try:
                ll = note_line.lstrip()
                if ll.lower().startswith("notes:"):
                    body = ll[6:].strip()
                else:
                    body = ll[5:].strip()
                title = (body[:80].strip() or "Note")
                get_notes_service().create_note(
                    workspace_id=user_id,
                    note_type=NoteType.CLARIFICATION,
                    title=title,
                    content=body,
                    tags=["email", "inbound"],
                    metadata={"from": sender}
                )
                return {"status": "ok", "action": "note_saved"}
            except Exception:
                return {"status": "error", "action": "note_failed"}

        # Treat imperatives and everything else as tasks
        task = tasks_svc.add_task(user_id, content, metadata={"source": "email", "from": sender})
        return {"status": "ok", "action": "task_added", "task": task.to_dict()}
    except Exception:
        return {"status": "ignored", "message": "ingestion_failed"}
