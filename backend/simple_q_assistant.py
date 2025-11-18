"""
Simple Q Assistant Chat - Works with or without full LLM configuration
Provides intelligent responses and guides user through setup if needed
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("q-ide-topdog")


def get_available_llm_source() -> Optional[str]:
    """Detect which LLM source is available and can be used"""
    
    # Check for OpenAI
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    
    # Check for Google
    if os.getenv("GOOGLE_API_KEY"):
        return "google"
    
    # Check for Anthropic
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    
    # Check for Ollama (local)
    try:
        import requests  # type: ignore[import-untyped]
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
        if response.status_code == 200:
            return "ollama"
    except:
        pass
    
    return None


from typing import List as _List
def get_simple_response(user_message: str, conversation_history: Optional[_List[Dict[str, Any]]] = None) -> str:
    """
    Get a response from Q Assistant
    Falls back to intelligent mock responses if no LLM is available
    """
    
    conversation_history = conversation_history or []
    
    # Build context from history
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-5:]])
    
    # Key phrases to detect user intent
    lower_msg = user_message.lower()
    
    # Detect app/build intent
    if any(word in lower_msg for word in ["app", "build", "create", "develop", "make", "cross-platform", "ios", "android", "mobile"]):
        return _handle_app_build_request(user_message, context)
    
    # Detect setup/configuration intent
    if any(word in lower_msg for word in ["setup", "configure", "llm", "api key", "provider", "connect"]):
        return _handle_setup_request()
    
    # Detect requirement gathering
    if any(word in lower_msg for word in ["what", "how", "tell", "explain", "describe", "like", "want", "need"]):
        return _handle_requirements_gathering(user_message, context)
    
    # Default response
    return _generate_default_response(user_message)


def _handle_app_build_request(user_message: str, context: str) -> str:
    """Handle requests to build or create an app"""
    return """Great! I'm ready to help you build your app. Let me gather some requirements:

📱 **App Details I Need:**
1. **Platform**: iOS, Android, or both (cross-platform)?
2. **App Type**: What does your app do? (e.g., social media, fitness tracker, note app, etc.)
3. **Core Features**: What are the 3-5 main features?
4. **Tech Stack Preference**: Any preference? (React Native, Flutter, Swift, Kotlin, etc.)
5. **User Authentication**: Do users need to log in?
6. **Backend**: Does it need a backend server/database?
7. **Timeline**: How urgent is this?

**Please describe your app idea in as much detail as possible.** The more you tell me, the better code I can generate for you!

For example: "I want to build a fitness tracking app for iOS and Android that lets users log workouts, track calories, and see progress charts. It needs user authentication and a backend to store data."

What's your app idea? 🚀"""


def _handle_setup_request() -> str:
    """Handle LLM setup requests"""
    return """I see you're setting up your LLM provider. Here's what you need to do:

**Quick Setup (Choose One):**

🔓 **Option 1: Use FREE Local LLM (Ollama)**
- Download Ollama: https://ollama.ai
- Run: `ollama run mistral`
- Done! No API keys needed, completely free!

🔑 **Option 2: OpenAI (Recommended for Power Users)**
- Get API key: https://platform.openai.com/api-keys
- Set environment variable: `set OPENAI_API_KEY=your_key`
- Requires credits ($)

🌐 **Option 3: Google Gemini (Free Tier Available)**
- Get API key: https://ai.google.dev
- Set: `set GOOGLE_API_KEY=your_key`

📎 **Option 4: Anthropic Claude**
- Get API key: https://claude.ai
- Set: `set ANTHROPIC_API_KEY=your_key`

**After Setup:**
1. Restart Q-IDE: Close and re-run LAUNCH_Q-IDE.bat
2. Come back here and start building!

Which LLM are you using? ✨"""


def _handle_requirements_gathering(user_message: str, context: str) -> str:
    """Handle requirement gathering questions"""
    
    lower_msg = user_message.lower()
    
    if any(word in lower_msg for word in ["feature", "requirement"]):
        return """Perfect! For your app, I'll need to know:

**Features I should understand:**
- What specific functionality does each feature need?
- Are there user roles? (admin, user, guest, etc.)
- Do users collaborate or just individual use?
- Real-time updates needed?
- Offline functionality?

**Performance Considerations:**
- How many users do you expect?
- How large is the data you're storing?
- Does it need real-time syncing?

Tell me more details and I'll generate the perfect code structure! 🎯"""
    
    if any(word in lower_msg for word in ["database", "data", "storage", "backend"]):
        return """Great question about backend/data!

**For your app, I need to know:**
- What data will you store? (users, posts, files, etc.)
- How much data? (KB, MB, GB?)
- Need real-time updates?
- Multiple users accessing same data?
- Offline-first or cloud-first?

**Backend Options I can set up:**
1. **Node.js + MongoDB** - Great for apps with flexible data
2. **Python + PostgreSQL** - Best for structured data
3. **Firebase** - Easiest (no backend code needed!)
4. **Serverless (AWS Lambda)** - For scale without maintenance

What type of backend fits best? 🔧"""
    
    if any(word in lower_msg for word in ["user", "auth", "login", "account"]):
        return """Smart thinking about user authentication!

**Authentication options I can implement:**
1. **Simple Username/Password** - Basic & traditional
2. **OAuth 2.0** - Let users login with Google/Apple/Facebook
3. **JWT Tokens** - Secure API-based authentication
4. **Biometric** (iOS: Face ID/Touch ID, Android: Fingerprint)

**For your app:**
- Do users create accounts or use social login?
- Should data be private per user?
- Any admin features needed?
- Session timeout preferences?

Tell me your authentication needs! 🔐"""
    
    return """I'm here to help! You can ask me:
- About your app idea
- What features to include
- How to set up your LLM
- Technical architecture questions
- Code generation help
- Debugging issues

What would you like to discuss? 💡"""


def _generate_default_response(user_message: str) -> str:
    """Generate a contextual default response"""
    
    # Check if LLM is available
    available_llm = get_available_llm_source()
    
    if available_llm:
        return f"""I'm your Q Assistant! I detected you have {available_llm.upper()} configured.

However, I'm running in smart-response mode to help you describe your app clearly.

**To build your cross-platform app, tell me:**
1. What does your app do?
2. What are the main features?
3. Who are your users?
4. What platforms? (iOS, Android, or both?)

Once I understand your requirements, I'll generate the complete, production-ready codebase for you! 🚀

What's your app idea? 💡"""
    else:
        return """👋 Welcome to Q Assistant!

I can help you build your iOS/Android app, but first I need to know:

**📝 Your App:**
- What's the idea? (e.g., fitness app, todo app, etc.)
- Main features? (3-5 key features)
- Target platforms? (iOS, Android, or both?)

**⚙️ Setup Needed:**
I see you haven't configured an LLM provider yet. That's OK! You can:
1. Use **free local Ollama** (recommended for testing)
2. Add your **OpenAI/Google/Claude API key**

**Quick Start:**
Tell me your app idea now, and I'll guide you through setup!

What would you like to build? 🎯"""
