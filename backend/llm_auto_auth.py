"""
LLM Auto-Authentication System
Q-IDE - Intelligent Development Environment

Copyright (c) 2025 Quellum Technologies. All rights reserved.
Licensed under the MIT License

On startup, this system:
1. Checks which LLMs are assigned to roles
2. Checks if credentials exist for those LLMs
3. If missing, returns a list of what needs setup
4. Frontend can then prompt user or suggest alternatives
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from llm_config import CLOUD_LLMS, LLM_ROLES, get_api_key, get_model_for_role
from logger_utils import get_logger

logger = get_logger(__name__)

CONFIG_DIR = Path.home() / ".q-ide"


class LLMAuthenticationStatus:
    """Tracks authentication status for all LLMs"""
    
    def __init__(self):
        self.assigned_llms: Dict[str, str] = {}  # role -> llm_id
        self.missing_credentials: List[str] = []  # llm_ids without credentials
        self.authenticated_llms: List[str] = []  # llm_ids with credentials
        self.needs_setup: List[Dict] = []  # detailed setup info
    
    def to_dict(self):
        return {
            'assigned_llms': self.assigned_llms,
            'missing_credentials': self.missing_credentials,
            'authenticated_llms': self.authenticated_llms,
            'needs_setup': self.needs_setup,
            'all_ready': len(self.missing_credentials) == 0
        }


def get_assigned_llms() -> Dict[str, str]:
    """
    Get all LLMs assigned to roles.
    Returns: {role_id: llm_id}
    """
    roles_file = CONFIG_DIR / "llm_roles.json"
    
    if not roles_file.exists():
        return {}
    
    try:
        with open(roles_file) as f:
            roles_config = json.load(f)
            # Extract model_name (llm_id) from each role
            return {
                role_id: role_data.get('model_name', '')
                for role_id, role_data in roles_config.items()
                if role_data.get('model_name')
            }
    except Exception as e:
        logger.error(f"Error reading roles file: {e}")
        return {}


def check_credential_exists(llm_id: str) -> bool:
    """Check if API key or credential exists for an LLM"""
    try:
        key = get_api_key(llm_id)
        return bool(key)
    except:
        return False


def get_llm_setup_info(llm_id: str) -> Dict:
    """Get setup information for an LLM"""
    if llm_id not in CLOUD_LLMS:
        return {}
    
    llm_config = CLOUD_LLMS[llm_id]
    
    return {
        'llm_id': llm_id,
        'name': llm_config.get('name', llm_id),
        'provider': llm_config.get('provider', 'unknown'),
        'auth_type': llm_config.get('auth_type', 'unknown'),
        'notes': llm_config.get('notes', ''),
        'setup_url': get_setup_url(llm_id),
        'is_paid': llm_config.get('requires_key', False),
        'alternatives': get_alternative_llms(llm_id)
    }


def get_setup_url(llm_id: str) -> str:
    """Get URL where user can get credentials for an LLM"""
    urls = {
        'gpt-4': 'https://platform.openai.com/account/api-keys',
        'gpt-4o': 'https://platform.openai.com/account/api-keys',
        'gpt-3.5-turbo': 'https://platform.openai.com/account/api-keys',
        'gemini-pro': 'https://ai.google.dev/tutorials/setup',
        'gemini-1.5-pro': 'https://ai.google.dev/tutorials/setup',
        'gemini-1.5-flash': 'https://ai.google.dev/tutorials/setup',
        'claude-3-opus': 'https://console.anthropic.com/account/keys',
        'claude-3-sonnet': 'https://console.anthropic.com/account/keys',
        'claude-3-haiku': 'https://console.anthropic.com/account/keys',
        'copilot': 'https://github.com/settings/copilot',
        'grok': 'https://console.x.ai/account/keys',
        'groq': 'https://console.groq.com',
        'perplexity': 'https://www.perplexity.ai/settings',
        'ollama': 'https://ollama.ai/download'
    }
    return urls.get(llm_id, 'https://ai.google.dev')


def get_alternative_llms(llm_id: str) -> List[str]:
    """Get alternative LLMs that don't require paid credentials"""
    # Free/local alternatives
    free_alternatives = {
        'gpt-4': ['gemini-1.5-flash', 'ollama'],  # Gemini has free tier
        'gpt-4o': ['gemini-1.5-flash', 'ollama'],
        'gpt-3.5-turbo': ['gemini-1.5-flash', 'ollama'],
        'claude-3-opus': ['gemini-1.5-pro', 'gpt-3.5-turbo'],
        'claude-3-sonnet': ['gemini-1.5-flash', 'gpt-3.5-turbo'],
        'claude-3-haiku': ['gemini-1.5-flash', 'ollama'],
        'grok': ['gemini-1.5-flash', 'gpt-3.5-turbo'],
        'groq': ['gemini-1.5-flash', 'ollama'],
        'perplexity': ['gemini-1.5-flash', 'gpt-3.5-turbo'],
        'copilot': ['gemini-1.5-flash', 'ollama']
    }
    return free_alternatives.get(llm_id, ['gemini-1.5-flash', 'ollama'])


