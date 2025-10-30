"""
Unified Authentication API Routes for Q-IDE
Handles OAuth flows, credential management, and service integration
"""
from fastapi import APIRouter, HTTPException, Query, Body, BackgroundTasks
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Dict, List, Optional, Any
import os
import secrets
from datetime import datetime
from .unified_auth_service import UnifiedAuthService

# Initialize service
auth_service = UnifiedAuthService()

router = APIRouter(prefix="/auth", tags=["authentication"])

# ============================================================================
# Pydantic Models
# ============================================================================

class OAuthInitRequest(BaseModel):
    provider: str  # 'github', 'google', 'microsoft'


class OAuthInitResponse(BaseModel):
    session_id: str
    auth_url: str
    state: str


class OAuthCallbackRequest(BaseModel):
    session_id: str
    code: str
    state: str


class UserProfileResponse(BaseModel):
    user_id: str
    email: str
    name: str
    avatar_url: Optional[str]
    github_username: Optional[str]
    github_repos: List[str]
    connected_services: Dict[str, bool]
    created_at: str
    last_login: str


class LLMCredentialRequest(BaseModel):
    service: str  # 'openai', 'anthropic', 'github_copilot', etc.
    api_key: str
    is_active: bool = True


class ServiceStatusResponse(BaseModel):
    github: Dict[str, Any]
    copilot: Dict[str, Any]
    google: Dict[str, Any]
    llm_services: Dict[str, Any]


class RepositoryInfo(BaseModel):
    name: str
    full_name: str
    description: Optional[str]
    url: str
    language: Optional[str]


# ============================================================================
# OAuth Initialization
# ============================================================================

OAUTH_CONFIGS = {
    'github': {
        'client_id': os.getenv('GITHUB_OAUTH_CLIENT_ID', ''),
        'client_secret': os.getenv('GITHUB_OAUTH_CLIENT_SECRET', ''),
        'auth_url': 'https://github.com/login/oauth/authorize',
        'token_url': 'https://github.com/login/oauth/access_token',
        'user_url': 'https://api.github.com/user',
        'scopes': ['user:email', 'read:user', 'repo'],
    },
    'google': {
        'client_id': os.getenv('GOOGLE_OAUTH_CLIENT_ID', ''),
        'client_secret': os.getenv('GOOGLE_OAUTH_CLIENT_SECRET', ''),
        'auth_url': 'https://accounts.google.com/o/oauth2/v2/auth',
        'token_url': 'https://oauth2.googleapis.com/token',
        'user_url': 'https://openidconnect.googleapis.com/v1/userinfo',
        'scopes': ['openid', 'email', 'profile'],
    },
    'microsoft': {
        'client_id': os.getenv('MICROSOFT_OAUTH_CLIENT_ID', ''),
        'client_secret': os.getenv('MICROSOFT_OAUTH_CLIENT_SECRET', ''),
        'auth_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
        'token_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
        'user_url': 'https://graph.microsoft.com/v1.0/me',
        'scopes': ['openid', 'email', 'profile'],
    }
}


@router.post("/oauth/init", response_model=OAuthInitResponse)
async def init_oauth(request: OAuthInitRequest):
    """
    Initialize OAuth flow for specified provider
    Returns auth URL and session ID
    """
    provider = request.provider.lower()
    
    if provider not in OAUTH_CONFIGS:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
    
    config = OAUTH_CONFIGS[provider]
    if not config['client_id']:
        raise HTTPException(
            status_code=400,
            detail=f"{provider} OAuth not configured. Set environment variables."
        )
    
    # Create OAuth session
    session = auth_service.create_oauth_session(provider)
    
    # Build auth URL
    params = {
        'client_id': config['client_id'],
        'redirect_uri': f"{os.getenv('APP_URL', 'http://localhost:3000')}/auth/oauth/callback",
        'scope': ' '.join(config['scopes']),
        'state': session.state,
        'response_type': 'code',
    }
    
    auth_url = f"{config['auth_url']}?" + "&".join(
        f"{k}={v}" for k, v in params.items()
    )
    
    return OAuthInitResponse(
        session_id=session.session_id,
        auth_url=auth_url,
        state=session.state,
    )


