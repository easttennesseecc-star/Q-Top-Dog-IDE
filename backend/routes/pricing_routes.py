"""Pricing routes providing tier metadata for frontend components.
Simple static tiers plus current tier lookup bridging to subscription if present.
"""

from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from datetime import datetime
from backend.models.subscription import Subscription, SubscriptionTier
from backend.database.database_service import get_db
from auth import get_current_user

router = APIRouter(prefix="/api", tags=["pricing"])

# Canonical tier definitions used by PricingPage & PricingComparison
TIERS: List[Dict[str, Any]] = [
    {
        "id": "FREE", "name": "Free", "emoji": "🟢", "price": 0,
        "description": "Starter access for evaluation",
        "features": ["Basic IDE", "Community Support", "Limited API Calls"],
        "team_members": 1, "daily_api_calls": 20, "support_level": "Community", "popular": False
    },
    {
        "id": "MAKER", "name": "Maker", "emoji": "🔧", "price": 9,
        "description": "Solo builder plan",
        "features": ["Extended API Calls", "Basic LLM Pool", "Email Support"],
        "team_members": 1, "daily_api_calls": 200, "support_level": "Email", "popular": True
    },
    {
        "id": "PRO", "name": "Pro", "emoji": "🚀", "price": 29,
        "description": "Professional development workflows",
        "features": ["High API Limits", "Priority Queue", "LLM Multi-provider", "Basic Phone Pairing"],
        "team_members": 3, "daily_api_calls": 1000, "support_level": "Priority", "popular": True
    },
    {
        "id": "PRO_TEAM", "name": "Pro Team", "emoji": "👥", "price": 79,
        "description": "Team collaboration and advanced orchestration",
        "features": ["Team Seats", "Shared Workflows", "Advanced Phone Pairing", "Model Orchestration"],
        "team_members": 10, "daily_api_calls": 5000, "support_level": "Priority", "popular": False
    },
    {
        "id": "ENTERPRISE", "name": "Enterprise", "emoji": "🏢", "price": 199,
        "description": "Scaled, compliant deployments",
        "features": ["SAML/SSO", "Audit Trails", "Custom LLM Routing", "Dedicated Support"],
        "team_members": 25, "daily_api_calls": 20000, "support_level": "24h SLA", "popular": False
    },
    {
        "id": "ENTERPRISE_PLUS", "name": "Enterprise Plus", "emoji": "💼", "price": 399,
        "description": "Enhanced security & priority throughput",
        "features": ["Private Model Hosting", "Advanced Compliance", "Priority Scaling"],
        "team_members": 50, "daily_api_calls": 50000, "support_level": "12h SLA", "popular": False
    },
]


@router.get("/tiers")
async def list_tiers() -> List[Dict[str, Any]]:
    """Return all pricing tiers as a bare array (compat with PricingComparison)."""
    return TIERS


@router.get("/tier/info")
async def get_tier_info(current_user: str = Depends(get_current_user), db=Depends(get_db)) -> Dict[str, Any]:
    """Return current user's tier id; fall back to FREE if no subscription row."""
    try:
        sub = db.query(Subscription).filter(Subscription.user_id == current_user).first()
        tier_id = (sub.tier.value.upper() if sub else SubscriptionTier.FREE.value.upper())
        return {"tier_id": tier_id, "user_id": current_user, "timestamp": datetime.utcnow().isoformat()}
    except Exception:
        return {"tier_id": SubscriptionTier.FREE.value.upper(), "user_id": current_user, "timestamp": datetime.utcnow().isoformat(), "warning": "subscription_lookup_failed"}
