"""Pricing routes providing tier metadata for frontend components.

Canonical source: backend/config/pricing_tiers.json (Aura suites)
Falls back to legacy static tiers if the JSON file is unavailable.
Also bridges current subscription tier to a suggested Aura suite.
"""

from fastapi import APIRouter, Depends, Header, HTTPException
from typing import List, Dict, Any
from datetime import datetime
from backend.models.subscription import Subscription, SubscriptionTier
from backend.database.database_service import get_db
from backend.auth import get_current_user
from pathlib import Path
import json
from backend.services.rate_limiter import RateLimiter
from backend.services.ai_auth_service import auth_service
from backend.database.tier_schema import MembershipTierSchema, TIER_CONFIGS
import os

router = APIRouter(prefix="/api", tags=["pricing"])

JSON_PATH = Path(__file__).resolve().parents[1] / "config" / "pricing_tiers.json"


def _load_aura_tiers() -> List[Dict[str, Any]]:
    """Load Aura suite tiers from canonical JSON. Returns [] on error."""
    try:
        with JSON_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


# Legacy fallback used only if JSON is missing
_LEGACY_TIERS: List[Dict[str, Any]] = [
    {
        "id": "FREE",
        "name": "Free",
        "emoji": "�",
        "price": 0,
        "description": "Starter access for evaluation",
        "features": [
            "Basic IDE",
            "Community Support",
            "Limited API Calls",
        ],
        "team_members": 1,
        "daily_api_calls": 20,
        "support_level": "Community",
        "popular": False,
    },
]


@router.get("/tiers")
async def list_tiers() -> List[Dict[str, Any]]:
    """Return all pricing tiers as a bare array (compat with PricingComparison).

    Prefers Aura suites from JSON; falls back to a minimal legacy list.
    """
    tiers = _load_aura_tiers()
    return tiers if tiers else _LEGACY_TIERS


@router.get("/tier/info")
async def get_tier_info(
    current_user: str = Depends(get_current_user),
    db=Depends(get_db),
) -> Dict[str, Any]:
    """Return user's legacy tier and suggested Aura tier.

    - legacy_tier: from Subscription.tier (FREE/PRO/TEAMS/ENTERPRISE)
    - suggested_aura_tier: mapped into Aura suites (DEV_*, MED_*, SCI_*)
    """
    legacy = SubscriptionTier.FREE
    try:
        sub = db.query(Subscription).filter(Subscription.user_id == current_user).first()
        if sub and sub.tier:
            legacy = sub.tier
    except Exception:
        # fall back silently; include warning below
        pass

    legacy_upper = legacy.value.upper()
    mapping = {
        "FREE": "DEV_FREE",
        "PRO": "DEV_PRO",
        "TEAMS": "DEV_TEAMS",
        "ENTERPRISE": "MED_ENTERPRISE",
    }
    suggested = mapping.get(legacy_upper, "DEV_FREE")

    payload = {
        "user_id": current_user,
        "legacy_tier": legacy_upper,
        "suggested_aura_tier": suggested,
        "timestamp": datetime.utcnow().isoformat(),
    }
    return payload


@router.get("/tier/limits")
async def get_tier_limits(
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> Dict[str, Any]:
    """Return current user's tier caps and today's usage.

    Auth via Authorization: Bearer <token> (marketplace auth service).
    Response shape:
    {
      success: True,
      data: {
        user_id, tier: { tier_id, name, daily_call_limit, price, ... },
        usage: { api_calls_used, llm_requests_used, code_executions_used, storage_used_gb },
        remaining: int, limit: int
      }
    }
    """
    # Extract token and resolve user
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.replace("Bearer ", "").strip()
    ok, user_id = auth_service.verify_token(token)
    if not ok or not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    rl = RateLimiter()
    tier = rl.get_user_tier(user_id)
    usage = rl.get_daily_usage(user_id) or {}

    if not tier:
        return {"success": False, "error": "No active subscription found", "user_id": user_id}

    daily_limit = tier.get("daily_call_limit", 0)
    used = int(usage.get("api_calls_used", 0))
    remaining = max(0, int(daily_limit) - used)
    # Soft warning threshold (percent of limit), default 10%
    try:
        warn_pct = float(os.getenv("RATE_LIMIT_SOFT_WARN_PCT", "10"))
    except Exception:
        warn_pct = 10.0
    soft_warning = False
    if isinstance(daily_limit, int) and daily_limit > 0:
        soft_warning = (remaining / daily_limit) * 100.0 < warn_pct

    return {
        "success": True,
        "data": {
            "user_id": user_id,
            "tier": {
                "tier_id": tier.get("tier_id"),
                "name": tier.get("name"),
                "daily_call_limit": daily_limit,
                "price": tier.get("price"),
            },
            "usage": usage,
            "limit": daily_limit,
            "used": used,
            "remaining": remaining,
            "soft_warning": soft_warning,
        },
    }


@router.post("/tier/dev/seed")
async def seed_dev_tiers(
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_dev_seed_key: str | None = Header(default=None, alias="X-Dev-Seed-Key"),
    desired_tier: str | None = None,
):
    """DEV ONLY: Seed membership tables and assign a tier to the current user.

    Guarded by X-Dev-Seed-Key matching env DEV_SEED_KEY. Not for production use.
    - Creates tables if missing
    - Upserts TIER_CONFIGS into membership_tiers
    - Ensures a user_subscriptions row for the caller (default 'pro' or 'free')
    """
    expected = os.getenv("DEV_SEED_KEY", "local-dev-seed")
    if not x_dev_seed_key or x_dev_seed_key != expected:
        raise HTTPException(status_code=403, detail="Forbidden")
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.replace("Bearer ", "").strip()
    ok, user_id = auth_service.verify_token(token)
    if not ok or not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Setup tables
    MembershipTierSchema.setup_all_tables()

    # Upsert tiers
    import sqlite3
    db = sqlite3.connect(MembershipTierSchema.get_db_path())
    cur = db.cursor()
    cols = [
        "tier_id","name","price","daily_call_limit","daily_llm_requests",
        "concurrent_sessions","storage_gb","code_execution","data_persistence",
        "webhooks","api_keys_limit","debug_logs_retention_days","custom_llms",
        "team_members","role_based_access","shared_workspaces","audit_logs",
        "resource_quotas","hipaa_ready","soc2_certified","sso_saml","data_residency",
        "custom_integrations","on_premise_deploy","account_manager","support_tier",
        "support_response_hours"
    ]
    placeholders = ",".join(["?"] * len(cols))
    update_set = ",".join([f"{c}=excluded.{c}" for c in cols if c != "tier_id"])
    sql = f"""
        INSERT INTO membership_tiers ({','.join(cols)})
        VALUES ({placeholders})
        ON CONFLICT(tier_id) DO UPDATE SET {update_set}
    """
    for cfg in TIER_CONFIGS:
        row = [cfg.get(c, None) for c in cols]
        cur.execute(sql, row)

    # Upsert user subscription
    selected_tier = (desired_tier or "pro").lower()
    cur.execute(
        """
        INSERT INTO user_subscriptions (user_id, tier_id, is_active)
        VALUES (?, ?, 1)
        ON CONFLICT(user_id) DO UPDATE SET tier_id=excluded.tier_id, is_active=1
        """,
        (user_id, selected_tier),
    )
    db.commit()
    db.close()

    return {"success": True, "message": "Dev tiers seeded and subscription set", "user_id": user_id, "tier": selected_tier}
