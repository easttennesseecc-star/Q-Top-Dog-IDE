"""
LLM Configuration and Role Assignment System

Manages:
- API keys for cloud LLMs (Copilot, Gemini, ChatGPT, Grok, Claude)
- Local model downloads and installation
- Role assignments (Analysis, Code Generation, Research, Documentation, etc.)
- Model capabilities and constraints
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

# Configuration file paths
CONFIG_DIR = Path.home() / ".q-ide"
CONFIG_DIR.mkdir(exist_ok=True)

KEYS_FILE = CONFIG_DIR / "llm_keys.json"
ROLES_FILE = CONFIG_DIR / "llm_roles.json"
MODELS_FILE = CONFIG_DIR / "llm_models.json"

# LLM Role Definitions
LLM_ROLES = {
    "analysis": {
        "name": "Analysis & Understanding",
        "description": "Analyzes code, documents, and user intent",
        "capabilities": ["code_review", "documentation_analysis", "intent_parsing"],
        "recommended_models": ["copilot", "gpt-4", "gemini-pro", "claude-3"]
    },
    "coding": {
        "name": "Code Generation",
        "description": "Generates code, fixes bugs, writes tests",
        "capabilities": ["code_generation", "bug_fixing", "test_writing", "refactoring"],
        "recommended_models": ["copilot", "gpt-4", "claude-3", "gemini-pro"]
    },
    "research": {
        "name": "Research & Learning",
        "description": "Researches topics, provides explanations, educational content",
        "capabilities": ["research", "explanation", "learning", "tutorials"],
        "recommended_models": ["gemini-pro", "gpt-4", "claude-3", "perplexity"]
    },
    "documentation": {
        "name": "Documentation",
        "description": "Writes documentation, API docs, comments",
        "capabilities": ["documentation_writing", "api_documentation", "comments", "examples"],
        "recommended_models": ["gpt-4", "claude-3", "copilot", "gemini-pro"]
    },
    "optimization": {
        "name": "Optimization & Performance",
        "description": "Optimizes code performance, analyzes complexity",
        "capabilities": ["performance_analysis", "optimization", "complexity_analysis"],
        "recommended_models": ["gpt-4", "claude-3", "copilot"]
    },
    "creative": {
        "name": "Creative & Writing",
        "description": "Creative writing, content generation, brainstorming",
        "capabilities": ["creative_writing", "brainstorming", "content_generation"],
        "recommended_models": ["claude-3", "gpt-4", "gemini-pro"]
    },
    "local": {
        "name": "Local Processing",
        "description": "Private local processing, no API calls",
        "capabilities": ["local_code_analysis", "formatting", "linting"],
        "recommended_models": ["ollama", "llama-cpp", "gpt4all"]
    }
}

# Cloud LLM Configuration
CLOUD_LLMS = {
    "copilot": {
        "name": "GitHub Copilot",
        "provider": "github",
        "api_endpoint": "https://api.github.com/copilot",
        "auth_type": "github_token",
        "requires_vscode": True,
        "notes": "Best for coding. Requires VS Code + GitHub account."
    },
    "gpt-4": {
        "name": "OpenAI GPT-4",
        "provider": "openai",
        "api_endpoint": "https://api.openai.com/v1/chat/completions",
        "auth_type": "api_key",
        "requires_key": True,
        "notes": "Most capable. Requires OpenAI API key ($0.03-0.06 per 1K tokens)."
    },
    "gpt-4o": {
        "name": "OpenAI GPT-4 Omni",
        "provider": "openai",
        "api_endpoint": "https://api.openai.com/v1/chat/completions",
        "auth_type": "api_key",
        "requires_key": True,
        "notes": "Fast GPT-4 with vision. Same key as GPT-4."
    },
    "gemini-pro": {
        "name": "Google Gemini Pro",
        "provider": "google",
        "api_endpoint": "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent",
        "auth_type": "api_key",
        "requires_key": True,
        "free_tier": True,
        "notes": "Good quality, free tier available. Requires Google API key."
    },
    "claude-3": {
        "name": "Anthropic Claude 3",
        "provider": "anthropic",
        "api_endpoint": "https://api.anthropic.com/v1/messages",
        "auth_type": "api_key",
        "requires_key": True,
        "notes": "Excellent reasoning. Requires Anthropic API key."
    },
    "grok": {
        "name": "xAI Grok",
        "provider": "xai",
        "api_endpoint": "https://api.x.ai/v1/chat/completions",
        "auth_type": "api_key",
        "requires_key": True,
        "notes": "Real-time knowledge. Requires xAI API key."
    },
    "perplexity": {
        "name": "Perplexity AI",
        "provider": "perplexity",
        "api_endpoint": "https://api.perplexity.ai/chat/completions",
        "auth_type": "api_key",
        "requires_key": True,
        "free_tier": True,
        "notes": "Research focused with real-time web access. Requires API key."
    }
}

# Local Model Sources
LOCAL_MODELS = {
    "ollama": {
        "name": "Ollama",
        "type": "local_cli",
        "download_url": "https://ollama.ai",
        "setup_cmd": "ollama pull mistral",  # or llama2, neural-chat, etc
        "available_models": [
            "mistral:7b",
            "llama2:7b",
            "neural-chat:7b",
            "orca-mini:3b",
            "vicuna:7b"
        ],
        "notes": "Easy local LLM, supports multiple models, privacy-first"
    },
    "llama-cpp": {
        "name": "LLaMA C++",
        "type": "local_cli",
        "download_url": "https://github.com/ggerganov/llama.cpp",
        "setup_cmd": "See GitHub for model files",
        "available_models": [
            "mistral-7b-instruct-v0.2",
            "neural-chat-7b-v3-2",
            "orca-mini-7b-gguf"
        ],
        "notes": "Fast C++ implementation, good for CPU-only"
    },
    "gpt4all": {
        "name": "GPT4All",
        "type": "local_cli",
        "download_url": "https://gpt4all.io",
        "setup_cmd": "gpt4all-lora",
        "available_models": [
            "mistral-7b",
            "neural-chat-7b",
            "orca-mini-3b"
        ],
        "notes": "Easy installation, good quality models"
    }
}


def load_api_keys() -> Dict[str, str]:
    """Load saved API keys from config file."""
    if KEYS_FILE.exists():
        try:
            with open(KEYS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_api_key(provider: str, key: str) -> bool:
    """Save API key for a provider."""
    try:
        keys = load_api_keys()
        keys[provider] = key
        with open(KEYS_FILE, 'w') as f:
            json.dump(keys, f, indent=2)
        # Set restrictive permissions (Windows: hide file)
        os.chmod(KEYS_FILE, 0o600)
        return True
    except Exception as e:
        print(f"Error saving API key: {e}")
        return False


def get_api_key(provider: str) -> Optional[str]:
    """Get API key for a provider."""
    keys = load_api_keys()
    return keys.get(provider)


def delete_api_key(provider: str) -> bool:
    """Delete API key for a provider."""
    try:
        keys = load_api_keys()
        if provider in keys:
            del keys[provider]
            with open(KEYS_FILE, 'w') as f:
                json.dump(keys, f, indent=2)
            return True
        return False
    except Exception as e:
        print(f"Error deleting API key: {e}")
        return False


def load_role_assignments() -> Dict[str, str]:
    """Load LLM role assignments (slot -> model_name)."""
    if ROLES_FILE.exists():
        try:
            with open(ROLES_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_role_assignment(role: str, model_name: str) -> bool:
    """Assign a model to a role."""
    if role not in LLM_ROLES:
        return False
    
    try:
        assignments = load_role_assignments()
        assignments[role] = model_name
        
        with open(ROLES_FILE, 'w') as f:
            json.dump(assignments, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving role assignment: {e}")
        return False


def get_model_for_role(role: str) -> Optional[str]:
    """Get assigned model for a role."""
    assignments = load_role_assignments()
    return assignments.get(role)


def list_available_providers() -> Dict[str, Dict]:
    """List all available LLM providers with status."""
    providers = {}
    keys = load_api_keys()
    
    # Cloud LLMs
    for provider_id, config in CLOUD_LLMS.items():
        has_key = provider_id in keys and keys[provider_id]
        providers[provider_id] = {
            **config,
            "type": "cloud",
            "has_key": has_key,
            "configured": has_key or config.get("requires_vscode", False)
        }
    
    # Local models
    for model_id, config in LOCAL_MODELS.items():
        providers[model_id] = {
            **config,
            "type": "local",
            "configured": False  # Would need to check if installed
        }
    
    return providers


def get_role_recommendations(role: str) -> List[str]:
    """Get recommended models for a role."""
    if role not in LLM_ROLES:
        return []
    return LLM_ROLES[role].get("recommended_models", [])


def validate_api_key(provider: str, key: str) -> bool:
    """Validate API key format (basic check)."""
    if not key or len(key) < 10:
        return False
    
    # Provider-specific validation
    if provider == "openai":
        return key.startswith("sk-")
    elif provider == "google":
        return len(key) > 30
    elif provider == "anthropic":
        return key.startswith("sk-ant-")
    
    # Default: just check it's not empty
    return len(key) > 5


def get_setup_instructions(provider: str) -> str:
    """Get setup instructions for a provider."""
    instructions = {
        "openai": """
