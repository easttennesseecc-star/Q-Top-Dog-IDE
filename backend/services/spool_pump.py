"""Spool background pump

Pulls messages from the file-based spool and invokes the internal orchestrator via ASGI.
Enabled with env ASSISTANT_SPOOL_PUMP=true (disabled by default and during tests).

Also exposes a single-shot pump_once_async(app, user_id) used by the /spool/pump-once endpoint.
"""
from __future__ import annotations
import os
import time
import asyncio
from typing import Optional, Dict, Any
from .spool_dropbox import SpoolMessage, pump_once as spool_pump_once

# Use httpx with ASGI transport to call the app-internal /agent/orchestrate endpoint
import httpx

# Optional Prometheus metrics (best-effort; ignored if library unavailable)
try:
    from prometheus_client import Counter, Summary
    SPOOL_PUMP_MESSAGES = Counter(
        "spool_pump_messages_total",
        "Total messages processed by spool pump",
        labelnames=("status",),
    )
    SPOOL_PUMP_FAILURES = Counter(
        "spool_pump_failures_total",
        "Total failures in spool pump orchestration",
    )
    SPOOL_PUMP_LATENCY = Summary(
        "spool_pump_orchestrate_seconds",
        "Latency of orchestrate call triggered by spool pump",
    )
except Exception:
    SPOOL_PUMP_MESSAGES = None  # type: ignore
    SPOOL_PUMP_FAILURES = None  # type: ignore
    SPOOL_PUMP_LATENCY = None  # type: ignore

async def _orchestrate_via_asgi(app, payload: Dict[str, Any]) -> Dict[str, Any]:
    from httpx import ASGITransport
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://app.local") as client:
        start = time.perf_counter()
        resp = await client.post("/agent/orchestrate", json=payload, timeout=10.0)
        dur = time.perf_counter() - start
        try:
            if SPOOL_PUMP_LATENCY is not None:
                SPOOL_PUMP_LATENCY.observe(dur)
        except Exception:
            pass
        try:
            return resp.json()
        except Exception:
            return {"status": "error", "message": f"bad response: {resp.status_code}", "body": resp.text}


def _build_payload_from_message(msg: SpoolMessage) -> Dict[str, Any]:
    return {
        "task_type": "inbound_message",
        "input_data": {
            "prompt": msg.text,
            "source": msg.source,
            "user_id": msg.user_id,
            "metadata": msg.metadata or {},
        },
    }

async def pump_once_async(app, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Process a single message from the spool.

    Optimizations / robustness:
    - Avoid building two payloads (previous version duplicated work).
    - Fail fast with structured error if orchestrate call times out.
    - Metric labeling preserved; failures increment failure counter.
    """
    msg = spool_pump_once(lambda m: None, user_id=user_id)
    if not msg:
        return {"status": "empty"}
    payload = _build_payload_from_message(msg)
    try:
        result = await _orchestrate_via_asgi(app, payload)
    except Exception as e:
        try:
            if SPOOL_PUMP_FAILURES is not None:
                SPOOL_PUMP_FAILURES.inc()
        except Exception:
            pass
        return {"status": "error", "error": str(e), "message": {
            "id": msg.id, "user_id": msg.user_id, "source": msg.source, "text": msg.text, "metadata": msg.metadata, "ts": msg.ts
        }}
    try:
        if SPOOL_PUMP_MESSAGES is not None:
            SPOOL_PUMP_MESSAGES.labels(status=str(result.get("status", "ok"))).inc()
    except Exception:
        pass
    return {"status": "ok", "orchestrate": result, "message": {
        "id": msg.id, "user_id": msg.user_id, "source": msg.source, "text": msg.text, "metadata": msg.metadata, "ts": msg.ts
    }}

async def pump_loop(app, stop_event: asyncio.Event, interval_seconds: float = 0.5):
    # Rate limit: max messages per minute
    try:
        max_per_min = int(os.getenv("ASSISTANT_SPOOL_RATE_PER_MIN", "60"))
    except Exception:
        max_per_min = 60
    window_start = time.time()
    processed_in_window = 0
    # Exponential backoff on failure
    backoff = 0.0
    max_backoff = float(os.getenv("ASSISTANT_SPOOL_BACKOFF_MAX_SECONDS", "5"))
    while not stop_event.is_set():
        now = time.time()
        if now - window_start >= 60.0:
            window_start = now
            processed_in_window = 0
        if processed_in_window >= max_per_min:
            await asyncio.sleep(0.25)
            continue
        try:
            res = await pump_once_async(app)
            if res.get("status") == "ok":
                processed_in_window += 1
                backoff = 0.0
                await asyncio.sleep(interval_seconds)
            else:
                await asyncio.sleep(max(interval_seconds, 0.25))
        except asyncio.CancelledError:
            break
        except Exception:
            try:
                if SPOOL_PUMP_FAILURES is not None:
                    SPOOL_PUMP_FAILURES.inc()
            except Exception:
                pass
            backoff = 1.0 if backoff == 0.0 else min(max_backoff, backoff * 2.0)
            await asyncio.sleep(backoff)


def is_enabled_in_env() -> bool:
    val = os.getenv("ASSISTANT_SPOOL_PUMP", "false").strip().lower()
    return val in ("1", "true", "yes")
