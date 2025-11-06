"""
SMS Session Log

File-backed JSONL log per phone number capturing inbound/outbound messages.
Utility functions to log events and query recent conversations.
"""
from __future__ import annotations

import os
import json
import time
from pathlib import Path
from typing import Optional, Dict, List

_ROOT = Path(os.getenv("SMS_LOG_DIR", "./.sms_logs")).resolve()
_ROOT.mkdir(exist_ok=True)


def _phone_key(phone: str) -> str:
    return ''.join(ch for ch in str(phone) if ch.isdigit() or ch == '+') or 'unknown'


def _file_for(phone: str) -> Path:
    return _ROOT / f"{_phone_key(phone)}.jsonl"


def log_inbound(phone: str, user_id: Optional[str], body: str, meta: Optional[Dict] = None) -> None:
    _write_event(phone, {
        "ts": time.time(),
        "dir": "in",
        "phone": phone,
        "user_id": user_id,
        "body": body,
        "meta": meta or {},
    })


def log_outbound(phone: str, user_id: Optional[str], body: str, meta: Optional[Dict] = None) -> None:
    _write_event(phone, {
        "ts": time.time(),
        "dir": "out",
        "phone": phone,
        "user_id": user_id,
        "body": body,
        "meta": meta or {},
    })


def _write_event(phone: str, event: Dict) -> None:
    f = _file_for(phone)
    try:
        with f.open('a', encoding='utf-8') as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass


def get_conversation(phone: str, limit: int = 200) -> List[Dict]:
    f = _file_for(phone)
    if not f.exists():
        return []
    try:
        lines = f.read_text(encoding='utf-8').splitlines()[-limit:]
        return [json.loads(x) for x in lines if x.strip()]
    except Exception:
        return []


def list_conversations_for_user(user_id: str, max_items: int = 50) -> List[Dict]:
    # Simple scan to find files with last event matching user_id
    items: List[Dict] = []
    try:
        for f in sorted(_ROOT.glob('*.jsonl')):
            try:
                last = None
                with f.open('r', encoding='utf-8') as fh:
                    for line in fh:
                        if line.strip():
                            last = json.loads(line)
                if last and (last.get('user_id') == user_id or user_id is None):
                    items.append({
                        "phone": f.stem,
                        "last_ts": last.get('ts'),
                        "last_dir": last.get('dir'),
                        "last_body": last.get('body'),
                    })
            except Exception:
                continue
    except Exception:
        pass
    # Return most recent first
    items.sort(key=lambda x: x.get('last_ts') or 0, reverse=True)
    return items[:max_items]
