"""
LLM Setup Wizard - Guides users through authenticating with LLM providers
and automatically assigns models to roles
"""

import logging
from typing import Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger("q-ide-topdog")

router = APIRouter(prefix="/api/setup", tags=["Setup Wizard"])


class LLMProvider(BaseModel):
    """LLM Provider configuration"""
    name: str                      # "OpenAI", "Anthropic", etc
    provider_id: str               # "openai", "anthropic", etc
    website: str                   # Link to sign up
    auth_method: str               # "api_key", "oauth", etc
    docs_link: str                 # Link to API docs
    description: str               # What this provider is good for
    free_tier: bool                # Has free tier?
    free_tier_notes: str          # Notes about free tier


# Known LLM providers
AVAILABLE_PROVIDERS = [
    LLMProvider(
        name="OpenAI",
        provider_id="openai",
        website="https://platform.openai.com/account/api-keys",
        auth_method="api_key",
        docs_link="https://platform.openai.com/docs/guides/authentication",
        description="GPT-4, GPT-3.5 - Best for planning, coding, and verification",
        free_tier=True,
        free_tier_notes="$5 free credits for 3 months"
    ),
    LLMProvider(
        name="Anthropic (Claude)",
        provider_id="anthropic",
        website="https://console.anthropic.com/account/keys",
        auth_method="api_key",
        docs_link="https://docs.anthropic.com/en/api/getting-started",
        description="Claude 3 - Excellent for code generation and reasoning",
        free_tier=True,
        free_tier_notes="$5 free credits"
    ),
    LLMProvider(
        name="Google (Gemini)",
        provider_id="google",
        website="https://makersuite.google.com/app/apikey",
        auth_method="api_key",
        docs_link="https://ai.google.dev/",
        description="Gemini Pro - Good all-around model",
        free_tier=True,
        free_tier_notes="Free tier available with rate limits"
    ),
    LLMProvider(
        name="Mistral AI",
        provider_id="mistral",
        website="https://console.mistral.ai/",
        auth_method="api_key",
        docs_link="https://docs.mistral.ai/getting-started/quickstart/",
        description="Mistral Large - Fast, cost-effective code generation",
        free_tier=True,
        free_tier_notes="$5 free credits"
    ),
]


class SetupStep(BaseModel):
    """A step in the setup wizard"""
    step_number: int
    title: str
    description: str
    action: str                    # "choose_provider", "enter_api_key", "verify_connection", etc
    data: Dict


@router.get("/wizard/start")
async def start_setup_wizard():
    """
    Start the setup wizard - guides user through LLM configuration
    
    Returns:
        Setup instructions and available providers
    """
    logger.info("[Setup Wizard] Starting setup wizard")
    
    return {
        "status": "wizard_started",
        "title": "Q-IDE LLM Setup Wizard",
        "description": "Let's set up your AI models to build amazing apps!",
        "steps": [
            {
                "step": 1,
                "title": "Choose LLM Provider(s)",
                "description": "Select which AI providers you want to use. You can use multiple!",
                "action": "select_providers",
                "providers": [
                    {
                        "name": p.name,
                        "provider_id": p.provider_id,
                        "description": p.description,
                        "free_tier": p.free_tier,
                        "free_tier_notes": p.free_tier_notes,
                        "website": p.website,
                    }
                    for p in AVAILABLE_PROVIDERS
                ]
            },
            {
                "step": 2,
                "title": "Get API Keys",
                "description": "Sign up and create API keys for your chosen providers",
                "action": "get_api_keys",
                "instructions": "Visit the provider websites to create free accounts and generate API keys"
            },
            {
                "step": 3,
                "title": "Enter API Keys",
                "description": "Enter your API keys in Q-IDE",
                "action": "enter_api_keys",
                "instructions": "Your API keys are stored securely locally on your PC"
            },
            {
                "step": 4,
                "title": "Verify & Auto-Assign",
                "description": "Q-IDE will automatically test your APIs and assign models to roles",
                "action": "verify_and_assign",
                "instructions": "This ensures your models are working and optimally assigned"
            },
        ],
        "estimated_time": "5 minutes"
    }


@router.get("/wizard/providers")
async def list_providers():
    """Get list of available LLM providers"""
    return {
        "providers": [
            {
                "name": p.name,
                "provider_id": p.provider_id,
                "description": p.description,
                "free_tier": p.free_tier,
                "free_tier_notes": p.free_tier_notes,
                "website": p.website,
                "auth_method": p.auth_method,
                "docs_link": p.docs_link,
            }
            for p in AVAILABLE_PROVIDERS
        ],
        "recommended": ["openai", "anthropic"],  # Start with these two
        "total_providers": len(AVAILABLE_PROVIDERS),
    }


