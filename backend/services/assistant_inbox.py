"""
Assistant Inbox Store

Captures non-command inbound messages (SMS/email) so they appear as an inbox
feed for the assistant. File-backed for development.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import time
import uuid
import os

_STORE_PATH = Path(os.getenv("ASSISTANT_INBOX_STORE", "./.assistant_inbox.json")).resolve()


def _load() -> Dict[str, Any]:
    try:
        if _STORE_PATH.exists():
            return json.loads(_STORE_PATH.read_text())
    except Exception:
        pass
    return {"items": []}


def _save(data: Dict[str, Any]) -> None:
    try:
        _STORE_PATH.write_text(json.dumps(data))
    except Exception:
        pass


def add_message(user_id: str, source: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    data = _load()
    items = data.get("items", [])
    msg = {
        "id": uuid.uuid4().hex,
        "user_id": user_id,
        "source": source,
        "text": text,
        "metadata": metadata or {},
        "ts": int(time.time()),
        "consumed": False,
    }
    items.append(msg)
    data["items"] = items
    _save(data)
    return msg


def list_messages(user_id: Optional[str] = None, limit: int = 50, include_consumed: bool = False) -> List[Dict[str, Any]]:
    data = _load()
    items: List[Dict[str, Any]] = data.get("items", [])
    out = []
    for m in reversed(items):  # newest first
        if user_id and m.get("user_id") != user_id:
            continue
        if not include_consumed and m.get("consumed"):
            continue
        out.append(m)
        if len(out) >= limit:
            break
    return out


def consume_message(msg_id: str) -> Optional[Dict[str, Any]]:
    data = _load()
    items = data.get("items", [])
    target = None
    for m in items:
        if m.get("id") == msg_id:
            target = m
            break
    if not target:
        return None
    if not target.get("consumed"):
        target["consumed"] = True
        _save({"items": items})
    return target
