"""
OAuth Authentication Routes for LLM Providers
Q-IDE - Intelligent Development Environment

Copyright (c) 2025 Quellum Technologies. All rights reserved.
Licensed under the MIT License

Endpoints:
- GET /llm_auth/providers - List OAuth-enabled providers
- GET /llm_auth/login/{provider} - Initiate OAuth login
- GET /llm_auth/callback - Handle OAuth callback
- GET /llm_auth/status - Check authentication status
- POST /llm_auth/logout/{provider} - Revoke OAuth token
- GET /llm_auth/user/{provider} - Get user info from OAuth provider
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, Optional

from backend.llm_oauth_auth import get_oauth_handler, OAUTH_PROVIDERS

router = APIRouter(prefix="/llm_auth", tags=["llm_oauth_auth"])


class OAuthLoginResponse(BaseModel):
    provider: str
    oauth_url: str
    client_required: bool
    message: Optional[str] = None


class OAuthCallbackResponse(BaseModel):
    success: bool
    provider: str
    user_id: Optional[str] = None
    message: str


class AuthStatusResponse(BaseModel):
    provider: str
    authenticated: bool
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    expires_at: Optional[str] = None
    auth_method: str


@router.get("/providers")
async def get_oauth_providers():
    """
    Get list of OAuth-enabled LLM providers

    Returns:
    {
        "providers": [
            {
                "id": "google",
                "name": "Google",
                "configured": true/false,
                "description": "Sign in with Google Credentials"
            },
            ...
        ]
    }
    """
    handler = get_oauth_handler()

    providers_list = []
    for provider_id, provider_config in OAUTH_PROVIDERS.items():
        is_configured = handler.config.has_client_id(provider_id)
        providers_list.append(
            {
                "id": provider_id,
                "name": provider_config.get("name", provider_id.capitalize()),
                "configured": is_configured,
                "description": f"Sign in with {provider_config.get('name', provider_id.capitalize())}",
                "oauth_enabled": True,
            }
        )

    return {"providers": providers_list, "total": len(providers_list)}


@router.get("/login/{provider}")
async def initiate_oauth_login(provider: str):
    """
    Initiate OAuth login flow for provider

    Returns:
    {
        "success": true,
        "provider": "google",
        "oauth_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
        "message": "Redirect to this URL to sign in"
    }
    OR
    {
        "success": false,
        "provider": "google",
        "client_required": true,
        "message": "OAuth client ID not configured"
    }
    """
    handler = get_oauth_handler()

    # Validate provider
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=400, detail="Invalid provider")

    # Check if OAuth is configured
    if not handler.config.has_client_id(provider):
        return {
            "success": False,
            "provider": provider,
            "client_required": True,
            "message": f"OAuth not configured for {provider}. Setup client ID in environment or config.",
        }

    # Generate OAuth URL
    oauth_url = handler.get_oauth_url(provider)
    if not oauth_url:
        raise HTTPException(status_code=500, detail="Failed to generate OAuth URL")

    return {
        "success": True,
        "provider": provider,
        "oauth_url": oauth_url,
        "message": "Redirect user to this URL to sign in",
    }


@router.get("/callback")
async def handle_oauth_callback(
    code: str = Query(...), state: str = Query(...), provider: str = Query(...)
):
    """
    Handle OAuth provider callback

    This endpoint receives the authorization code from the OAuth provider
    and exchanges it for an access token.

    Query Parameters:
    - code: Authorization code from provider
    - state: State token for security verification
    - provider: OAuth provider (google, github, etc.)

    Returns:
    {
        "success": true,
        "provider": "google",
        "user_id": "user@example.com",
        "message": "Successfully authenticated!"
    }
    """
    handler = get_oauth_handler()

    # Validate provider
    if provider not in OAUTH_PROVIDERS:
        error_html = """
        <html>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>❌ Authentication Error</h1>
                <p>Invalid OAuth provider</p>
                <p><a href="http://localhost:1431">Return to Q-IDE</a></p>
            </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=400)

    # Handle OAuth callback
    success, token_data, error = handler.handle_callback(provider, code, state)

    if not success:
        error_html = f"""
        <html>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>❌ Authentication Failed</h1>
                <p>{error}</p>
                <p><a href="http://localhost:1431">Return to Q-IDE</a></p>
            </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=400)

    # Get user info
    token_data = token_data or {}
    access_token = token_data.get("access_token")
    user_info = None
    if isinstance(access_token, str):
        user_info = handler.get_user_info(provider, access_token)

    if user_info:
        token_data["user_info"] = user_info

    # Store token
    handler.store_token(provider, token_data)

    # Get stored token to verify
    stored = handler.get_stored_token(provider)
    user_id = stored.get("user_id") if stored else None

    # Return success HTML that signals the main window
    success_html = f"""
    <html>
        <head>
            <title>Q-IDE OAuth Success</title>
        </head>
        <body style="font-family: Arial; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <div style="background: white; border-radius: 10px; padding: 40px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); max-width: 500px; margin: 0 auto;">
                <h1>✅ Authentication Successful!</h1>
                <p style="font-size: 16px; color: #666;">
                    Successfully signed in with <strong>{provider.capitalize()}</strong>
                </p>
                <p style="font-size: 14px; color: #999;">
                    User ID: {user_id}
                </p>
                <p style="margin-top: 20px; color: #666;">
                    You can close this window and return to Q-IDE.
                </p>
            </div>

            <script>
                // Signal parent window
                if (window.opener) {{
                    window.opener.postMessage({{
                        type: 'oauth_success',
                        provider: '{provider}',
                        user_id: '{user_id}'
                    }}, '*');
                    
                    // Close this window
                    setTimeout(() => window.close(), 2000);
                }}
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=success_html)