@router.post("/wizard/save-api-keys")
async def save_api_keys(keys: Dict[str, str]):
    """
    Save API keys from setup wizard
    
    Args:
        keys: Dict like {"openai": "sk-...", "anthropic": "sk-ant-..."}
    
    Returns:
        Verification result
    """
    if not keys:
        raise HTTPException(status_code=400, detail="No API keys provided")
    
    logger.info(f"[Setup Wizard] Saving API keys for {len(keys)} provider(s)")
    
    try:
        from backend.llm_config import save_api_key
        
        saved_count = 0
        failed = []
        
        for provider_id, api_key in keys.items():
            try:
                save_api_key(provider_id, api_key)
                saved_count += 1
                logger.info(f"[Setup Wizard] Saved API key for {provider_id}")
            except Exception as e:
                logger.error(f"[Setup Wizard] Failed to save {provider_id}: {str(e)}")
                failed.append(provider_id)
        
        return {
            "status": "saved",
            "saved_count": saved_count,
            "failed": failed,
            "next_step": "verify_connections"
        }
    except Exception as e:
        logger.error(f"[Setup Wizard] Error saving API keys: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/wizard/verify-connections")
async def verify_connections():
    """
    Verify that all configured API keys work
    
    Returns:
        Connection status for each provider
    """
    logger.info("[Setup Wizard] Verifying API connections")
    
    try:
        from backend.llm_auth import verify_provider_connection, get_authenticated_providers
        
        authenticated = get_authenticated_providers()
        verification_results = {}
        
        for provider_id, is_auth in authenticated.items():
            if is_auth:
                try:
                    # Try to verify connection
                    result = verify_provider_connection(provider_id)
                    verification_results[provider_id] = {
                        "status": "connected",
                        "verified": result
                    }
                    logger.info(f"[Setup Wizard] {provider_id} verified")
                except Exception as e:
                    verification_results[provider_id] = {
                        "status": "error",
                        "error": str(e)
                    }
                    logger.error(f"[Setup Wizard] {provider_id} verification failed: {str(e)}")
        
        return {
            "status": "verification_complete",
            "results": verification_results,
            "next_step": "auto_assign_models"
        }
    except Exception as e:
        logger.error(f"[Setup Wizard] Verification error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/wizard/complete")
async def complete_setup():
    """
    Complete setup: verify APIs and auto-assign models
    
    Returns:
        Final setup status and LLM assignments
    """
    logger.info("[Setup Wizard] Completing setup - auto-assigning models")
    
    try:
        from backend.llm_auth import get_authenticated_providers
        from llm_auto_assignment import LLMAutoAssignment
        
        # Get authenticated providers
        authenticated_providers = get_authenticated_providers()
        
        if not any(authenticated_providers.values()):
            raise HTTPException(
                status_code=400,
                detail="No LLM providers authenticated. Please configure at least one API key."
            )
        
        # Auto-assign models
        assignment_system = LLMAutoAssignment()
        assignments = assignment_system.auto_assign_models(authenticated_providers)
        
        logger.info("[Setup Wizard] Setup complete - models assigned to roles")
        
        return {
            "status": "setup_complete",
            "message": "Your AI team is ready! Q-IDE will now help you build your app.",
            "assignments": {
                role.value: (model.model_id if model else None)
                for role, model in assignments.items()
            },
            "summary": assignment_system.get_assignment_summary(),
            "next_action": "redirect_to_dashboard"
        }
    except Exception as e:
        logger.error(f"[Setup Wizard] Setup completion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_setup_status():
    """Get current setup status"""
    try:
        from backend.llm_auth import get_authenticated_providers
        
        authenticated = get_authenticated_providers()
        completed_providers = [p for p, is_auth in authenticated.items() if is_auth]
        
        if not completed_providers:
            return {
                "status": "not_started",
                "message": "No LLM providers configured yet",
                "action": "start_wizard"
            }
        elif len(completed_providers) < 2:
            return {
                "status": "in_progress",
                "configured_providers": completed_providers,
                "message": f"You have {len(completed_providers)} provider(s) configured. Add more for better coverage!",
                "action": "add_more_providers"
            }
        else:
            return {
                "status": "complete",
                "configured_providers": completed_providers,
                "message": f"You're all set! {len(completed_providers)} LLM provider(s) configured",
                "action": "start_building"
            }
    except Exception as e:
        logger.error(f"[Setup Status] Error: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }
