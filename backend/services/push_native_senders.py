"""
Native push senders for mobile providers (low-cost/secure): OneSignal and FCM.

These are optional; functions return True on success, False otherwise.
Configure via environment:
- OneSignal: ONESIGNAL_APP_ID, ONESIGNAL_API_KEY
- FCM legacy: FCM_SERVER_KEY
"""
from __future__ import annotations

import json
import os
import urllib.request
from typing import Any, Dict


def send_onesignal(player_id: str, title: str, body: str, data: Dict[str, Any] | None = None) -> bool:
    app_id = os.getenv("ONESIGNAL_APP_ID")
    api_key = os.getenv("ONESIGNAL_API_KEY")
    if not app_id or not api_key:
        return False
    url = "https://onesignal.com/api/v1/notifications"
    payload = {
        "app_id": app_id,
        "include_player_ids": [player_id],
        "headings": {"en": title or ""},
        "contents": {"en": body or ""},
        "data": data or {},
    }
    req = urllib.request.Request(url, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Basic {api_key}")
    try:
        with urllib.request.urlopen(req, data=json.dumps(payload).encode("utf-8"), timeout=8) as resp:
            return 200 <= resp.status < 300
    except Exception:
        return False


def send_fcm(token: str, title: str, body: str, data: Dict[str, Any] | None = None) -> bool:
    server_key = os.getenv("FCM_SERVER_KEY")
    if not server_key:
        return False
    url = "https://fcm.googleapis.com/fcm/send"
    payload = {
        "to": token,
        "notification": {"title": title or "", "body": body or ""},
        "data": data or {},
        "priority": "high",
    }
    req = urllib.request.Request(url, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"key={server_key}")
    try:
        with urllib.request.urlopen(req, data=json.dumps(payload).encode("utf-8"), timeout=8) as resp:
            return 200 <= resp.status < 300
    except Exception:
        return False
