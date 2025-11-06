"""
Assistant Inbox Triage and Autopilot

Processes assistant inbox messages and triggers actions automatically
so Q Assistant keeps working while you're away.

Rules:
- If the message already looks like a command (BUILD/DEPLOY/PLAN/UIDRAFT/MODIFY/TODO/NOTE), execute it.
- If it looks like an imperative request ("build", "create", "wire", etc.), convert to PLAN: <text>.
- If it starts with TODO/TASK, add a task.
- Otherwise treat as a note/explanation and mark consumed.

Optionally sends a brief confirmation back via SMS/email when possible.
"""
from __future__ import annotations

import os
import re
import logging
import asyncio
from typing import Dict, Any, List, Optional

from backend.services.assistant_inbox import list_messages, consume_message
from backend.services.sms_command_handler import get_sms_command_handler, SMSCommandType, SMSCommand
from backend.services.tasks_service import get_tasks_service

logger = logging.getLogger(__name__)


COMMAND_HINTS = [
    (r"^\s*build\b", "BUILD"),
    (r"^\s*deploy\b", "DEPLOY"),
    (r"^(?:ui\s*draft|draft\s*ui|wireframe)\b", "UIDRAFT"),
    (r"^\s*plan[:\s]", "PLAN"),
    (r"^\s*approve\s+", "APPROVE"),
    (r"^\s*modify[:\s]", "MODIFY"),
    (r"^\s*todo[:\s]", "TODO"),
    (r"^\s*task[:\s]", "TODO"),
    (r"^\s*note[:\s]", "NOTE"),
    # Common imperative synonyms that we normalize to PLAN below
    (r"^\s*add\b", "PLAN"),
    (r"^\s*set\s*up\b", "PLAN"),
    (r"^\s*setup\b", "PLAN"),
    (r"^\s*enable\b", "PLAN"),
    (r"^\s*configure\b", "PLAN"),
    (r"^\s*provision\b", "PLAN"),
    (r"^\s*migrat(e|ion)\b", "PLAN"),
    (r"^\s*rename\b", "PLAN"),
    (r"^\s*clean\s*up\b", "PLAN"),
    (r"^\s*hook\s*up\b", "PLAN"),
    (r"^\s*prepare\b", "PLAN"),
    (r"^\s*schedule\b", "PLAN"),
    (r"^\s*spin\s*up\b", "PLAN"),
    (r"^\s*wire\s*up\b", "PLAN"),
]


def _normalize(text: str) -> Optional[str]:
    s = (text or "").strip()
    if not s:
        return None
    low = s.lower()
    # If already prefixed with a known command, keep as-is
    for pat, token in COMMAND_HINTS:
        if re.match(pat, low):
            # Ensure canonical form with colon where needed
            if token in ("PLAN", "UIDRAFT", "MODIFY", "TODO") and ":" not in s.split(" ", 1)[0]:
                # Add colon if missing and there is trailing content
                parts = s.split(None, 1)
                if len(parts) == 2:
                    return f"{token}: {parts[1]}"
            # Map TASK -> TODO
            if token == "TODO" and not low.startswith("todo"):
                return re.sub(r"^\s*task[:\s]*", "TODO: ", s, flags=re.IGNORECASE)
            return s
    # Imperative heuristics → PLAN
    if len(s) <= 280 and re.match(r"^(please\s+)?(build|create|add|remove|implement|integrate|refactor|optimi[sz]e|wire|wire\s*up|connect|generate|ship|deploy|test|fix|setup|set\s*up|spin\s*up|enable|configure|provision|migrate|rename|clean\s*up|hook\s*up|prepare|schedule)\b", low):
        return f"PLAN: {s}"
    return None


async def triage_and_act(user_id: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
    msgs = list_messages(user_id=user_id, limit=limit, include_consumed=False)
    handler = get_sms_command_handler()
    tasks_created = 0
    acted = 0
    notes = 0
    results: List[Dict[str, Any]] = []
    for m in msgs:
        uid = m.get("user_id")
        src = m.get("source")
        text = (m.get("text") or "").strip()
        meta = m.get("metadata") or {}
        norm = _normalize(text)
        try:
            if norm:
                # Execute via SMS handler (reuses existing flows)
                phone = meta.get("phone") or meta.get("from") or "autopilot"
                res = await handler.handle_sms(norm, uid, str(phone))
                acted += 1
                results.append({"id": m.get("id"), "action": "executed", "norm": norm, "result": res})
                # Notify sender when possible
                try:
                    if src == "sms" and meta.get("phone"):
                        from backend.services.sms_sender import get_sms_sender
                        rep = (res.get("result", {}) or {}).get("reply") or "OK"
                        get_sms_sender().send_sms_text(meta.get("phone"), f"Q Assistant: {rep}")
                    elif src == "email" and meta.get("from"):
                        from backend.services.email_service import get_email_service
                        rep = (res.get("result", {}) or {}).get("reply") or f"Processed: {norm}"
                        get_email_service().send(
                            subject="Q Assistant — Update",
                            recipients=[meta.get("from")],
                            text=rep,
                            html=f"<p>{rep}</p>"
                        )
                except Exception:
                    pass
            else:
                # Not actionable → save as note (context) and skip task backlog
                try:
                    from backend.services.user_notes_service import get_notes_service, NoteType
                    get_notes_service().create_note(
                        workspace_id=uid,
                        note_type=NoteType.CLARIFICATION,
                        title=(text[:80] or "Note"),
                        content=text,
                        tags=["inbox", src],
                        metadata={"inbox_id": m.get("id")}
                    )
                    notes += 1
                    results.append({"id": m.get("id"), "action": "noted"})
                except Exception:
                    results.append({"id": m.get("id"), "action": "skipped"})
        except Exception as e:
            logger.warning(f"Autopilot failed for inbox item {m.get('id')}: {e}")
            results.append({"id": m.get("id"), "action": "error", "error": str(e)})
        finally:
            # Always consume to avoid loops
            try:
                consume_message(m.get("id"))
            except Exception:
                pass
    return {"processed": len(msgs), "acted": acted, "notes": notes, "results": results}


async def autopilot_loop(stop_event: asyncio.Event, interval_seconds: int = 30):
    """Background loop that processes assistant inbox when enabled via env.

    Enable with ASSISTANT_AUTOPILOT=true
    """
    if os.getenv("ASSISTANT_AUTOPILOT", "false").lower() not in ("1", "true", "yes"):  # quick exit
        logger.info("Assistant autopilot disabled (ASSISTANT_AUTOPILOT=false)")
        return
    logger.info("Assistant autopilot loop started")
    while not stop_event.is_set():
        try:
            await triage_and_act(user_id=None, limit=50)
        except Exception as e:
            logger.warning(f"Autopilot loop iteration failed: {e}")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval_seconds)
        except asyncio.TimeoutError:
            continue
        except Exception:
            break
    logger.info("Assistant autopilot loop stopped")
