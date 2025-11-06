"""
Assistant Inbox Triage API

Endpoints to manually trigger triage and to toggle autopilot.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os

from backend.services.assistant_inbox_triage import triage_and_act

router = APIRouter(prefix="/assistant-inbox", tags=["assistant-inbox-triage"])


class TriagePayload(BaseModel):
    user_id: Optional[str] = None
    limit: int = 50


@router.post("/triage")
async def api_triage(payload: TriagePayload):
    res = await triage_and_act(user_id=payload.user_id, limit=payload.limit)
    return {"status": "ok", **res}


@router.get("/autopilot/status")
def autopilot_status():
    val = os.getenv("ASSISTANT_AUTOPILOT", "false").lower() in ("1", "true", "yes")
    return {"status": "ok", "enabled": val}


class TogglePayload(BaseModel):
    enabled: bool


@router.post("/autopilot/toggle")
def autopilot_toggle(payload: TogglePayload):
    # Update env for current process only (ephemeral)
    os.environ["ASSISTANT_AUTOPILOT"] = "true" if payload.enabled else "false"
    return {"status": "ok", "enabled": payload.enabled}