@router.post("/oauth/callback")
async def oauth_callback(request: OAuthCallbackRequest, background_tasks: BackgroundTasks):
    """
    Handle OAuth callback from provider
    Exchanges authorization code for access token
    """
    session = auth_service.get_oauth_session(request.session_id)
    if not session:
        raise HTTPException(status_code=400, detail="Invalid or expired session")
    
    if session.state != request.state:
        raise HTTPException(status_code=400, detail="State mismatch")
    
    provider = session.provider
    config = OAUTH_CONFIGS[provider]
    
    try:
        import requests
        
        # Exchange code for token
        token_response = requests.post(
            config['token_url'],
            data={
                'client_id': config['client_id'],
                'client_secret': config['client_secret'],
                'code': request.code,
                'grant_type': 'authorization_code',
                'redirect_uri': f"{os.getenv('APP_URL', 'http://localhost:3000')}/auth/oauth/callback",
            },
            headers={'Accept': 'application/json'},
        )
        
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        
        token_data = token_response.json()
        access_token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token')
        
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token in response")
        
        # Get user info
        user_response = requests.get(
            config['user_url'],
            headers={'Authorization': f'Bearer {access_token}'},
        )
        
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        user_info = user_response.json()
        
        # Complete session and create profile
        profile = auth_service.complete_oauth_session(
            request.session_id,
            user_info,
            access_token,
            refresh_token,
        )
        
        if not profile:
            raise HTTPException(status_code=400, detail="Failed to create user profile")
        
        # Fetch GitHub repos in background if GitHub provider
        if provider == 'github':
            background_tasks.add_task(auth_service.fetch_github_repos, profile.user_id)
        
        return {
            'success': True,
            'user_id': profile.user_id,
            'email': profile.email,
            'name': profile.name,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth error: {str(e)}")


# ============================================================================
# User Profile Management
# ============================================================================

@router.get("/profile/{user_id}", response_model=UserProfileResponse)
async def get_profile(user_id: str):
    """Get user profile with all connected services"""
    profile = auth_service.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserProfileResponse(
        user_id=profile.user_id,
        email=profile.email,
        name=profile.name,
        avatar_url=profile.avatar_url,
        github_username=profile.github_username,
        github_repos=profile.github_repos,
        connected_services=profile.connected_services,
        created_at=profile.created_at.isoformat(),
        last_login=profile.last_login.isoformat(),
    )


# ============================================================================
# LLM Credential Management
# ============================================================================

@router.post("/credentials/add")
async def add_credential(user_id: str = Query(...), request: LLMCredentialRequest = Body(...)):
    """Add or update LLM credential for user"""
    success = auth_service.add_llm_credential(
        user_id=user_id,
        service=request.service,
        api_key=request.api_key,
        is_active=request.is_active,
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add credential")
    
    return {'success': True, 'message': f'{request.service} credential added'}


@router.post("/credentials/remove")
async def remove_credential(user_id: str = Query(...), service: str = Query(...)):
    """Remove LLM credential"""
    success = auth_service.remove_llm_credential(user_id, service)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to remove credential")
    
    return {'success': True, 'message': f'{service} credential removed'}


@router.get("/credentials/active/{user_id}")
async def get_active_credentials(user_id: str):
    """Get all active credentials for user"""
    credentials = auth_service.get_active_credentials(user_id)
    return {
        'user_id': user_id,
        'active_services': list(credentials.keys()),
        'count': len(credentials),
    }


# ============================================================================
# Service Status
# ============================================================================

@router.get("/services/status/{user_id}", response_model=ServiceStatusResponse)
async def get_services_status(user_id: str):
    """Get status of all connected services"""
    status = auth_service.get_service_status(user_id)
    if not status:
        raise HTTPException(status_code=404, detail="User not found")
    
    return status


@router.get("/services/available")
async def get_available_services():
    """Get information about all available services"""
    return auth_service.get_all_available_services()


# ============================================================================
# GitHub Repository Access
# ============================================================================

@router.get("/github/repos/{user_id}")
async def get_github_repos(user_id: str, background_tasks: BackgroundTasks):
    """Get user's GitHub repositories"""
    profile = auth_service.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    
    if 'github_oauth' not in profile.credentials:
        raise HTTPException(status_code=400, detail="GitHub not connected")
    
    # Refresh repos in background
    background_tasks.add_task(auth_service.fetch_github_repos, user_id)
    
    return {
        'repos': profile.github_repos,
        'count': len(profile.github_repos),
        'username': profile.github_username,
    }


@router.get("/github/repos/{user_id}/{repo_name}/content")
async def get_repo_content(user_id: str, repo_name: str, path: str = Query("")):
    """Get repository file or folder content"""
    profile = auth_service.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    
    if 'github_oauth' not in profile.credentials:
        raise HTTPException(status_code=400, detail="GitHub not connected")
    
    # Build full repo name
    repo_full_name = f"{profile.github_username}/{repo_name}"
    
    content = auth_service.get_repository_content(user_id, repo_full_name, path)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return content


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def health_check():
    """Check authentication service health"""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'oauth_providers_configured': [
            p for p in OAUTH_CONFIGS.keys()
            if OAUTH_CONFIGS[p]['client_id']
        ],
    }
