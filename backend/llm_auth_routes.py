"""
LLM Authentication API Routes

Endpoints for:
- Checking authentication status
- Initiating OAuth flows
- Storing/revoking credentials
- Validating provider access
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from llm_auth import (
    get_provider_auth_status, get_all_auth_status, get_authenticated_providers,
    store_api_key, retrieve_api_key, store_oauth_token, retrieve_oauth_token,
    exchange_oauth_code, revoke_provider_auth, validate_provider_access,
    get_oauth_config
)
from logger_utils import get_logger

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
        config = get_oauth_config(provider)
        if not config:
            raise HTTPException(status_code=404, detail=f"No OAuth config for {provider}")
        
        # Don't expose client_secret to frontend
        safe_config = {
            'provider': provider,
            'auth_url': config.get('auth_url'),
            'scopes': config.get('scopes', []),
            'client_id': config.get('client_id'),  # Safe to expose
        }
        
        logger.info(f"OAuth config requested for {provider}")
        return safe_config
    except Exception as e:
        logger.error(f"Failed to get OAuth config for {provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/oauth/exchange")
async def exchange_oauth_code_endpoint(request: OAuthCodeExchange):
    """
    Exchange OAuth authorization code for access token.
    
    Typically called after user completes OAuth flow in browser.
    """
    try:
        token_response = exchange_oauth_code(
            request.provider,
            request.code,
            request.redirect_uri
        )
        
        if not token_response:
            raise HTTPException(status_code=400, detail="OAuth exchange failed")
        
        # Extract user info (varies by provider)
        user_id = token_response.get('id') or token_response.get('email') or 'unknown'
        
        # Store the token
        store_oauth_token(
            request.provider,
            token_response.get('access_token'),
            user_id,
            token_response.get('expires_in'),
            token_response.get('refresh_token'),
            token_response.get('scope', '').split() if token_response.get('scope') else []
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
async def store_api_key_endpoint(credential: APIKeyCredential):
    """
    Store API key for a provider.
    
    Keys are stored in ~/.q-ide/llm_credentials.json
    """
    try:
        if not credential.key:
            raise HTTPException(status_code=400, detail="API key is required")
        
        if not credential.key.strip():
            raise HTTPException(status_code=400, detail="API key cannot be empty")
        
        store_api_key(credential.provider, credential.key, credential.user)
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
        required_scopes = None
        if scopes:
            required_scopes = [s.strip() for s in scopes.split(',')]
        
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
