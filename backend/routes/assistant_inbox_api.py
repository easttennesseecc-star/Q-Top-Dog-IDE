"""
Assistant Inbox API

Expose endpoints to list, add, and consume assistant inbox messages.
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from backend.services.assistant_inbox import add_message, list_messages, consume_message

router = APIRouter(prefix="/assistant-inbox", tags=["assistant-inbox"])


class AddPayload(BaseModel):
    user_id: str
    source: str = Field(pattern=r"^(sms|email|api|other)$", default="other")
    text: str
    metadata: Optional[Dict[str, Any]] = None


@router.post("/add")
def api_add(req: AddPayload):
    msg = add_message(req.user_id, req.source, req.text, req.metadata)
    return {"status": "ok", "message": msg}


@router.get("/list")
def api_list(user_id: Optional[str] = None, limit: int = 50, include_consumed: bool = False):
    return {"status": "ok", "messages": list_messages(user_id, limit, include_consumed)}


class ConsumePayload(BaseModel):
    id: str


@router.post("/consume")
def api_consume(req: ConsumePayload):
    msg = consume_message(req.id)
    if not msg:
        return {"status": "error", "message": "not_found"}
    return {"status": "ok", "message": msg}
