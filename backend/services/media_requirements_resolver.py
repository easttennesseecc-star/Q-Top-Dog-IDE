"""
Media Requirements Resolver

Determines target resolution and format for media generation, using (in order):
- Project-specific plan file (optional; path via env MEDIA_PLAN_JSON)
- Simple heuristics based on description and media_type

This is a lightweight hook Q Assistant/Overwatch can extend by writing a plan
JSON to the configured path or by calling into this module with richer context.
"""

from __future__ import annotations

import json
import os
from typing import Optional, Tuple, Dict


DEFAULTS = {
    "image": {"resolution": "1024x1024", "format": "png"},
    "video": {"resolution": "1280x720", "format": "mp4"},
    "audio": {"resolution": None, "format": "wav"},
}


def _load_plan() -> Dict:
    """Load a plan JSON if MEDIA_PLAN_JSON points to a file.

    Expected minimal structure:
    {
      "projects": {
        "project_id": {
          "assets": [
            {"name": "hero-image", "resolution": "1920x1080", "format": "jpg"},
            {"name": "app-icon", "resolution": "512x512", "format": "png"}
          ]
        }
      }
    }
    """
    path = os.getenv("MEDIA_PLAN_JSON")
    if not path or not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception:
        return {}


def resolve_requirements(
    project_id: Optional[str],
    description: str,
    media_type: str,
) -> Dict[str, Optional[str]]:
    """Return resolved requirements: {"resolution": str|None, "format": str|None}.

    Strategy:
    1) If plan JSON has an exact match by asset hint in description, use it.
    2) Fallback to heuristics: detect common asset names; else media-type defaults.
    """
    media_type = (media_type or "image").lower()
    plan = _load_plan()

    # 1) Try to detect by plan entries
    if project_id and plan.get("projects", {}).get(project_id):
        assets = plan["projects"][project_id].get("assets", [])
        desc_lower = description.lower()
        for asset in assets:
            name = (asset.get("name") or "").lower()
            if name and name in desc_lower:
                return {
                    "resolution": asset.get("resolution") or DEFAULTS.get(media_type, {}).get("resolution"),
                    "format": asset.get("format") or DEFAULTS.get(media_type, {}).get("format"),
                }

    # 2) Heuristics by description
    desc = description.lower()
    if any(k in desc for k in ["hero", "banner", "cover"]):
        return {"resolution": "1920x1080", "format": "jpg"}
    if any(k in desc for k in ["icon", "favicon", "logo"]):
        return {"resolution": "512x512", "format": "png"}
    if "thumbnail" in desc or "thumb" in desc:
        return {"resolution": "1280x720", "format": "jpg"}

    # 3) Defaults by media_type
    return {
        "resolution": DEFAULTS.get(media_type, {}).get("resolution"),
        "format": DEFAULTS.get(media_type, {}).get("format"),
    }
