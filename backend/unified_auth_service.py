"""
Unified Authentication Service for Q-IDE
Handles GitHub OAuth, Copilot API, LLM credentials, and repository access
"""
import os
import json
import secrets
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import hashlib
import base64
from dataclasses import dataclass, asdict


@dataclass
class OAuthSession:
    """OAuth session state"""
    session_id: str
    provider: str  # 'github', 'google', 'microsoft'
    state: str
    code_verifier: str
    created_at: datetime
    expires_at: datetime
    user_info: Optional[Dict] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    
    def is_valid(self) -> bool:
        return datetime.now() < self.expires_at
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'provider': self.provider,
            'state': self.state,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'user_info': self.user_info,
            'access_token': self.access_token,
        }


@dataclass
class UserProfile:
    """Unified user profile across all services"""
    user_id: str
    email: str
    name: str
    avatar_url: Optional[str] = None
    github_username: Optional[str] = None
    github_repos: List[str] = None
    connected_services: Dict[str, bool] = None  # {service: has_token}
    credentials: Dict[str, str] = None  # {service: encrypted_token}
    created_at: datetime = None
    last_login: datetime = None
    
    def __post_init__(self):
        if self.github_repos is None:
            self.github_repos = []
        if self.connected_services is None:
            self.connected_services = {}
        if self.credentials is None:
            self.credentials = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_login is None:
            self.last_login = datetime.now()
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'email': self.email,
            'name': self.name,
            'avatar_url': self.avatar_url,
            'github_username': self.github_username,
            'github_repos': self.github_repos,
            'connected_services': self.connected_services,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat(),
        }


@dataclass
class LLMCredential:
    """Individual LLM service credential"""
    service: str  # 'github_copilot', 'openai', 'anthropic', 'gemini', 'ollama'
    api_key: Optional[str] = None
    is_active: bool = False
    added_date: datetime = None
    last_used: Optional[datetime] = None
    cost_tier: Optional[str] = None  # 'free', 'paid', 'subscription'
    
    def __post_init__(self):
        if self.added_date is None:
            self.added_date = datetime.now()


