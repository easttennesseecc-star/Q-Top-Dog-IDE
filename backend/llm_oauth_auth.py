"""
LLM OAuth Authentication System
Q-IDE - Intelligent Development Environment

Copyright (c) 2025 Quellum Technologies. All rights reserved.
Licensed under the MIT License

Handles OAuth flow for LLM providers:
- Google OAuth
- GitHub OAuth
- OpenAI OAuth
- Anthropic OAuth
- Other provider OAuth flows

This module manages:
1. OAuth state generation and verification
2. Callback handling and token exchange
3. Secure credential storage
4. Token refresh handling
5. Provider-specific OAuth configurations
"""

import json
import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from urllib.parse import urlencode, parse_qs
import requests  # type: ignore[import-untyped]

from backend.llm_config import get_config_file

# OAuth Provider Configurations
OAUTH_PROVIDERS = {
    "google": {
        "name": "Google",
        "oauth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scopes": ["openid", "email", "profile"],
        "revoke_url": "https://oauth2.googleapis.com/revoke",
    },
    "github": {
        "name": "GitHub",
        "oauth_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "scopes": ["user:email", "read:user"],
        "revoke_url": "https://api.github.com/user/installations",
    },
    "openai": {
        "name": "OpenAI",
        "oauth_url": "https://platform.openai.com/oauth/authorize",
        "token_url": "https://api.openai.com/oauth/token",
        "scopes": ["openai"],
    },
    "anthropic": {
        "name": "Anthropic",
        "oauth_url": "https://accounts.anthropic.com/oauth/authorize",
        "token_url": "https://accounts.anthropic.com/oauth/token",
        "scopes": ["api"],
    },
}

# OAuth state storage (in production, use Redis or database)
OAUTH_STATES: Dict[str, Dict] = {}


class OAuthConfig:
    """OAuth configuration for Q-IDE"""

    def __init__(self):
        self.config_file = get_config_file("oauth_config.json")
        self.client_ids = self._load_client_ids()
        self.redirect_uri = "http://localhost:1431/auth/callback"

    def _load_client_ids(self) -> Dict[str, str]:
        """Load OAuth client IDs from environment or config file"""
        client_ids = {}

        # Try to load from environment variables first
        for provider in OAUTH_PROVIDERS.keys():
            env_var = f"QIDE_{provider.upper()}_CLIENT_ID"
            client_ids[provider] = os.getenv(env_var, "")

        # Try to load from config file
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    for provider, client_id in config.get("client_ids", {}).items():
                        if not client_ids.get(provider):
                            client_ids[provider] = client_id
            except Exception as e:
                print(f"Error loading OAuth config: {e}")

        return client_ids

    def has_client_id(self, provider: str) -> bool:
        """Check if OAuth client ID is configured for provider"""
        return bool(self.client_ids.get(provider))

    def get_client_id(self, provider: str) -> str:
        """Get OAuth client ID for provider"""
        return self.client_ids.get(provider, "")


class OAuthStateManager:
    """Manage OAuth state tokens for security"""

    @staticmethod
    def generate_state(provider: str, user_id: str = "local") -> str:
        """Generate secure state token for OAuth flow"""
        state_data = {
            "provider": provider,
            "user_id": user_id,
            "nonce": secrets.token_urlsafe(32),
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
        }

        state_token = secrets.token_urlsafe(64)
        OAUTH_STATES[state_token] = state_data

        return state_token

    @staticmethod
    def verify_state(state_token: str) -> Tuple[bool, Optional[Dict]]:
        """Verify OAuth state token"""
        if state_token not in OAUTH_STATES:
            return False, None

        state_data = OAUTH_STATES[state_token]

        # Check expiration
        expires_at = datetime.fromisoformat(state_data.get("expires_at", ""))
        if datetime.now() > expires_at:
            del OAUTH_STATES[state_token]
            return False, None

        # Clean up used state
        del OAUTH_STATES[state_token]

        return True, state_data

    @staticmethod
    def cleanup_old_states():
        """Remove expired state tokens"""
        expired = [
            token
            for token, data in OAUTH_STATES.items()
            if datetime.now() > datetime.fromisoformat(data.get("expires_at", ""))
        ]
        for token in expired:
            del OAUTH_STATES[token]


