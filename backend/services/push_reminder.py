"""
Push Reminder Loop

Background task that checks pending actions and sends a push notification if
no response within REMINDER_PUSH_MINUTES (default 15).
"""
from __future__ import annotations

import asyncio
import os
import time
from typing import Optional
import logging

from backend.services.pending_action_store import list_pending, mark_reminder_sent
from backend.services.push_service import get_push_service

logger = logging.getLogger(__name__)


async def reminder_loop(stop_event: Optional[asyncio.Event] = None):
    try:
        interval = int(os.getenv("REMINDER_CHECK_INTERVAL_SECONDS", "60"))
        max_age_min = int(os.getenv("REMINDER_PUSH_MINUTES", "15"))
        enabled = (os.getenv("REMINDER_PUSH_ENABLED", "true").lower() in ("1","true","yes"))
    except Exception:
        interval = 60
        max_age_min = 15
        enabled = True

    logger.info(f"Push reminder loop started (enabled={enabled}, threshold={max_age_min}min, interval={interval}s)")
    while True:
        if stop_event and stop_event.is_set():
            break
        if enabled:
            try:
                now = int(time.time())
                age_sec = max_age_min * 60
                for item in list_pending():
                    if item.get("resolved_at"):
                        continue
                    if item.get("reminder_sent_at"):
                        continue
                    created = int(item.get("created_at", now))
                    if (now - created) >= age_sec:
                        # Send a gentle push reminder
                        user = item.get("user_id")
                        kind = item.get("kind")
                        token = item.get("token")
                        title = "Action pending"
                        if kind == "ui_draft_approval":
                            title = "Approve UI draft?"
                        elif kind == "plan_approval":
                            title = "Approve revised plan?"
                        body = "You can approve or request changes from your device."
                        data = {"token": token, "kind": kind}
                        try:
                            sent = get_push_service().send(user, title, body, data)
                            logger.info(f"Reminder push sent={sent} user={user} kind={kind}")
                            if isinstance(token, str) and token:
                                mark_reminder_sent(token)
                        except Exception as e:
                            logger.warning(f"Reminder push failed: {e}")
            except Exception as e:
                logger.warning(f"Reminder loop error: {e}")
        try:
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            break
        except Exception:
            # Ignore and continue
            pass
    logger.info("Push reminder loop stopped")
