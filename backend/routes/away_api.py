"""
Away Mode API

Endpoints to pair/unpair an away phone number and check status.
Uses session_id to resolve user_id when possible.
"""
from fastapi import APIRouter, Body, Query
from pydantic import BaseModel
from typing import Optional
from backend.services.away_store import set_away_phone, clear_away_phone, get_away_phone
from backend.services.email_token_service import register_token, consume_token
from backend.services.sms_sender import get_sms_sender
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/api/away", tags=["away"])


class PairRequest(BaseModel):
    phone: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None


@router.post("/pair")
async def pair_away(req: PairRequest):
    uid = req.user_id
    if not uid and req.session_id:
        try:
            from backend.main import get_session_user
            uid = get_session_user(req.session_id)
        except Exception:
            uid = None
    # Create a verification token and send SMS
    token = register_token({
        "kind": "away_pair_verify",
        "user_id": uid,
        "phone": req.phone,
    }, expires_seconds=30*60)
    import os
    backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
    verify_link = f"{backend_url.rstrip('/')}/api/away/verify-sms?token={token}"
    body = (
        "Q‑IDE: Tap to confirm pairing and enable SMS-first away mode.\n" 
        f"Verify: {verify_link}"
    )
    try:
        sms = get_sms_sender()
        sms.send_sms_text(req.phone, body)
    except Exception:
        pass
    return {"status": "verification_sent", "user_id": uid or "__global__", "phone": req.phone}


class UnpairRequest(BaseModel):
    user_id: Optional[str] = None
    session_id: Optional[str] = None


@router.post("/unpair")
async def unpair_away(req: UnpairRequest):
    uid = req.user_id
    if not uid and req.session_id:
        try:
            from backend.main import get_session_user
            uid = get_session_user(req.session_id)
        except Exception:
            uid = None
    clear_away_phone(uid)
    return {"status": "ok", "user_id": uid or "__global__"}


@router.get("/status")
async def away_status(user_id: Optional[str] = Query(None), session_id: Optional[str] = Query(None)):
    uid = user_id
    if not uid and session_id:
        try:
            from backend.main import get_session_user
            uid = get_session_user(session_id)
        except Exception:
            uid = None
    phone = get_away_phone(uid)
    return {"status": "ok", "user_id": uid or "__global__", "paired": bool(phone), "phone": phone}


@router.get("/verify-sms", response_class=HTMLResponse)
async def verify_sms(token: str = Query(...)):
    try:
        payload = consume_token(token)
        if not payload or payload.get("kind") != "away_pair_verify":
            return HTMLResponse(status_code=400, content="<h3>Invalid or expired link.</h3>")
        uid = payload.get("user_id")
        phone = payload.get("phone")
        if not phone:
            return HTMLResponse(status_code=400, content="<h3>Missing phone number.</h3>")
        set_away_phone(uid, phone)
        # Send welcome SMS and log it
        try:
            body = (
                "Paired with Q‑IDE. SMS-first mode is ON.\n"
                "Commands: UIDRAFT <desc>, PLAN <f1, f2>, APPROVE <plan>, MODIFY <notes>, UNPAIR."
            )
            get_sms_sender().send_sms_text(phone, body, user_id=str(uid) if uid else None)
        except Exception:
            pass
        return HTMLResponse(content=(
            "<h3>Phone paired successfully.</h3>"
            "<p>SMS-first away mode is now enabled. You can send UNPAIR by SMS anytime.</p>"
        ))
    except Exception:
        return HTMLResponse(status_code=500, content="<h3>An error occurred. Please try again.</h3>")
