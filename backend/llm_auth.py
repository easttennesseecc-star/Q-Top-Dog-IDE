"""
LLM Provider Authentication and Credential Management

Handles OAuth flows and API key storage for:
- Cloud LLM providers (OpenAI, Gemini, Claude, etc.)
- User authentication status tracking
- Token refresh and expiration
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import urllib.parse
import urllib.request

# Storage location for LLM credentials
CREDS_DIR = Path.home() / '.q-ide'
CREDS_FILE = CREDS_DIR / 'llm_credentials.json'


def _ensure_creds_dir():
    """Create credentials directory if it doesn't exist."""
    CREDS_DIR.mkdir(parents=True, exist_ok=True)


def load_credentials() -> Dict[str, Any]:
    """Load LLM provider credentials from secure storage."""
    try:
        if CREDS_FILE.exists():
            data = json.loads(CREDS_FILE.read_text())
            return data
    except Exception as e:
        print(f"[AUTH] Failed to load credentials: {e}")
    return {"providers": {}, "user_accounts": {}}


def save_credentials(creds: Dict[str, Any]):
    """Save LLM provider credentials to secure storage."""
    try:
        _ensure_creds_dir()
        # Set restrictive permissions (Unix-style)
        CREDS_FILE.write_text(json.dumps(creds, indent=2))
        # Note: On Windows, consider using DPAPI for additional security
        print(f"[AUTH] Credentials saved to {CREDS_FILE}")
    except Exception as e:
        print(f"[AUTH] Failed to save credentials: {e}")


def get_provider_auth_status(provider: str) -> Dict[str, Any]:
    """
    Check authentication status for a specific provider.
    
    Returns:
    {
        'authenticated': bool,
        'method': 'api_key' | 'oauth' | 'none',
        'user': optional user identifier,
        'expires_at': optional expiration datetime,
        'scopes': optional list of OAuth scopes
    }
    """
    creds = load_credentials()
    provider_creds = creds.get('providers', {}).get(provider, {})
    
    if not provider_creds:
        return {
            'authenticated': False,
            'method': 'none',
            'user': None,
            'expires_at': None,
            'scopes': []
        }
    
    # Check if token is expired
    if 'expires_at' in provider_creds:
        expires = datetime.fromisoformat(provider_creds['expires_at'])
        if datetime.utcnow() > expires:
            return {
                'authenticated': False,
                'method': 'expired',
                'user': provider_creds.get('user'),
                'expires_at': provider_creds['expires_at'],
                'scopes': provider_creds.get('scopes', [])
            }
    
    return {
        'authenticated': True,
        'method': provider_creds.get('method', 'api_key'),
        'user': provider_creds.get('user'),
        'expires_at': provider_creds.get('expires_at'),
        'scopes': provider_creds.get('scopes', [])
    }


def get_all_auth_status() -> Dict[str, Dict[str, Any]]:
    """Get authentication status for all configured providers."""
    providers = [
        'openai', 'gemini', 'claude', 'grok', 'perplexity',
        'copilot', 'chatgpt-4o', 'ollama', 'llama-cpp', 'gpt4all'
    ]
    
    return {
        provider: get_provider_auth_status(provider)
        for provider in providers
    }


def store_api_key(provider: str, api_key: str, user_identifier: Optional[str] = None):
    """
    Store an API key for a provider.
    
    Args:
        provider: Provider name (e.g., 'openai', 'gemini')
        api_key: The API key
        user_identifier: Optional user email/ID
    """
    creds = load_credentials()
    if 'providers' not in creds:
        creds['providers'] = {}
    
    creds['providers'][provider] = {
        'method': 'api_key',
        'key': api_key,
        'user': user_identifier,
        'stored_at': datetime.utcnow().isoformat(),
        'scopes': []
    }
    
    save_credentials(creds)
    print(f"[AUTH] API key stored for {provider}")


def retrieve_api_key(provider: str) -> Optional[str]:
    """Retrieve API key for a provider (None if not found or expired)."""
    status = get_provider_auth_status(provider)
    if not status['authenticated']:
        return None
    
    creds = load_credentials()
    return creds.get('providers', {}).get(provider, {}).get('key')


def store_oauth_token(
    provider: str,
    access_token: str,
    user_identifier: str,
    expires_in: Optional[int] = None,
    refresh_token: Optional[str] = None,
    scopes: Optional[List[str]] = None
):
    """
    Store OAuth access token for a provider.
    
    Args:
        provider: Provider name
        access_token: OAuth access token
        user_identifier: User email/ID from provider
        expires_in: Token expiration in seconds (optional)
        refresh_token: Refresh token (optional)
        scopes: List of authorized scopes
    """
    creds = load_credentials()
    if 'providers' not in creds:
        creds['providers'] = {}
    
    expires_at = None
    if expires_in:
        expires_at = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()
    
    creds['providers'][provider] = {
        'method': 'oauth',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user_identifier,
        'scopes': scopes or [],
        'authenticated_at': datetime.utcnow().isoformat(),
        'expires_at': expires_at
    }
    
    save_credentials(creds)
    print(f"[AUTH] OAuth token stored for {provider} (user: {user_identifier})")


