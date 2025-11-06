"""
Email Approval Token Service

A minimal in-memory/file-backed token store for one-click approvals.
For production, replace with a durable store (DB/Redis with TTL).
"""
from __future__ import annotations

import os
import json
import time
import secrets
from pathlib import Path
from typing import Optional, Dict, Any

_STORE_PATH = Path(os.getenv("EMAIL_TOKEN_STORE", "./.email_tokens.json")).resolve()
_TOKENS: Dict[str, Dict[str, Any]] = {}
_LOADED = False

_DEF_TTL = 7 * 24 * 3600  # 7 days


def _load() -> None:
    global _LOADED, _TOKENS
    if _LOADED:
        return
    if _STORE_PATH.exists():
        try:
            data = json.loads(_STORE_PATH.read_text())
            if isinstance(data, dict):
                _TOKENS = data
        except Exception:
            _TOKENS = {}
    _LOADED = True


def _save() -> None:
    try:
        _STORE_PATH.write_text(json.dumps(_TOKENS))
    except Exception:
        pass


def register_token(payload: Dict[str, Any], expires_seconds: Optional[int] = None) -> str:
    """Register a token and return it. Payload merged with exp epoch.
    """
    _load()
    token = secrets.token_urlsafe(24)
    exp = int(time.time()) + int(expires_seconds or _DEF_TTL)
    _TOKENS[token] = {"payload": payload, "exp": exp}
    _save()
    return token


def consume_token(token: str) -> Optional[Dict[str, Any]]:
    """Return payload and delete token if valid and not expired."""
    _load()
    entry = _TOKENS.get(token)
    if not entry:
        return None
    if int(time.time()) > int(entry.get("exp", 0)):
        # expired
        _TOKENS.pop(token, None)
        _save()
        return None
    _TOKENS.pop(token, None)
    _save()
    return entry.get("payload")
