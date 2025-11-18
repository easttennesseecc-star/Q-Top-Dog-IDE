"""Assistant Inbox (Rewritten)

Core goals of the rewritten inbox:
1. Deterministic, race-safe operations (atomic in SQLite; file-lock fallback for dev).
2. Minimal surface: add, list, consume, delete, clear.
3. No implicit triage/autopilot coupling; higher layers can decide what to do with messages.
4. Fast reads (indexed by user_id + ts) and bounded result sizes.
5. Extensible metadata (stored as JSON) without schema churn.

Environment switches:
ASSISTANT_INBOX_BACKEND=sqlite | file (default: sqlite outside test, file in tests)
ASSISTANT_INBOX_DB=./assistant_inbox.db (path for sqlite backend)
ASSISTANT_INBOX_STORE=./.assistant_inbox.json (path for file backend)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import time
import uuid
import os

_STORE_PATH = Path(os.getenv("ASSISTANT_INBOX_STORE", "./.assistant_inbox.json")).resolve()
_LOCK_PATH = _STORE_PATH.with_suffix(_STORE_PATH.suffix + ".lock")
from backend.utils.file_lock import file_lock

def _use_sqlite() -> bool:
    """Default to SQLite in non-test environments.

    Order:
    - If ASSISTANT_INBOX_BACKEND is set, honor it.
    - Else, in pytest/testing: default to file
    - Else: default to sqlite
    """
    try:
        override = os.getenv("ASSISTANT_INBOX_BACKEND")
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
        # Atomic write: write to temp file then replace
        tmp = _STORE_PATH.with_suffix(_STORE_PATH.suffix + ".tmp")
        tmp.write_text(json.dumps(data))
        os.replace(str(tmp), str(_STORE_PATH))
    except Exception:
        pass


def add_message(user_id: str, source: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if _use_sqlite():
        from backend.services.assistant_inbox_sqlite import add_message as _add
        msg = _add(user_id, source, text, metadata)
        _maybe_auto_task(msg)
        return msg
    # Serialize read-modify-write to avoid losing items under concurrent writes
    with file_lock(_LOCK_PATH, timeout=2.0):
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
    if _use_sqlite():
        from backend.services.assistant_inbox_sqlite import list_messages as _list
        return _list(user_id=user_id, limit=limit, include_consumed=include_consumed)
    # Guard reads to avoid races with writers in file backend
    with file_lock(_LOCK_PATH, timeout=2.0):
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
    if _use_sqlite():
        from backend.services.assistant_inbox_sqlite import consume_message as _consume
        return _consume(msg_id)
    # Serialize update to avoid race conditions with triage/autopilot
    with file_lock(_LOCK_PATH, timeout=2.0):
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


def delete_message(msg_id: str) -> bool:
    """Remove a message entirely. Returns True if deleted, False if not found."""
    if _use_sqlite():
        from backend.services.assistant_inbox_sqlite import delete_message as _delete
        return _delete(msg_id)
    with file_lock(_LOCK_PATH, timeout=2.0):
        data = _load()
        items = data.get("items", [])
        original_len = len(items)
        items = [m for m in items if m.get("id") != msg_id]
        if len(items) != original_len:
            _save({"items": items})
            return True
        return False


def clear_inbox(user_id: Optional[str] = None) -> int:
    """Delete all messages (optionally scoped to user). Returns count removed."""
    if _use_sqlite():
        from backend.services.assistant_inbox_sqlite import clear_inbox as _clear
        return _clear(user_id)
    with file_lock(_LOCK_PATH, timeout=5.0):
        data = _load()
        items = data.get("items", [])
        if user_id:
            remaining = [m for m in items if m.get("user_id") != user_id]
            removed = len(items) - len(remaining)
            _save({"items": remaining})
            return removed
        removed = len(items)
        _save({"items": []})
        return removed

# --- Auto TODO Ingestion -------------------------------------------------
_AUTO_ACTION_PATTERNS = [
    # leading verbs suggest an actionable task
    r"^add\b",
    r"^create\b",
    r"^implement\b",
    r"^integrate\b",
    r"^fix\b",
    r"^refactor\b",
    r"^optimi[sz]e\b",
    r"^wire\b",
    r"^setup\b|^set\s*up\b",
    r"^enable\b",
    r"^configure\b",
    r"^provision\b",
    r"^migrat(e|ion)\b",
    r"^rename\b",
    r"^clean\s*up\b",
    r"^prepare\b",
    r"^schedule\b",
]

def _classify_actionable(text: str) -> bool:
    import re
    s = (text or "").strip().lower()
    if not s:
        return False
    # skip NOTE:, FYI:, etc.
    if re.match(r"^(note|fyi|info)[:\s]", s):
        return False
    for pat in _AUTO_ACTION_PATTERNS:
        if re.match(pat, s):
            return True
    return False

def _maybe_auto_task(msg: Dict[str, Any]) -> None:
    """Create a task automatically for actionable inbox messages.

    Idempotency: relies on metadata flag 'auto_task_created'.
    """
    try:
        if not msg or msg.get("metadata", {}).get("auto_task_created"):
            return
        if not _classify_actionable(msg.get("text", "")):
            return
        from backend.services.tasks_service import get_tasks_service
        svc = get_tasks_service()
        title = msg.get("text", "").strip()[:160]
        user_id = str(msg.get("user_id") or "__global__")
        task = svc.add_task(user_id, title, metadata={"inbox_id": msg.get("id"), "source": msg.get("source")})
        # mutate metadata to reflect linkage
        try:
            meta = msg.get("metadata") or {}
            meta["auto_task_created"] = True
            meta["task_id"] = task.id
        except Exception:
            pass
    except Exception:
        # Swallow errors — inbox write path must remain robust
        pass
