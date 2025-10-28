"""
Auto-setup Q Assistant with available LLMs
Try to detect and configure Q Assistant automatically if possible
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from llm_config import get_q_assistant_llm

logger = logging.getLogger("q-ide-topdog")


def check_ollama_available() -> bool:
    """Check if Ollama is running on localhost:11434"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def check_openai_configured() -> bool:
    """Check if OpenAI API key is already in env vars"""
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
    return bool(api_key)


def auto_setup_q_assistant() -> Optional[Dict[str, Any]]:
    """
    Try to auto-configure Q Assistant:
    1. Check if already configured
    2. Try Ollama
    3. Try OpenAI from env vars
    4. Return None if nothing works
    """
    try:
        # First check if Q Assistant is already configured
        existing_llm = get_q_assistant_llm()
        if existing_llm:
            logger.info(f"Q Assistant already configured with: {existing_llm.get('name')}")
            return existing_llm
        
        # Try Ollama
        logger.info("Checking for Ollama...")
        if check_ollama_available():
            logger.info("✓ Ollama detected at localhost:11434")
            return {
                "name": "Mistral (Ollama)",
                "source": "ollama",
                "status": "available"
            }
        
        # Try OpenAI from environment
        if check_openai_configured():
            logger.info("✓ OpenAI API key detected in environment variables")
            return {
                "name": "GPT-4 (OpenAI)",
                "source": "openai",
                "status": "available"
            }
        
        logger.info("No LLM auto-detected. User should configure one manually via LLM Setup.")
        return None
        
    except Exception as e:
        logger.error(f"Error in auto_setup_q_assistant: {str(e)}")
        return None


if __name__ == "__main__":
    result = auto_setup_q_assistant()
    if result:
        print(f"✓ Q Assistant auto-detected: {result['name']}")
    else:
        print("⚠ Could not auto-configure Q Assistant")

