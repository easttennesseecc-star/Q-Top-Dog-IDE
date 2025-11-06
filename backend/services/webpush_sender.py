"""
Web Push sender using pywebpush when available.

Requires env:
- VAPID_PUBLIC_KEY (Base64URL-encoded public key)
- VAPID_PRIVATE_KEY (Base64URL-encoded private key)
- VAPID_SUBJECT (mailto: or https: URL identifying sender)

subscription example (from Push API):
{
  "endpoint": "https://fcm.googleapis.com/fcm/send/....",
  "keys": {"p256dh": "...", "auth": "..."}
}
"""
from __future__ import annotations

from typing import Any, Dict, Optional
import os
import logging

logger = logging.getLogger(__name__)

try:
    from pywebpush import webpush, WebPushException  # type: ignore
except Exception:  # pragma: no cover
    webpush = None  # type: ignore
    WebPushException = Exception  # type: ignore


def send_webpush(subscription: Dict[str, Any], title: str, body: str, data: Optional[Dict[str, Any]] = None) -> bool:
    if webpush is None:
        logger.debug("pywebpush not installed; skipping web push send")
        return False
    vapid_private = os.getenv("VAPID_PRIVATE_KEY")
    vapid_public = os.getenv("VAPID_PUBLIC_KEY")
    subject = os.getenv("VAPID_SUBJECT", "mailto:admin@example.com")
    if not vapid_private or not vapid_public:
        logger.debug("VAPID keys not configured; skipping web push send")
        return False
    payload = {
        "title": title,
        "body": body,
        "data": data or {},
    }
    try:
        webpush(
            subscription_info=subscription,
            data=str(payload),  # small JSON as string
            vapid_private_key=vapid_private,
            vapid_claims={"sub": subject},
        )
        return True
    except WebPushException as e:  # pragma: no cover
        logger.warning(f"WebPush failed: {e}")
        return False
