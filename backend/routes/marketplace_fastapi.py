"""FastAPI Marketplace Routers

Ports the Flask blueprints in `backend/api/v1/ai_marketplace_routes.py` to native
FastAPI `APIRouter` instances so they can be mounted directly in `main.py`.

Three routers:
 - marketplace_router (prefix=/api/v1/marketplace)
 - agent_router (prefix=/api/v1/agent)
 - marketplace_auth_router (prefix=/api/v1/auth)

Relies on existing service singletons:
 - registry (AIMarketplaceRegistry)
 - auth_service (AIAuthService)
 - recommendation_engine (RecommendationEngine)

If `recommendation_engine` failed to initialize (None), routes that depend on it
return a 500 until startup repair logic re-initializes it.
"""

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import os
import logging

from backend.services.ai_marketplace_registry import registry
from backend.services.ai_auth_service import auth_service, ProviderType, APIKeyStatus
from backend.services.ai_recommendation_engine import recommendation_engine
from backend.services.rate_limiter import RateLimiter

logger = logging.getLogger("marketplace")

# ---------------- Dependency Helpers -----------------

def get_token(authorization: Optional[str] = Header(None)) -> Optional[str]:
    if not authorization:
        return None
    return authorization.replace("Bearer ", "").strip()

def require_user(token: Optional[str]) -> str:
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    ok, user_id = auth_service.verify_token(token)
    if not ok or not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user_id

def _soft_warning_from_rl(rl: Dict) -> bool:
    """Compute soft warning based on remaining/limit vs env RATE_LIMIT_SOFT_WARN_PCT.
    rl: result dict from RateLimiter.check_limit
    """
    try:
        warn_pct = float(os.getenv("RATE_LIMIT_SOFT_WARN_PCT", "10"))
    except Exception:
        warn_pct = 10.0
    limit = rl.get("limit")
    remaining = rl.get("remaining")
    if isinstance(limit, int) and limit > 0 and isinstance(remaining, int):
        return (remaining / limit) * 100.0 < warn_pct
    return False

# ---------------- Marketplace Router -----------------

marketplace_router = APIRouter(prefix="/api/v1/marketplace", tags=["marketplace"])

# Initialize rate limiter instance for gating per-tier usage
rate_limiter = RateLimiter()

