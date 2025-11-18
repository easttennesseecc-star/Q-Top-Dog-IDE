"""
File-backed push subscriber store.

Stores per-user push tokens/endpoints so the backend can send push notifications
when available. For production, replace with a database.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List
import os

_STORE_PATH = Path(os.getenv("PUSH_SUBSCRIBERS_STORE", "./.push_subscribers.json")).resolve()

def _use_sqlite() -> bool:
    """Default to SQLite in non-test environments with env override."""
    try:
        override = os.getenv("PUSH_STORE_BACKEND")
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
    return {}


def _save(data: Dict[str, Any]) -> None:
    try:
        _STORE_PATH.write_text(json.dumps(data))
    except Exception:
        pass


def add_subscriber(user_id: str, token: str | None = None, platform: str = "web", meta: Dict[str, Any] | None = None, subscription: Dict[str, Any] | None = None) -> None:
    if _use_sqlite():
        from backend.services.push_store_sqlite import add_subscriber as _add
        return _add(user_id, token, platform, meta, subscription)
    data = _load()
    arr = data.get(user_id) or []
    entry: Dict[str, Any] = {"platform": platform, "meta": meta or {}}
    if token:
        entry["token"] = token
    if subscription:
        entry["subscription"] = subscription
    # de-duplicate by token or endpoint
    def _same(a: Dict[str, Any]) -> bool:
        if token and a.get("token") == token:
            return True
        if subscription and a.get("subscription", {}).get("endpoint") == subscription.get("endpoint"):
            return True
        return False
    if not any(_same(s) for s in arr):
        arr.append(entry)
    data[user_id] = arr
    _save(data)


def list_subscribers(user_id: str) -> List[Dict[str, Any]]:
    if _use_sqlite():
        from backend.services.push_store_sqlite import list_subscribers as _list
        return _list(user_id)
    data = _load()
    return data.get(user_id) or []


def remove_subscriber(user_id: str, token: str) -> None:
    if _use_sqlite():
        from backend.services.push_store_sqlite import remove_subscriber as _remove
        return _remove(user_id, token)
    data = _load()
    arr = data.get(user_id) or []
    arr = [s for s in arr if s.get("token") != token]
    data[user_id] = arr
    _save(data)


def list_all() -> Dict[str, Any]:
    if _use_sqlite():
        from backend.services.push_store_sqlite import list_all as _all
        return _all()
    return _load()
