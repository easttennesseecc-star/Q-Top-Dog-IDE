"""
Pending Action Store

Tracks pending approval/modify tokens so we can send reminder push notifications
if the user doesn't respond within a timeout window (e.g., 15 minutes).

For production, replace with a database or Redis with TTL.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import os

_STORE_PATH = Path(os.getenv("PENDING_ACTIONS_STORE", "./.pending_actions.json")).resolve()

def _use_sqlite() -> bool:
    """Default to SQLite in non-test environments with env override."""
    try:
        override = os.getenv("PENDING_ACTIONS_BACKEND")
        if override:
            return override.strip().lower() == "sqlite"
        if os.getenv("PYTEST_CURRENT_TEST") or (os.getenv("ENVIRONMENT", "").strip().lower() in {"test", "testing"}):
            return False
        return True
    except Exception:
        return True


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


def add_pending(kind: str, token: str, user_id: Optional[str], meta: Optional[Dict[str, Any]] = None) -> None:
    if _use_sqlite():
        from backend.services.pending_action_store_sqlite import add_pending as _add
        return _add(kind, token, user_id, meta)
    data = _load()
    items = data.get("items", [])
    now = int(time.time())
    # Avoid duplicates by token
    if any(i.get("token") == token for i in items):
        return
    items.append({
        "kind": kind,
        "token": token,
        "user_id": user_id or "__global__",
        "meta": meta or {},
        "created_at": now,
        "resolved_at": None,
        "reminder_sent_at": None,
    })
    data["items"] = items
    _save(data)


def mark_resolved_by_token(token: str) -> None:
    if _use_sqlite():
        from backend.services.pending_action_store_sqlite import mark_resolved_by_token as _mark
        return _mark(token)
    data = _load()
    items = data.get("items", [])
    changed = False
    for i in items:
        if i.get("token") == token and i.get("resolved_at") is None:
            i["resolved_at"] = int(time.time())
            changed = True
    if changed:
        data["items"] = items
        _save(data)


def mark_reminder_sent(token: str) -> None:
    if _use_sqlite():
        from backend.services.pending_action_store_sqlite import mark_reminder_sent as _mark
        return _mark(token)
    data = _load()
    items = data.get("items", [])
    changed = False
    for i in items:
        if i.get("token") == token:
            i["reminder_sent_at"] = int(time.time())
            changed = True
    if changed:
        data["items"] = items
        _save(data)


def list_pending() -> List[Dict[str, Any]]:
    if _use_sqlite():
        from backend.services.pending_action_store_sqlite import list_pending as _list
        return _list()
    data = _load()
    return data.get("items", [])
