"""
Project Prometheus Metrics
Defines counters and histograms for SLI/SLO tracking:
- http_requests_total: total requests with status labels
- llm_ttft_seconds: time to first token (TTFT)
- llm_response_seconds: end-to-end streaming response latency
- overwatch_flagged_total: responses flagged by Overwatch
Additional cost observability:
- llm_tokens_total: tokens counted by direction (in/out), labeled by model/provider
- llm_cost_usd_total: accumulated USD cost, labeled by model/provider

Reliability business SLOs:
- llm_requests_total (with failure_cost_usd label, bucketed): request outcomes with attached cost bucket
- tcu_unreliability_cost_usd_total: accumulated Total Cost of Unreliability (TCU)
"""

from __future__ import annotations

import time
from typing import Optional

try:
    from prometheus_client import Counter, Histogram, Gauge
except Exception:  # Fallback stubs if library not installed (dev only)
    class _Noop:
        def labels(self, *args, **kwargs):
            return self
        def inc(self, *args, **kwargs):
            pass
        def observe(self, *args, **kwargs):
            pass
        def set(self, *args, **kwargs):
            pass
    Counter = Histogram = Gauge = lambda *a, **k: _Noop()  # type: ignore


HTTP_REQUESTS = Counter(
    "http_requests_total",
    "HTTP requests total",
    labelnames=["endpoint", "status"],
)

LLM_TTFT = Histogram(
    "llm_ttft_seconds",
    "Time to first token (TTFT)",
    labelnames=["endpoint", "llm"],
    buckets=(0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0)
)

LLM_LATENCY = Histogram(
    "llm_response_seconds",
    "End-to-end LLM streaming response time",
    labelnames=["endpoint", "llm"],
    buckets=(0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0, 8.0, 12.0)
)

OVERWATCH_FLAGGED = Counter(
    "overwatch_flagged_total",
    "Responses flagged by Overwatch verification",
    labelnames=["endpoint", "domain", "overwatch"],
)

# Token and cost counters (labels: model name and provider source)
LLM_TOKENS = Counter(
    "llm_tokens_total",
    "Total LLM tokens by direction (in/out)",
    labelnames=["model", "provider", "direction"],  # direction in|out
)

LLM_COST_USD = Counter(
    "llm_cost_usd_total",
    "Accumulated USD cost for LLM usage",
    labelnames=["model", "provider"],
)

# Requests counter with outcome and a bucketed failure_cost_usd label.
# Note: labels are strings; we bucket to a small, fixed set to avoid high cardinality.
LLM_REQUESTS = Counter(
    "llm_requests_total",
    "LLM requests categorized by outcome and failure cost bucket",
    labelnames=["outcome", "failure_cost_usd"],
)

# Total Cost of Unreliability (TCU) in USD; no labels to keep cardinality low.
TCU_UNRELIABILITY_COST_USD = Counter(
    "tcu_unreliability_cost_usd_total",
    "Accumulated Total Cost of Unreliability (USD)",
)

# Consistency score SLI (0..1). Keep labels minimal; default label records component.
CONSISTENCY_SCORE = Gauge(
    "consistency_score",
    "Real-time consistency score across N-variant probes (0..1)",
    labelnames=["component", "plan", "data_segment"],
)

# Player Frustration Score (PFS) 0..1 (higher means more frustration)
PFS_SCORE = Gauge(
    "pfs_score",
    "Player Frustration Score (0..1)",
    labelnames=["game"],
)

# Hallucination severity (0..1), higher means worse.
HALLUCINATION_SEVERITY = Gauge(
    "hallucination_severity",
    "Hallucination severity metric (0..1), higher is worse",
    labelnames=["component", "plan", "data_segment"],
)


class Stopwatch:
    def __init__(self):
        self._start: Optional[float] = None
    def start(self):
        self._start = time.time()
        return self
    def elapsed(self) -> float:
        if self._start is None:
            return 0.0
        return time.time() - self._start


# --- Helper API ---

_COST_BUCKETS = ("0", "0.01", "1", "10", "100", "1000")

def _bucket_cost(value: float) -> str:
    try:
        v = float(value)
    except Exception:
        return "0"
    # Simple step buckets; extend if needed
    if v <= 0:
        return "0"
    if v <= 0.01:
        return "0.01"
    if v <= 1:
        return "1"
    if v <= 10:
        return "10"
    if v <= 100:
        return "100"
    return "1000"


def record_llm_request(outcome: str, failure_cost_usd: float = 0.0) -> None:
    """Record a request outcome and attach a bucketed failure cost; also add to TCU.

    outcome: "ok" | "error" | more specific labels as needed
    failure_cost_usd: numeric cost mapped to small fixed string buckets
    """
    try:
        bucket = _bucket_cost(failure_cost_usd)
        LLM_REQUESTS.labels(outcome=outcome, failure_cost_usd=bucket).inc()
        if failure_cost_usd > 0:
            TCU_UNRELIABILITY_COST_USD.inc(failure_cost_usd)
    except Exception:
        # Metrics are best-effort
        pass