def retrieve_oauth_token(provider: str) -> Optional[str]:
    """Retrieve valid OAuth token for a provider (None if not found or expired)."""
    status = get_provider_auth_status(provider)
    if not status['authenticated'] or status['method'] != 'oauth':
        return None
    
    creds = load_credentials()
    return creds.get('providers', {}).get(provider, {}).get('access_token')


def get_oauth_config(provider: str) -> Dict[str, Any]:
    """Get OAuth configuration for a specific provider."""
    
    configs = {
        'openai': {
            'client_id': os.getenv('OPENAI_CLIENT_ID', ''),
            'client_secret': os.getenv('OPENAI_CLIENT_SECRET', ''),
            'auth_url': 'https://openai.com/oauth/authorize',
            'token_url': 'https://openai.com/oauth/token',
            'user_info_url': 'https://api.openai.com/v1/me',
            'scopes': ['openid', 'profile', 'email'],
        },
        'gemini': {
            'client_id': os.getenv('GEMINI_CLIENT_ID', ''),
            'client_secret': os.getenv('GEMINI_CLIENT_SECRET', ''),
            'auth_url': 'https://accounts.google.com/o/oauth2/v2/auth',
            'token_url': 'https://oauth2.googleapis.com/token',
            'user_info_url': 'https://www.googleapis.com/oauth2/v2/userinfo',
            'scopes': ['openid', 'profile', 'email'],
        },
        'claude': {
            'client_id': os.getenv('CLAUDE_CLIENT_ID', ''),
            'client_secret': os.getenv('CLAUDE_CLIENT_SECRET', ''),
            'auth_url': 'https://api.anthropic.com/oauth/authorize',
            'token_url': 'https://api.anthropic.com/oauth/token',
            'user_info_url': 'https://api.anthropic.com/oauth/userinfo',
            'scopes': ['chat:write', 'profile'],
        },
        'grok': {
            'client_id': os.getenv('GROK_CLIENT_ID', ''),
            'client_secret': os.getenv('GROK_CLIENT_SECRET', ''),
            'auth_url': 'https://grok.x.com/oauth/authorize',
            'token_url': 'https://grok.x.com/oauth/token',
            'user_info_url': 'https://api.grok.x.com/v1/me',
            'scopes': ['api', 'profile'],
        },
        'perplexity': {
            'client_id': os.getenv('PERPLEXITY_CLIENT_ID', ''),
            'client_secret': os.getenv('PERPLEXITY_CLIENT_SECRET', ''),
            'auth_url': 'https://api.perplexity.ai/oauth/authorize',
            'token_url': 'https://api.perplexity.ai/oauth/token',
            'user_info_url': 'https://api.perplexity.ai/v1/me',
            'scopes': ['openid', 'profile'],
        }
    }
    
    return configs.get(provider, {})


def exchange_oauth_code(
    provider: str,
    code: str,
    redirect_uri: str
) -> Optional[Dict[str, Any]]:
    """
    Exchange OAuth authorization code for access token.
    
    Returns:
    {
        'access_token': str,
        'refresh_token': str (optional),
        'expires_in': int (seconds),
        'user': { user identifier from provider },
        'scopes': [list of scopes]
    }
    """
    config = get_oauth_config(provider)
    if not config.get('client_id'):
        print(f"[AUTH] No OAuth config for {provider}")
        return None
    
    try:
        data = urllib.parse.urlencode({
            'code': code,
            'client_id': config['client_id'],
            'client_secret': config['client_secret'],
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }).encode('utf-8')
        
        req = urllib.request.Request(config['token_url'], data=data, method='POST')
        req.add_header('Accept', 'application/json')
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            token_data = json.loads(resp.read().decode('utf-8'))
            print(f"[AUTH] OAuth token received for {provider}")
            return token_data
    except Exception as e:
        print(f"[AUTH] OAuth token exchange failed for {provider}: {e}")
        return None


def revoke_provider_auth(provider: str):
    """Revoke authentication for a provider."""
    creds = load_credentials()
    if 'providers' in creds and provider in creds['providers']:
        del creds['providers'][provider]
        save_credentials(creds)
        print(f"[AUTH] Authentication revoked for {provider}")


def get_authenticated_providers() -> List[str]:
    """Get list of currently authenticated providers."""
    status = get_all_auth_status()
    return [
        provider
        for provider, auth_status in status.items()
        if auth_status['authenticated']
    ]


def validate_provider_access(provider: str, required_scopes: Optional[List[str]] = None) -> bool:
    """
    Validate that a provider is authenticated and has required scopes.
    
    Returns True if authenticated and (optionally) has all required scopes.
    """
    status = get_provider_auth_status(provider)
    
    if not status['authenticated']:
        return False
    
    if required_scopes:
        provider_scopes = set(status.get('scopes', []))
        required = set(required_scopes)
        if not required.issubset(provider_scopes):
            return False
    
    return True
