"""
LLM Configuration API Routes

Endpoints for:
- Managing API keys for cloud LLMs
- Assigning roles to LLMs
- Getting setup instructions
- Listing available providers
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import Dict, List, Optional, Any
from backend.llm_config import (
    CLOUD_LLMS, LOCAL_MODELS, LLM_ROLES,
    load_api_keys, save_api_key, delete_api_key, get_api_key,
    load_role_assignments, save_role_assignment, get_model_for_role,
    list_available_providers, get_role_recommendations, 
    validate_api_key, get_setup_instructions, format_provider_status,
    get_q_assistant_llm
)
from backend.llm_auto_auth import (
    check_all_llm_authentication, get_startup_auth_prompt,
    get_auto_setup_candidates, handle_missing_credentials_action,
    get_auth_status_for_startup
)
from backend.llm_pool import build_llm_report

router = APIRouter(prefix="/llm_config", tags=["llm_config"])


class APIKeyRequest(BaseModel):
    provider: str
    key: str


class RoleAssignmentRequest(BaseModel):
    role: str
    model_name: str
    # Suppress protected namespace warning for field name 'model_name'
    model_config = ConfigDict(protected_namespaces=())


@router.get("/providers")
async def get_providers():
    """Get all available LLM providers with configuration status."""
    return {
        "cloud": {k: v for k, v in list_available_providers().items() if v.get("type") == "cloud"},
        "local": {k: v for k, v in list_available_providers().items() if v.get("type") == "local"},
        "status": format_provider_status()
    }


@router.get("/roles")
async def get_roles():
    """Get all available LLM roles and their recommendations."""
    result: Dict[str, Any] = {}
    for role_id, role_info in LLM_ROLES.items():
        result[role_id] = {
            **role_info,
            "current_model": get_model_for_role(role_id)
        }
    return result


@router.get("/roles/{role_id}/recommendations")
async def get_role_recommendations_endpoint(role_id: str):
    """Get recommended models for a specific role."""
    if role_id not in LLM_ROLES:
        raise HTTPException(status_code=404, detail=f"Role '{role_id}' not found")
    
    recommendations = get_role_recommendations(role_id)
    role_info = LLM_ROLES[role_id]
    
    return {
        "role": role_id,
        "name": role_info["name"],
        "description": role_info["description"],
        "recommendations": recommendations,
        "current_assignment": get_model_for_role(role_id)
    }


@router.post("/api_key")
async def set_api_key(request: APIKeyRequest):
    """Save API key for a cloud provider."""
    if request.provider not in CLOUD_LLMS:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {request.provider}")
    
    if not validate_api_key(request.provider, request.key):
        raise HTTPException(status_code=400, detail=f"Invalid API key format for {request.provider}")
    
    if save_api_key(request.provider, request.key):
        return {
            "success": True,
            "provider": request.provider,
            "message": f"API key saved for {CLOUD_LLMS[request.provider]['name']}"
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to save API key")


@router.get("/api_key/{provider}")
async def check_api_key(provider: str):
    """Check if API key exists for a provider (doesn't return the key)."""
    if provider not in CLOUD_LLMS:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
    
    key = get_api_key(provider)
    return {
        "provider": provider,
        "has_key": bool(key),
        "configured": bool(key),
        "notes": CLOUD_LLMS[provider].get("notes", "")
    }


@router.delete("/api_key/{provider}")
async def delete_api_key_endpoint(provider: str):
    """Delete API key for a provider."""
    if provider not in CLOUD_LLMS:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
    
    if delete_api_key(provider):
        return {
            "success": True,
            "provider": provider,
            "message": f"API key deleted for {provider}"
        }
    else:
        return {
            "success": False,
            "provider": provider,
            "message": "No API key found for this provider"
        }


@router.post("/role_assignment")
async def assign_role(request: RoleAssignmentRequest):
    """Assign a model to a role."""
    if request.role not in LLM_ROLES:
        raise HTTPException(status_code=400, detail=f"Unknown role: {request.role}")
    
    # Verify model exists in providers
    if request.model_name not in list_available_providers():
        raise HTTPException(status_code=400, detail=f"Unknown model: {request.model_name}")
    
    if save_role_assignment(request.role, request.model_name):
        return {
            "success": True,
            "role": request.role,
            "model": request.model_name,
            "message": f"Assigned {request.model_name} to {LLM_ROLES[request.role]['name']}"
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to save role assignment")


@router.get("/role_assignment/{role_id}")
async def get_role_assignment(role_id: str):
    """Get current model assigned to a role."""
    if role_id not in LLM_ROLES:
        raise HTTPException(status_code=404, detail=f"Role '{role_id}' not found")
    
    current = get_model_for_role(role_id)
    role_info = LLM_ROLES[role_id]
    
    return {
        "role": role_id,
        "name": role_info["name"],
        "description": role_info["description"],
        "current_model": current,
        "recommendations": get_role_recommendations(role_id)
    }


@router.get("/setup/{provider}")
async def get_setup_instructions_endpoint(provider: str):
    """Get setup instructions for a provider."""
    if provider not in CLOUD_LLMS and provider not in LOCAL_MODELS:
        raise HTTPException(status_code=404, detail=f"Provider '{provider}' not found")
    
    config: Dict[str, Any] = (CLOUD_LLMS.get(provider) or LOCAL_MODELS.get(provider) or {})
    
    return {
        "provider": provider,
        "name": config.get("name"),
        "instructions": get_setup_instructions(provider),
        "notes": config.get("notes", ""),
        "url": config.get("download_url") or config.get("api_endpoint", "")
    }


@router.get("/q_assistant")
async def get_q_assistant_config():
    """Get the current LLM assigned to Q Assistant.
    
    Returns the LLM that Q Assistant will use for chat and operations.
    - If a model is assigned to the 'coding' role, uses that
    - Otherwise auto-selects the best available LLM
    - If no LLM is available, returns None with instructions
    """
    llm = get_q_assistant_llm()
    
    if not llm:
        return {
            "status": "not_configured",
            "llm": None,
            "message": "Q Assistant needs an LLM. Configure one via the LLM Setup panel.",
            "setup_url": "/llm_config/setup/openai",
            "instructions": "1. Go to LLM Setup -> Providers\n2. Choose a cloud provider (OpenAI, Gemini, etc.) or install local LLM (Ollama)\n3. Add API key or set up local model\n4. Assign to 'Coding' role\n5. Restart Q Assistant"
        }
    
    # LLM is configured
    response = {
        "status": "configured",
        "llm": llm,
        "ready": True
    }
    
    # Add warning if cloud provider but no credentials
    if llm.get("type") == "cloud" and not llm.get("has_credentials"):
        response["status"] = "needs_credentials"
        response["ready"] = False
        response["warning"] = f"API credentials needed for {llm['name']}"
    
    return response

@router.get("/local_detect")
async def detect_local_llms():
    """Detect locally available LLM tooling (BYOK local-first onboarding).

    Returns available local CLI / model entries and suggests an auto-assignment
    for Q Assistant if none is currently configured.
    """
    report = build_llm_report()
    available = report.get("available", [])
    local_entries = [i for i in available if (i.get("source") in ("cli", "local", "service", "process")) and ("ollama" in (i.get("name") or "").lower() or i.get("source") == "cli")]
    suggestion = None
    # Suggest Ollama first
    for item in local_entries:
        if "ollama" in (item.get("name") or "").lower():
            suggestion = item
            break
    if not suggestion and local_entries:
        suggestion = local_entries[0]
    # Check if q_assistant already configured
    from backend.llm_config import get_model_for_role, save_role_assignment
    already = get_model_for_role("q_assistant") or get_model_for_role("coding")
    auto_assigned = False
    if not already and suggestion:
        # Persist assignment so subsequent calls report configured
        save_role_assignment("q_assistant", suggestion.get("name"))
        auto_assigned = True
    return {
        "local_llms": local_entries,
        "total_local": len(local_entries),
        "suggestion": suggestion,
        "auto_assigned": auto_assigned,
        "assigned_model": get_model_for_role("q_assistant") or get_model_for_role("coding")
    }


@router.get("/status")
async def get_configuration_status():
    """Get overall LLM configuration status."""
    providers = list_available_providers()
    roles = LLM_ROLES
    
    configured_cloud = sum(1 for p in providers.values() if p.get("type") == "cloud" and p.get("configured"))
    total_cloud = sum(1 for p in providers.values() if p.get("type") == "cloud")
    
    assigned_roles = sum(1 for role in roles.keys() if get_model_for_role(role))
    total_roles = len(roles)
    
    return {
        "cloud_providers": {
            "configured": configured_cloud,
            "total": total_cloud
        },
        "role_assignments": {
            "assigned": assigned_roles,
            "total": total_roles
        },
        "status": "ready" if configured_cloud > 0 or assigned_roles > 0 else "needs_setup",
        "message": f"Configured {configured_cloud}/{total_cloud} cloud providers and assigned {assigned_roles}/{total_roles} roles"
    }


@router.get("/startup_auth_status")
async def get_startup_auth_status():
    """
    Get authentication status on startup.
    Checks which LLMs are assigned vs which have credentials.
    Returns what actions user needs to take.
    """
    return get_auth_status_for_startup()


@router.get("/missing_credentials")
async def get_missing_llm_credentials():
    """
    Get list of LLMs that are assigned but missing credentials.
    Includes setup URLs and alternatives.
    """
    status = check_all_llm_authentication()
    prompt = get_startup_auth_prompt()
    
    return {
        "has_issues": not status.all_ready,
        "missing_count": len(status.missing_credentials),
        "authenticated_count": len(status.authenticated_llms),
        "details": status.needs_setup,
        "user_prompt": prompt
    }


@router.get("/auto_setup_candidates")
async def get_llm_setup_candidates():
    """
    Get LLMs that can be used immediately (already have credentials)
    or are free/local alternatives.
    """
    candidates = get_auto_setup_candidates()
    
    return {
        "available_now": [c for c in candidates if c['status'] == 'ready'],
        "free_options": [c for c in candidates if c['status'] == 'free_available'],
        "total_options": len(candidates)
    }


class MissingCredentialsActionRequest(BaseModel):
    action: str  # 'add_credentials', 'use_alternatives', 'proceed'
    user_choice: Optional[str] = None  # alternative llm_id if using alternatives


@router.post("/handle_missing_credentials")
async def handle_missing_credentials(request: MissingCredentialsActionRequest):
    """
    Handle user's choice when LLM credentials are missing on startup.
    
    Actions:
    - 'add_credentials': Show Auth tab
    - 'use_alternatives': Get list of ready alternatives  
    - 'proceed': Continue with smart fallbacks
    """
    result = await handle_missing_credentials_action(request.action, request.user_choice)
    return result
