"""
SMS Log API

Endpoints to list conversations and fetch a conversation transcript.
"""
from fastapi import APIRouter, Query
from typing import Optional, List, Dict, Any
from backend.services.sms_session_log import list_conversations_for_user, get_conversation

router = APIRouter(prefix="/api/sms", tags=["sms"])


@router.get("/conversations")
async def list_conversations(user_id: Optional[str] = Query(None), session_id: Optional[str] = Query(None)):
    uid: Optional[str] = user_id
    if uid is None and session_id:
        try:
            from backend.main import get_session_user
            resolved = get_session_user(session_id)
            uid = resolved if isinstance(resolved, str) else None
        except Exception:
            uid = None
    # None means list all; underlying service expects a string; pass empty string for 'all'
    if uid is None:
        items: List[Dict[str, Any]] = list_conversations_for_user("")
    else:
        items = list_conversations_for_user(uid)
    return {"status": "ok", "user_id": uid, "items": items, "count": len(items)}


@router.get("/conversation")
async def get_conversation_api(phone: str = Query(...), limit: int = Query(200)):
    messages = get_conversation(phone, limit=limit)
    return {"status": "ok", "phone": phone, "limit": limit, "messages": messages, "count": len(messages)}
