"""
Away Mode Store

File-backed key-value store mapping user_id -> away phone number.
Supports a global fallback key "__global__" for system-wide away mode.
"""
from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Optional, Dict

_PATH = Path(os.getenv("AWAY_STORE_FILE", "./.away_store.json")).resolve()
_CACHE: Dict[str, str] = {}
_LOADED = False


def _load() -> None:
    global _LOADED, _CACHE
    if _LOADED:
        return
    if _PATH.exists():
        try:
            data = json.loads(_PATH.read_text())
            if isinstance(data, dict):
                _CACHE = {str(k): str(v) for k, v in data.items() if v}
        except Exception:
            _CACHE = {}
    _LOADED = True


def _save() -> None:
    try:
        _PATH.write_text(json.dumps(_CACHE))
    except Exception:
        pass


def set_away_phone(user_id: Optional[str], phone: str) -> None:
    _load()
    key = str(user_id) if user_id else "__global__"
    _CACHE[key] = str(phone)
    _save()


def clear_away_phone(user_id: Optional[str]) -> None:
    _load()
    key = str(user_id) if user_id else "__global__"
    if key in _CACHE:
        _CACHE.pop(key)
        _save()


def get_away_phone(user_id: Optional[str]) -> Optional[str]:
    _load()
    key = str(user_id) if user_id else "__global__"
    return _CACHE.get(key)


def get_away_phone_global() -> Optional[str]:
    return get_away_phone(None)
