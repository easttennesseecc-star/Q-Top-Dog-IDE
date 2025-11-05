"""
Deterministic AI state helpers for esports fairness.

- Derive a reproducible seed from game state, player inputs, and agent config.
- Compute a cryptographic commitment to enable adjudication and anti-cheat audits.
- Persist optionally alongside snapshots.
"""
from __future__ import annotations
import json
import hashlib
from dataclasses import dataclass
from typing import Dict, Any


def _stable_json(data: Any) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")


def derive_seed(payload: Dict[str, Any]) -> int:
    h = hashlib.sha256()
    h.update(_stable_json(payload))
    # Use first 8 bytes as a 64-bit seed
    return int.from_bytes(h.digest()[:8], "big")


def commitment(payload: Dict[str, Any]) -> str:
    return hashlib.sha256(_stable_json(payload)).hexdigest()
