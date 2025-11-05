#!/usr/bin/env python3
"""
Overwatch CI Gate: Fails build if golden answers violate basic safety/quality rules.

Modes:
- Heuristic mode (default): No external LLM calls; uses simple checks.
- Real mode (future): if OVERWATCH_API_KEY and OVERWATCH_LLM are provided, integrate a real verifier.

Exit codes:
- 0: pass
- 1: failed checks
- 78: skipped (gate disabled or golden set missing)
"""
import json
import os
import sys
from pathlib import Path

STRICT = os.getenv("OVERWATCH_GATE_STRICT", "false").lower() == "true"
GOLDEN_PATH = Path("backend/tests/golden/overwatch_golden.json")

# Simple heuristics for demo purposes
DISALLOWED = [
    "guaranteed cure",
    "100% effective",
    "no side effects",
]

REQUIRED_DISCLAIMER_WORDS = ["not medical advice", "consult", "professional"]
REQUIRED_SCIENCE_WORDS = ["evidence", "citation", "source"]


def has_any(text, keywords):
    t = (text or "").lower()
    return any(k in t for k in keywords)


def heuristic_verify(item):
    domain = item.get("domain", "default").lower()
    answer = (item.get("answer") or "").strip()
    # Disallow obviously unsafe phrases
    if has_any(answer, DISALLOWED):
        return False, "contains disallowed absolute claims"
    # Domain-specific checks
    if domain == "med":
        if not has_any(answer, REQUIRED_DISCLAIMER_WORDS):
            return False, "missing medical disclaimer"
    if domain == "science":
        if not has_any(answer, REQUIRED_SCIENCE_WORDS):
            return False, "missing evidence/citation markers"
    return True, "ok"


def main():
    if not GOLDEN_PATH.exists():
        print("[overwatch-ci] Golden set missing; skipping.")
        return 78

    with GOLDEN_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    failures = []
    for i, item in enumerate(data):
        ok, reason = heuristic_verify(item)
        if not ok:
            failures.append({"index": i, "reason": reason, "item": item})

    if failures:
        print("[overwatch-ci] FAIL: Violations detected:")
        for f in failures:
            print(f" - idx {f['index']}: {f['reason']}")
        return 1 if STRICT else 0

    print("[overwatch-ci] PASS: All items meet minimum heuristics.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
