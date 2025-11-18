#!/usr/bin/env python3
"""
Snapshot retention utility.
- Deletes oldest snapshots beyond a max count per workflow.
- Optionally deletes snapshots older than max age (days).

Environment variables:
  SNAPSHOT_DIR         Base directory for snapshots (default: backend/data/snapshots)
  MAX_SNAPSHOTS        Max snapshots to keep per workflow (default: 100)
  MAX_AGE_DAYS         Max age in days; snapshots older are removed (default: unset)

Usage:
  python tools/snapshot_retention.py [--dry-run]
"""
from __future__ import annotations
import os
import argparse
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", help="Don't delete, just print actions")
    return p.parse_args()


def main() -> int:
    ns = parse_args()
    base = Path(os.getenv("SNAPSHOT_DIR", "backend/data/snapshots")).resolve()
    max_count = int(os.getenv("MAX_SNAPSHOTS", "100"))
    max_age_days = os.getenv("MAX_AGE_DAYS")
    max_age_secs = int(max_age_days) * 86400 if max_age_days else None

    if not base.exists():
        print(f"Snapshot dir not found: {base}")
        return 0

    now = time.time()
    removed = 0

    # Expect structure: base/<workflow_id>/*.json
    for wf_dir in sorted((d for d in base.iterdir() if d.is_dir())):
        snaps = sorted((p for p in wf_dir.glob("*.json") if p.is_file()), key=lambda p: p.stat().st_mtime)
        # Age-based pruning
        if max_age_secs is not None:
            for p in list(snaps):
                age = now - p.stat().st_mtime
                if age > max_age_secs:
                    print(f"[AGE] remove {p} (age_days={(age/86400):.1f})")
                    if not ns.dry_run:
                        p.unlink(missing_ok=True)
                    removed += 1
            snaps = [p for p in snaps if p.exists()]
        # Count-based pruning
        if len(snaps) > max_count:
            to_remove = len(snaps) - max_count
            for p in snaps[:to_remove]:
                print(f"[COUNT] remove {p}")
                if not ns.dry_run:
                    p.unlink(missing_ok=True)
                removed += 1
    print(f"Removed {removed} snapshot files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
