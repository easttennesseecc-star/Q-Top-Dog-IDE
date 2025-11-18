# backend/assistant_routes.py
"""
Assistant orchestration endpoints that guide the user from idea → UI draft → plan approval → build.
- POST /api/assistant/ui-draft: produce a low-cost UI visual (free SVG fallback) or use configured providers
- POST /api/assistant/plan: turn features/requirements into a Build Plan (pending approval)
- POST /api/assistant/approve: approve a plan and start execution optionally
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

from backend.media_service import get_media_service, MediaType, MediaTier
from backend.services.media_requirements_resolver import resolve_requirements
from backend.services.build_plan_approval_service import (
    get_plan_approval_service,
    PlanStep,
)
try:
    if str(os.getenv("DISABLE_EMAIL", "0")).lower() in ("1","true","yes","on"):
        raise ImportError("Email disabled")
    from backend.services.email_token_service import register_token, consume_token
    EMAIL_FEATURES = True
except Exception:
    register_token = None  # type: ignore
    consume_token = None  # type: ignore
    EMAIL_FEATURES = False
from backend.services.sms_sender import get_sms_sender
from backend.services.pending_action_store import add_pending, mark_resolved_by_token
from pathlib import Path
import os

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/assistant", tags=["assistant"])


# ---- UI Draft ----
class UIDraftRequest(BaseModel):
    description: str = Field(..., description="What the UI should look like; pages, components, style")
    project_id: Optional[str] = None
    media_type: str = Field(default="image", pattern="^(image|video)$")
    resolution: Optional[str] = None
    format: Optional[str] = None
    tier: Optional[str] = Field(default=None, description="free|budget|premium; auto if omitted")
    use_oss: Optional[bool] = Field(default=True, description="Allow free/open-source fallbacks when premium not configured")
    email_to: Optional[str] = Field(default=None, description="If provided, email the draft for approval")


class UIDraftResponse(BaseModel):
    url: str
    media_type: str
    tier: str
    resolution: Optional[str] = None
    format: Optional[str] = None
    note: Optional[str] = None


@router.post("/ui-draft", response_model=UIDraftResponse)
async def create_ui_draft(req: UIDraftRequest) -> UIDraftResponse:
    try:
        try:
            mt = MediaType[req.media_type.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail="media_type must be 'image' or 'video'")
        selected_tier = None
        if req.tier:
            try:
                selected_tier = MediaTier[req.tier.upper()]
            except KeyError:
                raise HTTPException(status_code=400, detail="tier must be one of free|budget|premium")
        # Resolve defaults (size/format) if missing
        target_resolution = req.resolution
        target_format = req.format
        if not target_resolution or not target_format:
            try:
                resolved = resolve_requirements(req.project_id, req.description, mt.value)
                target_resolution = target_resolution or resolved.get("resolution")
                target_format = target_format or resolved.get("format")
            except Exception as re:
                logger.warning(f"requirements resolver failed: {re}")
        # Generate draft visual via media service (auto-fallback to free SVG)
        svc = get_media_service()
        result = await svc.generate(
            description=req.description,
            media_type=mt,
            tier=selected_tier,
            resolution=target_resolution,
            format=target_format,
        )
        note = None
        status = svc.get_provider_status()
        if result.tier.value == "free":
            note = "Using free SVG draft for cost effectiveness; configure providers for higher fidelity."
        elif result.tier.value == "premium" and not (status.get("premium", {}).get("providers", {}).get("dalle3") or status.get("premium", {}).get("providers", {}).get("runway")):
            note = "Using premium via configured proxy/provider; consider DALL·E 3 or Runway for best results."

        # Prepare one-click links upfront so we can include in SMS first
        backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
        if not EMAIL_FEATURES:
            # Skip email-token flows entirely when disabled
            approve_token = "email-disabled"
            modify_token = "email-disabled"
        else:
            approve_token = register_token({
            "kind": "ui_draft_approval",
            "project_id": req.project_id,
            "description": req.description,
            }, expires_seconds=7*24*3600)
            approve_link = f"{backend_url.rstrip('/')}/api/assistant/approve-email?token={approve_token}"
            modify_token = register_token({
            "kind": "ui_draft_modify",
            "project_id": req.project_id,
            "description": req.description,
            }, expires_seconds=7*24*3600)
            modify_link = f"{backend_url.rstrip('/')}/api/assistant/modify-email?token={modify_token}"
        # Track pending approval for reminder handling
        try:
            add_pending("ui_draft_approval", approve_token, req.project_id, {"description": req.description})
        except Exception:
            pass

        # Away mode: prefer SMS first, then email if SMS not possible or media too big
        try:
            from backend.services.away_store import get_away_phone, get_away_phone_global
            # Prefer user-specific away phone when project_id provided; else use global; else env
            sms_to = None
            if req.project_id:
                sms_to = get_away_phone(req.project_id)
            if not sms_to:
                sms_to = get_away_phone_global()
            if not sms_to:
                sms_to = os.getenv("AWAY_PHONE") or os.getenv("SMS_AWAY_TO") or os.getenv("PHONE_AWAY_NUMBER")
            if sms_to:
                sms = get_sms_sender()
                # Prefer sending an MMS snapshot when possible; fall back to SMS with links
                url_str = result.url if isinstance(result.url, str) else str(result.url)
                media_url_for_mms: Optional[str] = None
                if isinstance(url_str, str) and url_str.startswith("http"):
                    media_url_for_mms = url_str
                elif isinstance(url_str, str) and url_str.startswith("data:"):
                    # Host the inline image under /artifacts for MMS
                    try:
                        header, b64 = url_str.split(",", 1)
                        import base64
                        import uuid
                        ext = "png"
                        if "image/" in header:
                            ctype = header.split(":",1)[1].split(";",1)[0]
                            ext = {
                                "image/png": "png",
                                "image/jpeg": "jpg",
                                "image/webp": "webp",
                                "image/gif": "gif",
                            }.get(ctype, "png")
                        data = base64.b64decode(b64)
                        art_dir = Path(__file__).resolve().parent.parent / "artifacts"
                        art_dir.mkdir(exist_ok=True)
                        fname = f"ui-draft-{uuid.uuid4().hex[:8]}.{ext}"
                        (art_dir / fname).write_bytes(data)
                        media_url_for_mms = f"{backend_url.rstrip('/')}/artifacts/{fname}"
                    except Exception:
                        media_url_for_mms = None
                sms_body = (
                    f"UI draft ready. Tier={result.tier.value} Res={target_resolution} Fmt={target_format}.\n"
                    f"Approve: {approve_link}\n"
                    f"Modify: {modify_link}"
                )
                if media_url_for_mms:
                    sms.send_mms(sms_to, sms_body, media_url_for_mms, user_id=req.project_id)
                else:
                    # As a fallback, include draft link if available; otherwise just text + email will follow
                    if isinstance(url_str, str) and url_str.startswith("http"):
                        sms_body = (
                            f"UI draft ready. {url_str}\n"
                            f"Approve: {approve_link}\n"
                            f"Modify: {modify_link}"
                        )
                    sms.send_sms_text(sms_to, sms_body, user_id=req.project_id)
            else:
                pass
        except Exception as se:
            logger.warning(f"SMS send skipped/failed: {se}")

        # Optional: push notification as a supplemental channel (does not change priority order)
        try:
            from backend.services.push_service import get_push_service
            push_title = "UI draft ready"
            push_body = "Approve or request changes."
            _ = get_push_service().send(req.project_id, push_title, push_body, {
                "approve_link": approve_link,
                "modify_link": modify_link,
                "url": result.url,
            })
        except Exception:
            pass

        # Optional: email the draft for approval (preferred with attachment). Links are last resort.
        try:
            import base64
            from urllib.parse import urlparse
            if not EMAIL_FEATURES:
                raise RuntimeError("Email disabled")
            from backend.services.email_service import get_email_service
            to_addr = req.email_to or os.getenv("EMAIL_APPROVAL_TO")
            # Prefer sending email with attachment whenever an address is available
            if to_addr:
                img_bytes: Optional[bytes] = None
                filename = "ui-draft.png"
                ctype = "image/png"

                if isinstance(result.url, str) and result.url.startswith("data:"):
                    # data URI: data:image/png;base64,....
                    try:
                        header, b64 = result.url.split(",", 1)
                        if ";base64" in header:
                            if "image/" in header:
                                ctype = header.split(":",1)[1].split(";",1)[0]
                            img_bytes = base64.b64decode(b64)
                    except Exception:
                        img_bytes = None
                elif isinstance(result.url, str) and result.url.startswith("http"):
                    # Fetch the remote image
                    import aiohttp
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(result.url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                                if resp.status == 200:
                                    img_bytes = await resp.read()
                                    ctype = resp.headers.get("Content-Type", ctype)
                                    # best-effort filename from path
                                    path = urlparse(str(resp.url)).path
                                    if path and "/" in path:
                                        nm = path.rsplit("/",1)[-1]
                                        if nm:
                                            filename = nm
                    except Exception:
                        img_bytes = None

                subject = f"UI Draft for Approval — {req.project_id or 'Q-IDE'}"
                text = (
                    f"Description: {req.description}\n"
                    f"Tier: {result.tier.value}\nResolution: {target_resolution}\nFormat: {target_format}\n"
                    f"URL: {result.url}\n\n"
                    f"Quick reply by email (no links needed):\n"
                    f"ACCEPT {approve_token}\n"
                    f"DECLINE {approve_token}\n"
                    f"MODIFY {modify_token}: <your notes>\n"
                )
                html = (
                    f"<p><strong>UI Draft ready for approval</strong></p>"
                    f"<p><b>Description:</b> {req.description}</p>"
                    f"<p><b>Tier:</b> {result.tier.value} | <b>Resolution:</b> {target_resolution} | <b>Format:</b> {target_format}</p>"
                    f"<p><a href='{result.url}'>Open Draft</a></p>"
                    f"<p><a href='{approve_link}' style='background:#10b981;color:#fff;padding:8px 12px;text-decoration:none;border-radius:6px'>Approve and Build</a></p>"
                    f"<p><a href='{modify_link}' style='background:#0ea5e9;color:#fff;padding:8px 12px;text-decoration:none;border-radius:6px'>Request Changes</a></p>"
                    f"<hr><p><b>Prefer replying by email?</b> You can simply reply with:</p>"
                    f"<pre style='background:#f3f4f6;padding:8px;border-radius:6px'>ACCEPT {approve_token}\nDECLINE {approve_token}\nMODIFY {modify_token}: make primary button blue</pre>"
                )
                attachments = []
                if img_bytes:
                    attachments.append((filename, img_bytes, ctype))
                if EMAIL_FEATURES:
                    get_email_service().send(subject, [to_addr], html=html, text=text, attachments=attachments)
        except Exception as ee:
            logger.warning(f"Email send skipped/failed: {ee}")
        return UIDraftResponse(
            url=result.url,
            media_type=result.media_type.value,
            tier=result.tier.value,
            resolution=target_resolution,
            format=target_format,
            note=note,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"UI draft generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"UI draft generation failed: {str(e)}")


# ---- Plan Creation & Approval ----
class FeatureSpec(BaseModel):
    id: str
    description: str
    risk: Optional[str] = Field(default="low", pattern="^(low|medium|high)$")


class PlanInitRequest(BaseModel):
    workflow_id: str = Field(..., description="Workflow/session id for this build")
    generated_by: str = Field(default="q-assistant")
    objective: str
    scope: str
    features: List[FeatureSpec] = Field(default_factory=list)


@router.post("/plan")
async def create_plan(req: PlanInitRequest) -> Dict[str, Any]:
    try:
        svc = get_plan_approval_service()
        # Transform features into coarse PlanSteps if explicit steps are not provided
        steps: List[PlanStep] = []
        order = 1
        for f in req.features:
            steps.append(PlanStep(
                step_id=f"step-{order}",
                order=order,
                description=f"Implement feature: {f.description}",
                estimated_duration="1-2h",
                files_affected=[],
                dependencies=[],
                risk_level=f.risk or "low",
                verification_criteria=f"Unit tests pass for feature {f.id}"
            ))
            order += 1
        if not steps:
            # Provide a minimal two-step plan as a sensible default
            steps = [
                PlanStep(
                    step_id="step-1",
                    order=1,
                    description="Scaffold project and core modules",
                    estimated_duration="1h",
                    files_affected=[],
                    dependencies=[],
                    risk_level="low",
                    verification_criteria="Build passes and health checks green",
                ),
                PlanStep(
                    step_id="step-2",
                    order=2,
                    description="Implement first feature and tests",
                    estimated_duration="1-2h",
                    files_affected=[],
                    dependencies=[],
                    risk_level="low",
                    verification_criteria="Unit tests pass and endpoint returns 200",
                ),
            ]
        plan = svc.generate_plan(
            workflow_id=req.workflow_id,
            generated_by=req.generated_by,
            objective=req.objective,
            scope=req.scope,
            steps=steps,
            risks=[],
            dependencies_to_install=[],
            files_to_create=[],
            files_to_modify=[],
            files_to_delete=[],
            estimated_total_duration=None,
        )
        return plan.to_dict()
    except Exception as e:
        logger.error(f"Plan creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Plan creation failed: {str(e)}")


class PlanApproveRequest(BaseModel):
    plan_id: str
    approved_by: str = "user"
    start_execution: Optional[bool] = False


@router.post("/approve")
async def approve_plan(req: PlanApproveRequest) -> Dict[str, Any]:
    try:
        svc = get_plan_approval_service()
        plan = svc.approve_plan(req.plan_id, req.approved_by)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        assert plan is not None
        if req.start_execution:
            started = svc.start_execution(req.plan_id)
            if started:
                plan = started
        return {"message": "Plan approved", "plan": plan.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Plan approval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Plan approval failed: {str(e)}")


# --- One-click email approval endpoint ---
from fastapi.responses import HTMLResponse
from fastapi import Query, Form


@router.get("/approve-email", response_class=HTMLResponse)
async def approve_via_email(token: str = Query(..., description="Approval token from email")):
    try:
        # Re-import token consumer defensively in case module-level import was gated by env
        try:
            from backend.services.email_token_service import consume_token as _consume_token  # type: ignore
        except Exception:
            _consume_token = None  # type: ignore
        payload = _consume_token(token) if (_consume_token is not None) else None
        if not payload:
            return HTMLResponse(status_code=400, content="<h3>Invalid or expired link.</h3>")
        kind = payload.get("kind")
        if kind == "ui_draft_approval":
            # Create a simple plan and approve + start execution
            svc = get_plan_approval_service()
            import uuid
            workflow_id = f"wf-mail-{uuid.uuid4().hex[:8]}"
            desc = payload.get("description") or "User-approved UI draft"
            steps = [
                PlanStep(
                    step_id="step-1",
                    order=1,
                    description="Finalize UI assets and constraints",
                    estimated_duration="1h",
                    files_affected=[],
                    dependencies=[],
                    risk_level="low",
                    verification_criteria="UI snapshot matches draft"
                ),
                PlanStep(
                    step_id="step-2",
                    order=2,
                    description="Implement features and tests per draft",
                    estimated_duration="2h",
                    files_affected=[],
                    dependencies=[],
                    risk_level="low",
                    verification_criteria="Unit/integration tests pass"
                ),
            ]
            plan = svc.generate_plan(
                workflow_id=workflow_id,
                generated_by="email-approval",
                objective="Approved UI draft → build",
                scope=desc,
                steps=steps,
                risks=[],
                dependencies_to_install=[],
                files_to_create=[],
                files_to_modify=[],
                files_to_delete=[],
                estimated_total_duration=None,
            )
            svc.approve_plan(plan.plan_id, approved_by="email")
            svc.start_execution(plan.plan_id)
            try:
                token_val = token
                mark_resolved_by_token(token_val)
            except Exception:
                pass
            return "<h3>Approved. Your build plan is executing now.</h3>"
        elif kind == "plan_approval":
            svc = get_plan_approval_service()
            plan_id = payload.get("plan_id")
            if not plan_id:
                return HTMLResponse(status_code=400, content="<h3>Missing plan id.</h3>")
            approved_plan = svc.approve_plan(plan_id, approved_by="email")
            if not approved_plan:
                return HTMLResponse(status_code=404, content="<h3>Plan not found.</h3>")
            # Start execution if requested
            if payload.get("start_execution", True):
                svc.start_execution(plan_id)
                try:
                    mark_resolved_by_token(token)
                except Exception:
                    pass
                return "<h3>Revised plan approved. Execution has started.</h3>"
            try:
                mark_resolved_by_token(token)
            except Exception:
                pass
            return "<h3>Revised plan approved. Execution pending.</h3>"
        else:
            return HTMLResponse(status_code=400, content="<h3>Unsupported token kind.</h3>")
    except Exception as e:
        logger.error(f"Email approval failed: {e}")
        return HTMLResponse(status_code=500, content="<h3>An error occurred. Please try again.</h3>")


# --- Email-based Request Changes flow ---
@router.get("/modify-email", response_class=HTMLResponse)
async def request_changes_form(token: str = Query(..., description="Modify token from email")):
    try:
        # Always allow modify-email flow even when EMAIL_FEATURES is disabled so tests can exercise token logic.
        # Re-import token utilities unconditionally (initial module-level import may have been gated by DISABLE_EMAIL).
        try:
            from backend.services.email_token_service import consume_token, register_token  # type: ignore
        except Exception:
            consume_token = None  # type: ignore
            register_token = None  # type: ignore
        payload = consume_token(token) if (consume_token is not None) else None
        if not payload or payload.get("kind") != "ui_draft_modify":
            return HTMLResponse(status_code=400, content="<h3>Invalid or expired link.</h3>")
        # Re-issue a short-lived token to be submitted with the form
        if register_token is None:
            return HTMLResponse(status_code=500, content="<h3>Token service unavailable.</h3>")
        short_token = register_token(payload, expires_seconds=3600)
        html = f"""
        <html>
          <body style='font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial'>
            <h3>Request Changes</h3>
            <p>Describe the changes you want. We'll generate a revised plan for approval.</p>
            <form method='post' action='/api/assistant/modify-email'>
              <input type='hidden' name='token' value='{short_token}' />
              <div style='margin-bottom:10px'>
                <textarea name='changes' rows='6' style='width:100%' placeholder='Example: Make the primary button blue, add onboarding checklist, remove login for guests'></textarea>
              </div>
              <button type='submit' style='background:#0ea5e9;color:#fff;padding:8px 12px;border:none;border-radius:6px'>Submit Changes</button>
            </form>
          </body>
        </html>
        """
        return HTMLResponse(content=html)
    except Exception as e:
        logger.error(f"Render modify form failed: {e}")
        return HTMLResponse(status_code=500, content="<h3>An error occurred. Please try again.</h3>")


@router.post("/modify-email", response_class=HTMLResponse)
async def submit_changes(token: str = Form(...), changes: str = Form("")):
    try:
        # Always allow modify-email submission even when EMAIL_FEATURES is disabled; re-import token utilities.
        try:
            from backend.services.email_token_service import consume_token, register_token  # type: ignore
        except Exception:
            consume_token = None  # type: ignore
            register_token = None  # type: ignore
        payload = consume_token(token) if (consume_token is not None) else None
        if not payload or payload.get("kind") != "ui_draft_modify":
            return HTMLResponse(status_code=400, content="<h3>Invalid or expired submission.</h3>")
        desc = payload.get("description") or "UI draft"
        # Create a revised plan in pending approval state
        svc = get_plan_approval_service()
        import uuid
        import os
        workflow_id = f"wf-mod-{uuid.uuid4().hex[:8]}"
        steps = [
            PlanStep(
                step_id="step-1",
                order=1,
                description=f"Apply requested changes: {changes[:200]}" if changes else "Apply requested changes",
                estimated_duration="1-2h",
                files_affected=[],
                dependencies=[],
                risk_level="low",
                verification_criteria="Updated UI reflects requested changes",
            ),
            PlanStep(
                step_id="step-2",
                order=2,
                description="Regenerate UI draft and confirm",
                estimated_duration="1h",
                files_affected=[],
                dependencies=["step-1"],
                risk_level="low",
                verification_criteria="New draft approved",
            ),
        ]
        plan = svc.generate_plan(
            workflow_id=workflow_id,
            generated_by="email-modify",
            objective="Revise UI draft per requested changes",
            scope=f"Original: {desc}\nChanges: {changes}",
            steps=steps,
            risks=[],
            dependencies_to_install=[],
            files_to_create=[],
            files_to_modify=[],
            files_to_delete=[],
            estimated_total_duration=None,
        )
        # Issue approval link for this revised plan
        if register_token is None:
            return HTMLResponse(status_code=500, content="<h3>Token service unavailable.</h3>")
        backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
        approve_token = register_token({
            "kind": "plan_approval",
            "plan_id": plan.plan_id,
            "start_execution": True,
        }, expires_seconds=7*24*3600)
        approve_link = f"{backend_url.rstrip('/')}/api/assistant/approve-email?token={approve_token}"
        try:
            add_pending("plan_approval", approve_token, payload.get("project_id"), {"scope": f"Original: {desc}", "changes": changes})
        except Exception:
            pass
        html = f"""
        <html>
          <body style='font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial'>
            <h3>Changes received</h3>
            <p>A revised plan has been created and is pending your approval.</p>
            <p><a href='{approve_link}' style='background:#10b981;color:#fff;padding:8px 12px;text-decoration:none;border-radius:6px'>Approve Revised Plan</a></p>
          </body>
        </html>
        """
        return HTMLResponse(content=html)
    except Exception as e:
        logger.error(f"Submit modify failed: {e}")
        return HTMLResponse(status_code=500, content="<h3>An error occurred while submitting changes.</h3>")
