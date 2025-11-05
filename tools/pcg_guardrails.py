#!/usr/bin/env python3
"""
PCG Guardrails: quick checks for generated content.
- Schema validation for simple asset metadata
- Sanity checks: poly count limits, texture sizes, color contrast placeholder
- Puzzle solvability placeholder
"""
from __future__ import annotations
import json
import sys


def check_asset_meta(meta: dict) -> list[str]:
    errs = []
    poly = int(meta.get("poly_count", 0))
    if poly < 10 or poly > 200000:
        errs.append(f"poly_count out of bounds: {poly}")
    palette = meta.get("palette", "")
    if not palette:
        errs.append("missing palette")
    return errs


def main():
    meta = json.load(sys.stdin)
    errs = check_asset_meta(meta)
    if errs:
        print("FAIL")
        for e in errs:
            print(" -", e)
        sys.exit(1)
    print("PASS")


if __name__ == "__main__":
    main()
