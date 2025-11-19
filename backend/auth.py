"""
OAuth and session management for Q-TopDog.

Supports Google SSO (primary identity) and provider account linking (GitHub, OpenAI, etc.).
Local dev storage uses a JSON file; for production, use a database + secrets manager.
"""

import json
import uuid
import os
import hashlib
import base64
from secrets import token_bytes
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

# -----------------------------
# Password-based auth (dev/temporary use only)
# Stored inside same auth data file under key password_users.
# Uses PBKDF2-HMAC SHA256 with per-user random salt.
# -----------------------------

PBKDF2_ITERATIONS = 200_000

def _hash_password(password: str, salt: Optional[bytes] = None) -> tuple[str, str, int]:
    if salt is None:
        salt = token_bytes(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, PBKDF2_ITERATIONS)
    return base64.b64encode(salt).decode('utf-8'), base64.b64encode(dk).decode('utf-8'), PBKDF2_ITERATIONS

def _verify_password(password: str, salt_b64: str, hash_b64: str, iterations: int) -> bool:
    try:
        salt = base64.b64decode(salt_b64.encode('utf-8'))
        expected = base64.b64decode(hash_b64.encode('utf-8'))
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
        return hashlib.sha256(dk).hexdigest() == hashlib.sha256(expected).hexdigest()
    except Exception:
        return False

def register_password_user(email: str, password: str, require_admin: bool = True, admin_token: Optional[str] = None) -> bool:
    """Register a password user. Returns True if created, False if exists or failed."""
    data = load_auth_data()
    existing = data.get('password_users', {}).get(email)
    if existing:
        return False
    if require_admin:
        env_token = os.getenv('ADMIN_TOKEN', '').strip()
        if not env_token or not admin_token or admin_token != env_token:
            return False
    salt_b64, hash_b64, iters = _hash_password(password)
    data.setdefault('password_users', {})[email] = {
        'salt': salt_b64,
        'hash': hash_b64,
        'iterations': iters,
        'created_at': datetime.utcnow().isoformat(),
    }
    save_auth_data(data)
    # Also create basic user profile if not present
    data = load_auth_data()
    if email not in data.get('users', {}):
        data.setdefault('users', {})[email] = {
            'email': email,
            'name': email.split('@')[0],
            'picture': '',
            'created_at': datetime.utcnow().isoformat(),
        }
        save_auth_data(data)
    return True

def verify_password_user(email: str, password: str) -> bool:
    data = load_auth_data()
    info = data.get('password_users', {}).get(email)
    if not info:
        return False
    return _verify_password(password, info.get('salt',''), info.get('hash',''), int(info.get('iterations', PBKDF2_ITERATIONS)))

def change_password_user(email: str, old_password: str, new_password: str) -> bool:
    if not verify_password_user(email, old_password):
        return False
    data = load_auth_data()
    if email not in data.get('password_users', {}):
        return False
    salt_b64, hash_b64, iters = _hash_password(new_password)
    data['password_users'][email]['salt'] = salt_b64
    data['password_users'][email]['hash'] = hash_b64
    data['password_users'][email]['iterations'] = iters
    data['password_users'][email]['updated_at'] = datetime.utcnow().isoformat()
    save_auth_data(data)
    return True

def admin_reset_password_user(email: str, new_password: str, admin_token: Optional[str]) -> bool:
    """Force reset (or create) a password user entry with admin token validation."""
    env_token = os.getenv('ADMIN_TOKEN', '').strip()
    if not env_token or not admin_token or admin_token != env_token:
        return False
    data = load_auth_data()
    salt_b64, hash_b64, iters = _hash_password(new_password)
    data.setdefault('password_users', {})[email] = {
        'salt': salt_b64,
        'hash': hash_b64,
        'iterations': iters,
        'updated_at': datetime.utcnow().isoformat(),
    }
    # Ensure basic profile exists
    data.setdefault('users', {}).setdefault(email, {
        'email': email,
        'name': email.split('@')[0],
        'picture': '',
        'created_at': datetime.utcnow().isoformat(),
    })
    save_auth_data(data)
    return True

# Optional automatic temp user provisioning via env vars (executed on import)
try:
    temp_email = os.getenv('TEMP_PASSWORD_EMAIL')
    temp_pass = os.getenv('TEMP_PASSWORD_PLAIN')
    auto_admin_token = os.getenv('ADMIN_TOKEN')
    if temp_email and temp_pass:
        register_password_user(temp_email, temp_pass, require_admin=False, admin_token=auto_admin_token)
except Exception:
    pass

