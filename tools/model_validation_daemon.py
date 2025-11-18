#!/usr/bin/env python3
"""
Model Validation Daemon (skeleton): monitors Prometheus for consistency_score
and triggers a retrain webhook when the sustained average falls below threshold.

Env:
- PROM_URL, PROM_TOKEN
- CONSISTENCY_SLI_QUERY (e.g., avg_over_time(consistency_score[1h]))
- RETRAIN_WEBHOOK_URL
- THRESHOLD (default 0.9)
- CONSECUTIVE_FAILS (default 7)
"""
from __future__ import annotations
import os
import time
import json
import urllib.request


def prom_get(query: str) -> float | None:
    url = os.getenv("PROM_URL")
    tok = os.getenv("PROM_TOKEN")
    if not url:
        return None
    req = urllib.request.Request(f"{url}/api/v1/query?query={urllib.parse.quote(query)}")
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if data.get("status") != "success":
            return None
        res = data.get("data", {}).get("result", [])
        if not res:
            return None
        return float(res[0]["value"][1])
    except Exception:
        return None


def trigger_webhook():
    url = os.getenv("RETRAIN_WEBHOOK_URL")
    if not url:
        return False
    req = urllib.request.Request(url, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, data=b"{}", timeout=10) as resp:
            return 200 <= resp.getcode() < 300
    except Exception:
        return False


def main():
    q = os.getenv("CONSISTENCY_SLI_QUERY", "avg_over_time(consistency_score[24h])")
    threshold = float(os.getenv("THRESHOLD", "0.9"))
    consecutive = int(os.getenv("CONSECUTIVE_FAILS", "7"))
    fails = 0
    while True:
        v = prom_get(q)
        if v is not None and v < threshold:
            fails += 1
        else:
            fails = 0
        if fails >= consecutive:
            trigger_webhook()
            fails = 0
        time.sleep(3600)


if __name__ == "__main__":
    main()
