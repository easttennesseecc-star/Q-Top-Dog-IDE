"""
SMS Sender utility

Prefers Twilio if configured, otherwise falls back to a no-op logger.
Use send_sms_text for simple messages and avoid MMS unless you host media via HTTP URL.
"""
from __future__ import annotations

import os
import logging

logger = logging.getLogger(__name__)


class _NoopSmsSender:
    def send_sms_text(self, to: str, body: str, user_id: str | None = None) -> bool:
        try:
            from backend.services.sms_session_log import log_outbound
            log_outbound(to, user_id, body, {"transport": "noop"})
        except Exception:
            pass
        logger.info(f"[SMS NOOP] to={to} body={body[:140]}...")
        return True

    def send_mms(self, to: str, body: str, media_url: str, user_id: str | None = None) -> bool:
        try:
            from backend.services.sms_session_log import log_outbound
            log_outbound(to, user_id, f"{body}\n{media_url}", {"transport": "noop", "mms": True})
        except Exception:
            pass
        logger.info(f"[MMS NOOP] to={to} media={media_url} body={body[:140]}...")
        return True


class _TwilioSmsSender:
    def __init__(self, sid: str, token: str, from_number: str):
        try:
            from twilio.rest import Client  # type: ignore
        except Exception:
            raise RuntimeError("twilio package not installed")
        self._client = Client(sid, token)
        self._from = from_number

    def send_sms_text(self, to: str, body: str, user_id: str | None = None) -> bool:
        try:
            msg = self._client.messages.create(body=body, from_=self._from, to=to)
            try:
                from backend.services.sms_session_log import log_outbound
                log_outbound(to, user_id, body, {"transport": "twilio", "sid": getattr(msg, 'sid', None)})
            except Exception:
                pass
            return bool(getattr(msg, 'sid', None))
        except Exception as e:
            logger.warning(f"Twilio SMS failed: {e}")
            return False

    def send_mms(self, to: str, body: str, media_url: str, user_id: str | None = None) -> bool:
        try:
            msg = self._client.messages.create(body=body, from_=self._from, to=to, media_url=[media_url])
            try:
                from backend.services.sms_session_log import log_outbound
                log_outbound(to, user_id, f"{body}\n{media_url}", {"transport": "twilio", "sid": getattr(msg, 'sid', None), "mms": True})
            except Exception:
                pass
            return bool(getattr(msg, 'sid', None))
        except Exception as e:
            logger.warning(f"Twilio MMS failed: {e}")
            return False


_sender = None


def get_sms_sender():
    global _sender
    if _sender is not None:
        return _sender
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_FROM")
    if sid and token and from_number:
        try:
            _sender = _TwilioSmsSender(sid, token, from_number)
            return _sender
        except Exception as e:
            logger.warning(f"Twilio not available, falling back to NOOP SMS sender: {e}")
    _sender = _NoopSmsSender()
    return _sender
