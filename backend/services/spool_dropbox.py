"""
File-based dropbox (spool) for inbound SMS/Email -> Assistant input.

Design:
- One file per message to avoid file-locking complexity on Windows.
- Directory layout (default root: ./var/spool/assistant/):
  - incoming/: new messages
  - done/: processed messages (kept briefly for audit/debug)
- Message filename: {ts}-{user}-{uuid}.json
- Atomicity: write to a temp file then os.replace() into incoming.
- Retrieval: get_next(user_id) scans incoming for that user (or any if None),
  moves file to done/ and returns parsed payload.

Environment:
- ASSISTANT_SPOOL_DIR: root dir; default ./var/spool/assistant
- ASSISTANT_SPOOL_RETENTION_DAYS: how long to keep done/ files (optional)

Schema:
{
  "id": str,           # UUID
  "ts": str,           # ISO timestamp
  "user_id": str,
  "source": "sms"|"email"|"api"|"other",
  "text": str,
  "metadata": { ... }
}
"""
from __future__ import annotations
import os
import json
import uuid
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable


@dataclass
class SpoolMessage:
    id: str
    ts: str
    user_id: str
    source: str
    text: str
    metadata: Optional[Dict[str, Any]] = None


def _spool_root() -> Path:
    root = os.getenv("ASSISTANT_SPOOL_DIR", "./var/spool/assistant").strip()
    p = Path(root).resolve()
    (p / "incoming").mkdir(parents=True, exist_ok=True)
    (p / "done").mkdir(parents=True, exist_ok=True)
    return p


def enqueue(user_id: str, source: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> SpoolMessage:
    if not user_id or not text:
        raise ValueError("user_id and text are required")
    source = (source or "other").lower().strip()
    if source not in {"sms", "email", "api", "other"}:
        source = "other"
    msg = SpoolMessage(
        id=str(uuid.uuid4()),
        ts=datetime.utcnow().isoformat(),
        user_id=user_id,
        source=source,
        text=text,
        metadata=metadata or {},
    )
    root = _spool_root()
    fname = f"{int(time.time()*1000)}-{user_id}-{msg.id}.json"
    tmp = root / f"{fname}.tmp"
    dst = root / "incoming" / fname
    tmp.write_text(json.dumps(asdict(msg), ensure_ascii=False))
    os.replace(tmp, dst)
    return msg


def _matches_user(fname: str, user_id: Optional[str]) -> bool:
    if not user_id:
        return True
    # filename format: ts-user-uuid.json
    try:
        base = Path(fname).name
        parts = base.split("-")
        if len(parts) < 3:
            return False
        return parts[1] == user_id
    except Exception:
        return False


def get_next(user_id: Optional[str] = None) -> Optional[SpoolMessage]:
    root = _spool_root()
    incoming = root / "incoming"
    done = root / "done"
    # Scan oldest-first for stability
    files = sorted([p for p in incoming.glob("*.json") if _matches_user(p.name, user_id)], key=lambda p: p.name)
    if not files:
        return None
    f = files[0]
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        msg = SpoolMessage(**data)
    except Exception:
        # corrupt file, move aside and skip
        bad = done / f"bad-{f.name}"
        try:
            os.replace(f, bad)
        except Exception:
            pass
        return None
    # Move to done (at-most-once delivery)
    try:
        os.replace(f, done / f.name)
    except Exception:
        # If can't move, still return but risk duplicate; caller can de-dupe by id
        pass
    return msg


def cleanup_retention() -> int:
    """Delete old files in done/ per retention env; return count removed."""
    root = _spool_root()
    done = root / "done"
    days = float(os.getenv("ASSISTANT_SPOOL_RETENTION_DAYS", "2"))
    cutoff = datetime.utcnow() - timedelta(days=days)
    removed = 0
    for p in done.glob("*.json"):
        try:
            ts_ms = int(p.name.split("-")[0])
            ts = datetime.utcfromtimestamp(ts_ms / 1000.0)
        except Exception:
            ts = datetime.utcfromtimestamp(p.stat().st_mtime)
        if ts < cutoff:
            try:
                p.unlink()
                removed += 1
            except Exception:
                pass
    return removed

# ---------------- Background Pump -----------------
def pump_once(process: Callable[[SpoolMessage], None], user_id: Optional[str] = None) -> Optional[SpoolMessage]:
    """Fetch one message and hand it to process callback; return message or None.

    The callback must be fast or dispatch async work; errors are swallowed to keep the pump robust.
    """
    msg = get_next(user_id)
    if not msg:
        return None
    try:
        process(msg)
    except Exception:
        # swallow errors so pump loop can continue later
        pass
    return msg
