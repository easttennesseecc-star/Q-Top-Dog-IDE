"""
Safety prefilter: rule-engine + optional OPA decision + lightweight hallucination severity.

- is_prompt_safe(prompt): fast boolean for legacy callers.
- evaluate_prompt(prompt): returns dict with {safe: bool, reasons: list[str], severity: float}
  where severity is an estimate of hallucination risk (0..1, higher is worse).
"""
from __future__ import annotations
import os
import re
import json
from typing import Dict, List

_BLOCK_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"delete\s+.*file",
    r"drop\s+database",
    r"exfiltrate|leak\s+secrets",
    r"(?:sudo|rm\s+-rf)\s+/",
    r"system32|registry\s+edit",
]

_RISKY_PHRASES = [
    r"100%\s+guarantee",
    r"definitely\s+works",
    r"undetectable",
    r"bypass\s+(?:auth|security|safety)",
    r"unlimited\s+free",
]


def estimate_hallucination_severity(text: str) -> float:
    """Heuristic severity in [0,1]: certainty language without evidence, over-claims, etc."""
    t = (text or "").lower()
    if not t.strip():
        return 0.0
    score = 0.0
    # Long outputs with no numerics/citations get a tiny bump
    if len(t) > 400 and not re.search(r"\d|https?://|\[[0-9]+\]", t):
        score += 0.15
    # Certainty / overclaim language
    for pat in _RISKY_PHRASES:
        if re.search(pat, t):
            score += 0.2
    # Suspicious directives
    for pat in _BLOCK_PATTERNS:
        if re.search(pat, t):
            score += 0.25
    # Normalize to [0,1]
    return max(0.0, min(1.0, score))


def _opa_check(prompt: str) -> (bool, List[str]):
    """Optional OPA safety decision. Returns (allow, reasons).
    Uses OPA_URL env or defaults to http://opa:8181, path /v1/data/topdog/api/allow.
    """
    opa_url = os.getenv("OPA_URL", "http://opa:8181")
    endpoint = os.getenv("OPA_SAFETY_PATH", "/v1/data/topdog/api/allow")
    url = f"{opa_url.rstrip('/')}{endpoint}"
    try:
        import urllib.request
        body = json.dumps({"input": {"prompt": prompt}}).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=0.6) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            # Support either {result: {allow: bool, reasons: []}} or {result: bool}
            result = data.get("result")
            if isinstance(result, dict):
                allow = bool(result.get("allow", True))
                reasons = result.get("reasons", []) if isinstance(result.get("reasons"), list) else []
                return allow, reasons
            return (bool(result), [])
    except Exception:
        # OPA optional; if unreachable, defer to local rules
        return True, []


def evaluate_prompt(prompt: str) -> Dict:
    p = prompt or ""
    text = p.lower()
    reasons: List[str] = []
    safe = True
    # Local blocklist
    for pat in _BLOCK_PATTERNS:
        if re.search(pat, text):
            reasons.append(f"blocked:{pat}")
            safe = False
    # OPA decision (optional)
    opa_allow, opa_reasons = _opa_check(p)
    if not opa_allow:
        safe = False
        if opa_reasons:
            reasons.extend([f"opa:{r}" for r in opa_reasons])
        else:
            reasons.append("opa:denied")
    severity = estimate_hallucination_severity(p)
    return {"safe": safe, "reasons": reasons, "severity": severity}


def is_prompt_safe(prompt: str) -> bool:
    """Legacy boolean interface used by callers."""
    return bool(evaluate_prompt(prompt).get("safe", True))