class UnifiedAuthService:
    """
    Central authentication service for Q-IDE
    Manages OAuth flows, credential storage, and service integration
    """
    
    def __init__(self, storage_path: str = "./auth_storage"):
        self.storage_path = storage_path
        self.sessions: Dict[str, OAuthSession] = {}
        self.profiles: Dict[str, UserProfile] = {}
        self.ensure_storage()
        self.load_data()
    
    def ensure_storage(self):
        """Create storage directory"""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def load_data(self):
        """Load persisted data from storage"""
        profiles_file = os.path.join(self.storage_path, "profiles.json")
        if os.path.exists(profiles_file):
            try:
                with open(profiles_file, 'r') as f:
                    data = json.load(f)
                    # Reconstruct profiles
                    for user_id, profile_data in data.items():
                        self.profiles[user_id] = UserProfile(**profile_data)
            except Exception as e:
                print(f"Error loading profiles: {e}")
    
    def save_data(self):
        """Persist data to storage"""
        profiles_file = os.path.join(self.storage_path, "profiles.json")
        try:
            profiles_data = {
                uid: asdict(profile) 
                for uid, profile in self.profiles.items()
            }
            with open(profiles_file, 'w') as f:
                json.dump(profiles_data, f, default=str, indent=2)
        except Exception as e:
            print(f"Error saving profiles: {e}")
    
    # ============================================================================
    # OAuth Session Management
    # ============================================================================
    
    def create_oauth_session(self, provider: str) -> OAuthSession:
        """Create new OAuth session"""
        session_id = secrets.token_urlsafe(32)
        state = secrets.token_urlsafe(32)
        code_verifier = secrets.token_urlsafe(32)
        
        session = OAuthSession(
            session_id=session_id,
            provider=provider,
            state=state,
            code_verifier=code_verifier,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(minutes=15),
        )
        
        self.sessions[session_id] = session
        return session
    
    def get_oauth_session(self, session_id: str) -> Optional[OAuthSession]:
        """Retrieve and validate OAuth session"""
        session = self.sessions.get(session_id)
        if session and session.is_valid():
            return session
        else:
            self.sessions.pop(session_id, None)
            return None
    
    def complete_oauth_session(
        self,
        session_id: str,
        user_info: Dict[str, Any],
        access_token: str,
        refresh_token: Optional[str] = None
    ) -> Optional[UserProfile]:
        """Complete OAuth flow and create/update user profile"""
        session = self.get_oauth_session(session_id)
        if not session:
            return None
        
        email = user_info.get('email', '')
        name = user_info.get('name', 'User')
        avatar_url = user_info.get('picture', user_info.get('avatar_url'))
        
        # Check if user exists
        user_id = None
        for uid, profile in self.profiles.items():
            if profile.email == email:
                user_id = uid
                break
        
        # Create or update profile
        if not user_id:
            user_id = hashlib.sha256(email.encode()).hexdigest()[:16]
        
        if user_id in self.profiles:
            profile = self.profiles[user_id]
            profile.last_login = datetime.now()
        else:
            profile = UserProfile(
                user_id=user_id,
                email=email,
                name=name,
                avatar_url=avatar_url,
            )
        
        # Update with provider-specific info
        if session.provider == 'github':
            profile.github_username = user_info.get('login')
            profile.connected_services['github'] = True
            profile.credentials['github_oauth'] = access_token
        elif session.provider == 'google':
            profile.connected_services['google'] = True
            profile.credentials['google_oauth'] = access_token
        elif session.provider == 'microsoft':
            profile.connected_services['microsoft'] = True
            profile.credentials['microsoft_oauth'] = access_token
        
        self.profiles[user_id] = profile
        self.save_data()
        self.sessions.pop(session_id, None)
        
        return profile
    
    # ============================================================================
    # User Profile Management
    # ============================================================================
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile"""
        return self.profiles.get(user_id)
    
    def add_llm_credential(
        self,
        user_id: str,
        service: str,
        api_key: str,
        is_active: bool = True,
        cost_tier: Optional[str] = None
    ) -> bool:
        """Add LLM credential for user"""
        profile = self.profiles.get(user_id)
        if not profile:
            return False
        
        profile.credentials[service] = api_key
        profile.connected_services[service] = is_active
        profile.last_login = datetime.now()
        
        self.save_data()
        return True
    
    def remove_llm_credential(self, user_id: str, service: str) -> bool:
        """Remove LLM credential"""
        profile = self.profiles.get(user_id)
        if not profile:
            return False
        
        profile.credentials.pop(service, None)
        profile.connected_services.pop(service, None)
        self.save_data()
        return True
    
    def get_active_credentials(self, user_id: str) -> Dict[str, str]:
        """Get all active credentials for user"""
        profile = self.profiles.get(user_id)
        if not profile:
            return {}
        
        return {
            service: api_key
            for service, api_key in profile.credentials.items()
            if profile.connected_services.get(service, False)
        }
    
    # ============================================================================
    # GitHub Repository Access
    # ============================================================================
    
    def fetch_github_repos(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Fetch user's GitHub repositories
        Requires active GitHub OAuth token
        """
        profile = self.profiles.get(user_id)
        if not profile or 'github_oauth' not in profile.credentials:
            return []
        
        try:
            import requests
            
            access_token = profile.credentials['github_oauth']
            headers = {
                'Authorization': f'token {access_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Get user repos
            resp = requests.get(
                'https://api.github.com/user/repos',
                headers=headers,
                params={'per_page': 100}
            )
            
            if resp.status_code == 200:
                repos = resp.json()
                profile.github_repos = [r['full_name'] for r in repos]
                self.save_data()
                return repos
        except Exception as e:
            print(f"Error fetching GitHub repos: {e}")
        
        return []
    
    def get_repository_content(
        self,
        user_id: str,
        repo: str,
        path: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Get repository file/folder content
        Requires active GitHub OAuth token
        """
        profile = self.profiles.get(user_id)
        if not profile or 'github_oauth' not in profile.credentials:
            return None
        
        try:
            import requests
            
            access_token = profile.credentials['github_oauth']
            headers = {
                'Authorization': f'token {access_token}',
                'Accept': 'application/vnd.github.v3.raw'
            }
            
            resp = requests.get(
                f'https://api.github.com/repos/{repo}/contents/{path}',
                headers=headers
            )
            
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"Error fetching repo content: {e}")
        
        return None
    
    # ============================================================================
    # Service Status
    # ============================================================================
    
    def get_service_status(self, user_id: str) -> Dict[str, Any]:
        """Get status of all connected services"""
        profile = self.profiles.get(user_id)
        if not profile:
            return {}
        
        status = {
            'github': {
                'connected': profile.connected_services.get('github', False),
                'username': profile.github_username,
                'repos_count': len(profile.github_repos),
            },
            'copilot': {
                'connected': profile.connected_services.get('github_copilot', False),
                'configured': 'github_copilot' in profile.credentials,
            },
            'google': {
                'connected': profile.connected_services.get('google', False),
            },
            'llm_services': {
                service: profile.connected_services.get(service, False)
                for service in profile.credentials.keys()
                if service not in ['github_oauth', 'google_oauth', 'microsoft_oauth']
            }
        }
        
        return status
    
    # ============================================================================
    # All Services Overview
    # ============================================================================
    
    def get_all_available_services(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available services"""
        return {
            'github_oauth': {
                'name': 'GitHub OAuth',
                'description': 'Sign in with GitHub account',
                'category': 'authentication',
                'free': True,
            },
            'github_copilot': {
                'name': 'GitHub Copilot',
                'description': 'AI-powered code completion',
                'category': 'coding',
                'cost': 'paid',
                'requires': ['github_oauth'],
            },
            'google_oauth': {
                'name': 'Google OAuth',
                'description': 'Sign in with Google account',
                'category': 'authentication',
                'free': True,
            },
            'openai': {
                'name': 'OpenAI GPT-4',
                'description': 'ChatGPT API for advanced code generation',
                'category': 'llm',
                'cost': 'paid',
                'free_tier': True,
            },
            'anthropic': {
                'name': 'Claude (Anthropic)',
                'description': 'Claude AI for analysis and generation',
                'category': 'llm',
                'cost': 'paid',
                'free_tier': True,
            },
            'google_gemini': {
                'name': 'Google Gemini',
                'description': 'Google\'s AI model',
                'category': 'llm',
                'free': True,
            },
            'ollama_local': {
                'name': 'Ollama (Local)',
                'description': 'Run LLMs locally on your machine',
                'category': 'llm',
                'free': True,
                'local': True,
            },
            'gpt4all': {
                'name': 'GPT4All (Local)',
                'description': 'Free local AI models',
                'category': 'llm',
                'free': True,
                'local': True,
            },
        }
