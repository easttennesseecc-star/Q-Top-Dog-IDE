"""
Pluggable LLM failover policy interfaces and simple defaults.

This module defines a Policy interface for routing between multiple LLM
providers with adaptive timeouts/backoff strategies.

Integration sketch:
- Orchestration service constructs a FailoverPolicy from config (YAML/env).
- For each request, call policy.select_endpoint(context) to choose provider.
- On failure/timeout, call policy.on_failure(...) to update state and possibly
  adjust backoff or re-route.

Note: This module is intentionally not imported at runtime yet to avoid
introducing new dependencies or behavior changes. It's ready for wiring.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any
import random


@dataclass
class Endpoint:
    name: str
    weight: float = 1.0
    timeout_sec: float = 20.0
    base_backoff_ms: int = 200
    max_backoff_ms: int = 2000


class FailoverPolicy:
    def select_endpoint(self, context: Dict[str, Any]) -> Endpoint:
        raise NotImplementedError

    def on_success(self, endpoint: Endpoint, latency_ms: float) -> None:
        pass

    def on_failure(self, endpoint: Endpoint, error: Exception | str) -> None:
        pass


class WeightedRoundRobin(FailoverPolicy):
    def __init__(self, endpoints: List[Endpoint]):
        if not endpoints:
            raise ValueError("At least one endpoint required")
        self.endpoints = endpoints
        self._cursor = 0

    def select_endpoint(self, context: Dict[str, Any]) -> Endpoint:
        total_weight = sum(max(e.weight, 0.0) for e in self.endpoints)
        if total_weight <= 0:
            return self.endpoints[0]
        r = random.random() * total_weight
        acc = 0.0
        for e in self.endpoints:
            acc += max(e.weight, 0.0)
            if r <= acc:
                return e
        return self.endpoints[-1]


class AdaptiveTimeoutWrapper(FailoverPolicy):
    """Wrap another policy and adapt timeouts based on recent latency.

    Keeps a very small window of latency observations to tweak timeout_sec.
    """

    def __init__(self, inner: FailoverPolicy, min_timeout: float = 5.0, max_timeout: float = 60.0):
        self.inner = inner
        self.min_timeout = min_timeout
        self.max_timeout = max_timeout
        self._p50_ms: float = 500.0

    def select_endpoint(self, context: Dict[str, Any]) -> Endpoint:
        e = self.inner.select_endpoint(context)
        # Adjust timeout as a function of observed p50
        suggested = max(self.min_timeout, min(self.max_timeout, (self._p50_ms / 1000.0) * 4))
        return Endpoint(
            name=e.name,
            weight=e.weight,
            timeout_sec=suggested,
            base_backoff_ms=e.base_backoff_ms,
            max_backoff_ms=e.max_backoff_ms,
        )

    def on_success(self, endpoint: Endpoint, latency_ms: float) -> None:
        # Exponential moving average to approximate p50
        alpha = 0.2
        self._p50_ms = (1 - alpha) * self._p50_ms + alpha * latency_ms

    def on_failure(self, endpoint: Endpoint, error: Exception | str) -> None:
        # Slightly increase p50 on failure to relax timeout next time
        self._p50_ms *= 1.1


def example_policy() -> FailoverPolicy:
    endpoints = [
        Endpoint("primary-llm", weight=0.7),
        Endpoint("secondary-llm", weight=0.3),
    ]
    return AdaptiveTimeoutWrapper(WeightedRoundRobin(endpoints))
