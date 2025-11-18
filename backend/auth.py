"""
OAuth and session management for Q-TopDog.

Supports Google SSO (primary identity) and provider account linking (GitHub, OpenAI, etc.).
Local dev storage uses a JSON file; for production, use a database + secrets manager.
"""

import json
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import urllib.parse
import urllib.request
from fastapi import Header

# Simple in-memory session store + file-backed user/token store (dev-only)
SESSIONS: Dict[str, Dict[str, Any]] = {}
AUTH_DATA_FILE = Path(__file__).resolve().parent.parent / '.dev_auth_data.json'


def load_auth_data() -> Dict[str, Any]:
    """Load users and linked accounts from file."""
    try:
        if AUTH_DATA_FILE.exists():
            return json.loads(AUTH_DATA_FILE.read_text())
    except Exception as e:
        print(f"Failed to load auth data: {e}")
    return {"users": {}, "sessions": {}}


def save_auth_data(data: Dict[str, Any]):
    """Save users and linked accounts to file."""
    try:
        AUTH_DATA_FILE.write_text(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Failed to save auth data: {e}")


# Data model (all stored as JSON)
# users: { google_id -> { email, name, picture, created_at } }
# linked_accounts: { google_id -> { provider -> { access_token, provider_user, scopes, expires_at } } }


def exchange_code_for_token(code: str, client_id: str, client_secret: str, redirect_uri: str, token_url: str) -> Optional[Dict]:
    """Generic OAuth code exchange."""
    try:
        data = urllib.parse.urlencode({
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }).encode('utf-8')
        req = urllib.request.Request(token_url, data=data, method='POST')
        req.add_header('Accept', 'application/json')
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Token exchange failed: {e}")
        return None


def get_google_user_info(access_token: str) -> Optional[Dict]:
    """Fetch Google user profile."""
    try:
        req = urllib.request.Request('https://www.googleapis.com/oauth2/v2/userinfo')
        req.add_header('Authorization', f'Bearer {access_token}')
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Failed to fetch Google user info: {e}")
        return None


def get_github_user_info(access_token: str) -> Optional[Dict]:
    """Fetch GitHub user profile."""
    try:
        req = urllib.request.Request('https://api.github.com/user')
        req.add_header('Authorization', f'token {access_token}')
        req.add_header('Accept', 'application/vnd.github.v3+json')
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Failed to fetch GitHub user info: {e}")
        return None


def create_session(user_id: str) -> str:
    """Create a session token for a user."""
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {
        'user_id': user_id,
        'created_at': datetime.utcnow().isoformat(),
        'expires_at': (datetime.utcnow() + timedelta(days=7)).isoformat(),
    }
    return session_id


def get_session_user(session_id: str) -> Optional[str]:
    """Get user_id from session; return None if expired or invalid."""
    if session_id not in SESSIONS:
        return None
    sess = SESSIONS[session_id]
    if datetime.fromisoformat(sess['expires_at']) < datetime.utcnow():
        del SESSIONS[session_id]
        return None
    return sess['user_id']


def link_account(google_id: str, provider: str, provider_user: str, access_token: str, scopes: str, expires_at: Optional[str] = None):
    """Link a provider account to a user."""
    data = load_auth_data()
    if google_id not in data.get('linked_accounts', {}):
        data.setdefault('linked_accounts', {})[google_id] = {}
    data['linked_accounts'][google_id][provider] = {
        'provider_user': provider_user,
        'access_token': access_token,
        'scopes': scopes,
        'expires_at': expires_at,
        'created_at': datetime.utcnow().isoformat(),
    }
    save_auth_data(data)


def get_linked_accounts(google_id: str) -> Dict[str, Any]:
    """Get all linked accounts for a user."""
    data = load_auth_data()
    return data.get('linked_accounts', {}).get(google_id, {})


def create_or_get_user(google_id: str, email: str, name: str, picture: str) -> str:
    """Create a user if not exists; return google_id."""
    data = load_auth_data()
    if google_id not in data.get('users', {}):
        data.setdefault('users', {})[google_id] = {
            'email': email,
            'name': name,
            'picture': picture,
            'created_at': datetime.utcnow().isoformat(),
        }
        save_auth_data(data)
    return google_id


def get_user(google_id: str) -> Optional[Dict]:
    """Get user profile."""
    data = load_auth_data()
    return data.get('users', {}).get(google_id)


def get_current_user(x_user_id: Optional[str] = Header(None)) -> str:
    """
    Get current user ID from X-User-ID header.
    For development, accepts header like: X-User-ID: test-pro
    Returns user ID string.
    """
    if x_user_id:
        return x_user_id
    # Default test user if not provided
    return "test-user"

