"""SQLite-backed Assistant Inbox Store (Rewritten)

Mirror the file store API with additional maintenance helpers:
- add_message(user_id, source, text, metadata) -> dict
- list_messages(user_id=None, limit=50, include_consumed=False) -> [dict]
- consume_message(msg_id) -> dict|None
- delete_message(msg_id) -> bool
- clear_inbox(user_id: str|None) -> int

Env:
- ASSISTANT_INBOX_DB (default ./assistant_inbox.db)
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

_DB_PATH = Path(os.getenv("ASSISTANT_INBOX_DB", "./assistant_inbox.db")).resolve()


def _connect() -> sqlite3.Connection:
    # Ensure parent dir exists
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH), timeout=5, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Ensure schema exists for each new connection (CREATE TABLE IF NOT EXISTS is cheap)
    try:
        _init_schema(conn)
    except Exception:
        # If schema init fails, leave it to the caller to handle
        pass
    return conn


def _init_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS inbox (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            source TEXT NOT NULL,
            text TEXT NOT NULL,
            metadata TEXT,
            ts INTEGER NOT NULL,
            consumed INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    # Indexes for common queries
    cur.execute("CREATE INDEX IF NOT EXISTS idx_inbox_user_ts ON inbox(user_id, ts DESC)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_inbox_consumed ON inbox(consumed)")
    conn.commit()


def add_message(user_id: str, source: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    import logging
    logger = logging.getLogger("assistant_inbox_sqlite")
    logger.info(f"[INBOX] add_message user_id={user_id} source={source} text={text}")
    msg_id = uuid.uuid4().hex
    ts = int(time.time())
    mjson = json.dumps(metadata or {})
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO inbox (id, user_id, source, text, metadata, ts, consumed) VALUES (?,?,?,?,?,?,0)",
            (msg_id, user_id, source, text, mjson, ts),
        )
    logger.info(f"[INBOX] add_message complete id={msg_id}")
    return {
        "id": msg_id,
        "user_id": user_id,
        "source": source,
        "text": text,
        "metadata": metadata or {},
        "ts": ts,
        "consumed": False,
    }


def list_messages(user_id: Optional[str] = None, limit: int = 50, include_consumed: bool = False) -> List[Dict[str, Any]]:
    import logging
    logger = logging.getLogger("assistant_inbox_sqlite")
    logger.info(f"[INBOX] list_messages user_id={user_id} limit={limit} include_consumed={include_consumed}")
    params: List[Any] = []
    where = []
    if user_id:
        where.append("user_id = ?")
        params.append(user_id)
    if not include_consumed:
        where.append("consumed = 0")
    sql = "SELECT id, user_id, source, text, metadata, ts, consumed FROM inbox"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY ts DESC, id DESC LIMIT ?"
    params.append(limit)
    with _connect() as conn:
        cur = conn.cursor()
        rows = cur.execute(sql, params).fetchall()
    logger.info(f"[INBOX] list_messages got {len(rows)} rows")
    out: List[Dict[str, Any]] = []
    for r in rows:
        meta: Dict[str, Any] = {}
        try:
            if r["metadata"]:
                meta = json.loads(r["metadata"]) or {}
        except Exception:
            meta = {}
        out.append(
            {
                "id": r["id"],
                "user_id": r["user_id"],
                "source": r["source"],
                "text": r["text"],
                "metadata": meta,
                "ts": int(r["ts"]),
                "consumed": bool(r["consumed"]),
            }
        )
    return out


def consume_message(msg_id: str) -> Optional[Dict[str, Any]]:
    import logging
    logger = logging.getLogger("assistant_inbox_sqlite")
    logger.info(f"[INBOX] consume_message msg_id={msg_id}")
    with _connect() as conn:
        cur = conn.cursor()
        row = cur.execute(
            "SELECT id, user_id, source, text, metadata, ts, consumed FROM inbox WHERE id = ?",
            (msg_id,),
        ).fetchone()
        if not row:
            logger.info(f"[INBOX] consume_message not found id={msg_id}")
            return None
        if not bool(row["consumed"]):
            cur.execute("UPDATE inbox SET consumed = 1 WHERE id = ?", (msg_id,))
        meta: Dict[str, Any] = {}
        try:
            if row["metadata"]:
                meta = json.loads(row["metadata"]) or {}
        except Exception:
            meta = {}
        logger.info(f"[INBOX] consume_message returning id={msg_id}")
        return {
            "id": row["id"],
            "user_id": row["user_id"],
            "source": row["source"],
            "text": row["text"],
            "metadata": meta,
            "ts": int(row["ts"]),
            "consumed": True,
        }


def delete_message(msg_id: str) -> bool:
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM inbox WHERE id = ?", (msg_id,))
        return cur.rowcount > 0


def clear_inbox(user_id: Optional[str] = None) -> int:
    with _connect() as conn:
        cur = conn.cursor()
        if user_id:
            cur.execute("DELETE FROM inbox WHERE user_id = ?", (user_id,))
        else:
            cur.execute("DELETE FROM inbox")
        return cur.rowcount or 0