@marketplace_router.get("/models")
def list_models(skip: int = 0, limit: int = 50):
    """List all models with pagination."""
    try:
        models, total = registry.list_all_models(skip=skip, limit=limit)
        return {
            "success": True,
            "data": [m.to_dict() for m in models],
            "pagination": {"skip": skip, "limit": limit, "total": total},
        }
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@marketplace_router.get("/models/{model_id}")
def get_model(model_id: str):
    try:
        model = registry.get_model(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        return {"success": True, "data": model.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class ModelSearchPayload(BaseException):
    pass  # Placeholder to avoid accidental pydantic dependency pre-import

@marketplace_router.post("/models/search")
def search_models(payload: Dict[str, Any]):  # lightweight validation; keep in sync with Flask version
    try:
        query = payload.get("query", "")
        provider = payload.get("provider")
        min_rating = float(payload.get("min_rating", 0.0))
        max_price = payload.get("max_price")
        capability = payload.get("capability")
        skip = int(payload.get("skip", 0))
        limit = int(payload.get("limit", 50))

        # Map optional provider/capability enums
        from backend.services.ai_marketplace_registry import ModelProvider, ModelCapability
        provider_enum = ModelProvider(provider) if provider in [p.value for p in ModelProvider] else None
        capability_enum = ModelCapability(capability) if capability in [c.value for c in ModelCapability] else None

        models, total = registry.search_models(
            query=query,
            provider=provider_enum,
            min_rating=min_rating,
            capability=capability_enum,
            max_price=max_price,
            skip=skip,
            limit=limit,
        )
        return {
            "success": True,
            "data": [m.to_dict() for m in models],
            "pagination": {"skip": skip, "limit": limit, "total": total},
        }
    except Exception as e:
        logger.error(f"Error searching models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@marketplace_router.post("/recommendations")
def get_recommendations(payload: Dict[str, Any], token: Optional[str] = Depends(get_token)):
    try:
        user_id = require_user(token)
        # Tier-based rate limiting (skip for founders)
        user = auth_service.get_user(user_id)
        founder_bypass = getattr(user, "is_founder", False) if user else False
        try:
            if os.getenv("PYTEST_CURRENT_TEST") or (os.getenv("DISABLE_FOUNDER_BYPASS", "false").lower() in ("1","true","yes")):
                founder_bypass = False
        except Exception:
            pass
        if not founder_bypass:
            rl = rate_limiter.check_limit(user_id)
            if not rl.get("allowed"):
                return JSONResponse(status_code=429, content={
                    "success": False,
                    "error": rl.get("error", "Rate limit exceeded"),
                    "limit": rl.get("limit"),
                    "used": rl.get("used"),
                    "remaining": rl.get("remaining"),
                    "tier": rl.get("tier"),
                })
        if recommendation_engine is None:
            raise HTTPException(status_code=500, detail="Recommendation engine unavailable")
        query = payload.get("query", "")
        budget = payload.get("budget", "medium")
        preferences = user.preferences if user else {}
        success, recs = recommendation_engine.get_recommendations(
            query=query, user_budget=budget, user_preferences=preferences
        )
        if not success:
            raise HTTPException(status_code=500, detail="Could not generate recommendations")
        return {
            "success": True,
            "data": [
                {
                    "model_id": r.model_id,
                    "model_name": r.model_name,
                    "score": r.score,
                    "reasoning": r.reasoning,
                    "price_rank": r.price_rank,
                    "quality_rank": r.quality_rank,
                }
                for r in recs
            ],
            "rate_limit": None if founder_bypass else {
                "remaining": rl.get("remaining"),
                "limit": rl.get("limit"),
                "tier": rl.get("tier"),
                "soft_warning": _soft_warning_from_rl(rl),
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@marketplace_router.post("/select-model")
def select_model(payload: Dict[str, Any], token: Optional[str] = Depends(get_token)):
    try:
        user_id = require_user(token)
        model_id = payload.get("model_id")
        if not model_id:
            raise HTTPException(status_code=400, detail="Model ID required")
        registry.update_usage_count(model_id)
        return {"success": True, "message": f"Model {model_id} selected"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error selecting model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@marketplace_router.get("/stats")
def marketplace_stats():
    try:
        return {"success": True, "data": registry.get_statistics()}
    except Exception as e:
        logger.error(f"Error getting marketplace stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- Agent Router -----------------

agent_router = APIRouter(prefix="/api/v1/agent", tags=["agent"])

@agent_router.post("/chat")
def agent_chat(payload: Dict[str, Any], token: Optional[str] = Depends(get_token)):
    try:
        user_id = require_user(token)
        model_id = payload.get("model_id")
        messages = payload.get("messages", [])
        if not model_id:
            raise HTTPException(status_code=400, detail="Model ID required")
        model = registry.get_model(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        user = auth_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        # Tier-based rate limiting (skip for founders)
        founder_bypass = getattr(user, "is_founder", False)
        if not founder_bypass:
            rl = rate_limiter.check_limit(user_id)
            if not rl.get("allowed"):
                return JSONResponse(status_code=429, content={
                    "success": False,
                    "error": rl.get("error", "Rate limit exceeded"),
                    "limit": rl.get("limit"),
                    "used": rl.get("used"),
                    "remaining": rl.get("remaining"),
                    "tier": rl.get("tier"),
                })
        total_chars = sum(len(m.get("content", "")) for m in messages)
        estimated_tokens = max(1, total_chars // 4)
        input_cost = (estimated_tokens / 1000) * model.pricing.input_cost_per_1k_tokens
        # Simulated response; integrate real LLM invocation later
        response_text = "Simulated response (router integration pending)."
        output_tokens = 100
        total_cost = 0.0  # Pricing remains informational; enforcement is via tier limits
        return {
            "success": True,
            "data": {
                "response": response_text,
                "tokens_used": estimated_tokens + output_tokens,
                "cost": total_cost,
                "remaining_balance": user.balance.available_balance if not founder_bypass else "founder-unlimited",
                "rate_limit": None if founder_bypass else {
                    "remaining": rl.get("remaining"),
                    "limit": rl.get("limit"),
                    "tier": rl.get("tier"),
                    "soft_warning": _soft_warning_from_rl(rl),
                },
                "founder_bypass": founder_bypass,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@agent_router.post("/chat/stream")
def agent_chat_stream(payload: Dict[str, Any], token: Optional[str] = Depends(get_token)):
    try:
        user_id = require_user(token)
        user = auth_service.get_user(user_id)
        founder_bypass = getattr(user, "is_founder", False) if user else False
        return {"success": True, "message": "Streaming not implemented; use WebSocket.", "founder_bypass": founder_bypass}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initiating stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@agent_router.get("/history")
def agent_history(token: Optional[str] = Depends(get_token)):
    try:
        require_user(token)
        # Placeholder: integrate persistence store later
        return {"success": True, "data": []}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@agent_router.get("/usage")
def agent_usage(token: Optional[str] = Depends(get_token)):
    try:
        user_id = require_user(token)
        user = auth_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "success": True,
            "data": {
                "total_spent": user.balance.spent_balance,
                "transaction_count": len(user.balance.transactions),
                "current_balance": user.balance.available_balance,
                "total_balance": user.balance.total_balance,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- Auth Router -----------------

marketplace_auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@marketplace_auth_router.post("/register")
def auth_register(payload: Dict[str, Any]):
    try:
        email = payload.get("email")
        username = payload.get("username")
        password = payload.get("password")
        if not all([email, username, password]):
            raise HTTPException(status_code=400, detail="Email, username, and password required")
        # Type narrowing to satisfy static typing and avoid accidental non-str inputs
        if not isinstance(email, str) or not isinstance(username, str) or not isinstance(password, str):
            raise HTTPException(status_code=400, detail="Email, username, and password must be strings")
        success, msg, user = auth_service.register_user(email, username, password)
        if not success or not user:
            raise HTTPException(status_code=400, detail=msg)
        return {"success": True, "data": user.to_dict_safe()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@marketplace_auth_router.post("/login")
def auth_login(payload: Dict[str, Any]):
    try:
        email = payload.get("email")
        password = payload.get("password")
        if not all([email, password]):
            raise HTTPException(status_code=400, detail="Email and password required")
        if not isinstance(email, str) or not isinstance(password, str):
            raise HTTPException(status_code=400, detail="Email and password must be strings")
        success, msg, token = auth_service.login_user(email, password)
        if not success or not token:
            raise HTTPException(status_code=401, detail=msg)
        return {"success": True, "data": token.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@marketplace_auth_router.get("/me")
def auth_me(token: Optional[str] = Depends(get_token)):
    try:
        user_id = require_user(token)
        user = auth_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        connected = sorted([k.provider.value for k in user.api_keys.values() if k.status == APIKeyStatus.ACTIVE])
        info = user.to_dict_safe()
        info["connected_providers"] = connected
        return {"success": True, "data": info}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@marketplace_auth_router.get("/api-keys")
def list_api_keys(token: Optional[str] = Depends(get_token)):
    try:
        user_id = require_user(token)
        ok, keys = auth_service.get_api_keys(user_id)
        if not ok:
            raise HTTPException(status_code=500, detail="Could not fetch keys")
        return {"success": True, "data": keys}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing API keys: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@marketplace_auth_router.post("/credentials/add")
def add_credentials(user_id: Optional[str] = None, payload: Optional[Dict[str, Any]] = None):
    try:
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id required")
        payload = payload or {}
        service = payload.get("service")
        api_key = payload.get("api_key")
        if not service or not api_key:
            raise HTTPException(status_code=400, detail="service and api_key required")
        mapping = {
            'openai': ProviderType.OPENAI,
            'anthropic': ProviderType.ANTHROPIC,
            'google_gemini': ProviderType.GOOGLE_GEMINI,
            'google': ProviderType.GOOGLE_OAUTH,
            'github': ProviderType.GITHUB,
            'github_copilot': ProviderType.GITHUB_COPILOT,
            'huggingface': ProviderType.HUGGINGFACE,
            'cohere': ProviderType.COHERE,
        }
        provider = mapping.get(service)
        if not provider:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {service}")
        success, msg, key_obj = auth_service.add_api_key(user_id, provider, api_key, daily_limit=None)
        if not success or not key_obj:
            raise HTTPException(status_code=400, detail=msg)
        return {"success": True, "data": key_obj.to_dict_safe()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding credentials: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@marketplace_auth_router.post("/verify-token")
def verify_token(token: Optional[str] = Depends(get_token)):
    try:
        if not token:
            return JSONResponse(status_code=401, content={"success": False, "user_id": None})
        ok, user_id = auth_service.verify_token(token)
        if not ok:
            return JSONResponse(status_code=401, content={"success": False, "user_id": None})
        return {"success": True, "user_id": user_id}
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Founder grant & admin endpoints omitted in FastAPI port for safety; can be re-added with proper admin auth later.

# ---------------- Dev helper: add funds (guarded) -----------------

@marketplace_auth_router.post("/dev/add-funds")
def dev_add_funds(payload: Dict[str, Any], x_dev_funds_key: Optional[str] = Header(None)):
    """Seed a user's balance in development.

    Headers:
      - X-Dev-Funds-Key: must match env DEV_FUNDS_KEY

    Body (JSON): { email?: string, user_id?: string, amount: number, txn_id?: string }
    """
    try:
        expected = os.getenv("DEV_FUNDS_KEY", "")
        if not expected or x_dev_funds_key != expected:
            raise HTTPException(status_code=403, detail="Forbidden")
        email = (payload.get("email") or "").strip().lower()
        user_id = (payload.get("user_id") or "").strip()
        amount = float(payload.get("amount", 0))
        txn = (payload.get("txn_id") or "dev-seed").strip()
        user = None
        if user_id:
            user = auth_service.get_user(user_id)
        elif email:
            user = auth_service.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        ok, msg, balance = auth_service.add_funds(user.id, amount, txn)
        if not ok or not balance:
            raise HTTPException(status_code=400, detail=msg)
        return {"success": True, "data": balance.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error dev add funds: {e}")
        raise HTTPException(status_code=500, detail=str(e))