@router.get("/status")
async def get_auth_status():
    """
    Get authentication status for all providers

    Returns:
    {
        "providers": {
            "google": {
                "authenticated": true,
                "user_id": "user@example.com",
                "user_email": "user@example.com",
                "expires_at": "2025-11-28T...",
                "auth_method": "oauth"
            },
            ...
        }
    }
    """
    handler = get_oauth_handler()
    statuses = {}

    for provider in OAUTH_PROVIDERS.keys():
        token_data = handler.get_stored_token(provider)
        if token_data:
            statuses[provider] = {
                "authenticated": True,
                "user_id": token_data.get("user_id"),
                "user_email": token_data.get("user_email"),
                "expires_at": token_data.get("expires_at"),
                "auth_method": "oauth",
            }
        else:
            statuses[provider] = {
                "authenticated": False,
                "user_id": None,
                "user_email": None,
                "expires_at": None,
                "auth_method": None,
            }

    return {"providers": statuses}


@router.post("/logout/{provider}")
async def logout_provider(provider: str):
    """
    Logout from OAuth provider (revoke token)

    Returns:
    {
        "success": true,
        "provider": "google",
        "message": "Successfully logged out"
    }
    """
    handler = get_oauth_handler()

    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=400, detail="Invalid provider")

    success = handler.revoke_token(provider)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to revoke token")

    return {
        "success": True,
        "provider": provider,
        "message": f"Successfully logged out from {provider}",
    }


@router.get("/user/{provider}")
async def get_user_profile(provider: str):
    """
    Get user profile information from OAuth provider

    Returns:
    {
        "success": true,
        "user": {
            "id": "user@example.com",
            "email": "user@example.com",
            "name": "User Name",
            "picture": "https://..."
        }
    }
    """
    handler = get_oauth_handler()

    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=400, detail="Invalid provider")

    # Get stored token
    token_data = handler.get_stored_token(provider)
    if not token_data:
        raise HTTPException(status_code=401, detail="Not authenticated with this provider")

    # Get user info (already stored in token_data)
    user_info = {
        "id": token_data.get("user_id"),
        "email": token_data.get("user_email"),
    }

    return {"success": True, "user": user_info}


# Import HTMLResponse here to avoid circular import
from fastapi.responses import HTMLResponse
