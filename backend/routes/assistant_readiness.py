"""
Assistant Readiness and Capabilities Endpoint

Verifies that Q Assistant's core components are operational and aligned with
the intelligence pipeline (autopilot retired). Returns a structured report
covering storage backends, plan approval, LLM pool visibility, and comms.
"""
from __future__ import annotations

import os
import uuid
from typing import Any, Dict
from fastapi import APIRouter

"""Assistant readiness now validates the file-based spool instead of the legacy inbox.

The legacy assistant inbox (SQLite/file) has been deprecated in favor of a
simple file-based spool (`spool_dropbox`) plus a background pump. For
backward compatibility with existing tests and clients, the readiness payload
still exposes the key `inbox`, but `backend` will report `spool` and the probe
logic uses enqueue/get_next from the new subsystem.
"""
try:
    from backend.services.spool_dropbox import enqueue, get_next
except Exception:  # pragma: no cover - defensive fallback
    enqueue = None  # type: ignore
    get_next = None  # type: ignore

router = APIRouter(prefix="/assistant", tags=["assistant-readiness"])


def _inbox_backend_name() -> str:
    """Return the active backend label for readiness reporting.

    Always returns 'spool' now that the legacy inbox is removed. Retains the
    function for minimal code churn and clarity.
    """
    return "spool"


def _check_inbox() -> Dict[str, Any]:
    """Probe the file-based spool by enqueueing and immediately attempting retrieval.

    Uses a user-specific probe id to avoid interfering with real messages.
    If enqueue/get_next are unavailable, reports degraded status.
    """
    backend = _inbox_backend_name()
    uid = f"readiness-{uuid.uuid4().hex[:8]}"
    if enqueue is None or get_next is None:
        return {"ok": False, "backend": backend, "error": "spool subsystem unavailable"}
    try:
        msg = enqueue(uid, "api", "readiness probe", {"kind": "probe"})
        retrieved = get_next(uid)
        probe_seen = bool(retrieved and retrieved.id == msg.id)
        return {"ok": probe_seen, "backend": backend, "probe_seen": probe_seen}
    except Exception as e:
        return {"ok": False, "backend": backend, "error": str(e)}