1. Go to https://platform.openai.com/account/api-keys
2. Create a new API key
3. Copy the key (starts with sk-)
4. Paste it here
5. Set billing at https://platform.openai.com/account/billing/overview
        """,
        "google": """
1. Go to https://makersuite.google.com/app/apikey
2. Create a new API key
3. Enable the Generative AI API
4. Copy the key
5. Paste it here (free tier: 60 requests/minute)
        """,
        "anthropic": """
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key
5. Copy and paste it here
        """,
        "xai": """
1. Go to https://console.x.ai/
2. Create an account
3. Navigate to API Keys
4. Create a new key
5. Paste it here
        """,
        "perplexity": """
1. Go to https://www.perplexity.ai/api
2. Sign up and verify email
3. Navigate to API Keys
4. Create a new key
5. Paste it here (free tier available)
        """,
        "ollama": """
1. Download from https://ollama.ai
2. Install and run: ollama serve
3. In another terminal: ollama pull mistral
4. LLM will be available at http://localhost:11434
        """,
        "gpt4all": """
1. Download from https://gpt4all.io
2. Install application
3. Download models through UI
4. Automatically available for local use
        """,
    }
    return instructions.get(provider, "No setup instructions available")


def get_q_assistant_llm() -> Optional[Dict]:
    """Get the LLM currently assigned to the Q Assistant."""
    # Q Assistant uses the "coding" role by default (most versatile)
    assigned_model = get_model_for_role("coding")
    
    if not assigned_model:
        # Try to find best available LLM
        from llm_pool import get_best_llms_for_operations
        best = get_best_llms_for_operations(1)
        if best:
            return {
                "id": best[0].get("name"),
                "name": best[0].get("name"),
                "source": best[0].get("source"),
                "status": "auto_selected",
                "assigned_role": "coding (auto-selected)",
                "priority_score": best[0].get("priority_score", 0)
            }
        return None
    
    # Assigned model found - get full details
    providers = list_available_providers()
    
    # Check if it's a cloud provider
    if assigned_model in CLOUD_LLMS:
        config = CLOUD_LLMS[assigned_model]
        return {
            "id": assigned_model,
            "name": config["name"],
            "type": "cloud",
            "source": config["provider"],
            "assigned_role": "coding",
            "has_credentials": bool(get_api_key(config["provider"])),
            "endpoint": config["api_endpoint"]
        }
    
    # Check if it's a local model
    if assigned_model in LOCAL_MODELS:
        config = LOCAL_MODELS[assigned_model]
        return {
            "id": assigned_model,
            "name": config["name"],
            "type": "local",
            "source": config["type"],
            "assigned_role": "coding",
            "download_url": config["download_url"]
        }
    
    return None


def format_provider_status() -> str:
    """Format current provider status for display."""
    providers = list_available_providers()
    lines = ["=== LLM Provider Status ===\n"]
    
    # Cloud providers
    lines.append("CLOUD SERVICES:")
    for prov_id, config in providers.items():
        if config.get("type") == "cloud":
            status = "✓ Configured" if config.get("configured") else "✗ Needs setup"
            lines.append(f"  {config['name']}: {status}")
    
    lines.append("\nLOCAL MODELS:")
    for prov_id, config in providers.items():
        if config.get("type") == "local":
            lines.append(f"  {config['name']}: Download at {config['download_url']}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    print(format_provider_status())
    print("\n=== Available Roles ===")
    for role_id, role_info in LLM_ROLES.items():
        print(f"{role_id}: {role_info['name']}")
        print(f"  Recommended: {', '.join(role_info['recommended_models'][:3])}")