def check_all_llm_authentication() -> LLMAuthenticationStatus:
    """
    Check authentication status for all assigned LLMs.
    This runs on startup to see what's ready.
    """
    status = LLMAuthenticationStatus()
    
    # Get all assigned LLMs
    assigned = get_assigned_llms()
    status.assigned_llms = assigned
    
    logger.info(f"Checking authentication for {len(assigned)} assigned LLMs")
    
    # Check credentials for each
    for role_id, llm_id in assigned.items():
        if not llm_id:
            continue
        
        has_cred = check_credential_exists(llm_id)
        
        if has_cred:
            status.authenticated_llms.append(llm_id)
            logger.info(f"✓ {llm_id} authenticated (assigned to {role_id})")
        else:
            status.missing_credentials.append(llm_id)
            setup_info = get_llm_setup_info(llm_id)
            setup_info['assigned_role'] = LLM_ROLES.get(role_id, {}).get('name', role_id)
            status.needs_setup.append(setup_info)
            logger.warning(f"✗ {llm_id} missing credentials (assigned to {role_id})")
    
    return status


def get_startup_auth_prompt() -> Dict:
    """
    Get information to display to user on startup if credentials are missing.
    Returns dict with missing LLMs and what to do.
    """
    status = check_all_llm_authentication()
    
    if status.all_ready:
        return {
            'status': 'ready',
            'message': f"✓ All {len(status.authenticated_llms)} LLMs authenticated and ready!",
            'needs_action': False,
            'missing_count': 0
        }
    
    # Build user-friendly message
    return {
        'status': 'needs_setup',
        'message': f"⚠️ {len(status.missing_credentials)} LLM(s) need credentials",
        'missing_llms': status.needs_setup,
        'needs_action': True,
        'missing_count': len(status.missing_credentials),
        'action_options': [
            {
                'option': 'add_credentials',
                'label': 'Add Credentials Now',
                'description': 'Enter API keys for missing LLMs'
            },
            {
                'option': 'use_alternatives',
                'label': 'Use Alternative LLMs',
                'description': 'Switch to free/local alternatives'
            },
            {
                'option': 'proceed',
                'label': 'Proceed Without Setup',
                'description': 'Continue with smart fallback responses'
            }
        ]
    }


def get_auto_setup_candidates() -> List[Dict]:
    """
    Get LLMs that could be auto-setup (already have credentials).
    Or get free alternatives that could be recommended.
    """
    candidates = []
    
    # Check which LLMs have credentials
    for llm_id in CLOUD_LLMS.keys():
        if check_credential_exists(llm_id):
            candidates.append({
                'llm_id': llm_id,
                'name': CLOUD_LLMS[llm_id].get('name'),
                'status': 'ready',
                'action': 'assign_immediately'
            })
    
    # Add free options
    free_options = ['ollama', 'gemini-1.5-flash']  # Flash is free tier
    for llm_id in free_options:
        if llm_id not in [c['llm_id'] for c in candidates]:
            candidates.append({
                'llm_id': llm_id,
                'name': CLOUD_LLMS.get(llm_id, {}).get('name', llm_id),
                'status': 'free_available',
                'action': 'setup_free'
            })
    
    return candidates


async def handle_missing_credentials_action(action: str, user_choice: Optional[str] = None) -> Dict:
    """
    Handle user's choice when credentials are missing on startup.
    
    Actions:
    - 'add_credentials': Redirect to Auth tab
    - 'use_alternatives': Suggest alternatives
    - 'proceed': Continue with fallbacks
    """
    if action == 'add_credentials':
        return {
            'success': True,
            'action': 'redirect_to_auth',
            'message': 'Go to LLM Setup → Auth tab to add credentials',
            'url': '/llm_setup_auth'
        }
    
    elif action == 'use_alternatives':
        candidates = get_auto_setup_candidates()
        return {
            'success': True,
            'action': 'show_alternatives',
            'message': 'These LLMs are ready to use',
            'alternatives': candidates,
            'next_step': 'Choose one and assign in Roles tab'
        }
    
    elif action == 'proceed':
        return {
            'success': True,
            'action': 'use_fallbacks',
            'message': 'Proceeding with smart fallback responses',
            'note': 'Add credentials later in LLM Setup → Auth tab'
        }
    
    return {
        'success': False,
        'error': 'Unknown action'
    }


async def auto_setup_missing_llms() -> Dict:
    """
    Try to automatically setup missing LLMs using available credentials.
    Returns status of what was auto-assigned.
    """
    status = check_all_llm_authentication()
    
    if status.all_ready:
        return {'message': 'All LLMs already authenticated', 'auto_assigned': []}
    
    auto_assigned = []
    
    # For each missing credential
    for missing_setup in status.needs_setup:
        llm_id = missing_setup['llm_id']
        role_id = missing_setup.get('assigned_role')
        
        # Try to find an alternative that's ready
        alternatives = missing_setup.get('alternatives', [])
        
        for alt_id in alternatives:
            if check_credential_exists(alt_id):
                logger.info(f"Auto-assigning {alt_id} to replace missing {llm_id}")
                auto_assigned.append({
                    'original': llm_id,
                    'replacement': alt_id,
                    'role': role_id,
                    'reason': f'{alt_id} is available and has credentials'
                })
                break
    
    return {
        'message': f'Auto-assigned {len(auto_assigned)} LLM alternatives',
        'auto_assigned': auto_assigned,
        'still_missing': len(status.needs_setup) - len(auto_assigned)
    }


# Endpoint helpers for FastAPI integration
def get_auth_status_for_startup() -> Dict:
    """Get full authentication status for frontend on startup"""
    status = check_all_llm_authentication()
    prompt = get_startup_auth_prompt()
    candidates = get_auto_setup_candidates()
    
    return {
        **status.to_dict(),
        'startup_prompt': prompt,
        'auto_setup_candidates': candidates,
        'timestamp': str(Path.home() / ".q-ide" / "last_auth_check.txt")
    }
