"""
SQLite-backed Pending Action Store

Switch via PENDING_ACTIONS_BACKEND=sqlite
DB path via ASSISTANT_INBOX_DB (reuse same DB for simplicity)
API mirrors file-backed version.
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_DB_PATH = Path(os.getenv("ASSISTANT_INBOX_DB", "./assistant_inbox.db")).resolve()


def _connect() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH), timeout=5, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        _init_schema(conn)
    except Exception:
        pass
    return conn


def _init_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS pending_actions (
            token TEXT PRIMARY KEY,
            kind TEXT NOT NULL,
            user_id TEXT,
            meta TEXT,
            created_at INTEGER NOT NULL,
            resolved_at INTEGER,
            reminder_sent_at INTEGER
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pending_user ON pending_actions(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pending_created ON pending_actions(created_at)")


def add_pending(kind: str, token: str, user_id: Optional[str], meta: Optional[Dict[str, Any]] = None) -> None:
    now = int(time.time())
    with _connect() as conn:
        cur = conn.cursor()
        # INSERT OR IGNORE to avoid duplicates by token
        cur.execute(
            "INSERT OR IGNORE INTO pending_actions (token, kind, user_id, meta, created_at, resolved_at, reminder_sent_at) VALUES (?,?,?,?,?,NULL,NULL)",
            (token, kind, user_id or "__global__", json.dumps(meta or {}), now),
        )


def mark_resolved_by_token(token: str) -> None:
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE pending_actions SET resolved_at = ? WHERE token = ? AND resolved_at IS NULL", (int(time.time()), token))


def mark_reminder_sent(token: str) -> None:
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE pending_actions SET reminder_sent_at = ? WHERE token = ?", (int(time.time()), token))


def list_pending() -> List[Dict[str, Any]]:
    with _connect() as conn:
        cur = conn.cursor()
        rows = cur.execute(
            "SELECT token, kind, user_id, meta, created_at, resolved_at, reminder_sent_at FROM pending_actions ORDER BY created_at DESC"
        ).fetchall()
    out: List[Dict[str, Any]] = []
    for r in rows:
        meta: Dict[str, Any] = {}
        try:
            if r["meta"]:
                meta = json.loads(r["meta"]) or {}
        except Exception:
            meta = {}
        out.append(
            {
                "kind": r["kind"],
                "token": r["token"],
                "user_id": r["user_id"],
                "meta": meta,
                "created_at": int(r["created_at"]),
                "resolved_at": int(r["resolved_at"]) if r["resolved_at"] is not None else None,
                "reminder_sent_at": int(r["reminder_sent_at"]) if r["reminder_sent_at"] is not None else None,
            }
        )
    return out