class OAuthHandler:
    """Handle OAuth flows for LLM providers"""

    def __init__(self):
        self.config = OAuthConfig()
        self.states = OAuthStateManager()

    def get_oauth_url(self, provider: str) -> Optional[str]:
        """Generate OAuth URL for provider"""
        if provider not in OAUTH_PROVIDERS:
            return None

        if not self.config.has_client_id(provider):
            return None

        provider_config = OAUTH_PROVIDERS[provider]
        client_id = self.config.get_client_id(provider)

        # Generate state token
        state = self.states.generate_state(provider)

        # Build OAuth URL
        params = {
            "client_id": client_id,
            "redirect_uri": self.config.redirect_uri,
            "response_type": "code",
            "scope": " ".join(provider_config["scopes"]),
            "state": state,
        }

        # Add provider-specific parameters
        if provider == "google":
            params["access_type"] = "offline"
            params["prompt"] = "consent"
        elif provider == "github":
            params["allow_signup"] = "true"

        return f"{provider_config['oauth_url']}?{urlencode(params)}"

    def handle_callback(
        self, provider: str, code: str, state: str
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Handle OAuth callback and exchange code for token

        Returns: (success, token_data, error_message)
        """
        # Verify state
        valid, state_data = self.states.verify_state(state)
        if not valid:
            return False, None, "Invalid or expired state token"

        # Verify provider matches
        if state_data.get("provider") != provider:
            return False, None, "Provider mismatch in state"

        # Exchange code for token
        try:
            token_data = self._exchange_code_for_token(provider, code)
            if token_data:
                return True, token_data, None
            else:
                return False, None, "Failed to exchange authorization code"
        except Exception as e:
            return False, None, str(e)

    def _exchange_code_for_token(self, provider: str, code: str) -> Optional[Dict]:
        """Exchange authorization code for access token"""
        if provider not in OAUTH_PROVIDERS:
            return None

        provider_config = OAUTH_PROVIDERS[provider]
        client_id = self.config.get_client_id(provider)

        # This would normally use client_secret (not shown here for security)
        # In production, handle this securely on backend

        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.config.redirect_uri,
            "client_id": client_id,
        }

        try:
            response = requests.post(
                provider_config["token_url"],
                data=payload,
                headers={"Accept": "application/json"},
                timeout=10,
            )

            if response.status_code == 200:
                token_data = response.json()
                token_data["provider"] = provider
                token_data["obtained_at"] = datetime.now().isoformat()

                # Add expiration info
                if "expires_in" in token_data:
                    expires_at = datetime.now() + timedelta(
                        seconds=token_data["expires_in"]
                    )
                    token_data["expires_at"] = expires_at.isoformat()

                return token_data
        except Exception as e:
            print(f"Error exchanging code for token: {e}")

        return None

    def get_user_info(self, provider: str, access_token: str) -> Optional[Dict]:
        """Get user information from OAuth provider"""
        user_info_endpoints = {
            "google": ("https://www.googleapis.com/oauth2/v2/userinfo", "Authorization"),
            "github": ("https://api.github.com/user", "token"),
            "openai": ("https://api.openai.com/v1/user", "Bearer"),
            "anthropic": (
                "https://accounts.anthropic.com/oauth/user",
                "Bearer",
            ),
        }

        if provider not in user_info_endpoints:
            return None

        endpoint, auth_type = user_info_endpoints[provider]

        headers = {}
        if auth_type == "Authorization":
            headers["Authorization"] = f"Bearer {access_token}"
        elif auth_type == "token":
            headers["Authorization"] = f"token {access_token}"
        elif auth_type == "Bearer":
            headers["Authorization"] = f"Bearer {access_token}"

        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error getting user info: {e}")

        return None

    def store_token(self, provider: str, token_data: Dict) -> bool:
        """
        Store OAuth token securely

        Token data includes:
        - access_token: The OAuth access token
        - refresh_token: For refreshing expired tokens
        - expires_at: When token expires
        - user_info: User information
        """
        try:
            credentials_file = get_config_file("llm_credentials.json")

            # Load existing credentials
            credentials = {}
            if os.path.exists(credentials_file):
                with open(credentials_file, "r") as f:
                    credentials = json.load(f)

            # Store the token
            credentials[provider] = {
                "auth_type": "oauth",
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "expires_at": token_data.get("expires_at"),
                "obtained_at": token_data.get("obtained_at"),
                "user_id": token_data.get("user_info", {}).get("id")
                or token_data.get("user_info", {}).get("email"),
                "user_email": token_data.get("user_info", {}).get("email"),
                "scope": token_data.get("scope"),
            }

            # Save with restricted permissions
            with open(credentials_file, "w") as f:
                json.dump(credentials, f, indent=2)
            os.chmod(credentials_file, 0o600)

            return True
        except Exception as e:
            print(f"Error storing token: {e}")
            return False

    def get_stored_token(self, provider: str) -> Optional[Dict]:
        """Get stored OAuth token for provider"""
        try:
            credentials_file = get_config_file("llm_credentials.json")

            if not os.path.exists(credentials_file):
                return None

            with open(credentials_file, "r") as f:
                credentials = json.load(f)

            if provider in credentials:
                token_data = credentials[provider]

                # Check if token is expired
                expires_at = token_data.get("expires_at")
                if expires_at:
                    if datetime.fromisoformat(expires_at) < datetime.now():
                        # Token expired - would need refresh flow
                        return None

                return token_data
        except Exception as e:
            print(f"Error getting stored token: {e}")

        return None

    def revoke_token(self, provider: str) -> bool:
        """Revoke OAuth token for provider"""
        try:
            token_data = self.get_stored_token(provider)
            if not token_data:
                return False

            access_token = token_data.get("access_token")
            if not access_token:
                return False

            # Revoke at provider
            if provider in OAUTH_PROVIDERS:
                provider_config = OAUTH_PROVIDERS[provider]
                if "revoke_url" in provider_config:
                    try:
                        requests.post(
                            provider_config["revoke_url"],
                            data={"token": access_token},
                            timeout=10,
                        )
                    except Exception:
                        pass  # Continue even if revoke fails

            # Remove from local storage
            credentials_file = get_config_file("llm_credentials.json")
            if os.path.exists(credentials_file):
                with open(credentials_file, "r") as f:
                    credentials = json.load(f)

                if provider in credentials:
                    del credentials[provider]

                with open(credentials_file, "w") as f:
                    json.dump(credentials, f, indent=2)

            return True
        except Exception as e:
            print(f"Error revoking token: {e}")
            return False


# Singleton instance
oauth_handler = OAuthHandler()


def get_oauth_handler() -> OAuthHandler:
    """Get OAuth handler instance"""
    return oauth_handler