def _check_plan_approval() -> Dict[str, Any]:
    try:
        from backend.services.build_plan_approval_service import get_plan_approval_service, PlanStep
        from pathlib import Path
        import json
        svc = get_plan_approval_service()
        wf = f"wf-readiness-{uuid.uuid4().hex[:8]}"
        step = PlanStep(
            step_id="step-1",
            order=1,
            description="readiness noop",
            estimated_duration="1min",
            files_affected=[],
            dependencies=[],
            risk_level="low",
            verification_criteria="created and readable",
        )
        plan = svc.generate_plan(
            workflow_id=wf,
            generated_by="readiness",
            objective="validate plan store",
            scope="noop",
            steps=[step],
        )
        # Verify we can read it back
        ok = svc.get_plan(plan.plan_id) is not None
        # Cleanup: delete plan file and update index
        try:
            plan_file = svc._get_plan_file(plan.plan_id)  # type: ignore[attr-defined]
            if plan_file.exists():
                plan_file.unlink()
            # Remove from index
            idx_path = svc.index_file  # type: ignore[attr-defined]
            if Path(idx_path).exists():
                idx = json.loads(Path(idx_path).read_text())
                if plan.plan_id in idx:
                    idx.pop(plan.plan_id, None)
                    Path(idx_path).write_text(json.dumps(idx, indent=2))
        except Exception:
            pass
        return {"ok": ok}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _check_llm_pool() -> Dict[str, Any]:
    try:
        from backend.llm_pool import build_llm_report
        rep = build_llm_report()
        return {
            "ok": True,
            "available": len(rep.get("available", [])),
            "excluded": len(rep.get("excluded", [])),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _check_comms() -> Dict[str, Any]:
    """Report status of comms subsystems (email/SMS/push) with feature gating.

    Logic:
    - Email: enabled when DISABLE_EMAIL not true AND email service import succeeds.
    - SMS: present when Twilio creds exist OR a mock sender is configured.
    - Push: import push_store to validate persistence layer access.
    Provides individual component ok plus overall comms ok (non-blocking for readiness overall).
    """
    email_disabled = str(os.getenv("DISABLE_EMAIL", "0")).lower() in ("1","true","yes","on")
    if email_disabled:
        email_enabled = False
    else:
        try:
            from backend.services.email_service import get_email_service  # noqa: F401
            email_enabled = True
        except Exception:
            email_enabled = False
    # SMS availability: Twilio creds OR fallback/mock sender
    twilio_present = all(os.getenv(k) for k in ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_FROM"))
    try:
        from backend.services.sms_sender import get_sms_sender
        sms_sender = get_sms_sender()
        sms_available = bool(twilio_present or sms_sender)
    except Exception:
        sms_available = False
    # Push availability
    try:
        from backend.services.push_store import list_all  # noqa: F401
        push_ok = True
    except Exception:
        push_ok = False
    return {
        "ok": any([email_enabled, sms_available, push_ok]),
        "email": {"enabled": email_enabled, "disabled_flag": email_disabled},
        "sms": {"available": sms_available, "twilio": twilio_present},
        "push": {"available": push_ok},
    }


@router.get("/readiness")
async def assistant_readiness(dry_run: bool = False):
    """Return a readiness report for Q Assistant's core capabilities.

    When dry_run=true, also performs a sample PLAN command execution via the
    SMS command handler and cleans up the generated plan.
    """
    inbox = _check_inbox()
    plan = _check_plan_approval()
    llm = _check_llm_pool()
    comms = _check_comms()
    # Optional: expose configured flags for transparency
    flags = {
        "spool_pump_enabled": str(os.getenv("ASSISTANT_SPOOL_PUMP", "false")).lower() in ("1","true","yes"),
        "email_disabled": str(os.getenv("DISABLE_EMAIL", "0")).lower() in ("1","true","yes","on"),
        "reminder_loop_enabled": str(os.getenv("REMINDER_LOOP_ENABLED", "true")).lower() in ("1","true","yes"),
    }
    sample: Dict[str, Any] = {"performed": False}
    if dry_run:
        try:
            from backend.services.sms_command_handler import get_sms_command_handler
            from backend.services.build_plan_approval_service import get_plan_approval_service
            import json
            from pathlib import Path
            uid = f"readiness-{uuid.uuid4().hex[:8]}"
            handler = get_sms_command_handler()
            res = await handler.handle_sms("PLAN: readiness sample feature", uid, "readiness")
            plan_id = (res.get("result", {}) or {}).get("plan_id")
            ok = bool(plan_id)
            # Cleanup plan artifact
            try:
                svc = get_plan_approval_service()
                if plan_id:
                    pf = svc._get_plan_file(plan_id)  # type: ignore[attr-defined]
                    if pf.exists():
                        pf.unlink()
                    idx_path = svc.index_file  # type: ignore[attr-defined]
                    if Path(idx_path).exists():
                        idx = json.loads(Path(idx_path).read_text())
                        if plan_id in idx:
                            idx.pop(plan_id, None)
                            Path(idx_path).write_text(json.dumps(idx, indent=2))
            except Exception:
                pass
            sample = {"performed": True, "ok": ok, "plan_id": plan_id}
        except Exception as e:
            sample = {"performed": True, "ok": False, "error": str(e)}
    deprecated = {"autopilot": "retired"}
    overall = all([
        inbox.get("ok", False),
        plan.get("ok", False),
        llm.get("ok", False),
        comms.get("ok", True),
    ])
    return {
        "status": "ok" if overall else "degraded",
        "inbox": inbox,
        "plan_store": plan,
        "llm_pool": llm,
        "comms": comms,
        "flags": flags,
        "sample_plan": sample,
        "deprecated": deprecated,
        "note": "Autopilot is deprecated; realtime intelligence handles actions on demand.",
    }
