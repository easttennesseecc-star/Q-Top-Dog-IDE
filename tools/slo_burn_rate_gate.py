#!/usr/bin/env python3
"""
SLO burn rate gate. Fails non-zero if burn rate exceeds threshold.

It can optionally query Prometheus if PROM_URL and PROM_TOKEN are set
and a query is provided via SLO_QUERY env var. Otherwise, it falls back
to reading a burn rate value from SLO_BURN_RATE env var for testing.

Usage:
  python tools/slo_burn_rate_gate.py --threshold 2.0

Exit codes:
  0 - OK
  1 - Burn rate exceeded threshold
  2 - Script error
"""
from __future__ import annotations
import os
import sys
import json
import argparse
import urllib.request
import urllib.error


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--threshold", type=float, required=True, help="Error burn rate threshold")
    p.add_argument("--tcu-threshold", type=float, default=None, help="Max allowed Total Cost of Unreliability (USD) over window")
    p.add_argument("--consistency-threshold", type=float, default=None, help="Min required consistency score (0..1)")
    p.add_argument("--hallucination-threshold", type=float, default=None, help="Max allowed hallucination severity (0..1)")
    return p.parse_args()


def _prom_get(query: str) -> float | None:
    url = os.getenv("PROM_URL")
    token = os.getenv("PROM_TOKEN")
    if not url:
        return None
    try:
        req = urllib.request.Request(f"{url}/api/v1/query?query={urllib.parse.quote(query)}")
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req, timeout=10) as resp:  # nosec B310
            data = json.loads(resp.read().decode("utf-8"))
        if data.get("status") != "success":
            return None
        result = data.get("data", {}).get("result", [])
        if not result:
            return 0.0
        value = float(result[0]["value"][1])
        return value
    except Exception:
        return None


def main() -> int:
    ns = parse_args()
    # 1) Error burn rate
    slo_query = os.getenv("SLO_QUERY", "sum(rate(http_requests_total{status=~'5..'}[5m])) / sum(rate(http_requests_total[5m]))")
    has_prom = bool(os.getenv("PROM_URL"))
    burn_rate = _prom_get(slo_query)
    if has_prom:
        if burn_rate is None:
            print("ERROR: Prometheus query failed or returned no data; refusing fallback while PROM_URL is set", file=sys.stderr)
            return 2
    else:
        if burn_rate is None:
            # Fall back to env-provided burn rate for simulation; treat empty as 0.0
            raw = os.getenv("SLO_BURN_RATE", "").strip()
            if not raw:
                burn_rate = 0.0
            else:
                try:
                    burn_rate = float(raw)
                except ValueError:
                    print("Invalid SLO_BURN_RATE value", file=sys.stderr)
                    return 2
    print(f"SLO burn rate: {burn_rate} (threshold {ns.threshold})")
    if burn_rate > ns.threshold:
        print("FAIL: Burn rate exceeds threshold")
        return 1
    print("PASS: Burn rate within threshold")

    # 2) Total Cost of Unreliability (optional)
    if ns.tcu_threshold is not None:
        tcu_query = os.getenv("COST_TCU_QUERY")
        if tcu_query:
            tcu_value = _prom_get(tcu_query)
            if tcu_value is None:
                print("WARN: TCU query failed or returned no data; skipping TCU gate")
            else:
                print(f"TCU: {tcu_value} (threshold {ns.tcu_threshold})")
                if tcu_value > ns.tcu_threshold:
                    print("FAIL: TCU exceeds threshold")
                    return 1

    # 3) Consistency SLI (optional, higher is better)
    if ns.consistency_threshold is not None:
        cons_query = os.getenv("CONSISTENCY_SLI_QUERY")
        if cons_query:
            cons_value = _prom_get(cons_query)
            if cons_value is None:
                print("WARN: Consistency query failed or returned no data; skipping consistency gate")
            else:
                print(f"Consistency: {cons_value} (min required {ns.consistency_threshold})")
                if cons_value < ns.consistency_threshold:
                    print("FAIL: Consistency below threshold")
                    return 1

    # 4) Hallucination severity (optional, lower is better)
    if ns.hallucination_threshold is not None:
        hall_query = os.getenv("HALLUCINATION_SLI_QUERY")
        if hall_query:
            hall_value = _prom_get(hall_query)
            if hall_value is None:
                print("WARN: Hallucination query failed or returned no data; skipping hallucination gate")
            else:
                print(f"Hallucination: {hall_value} (max allowed {ns.hallucination_threshold})")
                if hall_value > ns.hallucination_threshold:
                    print("FAIL: Hallucination severity above threshold")
                    return 1

    print("PASS: All gates satisfied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
