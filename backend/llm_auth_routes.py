"""
LLM Authentication API Routes

Endpoints for:
- Checking authentication status
- Initiating OAuth flows
- Storing/revoking credentials
- Validating provider access
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from backend.llm_auth import (
    get_provider_auth_status, get_all_auth_status, get_authenticated_providers,
    store_api_key, retrieve_api_key, store_oauth_token, exchange_oauth_code, revoke_provider_auth, validate_provider_access,
    get_oauth_config
)
from backend.logger_utils import get_logger
from backend.services.rate_limiter import RateLimiter
import sqlite3
import hashlib

logger = get_logger(__name__)

router = APIRouter(prefix="/llm_auth", tags=["llm_auth"])


class APIKeyCredential(BaseModel):
    provider: str
    key: str
    user: Optional[str] = None


class OAuthCodeExchange(BaseModel):
    provider: str
    code: str
    redirect_uri: str


class OAuthTokenStorage(BaseModel):
    provider: str
    access_token: str
    user: str
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None


class ProviderRevokeRequest(BaseModel):
    provider: str


def _resolve_user_id(request: Request, payload_user: Optional[str]) -> Optional[str]:
    """Resolve user id from header or payload for BYOK enforcement.

    Order: X-Session-ID header -> query param session_id -> payload user field.
    Returns None if not available.
    """
    try:
        sid = request.headers.get("X-Session-ID") or request.query_params.get("session_id")
        if sid:
            try:
                from backend.auth import get_session_user  # lazy import to avoid cycles
                uid = get_session_user(sid)
                if uid:
                    return uid
            except Exception:
                pass
    except Exception:
        pass
    return payload_user


def _enforce_byok_capacity_and_record(user_id: Optional[str], provider: str, key_ref: str) -> None:
    """Enforce BYOK capacity using RateLimiter.get_byok_pool_status.

    - For org tiers: block when used >= capacity and record new credential row when allowed.
    - For solo tiers: no DB recording here; allow (UI can guide limits).
    """
    if not user_id:
        # Cannot enforce without user context; allow but log
        logger.warning("BYOK enforcement skipped: missing user context")
        return
    rl = RateLimiter()
    status = rl.get_byok_pool_status(user_id)
    if not status:
        return
    if status.get("scope") == "org":
        capacity = int(status.get("capacity") or 0)
        used = int(status.get("used") or 0)
        org_id = status.get("org_id")
        if used >= capacity:
            raise HTTPException(status_code=403, detail="Organization BYOK pool is at capacity. Deactivate a key or upgrade.")
        # Record usage idempotently in organization_byok_credentials
        try:
            try:
                from backend.database.tier_schema import MembershipTierSchema  # local import
                db_path = MembershipTierSchema.get_db_path()
            except Exception:
                db_path = "topdog_ide.db"
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute(
                """
                SELECT COUNT(1) FROM organization_byok_credentials
                WHERE org_id = ? AND provider = ? AND key_ref = ? AND active = 1
                """,
                (org_id, provider, key_ref)
            )
            exists = int(cur.fetchone()[0] or 0) > 0
            if not exists:
                cur.execute(
                    """
                    INSERT INTO organization_byok_credentials (org_id, provider, key_ref, active)
                    VALUES (?, ?, ?, 1)
                    """,
                    (org_id, provider, key_ref)
                )
                conn.commit()
        except Exception as e:
            logger.warning(f"Failed to record org BYOK credential: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass
@router.get("/providers")
async def list_oauth_providers():
    """Return known LLM OAuth-capable providers and whether OAuth is configured.
    elif status.get("scope") == "user":
        capacity = int(status.get("capacity") or 0)
        used = int(status.get("used") or 0)
        if used >= capacity and capacity > 0:
            raise HTTPException(status_code=403, detail="Personal BYOK slots exhausted for your tier. Remove a credential or upgrade.")
        # No persistence for personal keys beyond existing file; enforcement only.
    This is a convenience endpoint for the OAuth panel. Some providers (OpenAI/Anthropic)
    typically use API keys; we still surface them with oauth_enabled=false.
    """
    # Known set for UI; extend as needed
    known = [
        {"id": "openai", "name": "OpenAI", "description": "OpenAI platform", "oauth_enabled": False},
        {"id": "anthropic", "name": "Anthropic", "description": "Claude models", "oauth_enabled": False},
        {"id": "google", "name": "Google", "description": "Google account for Gemini", "oauth_enabled": True},
        {"id": "github", "name": "GitHub", "description": "GitHub account for Copilot", "oauth_enabled": True},
    ]
    # Mark configured if client_id present for oauth-enabled ones
    out: List[Dict[str, Any]] = []
    for p in known:
        cfg = get_oauth_config(p["id"]) if p.get("oauth_enabled") else {}
        configured = bool(cfg.get("client_id")) if p.get("oauth_enabled") else True
        out.append({
            **p,
            "configured": configured,
        })
    return {"providers": out}


@router.post("/login/{provider}")
async def oauth_login(provider: str):
    """Initiate OAuth login by returning an authorization URL.

    For providers without OAuth support, indicate client flow not available.
    """
    cfg = get_oauth_config(provider)
    if not cfg or not cfg.get("client_id"):
        return {"success": False, "client_required": True, "message": f"OAuth not configured for {provider}"}
    # Compose a minimal auth URL; frontend will open a popup
    scopes = cfg.get("scopes", [])
    from urllib.parse import urlencode
    # Use backend's configured URL as redirect base if available
    import os
    backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
    redirect_uri = f"{backend_url}/static/oauth-callback.html"  # neutral callback handled by main
    params = urlencode({
        "client_id": cfg.get("client_id", ""),
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(scopes),
        "state": provider,
    })
    oauth_url = f"{cfg.get('auth_url')}?{params}"
    return {"success": True, "oauth_url": oauth_url}


@router.post("/logout/{provider}")
async def oauth_logout(provider: str):
    """Logout/revoke local credentials for the provider."""
    try:
        revoke_provider_auth(provider)
        return {"success": True, "provider": provider}
    except Exception as e:
        logger.error(f"Failed to revoke {provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/status/{provider}")
async def check_provider_auth(provider: str):
    """
    Check authentication status for a specific provider.
    
    Returns:
    {
        'authenticated': bool,
        'method': 'api_key' | 'oauth' | 'expired' | 'none',
        'user': optional user identifier,
        'expires_at': optional expiration time,
        'scopes': list of authorized scopes
    }
    """
    try:
        status = get_provider_auth_status(provider)
        logger.info(f"Auth status check for {provider}: {status['authenticated']}")
        return status
    except Exception as e:
        logger.error(f"Failed to check auth status for {provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def check_all_auth():
    """Check authentication status for all providers."""
    try:
        status = get_all_auth_status()
        authenticated = get_authenticated_providers()
        logger.info(f"Auth status check: {len(authenticated)} providers authenticated")
        return {
            'providers': status,
            'authenticated_count': len(authenticated),
            'authenticated': authenticated
        }
    except Exception as e:
        logger.error(f"Failed to check all auth status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/oauth/config/{provider}")
async def get_oauth_configuration(provider: str):
    """
    Get OAuth configuration for a provider.
    
    Returns URLs and scopes needed for OAuth flow.
    Used by frontend to build login URLs.
    """
    try:
        config: Optional[Dict[str, Any]] = get_oauth_config(provider)
        if config is None:
            raise HTTPException(status_code=404, detail=f"No OAuth config for {provider}")
        
        # Don't expose client_secret to frontend
        auth_url = config.get('auth_url') if isinstance(config.get('auth_url'), str) else None
        scopes_val = config.get('scopes')
        scopes: List[str] = scopes_val if isinstance(scopes_val, list) else []
        client_id = config.get('client_id') if isinstance(config.get('client_id'), str) else None
        safe_config: Dict[str, Any] = {
            'provider': provider,
            'auth_url': auth_url,
            'scopes': scopes,
            'client_id': client_id,  # Safe to expose
        }
        
        logger.info(f"OAuth config requested for {provider}")
        return safe_config
    except Exception as e:
        logger.error(f"Failed to get OAuth config for {provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/oauth/exchange")
async def exchange_oauth_code_endpoint(request: OAuthCodeExchange, http_request: Request):
    """
    Exchange OAuth authorization code for access token.
    
    Typically called after user completes OAuth flow in browser.
    """
    try:
        token_response: Optional[Dict[str, Any]] = exchange_oauth_code(
            request.provider,
            request.code,
            request.redirect_uri
        )
        
        if token_response is None:
            raise HTTPException(status_code=400, detail="OAuth exchange failed")
        
        # Extract user info (varies by provider)
        user_id_raw = token_response.get('id') if 'id' in token_response else None
        if not isinstance(user_id_raw, str):
            email_raw = token_response.get('email') if 'email' in token_response else None
            user_id = email_raw if isinstance(email_raw, str) else 'unknown'
        else:
            user_id = user_id_raw
        
        # Enforce BYOK capacity prior to storing token
        access_token = token_response.get('access_token') if isinstance(token_response.get('access_token'), str) else None
        expires_in = token_response.get('expires_in') if isinstance(token_response.get('expires_in'), int) else None
        refresh_token = token_response.get('refresh_token') if isinstance(token_response.get('refresh_token'), str) else None
        scope_raw = token_response.get('scope') if isinstance(token_response.get('scope'), str) else ''
        scopes: List[str] = scope_raw.split() if scope_raw else []
        if access_token is None:
            raise HTTPException(status_code=400, detail="Missing access_token in OAuth response")
        # Use a stable reference to avoid storing secrets in DB
        token_ref = hashlib.sha256(access_token.encode("utf-8")).hexdigest()
        # Prefer resolved session user if available; else fall back to provider user_id
        resolved_uid = _resolve_user_id(http_request, user_id)
        _enforce_byok_capacity_and_record(resolved_uid, request.provider, token_ref)
        # Store the token
        store_oauth_token(
            request.provider,
            access_token,
            resolved_uid or user_id,
            expires_in,
            refresh_token,
            scopes
        )
        
        logger.info(f"OAuth token exchanged for {request.provider}")
        return {
            'success': True,
            'provider': request.provider,
            'user': user_id,
            'authenticated': True
        }
    except Exception as e:
        logger.error(f"OAuth exchange failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api_key/store")
async def store_api_key_endpoint(credential: APIKeyCredential, request: Request):
    """
    Store API key for a provider.
    
    Keys are stored in ~/.q-ide/llm_credentials.json
    """
    try:
        if not credential.key:
            raise HTTPException(status_code=400, detail="API key is required")
        
        if not credential.key.strip():
            raise HTTPException(status_code=400, detail="API key cannot be empty")
        
        # Enforce BYOK capacity (org tiers) using a hashed key reference
        key_ref = hashlib.sha256(credential.key.encode("utf-8")).hexdigest()
        user_id = _resolve_user_id(request, credential.user)
        _enforce_byok_capacity_and_record(user_id, credential.provider, key_ref)
        # Persist after enforcement
        store_api_key(credential.provider, credential.key, user_id)
        logger.info(f"API key stored for {credential.provider}")
        
        return {
            'success': True,
            'provider': credential.provider,
            'authenticated': True,
            'method': 'api_key'
        }
    except Exception as e:
        logger.error(f"Failed to store API key for {credential.provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api_key/retrieve/{provider}")
async def retrieve_api_key_endpoint(provider: str):
    """
    Check if API key exists for provider (doesn't return the actual key).
    """
    try:
        key = retrieve_api_key(provider)
        exists = key is not None
        
        logger.info(f"API key check for {provider}: {'exists' if exists else 'not found'}")
        return {
            'provider': provider,
            'has_key': exists,
            'authenticated': exists
        }
    except Exception as e:
        logger.error(f"Failed to check API key for {provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/revoke")
async def revoke_provider_auth_endpoint(request: ProviderRevokeRequest):
    """
    Revoke (delete) authentication for a provider.
    """
    try:
        revoke_provider_auth(request.provider)
        logger.info(f"Authentication revoked for {request.provider}")
        
        return {
            'success': True,
            'provider': request.provider,
            'authenticated': False
        }
    except Exception as e:
        logger.error(f"Failed to revoke auth for {request.provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validate/{provider}")
async def validate_provider_access_endpoint(provider: str, scopes: Optional[str] = None):
    """
    Validate that provider is authenticated and optionally check scopes.
    
    Query params:
    - scopes: comma-separated list of required scopes (optional)
    """
    try:
        required_scopes: Optional[List[str]] = None
        if scopes:
            parsed = [s.strip() for s in scopes.split(',') if s.strip()]
            required_scopes = parsed if parsed else None
        valid = validate_provider_access(provider, required_scopes)
        
        logger.info(f"Provider validation for {provider}: {valid}")
        return {
            'provider': provider,
            'valid': valid,
            'authenticated': valid
        }
    except Exception as e:
        logger.error(f"Failed to validate provider {provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/authenticated")
async def get_authenticated_providers_endpoint():
    """Get list of currently authenticated providers."""
    try:
        authenticated = get_authenticated_providers()
        logger.info(f"Retrieved {len(authenticated)} authenticated providers")
        
        return {
            'count': len(authenticated),
            'providers': authenticated
        }
    except Exception as e:
        logger.error(f"Failed to get authenticated providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate_before_use/{provider}")
async def validate_before_use(provider: str):
    """
    Full validation before using a provider for LLM operations.
    
    Checks:
    - Authentication exists
    - Token not expired
    - Credentials are valid
    
    Returns what's needed to actually use the provider.
    """
    try:
        status = get_provider_auth_status(provider)
        
        if not status['authenticated']:
            return {
                'valid': False,
                'reason': status['method'],  # 'none', 'expired', etc.
                'provider': provider,
                'action_required': True
            }
        
        # TODO: Could add credential validation by making a test API call
        
        return {
            'valid': True,
            'provider': provider,
            'method': status['method'],
            'user': status['user'],
            'action_required': False
        }
    except Exception as e:
        logger.error(f"Failed to validate {provider} for use: {e}")
        raise HTTPException(status_code=500, detail=str(e))
