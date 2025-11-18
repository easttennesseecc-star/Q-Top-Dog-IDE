"""
Simple in-process rate limiter utilities for FastAPI endpoints.

Provides a Depends()-compatible factory to enforce per-key limits.
Not distributed-safe; intended for single-process/dev/test or fronted
by an API gateway with global rate limits in production.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Callable, Deque, Dict, Iterable, Optional

from fastapi import HTTPException, Request


class _Bucket:
    def __init__(self) -> None:
        self.events: Deque[float] = deque()


_buckets: Dict[str, _Bucket] = defaultdict(_Bucket)


def make_rate_limiter(
    limit: int,
    period_seconds: int,
    bucket_name: str,
    key_headers: Optional[Iterable[str]] = None,
) -> Callable[[Request], None]:
    """
    Create a FastAPI dependency that enforces a limit per request key.

    Key = f"{bucket_name}:{client_ip}" by default. Can be extended by callers
    by adding headers (e.g., X-User-Id) to bucket_name.
    """

    def _dep(request: Request) -> None:
        now = time.time()
        client_ip = request.client.host if request.client else "unknown"
        # Compose a composite key using IP plus selected headers and path params when present.
        parts = [bucket_name, client_ip]
        # Common headers we consider if present (opt-in via key_headers)
        if key_headers:
            for h in key_headers:
                try:
                    v = request.headers.get(h)
                except Exception:
                    v = None
                if v:
                    parts.append(f"{h}={v}")
        # Include common path params that often matter (e.g., invite_code)
        try:
            path_params = getattr(request, "path_params", {}) or {}
            if "invite_code" in path_params:
                parts.append(f"invite={path_params['invite_code']}")
        except Exception:
            pass
        key = ":".join(parts)
        b = _buckets[key]
        # Evict old events
        cutoff = now - period_seconds
        while b.events and b.events[0] < cutoff:
            b.events.popleft()
        if len(b.events) >= limit:
            raise HTTPException(status_code=429, detail="Too Many Requests")
        b.events.append(now)

    return _dep
