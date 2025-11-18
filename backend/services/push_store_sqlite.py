"""
SQLite-backed push subscriber store.

Switch via PUSH_STORE_BACKEND=sqlite
DB path via ASSISTANT_INBOX_DB (reuse)
API mirrors file-backed version.
"""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List

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
        CREATE TABLE IF NOT EXISTS push_subscribers (
            user_id TEXT NOT NULL,
            platform TEXT NOT NULL,
            token TEXT,
            subscription TEXT,
            meta TEXT,
            PRIMARY KEY (user_id, platform, token)
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_push_user ON push_subscribers(user_id)")


def add_subscriber(user_id: str, token: str | None = None, platform: str = "web", meta: Dict[str, Any] | None = None, subscription: Dict[str, Any] | None = None) -> None:
    tok = token or ""
    sub_json = json.dumps(subscription or {})
    meta_json = json.dumps(meta or {})
    # Upsert-like behavior: INSERT OR REPLACE (keyed by user_id, platform, token)
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO push_subscribers(user_id, platform, token, subscription, meta) VALUES (?,?,?,?,?)",
            (user_id, platform, tok, sub_json, meta_json),
        )


def list_subscribers(user_id: str) -> List[Dict[str, Any]]:
    with _connect() as conn:
        cur = conn.cursor()
        rows = cur.execute(
            "SELECT platform, token, subscription, meta FROM push_subscribers WHERE user_id = ?",
            (user_id,),
        ).fetchall()
    out: List[Dict[str, Any]] = []
    for r in rows:
        sub: Dict[str, Any] = {}
        meta: Dict[str, Any] = {}
        try:
            sub = json.loads(r["subscription"]) or {}
        except Exception:
            sub = {}
        try:
            meta = json.loads(r["meta"]) or {}
        except Exception:
            meta = {}
        ent: Dict[str, Any] = {
            "platform": r["platform"],
            "meta": meta,
        }
        if r["token"]:
            ent["token"] = r["token"]
        if sub:
            ent["subscription"] = sub
        out.append(ent)
    return out


def remove_subscriber(user_id: str, token: str) -> None:
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM push_subscribers WHERE user_id = ? AND token = ?", (user_id, token))


def list_all() -> Dict[str, Any]:
    with _connect() as conn:
        cur = conn.cursor()
        rows = cur.execute("SELECT user_id, platform, token, subscription, meta FROM push_subscribers").fetchall()
    out: Dict[str, Any] = {}
    for r in rows:
        user = r["user_id"]
        sub: Dict[str, Any] = {}
        meta: Dict[str, Any] = {}
        try:
            sub = json.loads(r["subscription"]) or {}
        except Exception:
            sub = {}
        try:
            meta = json.loads(r["meta"]) or {}
        except Exception:
            meta = {}
        ent: Dict[str, Any] = {
            "platform": r["platform"],
            "meta": meta,
        }
        if r["token"]:
            ent["token"] = r["token"]
        if sub:
            ent["subscription"] = sub
        out.setdefault(user, []).append(ent)
    return out
