"""
Push notification sender stub.

This service looks up registered subscribers and attempts to send a push message.
Production deployments should implement platform-specific senders (FCM/APNS/WebPush).
"""
from __future__ import annotations

from typing import Any, Dict, Optional
import logging

from backend.services.push_store import list_subscribers
from backend.services.webpush_sender import send_webpush
from backend.services.push_native_senders import send_onesignal, send_fcm

logger = logging.getLogger(__name__)


class PushService:
    def __init__(self):
        pass

    def send(self, user_id: Optional[str], title: str, body: str, data: Optional[Dict[str, Any]] = None) -> int:
        subs = list_subscribers(user_id or "__global__")
        sent = 0
        for s in subs:
            try:
                platform = (s.get("platform") or "").lower()
                if platform in {"web", "webpush"} and s.get("subscription"):
                    ok = send_webpush(s["subscription"], title, body, data)
                    if ok:
                        sent += 1
                    else:
                        # fall back to no-op log
                        logger.info("Push notify (fallback log)", extra={"user_id": user_id, "title": title, "platform": platform})
                else:
                    # Try native providers if token is present
                    tok = s.get("token")
                    delivered = False
                    if tok:
                        # OneSignal first (lowest friction free tier)
                        if send_onesignal(tok, title, body, data or {}):
                            delivered = True
                        # FCM as alternative
                        elif send_fcm(tok, title, body, data or {}):
                            delivered = True
                    if delivered:
                        sent += 1
                    else:
                        # Fallback log only (maintain stub behavior by counting as sent)
                        logger.info("Push notify (token) — provider not configured", extra={
                            "user_id": user_id,
                            "title": title,
                            "platform": platform,
                        })
                        sent += 1
            except Exception as e:
                logger.warning(f"Push send failed: {e}")
        return sent


_svc: Optional[PushService] = None


def get_push_service() -> PushService:
    global _svc
    if _svc is None:
        _svc = PushService()
    return _svc
