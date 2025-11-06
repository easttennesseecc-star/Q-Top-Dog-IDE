"""
SMS Log API

Endpoints to list conversations and fetch a conversation transcript.
"""
from fastapi import APIRouter, Query
from typing import Optional
from backend.services.sms_session_log import list_conversations_for_user, get_conversation

router = APIRouter(prefix="/api/sms", tags=["sms"])


@router.get("/conversations")
async def list_conversations(user_id: Optional[str] = Query(None), session_id: Optional[str] = Query(None)):
    uid = user_id
    if not uid and session_id:
        try:
            from backend.main import get_session_user
            uid = get_session_user(session_id)
        except Exception:
            uid = None
    # None means list all; typically pass a user_id for filtering
    items = list_conversations_for_user(uid)
    return {"status": "ok", "items": items}


@router.get("/conversation")
async def get_conversation_api(phone: str = Query(...), limit: int = Query(200)):
    return {"status": "ok", "messages": get_conversation(phone, limit=limit)}
