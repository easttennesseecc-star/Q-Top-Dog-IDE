"""Spool ingestion API

Purpose: Accept inbound SMS/Email (or direct API calls) and drop them into the file-based spool.
Then the assistant UI (or polling task) can fetch the next message as if user typed it.

Endpoints:
POST /spool/ingest/sms   { user_id, text, metadata? }
POST /spool/ingest/email { user_id, subject?, text, metadata? }
POST /spool/ingest/api   { user_id, text, metadata? }
GET  /spool/next-input   ?user_id=...  -> { status, message? }
POST /spool/cleanup      -> retention cleanup (optional admin)
"""
from fastapi import APIRouter, Body, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from backend.services.spool_dropbox import enqueue, get_next, cleanup_retention
from pathlib import Path
from backend.services import spool_pump
from fastapi import Request

router = APIRouter(prefix="/spool", tags=["spool"])

class BaseIngest(BaseModel):
    user_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    metadata: Optional[Dict[str, Any]] = None

class EmailIngest(BaseIngest):
    subject: Optional[str] = None

@router.post("/ingest/sms")
def ingest_sms(payload: BaseIngest):
    msg = enqueue(payload.user_id, "sms", payload.text, payload.metadata)
    return {"status": "ok", "message": msg.__dict__}

@router.post("/ingest/email")
def ingest_email(payload: EmailIngest):
    # Combine subject + text for assistant continuity
    combined = payload.text if not payload.subject else f"{payload.subject.strip()}: {payload.text}".strip()
    msg = enqueue(payload.user_id, "email", combined, payload.metadata)
    return {"status": "ok", "message": msg.__dict__}

@router.post("/ingest/api")
def ingest_api(payload: BaseIngest):
    msg = enqueue(payload.user_id, "api", payload.text, payload.metadata)
    return {"status": "ok", "message": msg.__dict__}

@router.get("/next-input")
def next_input(user_id: Optional[str] = Query(None)):
    msg = get_next(user_id)
    if not msg:
        return {"status": "empty"}
    return {"status": "ok", "message": msg.__dict__}

@router.post("/cleanup")
def spool_cleanup():
    removed = cleanup_retention()
    return {"status": "ok", "removed": removed}


@router.get("/status")
def spool_status():
    """Return queue depth (incoming), processed count (done size), and last file timestamp."""
    import os, time
    root = Path(os.getenv("ASSISTANT_SPOOL_DIR", "./var/spool/assistant")).resolve()
    incoming = root / "incoming"
    done = root / "done"
    depth = 0
    processed = 0
    last_ts = None
    if incoming.exists():
        files = list(incoming.glob("*.json"))
        depth = len(files)
        for f in files:
            try:
                ts_part = f.name.split("-")[0]
                ts_val = int(ts_part) / 1000.0
                if last_ts is None or ts_val > last_ts:
                    last_ts = ts_val
            except Exception:
                pass
    if done.exists():
        processed = len(list(done.glob("*.json")))
    return {
        "status": "ok",
        "depth": depth,
        "processed_files": processed,
        "last_message_utc": None if last_ts is None else time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(last_ts)),
    }


@router.post("/pump-once")
async def spool_pump_once(request: Request, user_id: str | None = None):
    """Trigger a single pump iteration (manual) irrespective of background loop.

    Returns empty if no message; otherwise includes orchestrate result summary.
    """
    res = await spool_pump.pump_once_async(request.app, user_id=user_id)
    return res
