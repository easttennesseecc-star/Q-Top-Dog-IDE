"""
Thin LLM inference helper with optional OpenAI path and in-memory cache.
- If OPENAI_API_KEY is set, uses OpenAI Chat Completions API (gpt-4o-mini by default).
- Otherwise returns a simple echo fallback.
"""
from __future__ import annotations
import os
import json
import time
from typing import Optional, Dict

_CACHE: Dict[str, tuple[float, str]] = {}
_CACHE_TTL = float(os.getenv("CONSISTENCY_CACHE_TTL", "60"))


def llm_infer(prompt: str, max_tokens: int = 128, model: Optional[str] = None) -> str:
    key = f"{model or 'default'}::{max_tokens}::{prompt.strip()}"
    now = time.time()
    if key in _CACHE:
        ts, val = _CACHE[key]
        if now - ts < _CACHE_TTL:
            return val
    api_key = os.getenv("OPENAI_API_KEY")
    model = model or os.getenv("CONSISTENCY_MODEL", "gpt-4o-mini")
    if not api_key:
        val = f"{prompt.strip()} -> ok"
        _CACHE[key] = (now, val)
        return val
    try:
        import urllib.request
        req = urllib.request.Request("https://api.openai.com/v1/chat/completions")
        req.add_header("Authorization", f"Bearer {api_key}")
        req.add_header("Content-Type", "application/json")
        body = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.2,
        }
        data = json.dumps(body).encode("utf-8")
        with urllib.request.urlopen(req, data=data, timeout=15) as resp:
            j = json.loads(resp.read().decode("utf-8"))
            content = j["choices"][0]["message"]["content"].strip()
            _CACHE[key] = (now, content)
            return content
    except Exception:
        val = f"{prompt.strip()} -> ok"
        _CACHE[key] = (now, val)
        return val
