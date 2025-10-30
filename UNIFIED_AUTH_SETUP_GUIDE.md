# 🔐 Unified Authentication System for Q-IDE

## Overview

This is a **complete single sign-in system** that integrates:

✅ **GitHub OAuth** - Repository access + sign-in  
✅ **GitHub Copilot** - AI code completion  
✅ **LLM Models** - OpenAI, Claude, Gemini, Ollama, GPT4All  
✅ **Google OAuth** - Sign-in + Gemini access  
✅ **Microsoft OAuth** - Enterprise integration  

**One login. All tools. No manual config.**

---

## What's New

### Backend Files

**`backend/unified_auth_service.py`** (450 lines)
- Core authentication engine
- OAuth session management
- User profile management
- Credential storage
- GitHub repository integration
- Service status tracking

**`backend/unified_auth_routes.py`** (400 lines)
- 12 REST API endpoints for authentication
- OAuth initiation and callbacks
- Credential management
- Service status endpoints
- GitHub repository access endpoints

### Frontend Components

**`frontend/src/components/UnifiedSignInHub.tsx`** (650 lines)
- Complete sign-in UI
- Service status display
- Credential management forms
- Repository browsing (coming soon)
- Beautiful dark theme with gradients

---

## Architecture

```
User's Browser
    ↓
UnifiedSignInHub.tsx (Frontend UI)
    ↓
/auth/* API endpoints (Backend)
    ↓
UnifiedAuthService (Business Logic)
    ↓
OAuth Providers (GitHub, Google, Microsoft)
    ↓
LLM Services (OpenAI, Anthropic, Google, Ollama)
    ↓
GitHub API (Repository Access)
```

---

## Quick Setup (15 minutes)

### Step 1: Configure Environment Variables

Add to your `.env` file:

```bash
# GitHub OAuth
GITHUB_OAUTH_CLIENT_ID=your_github_app_client_id
GITHUB_OAUTH_CLIENT_SECRET=your_github_app_client_secret

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret

# Microsoft OAuth (Optional)
MICROSOFT_OAUTH_CLIENT_ID=your_microsoft_app_id
MICROSOFT_OAUTH_CLIENT_SECRET=your_microsoft_app_secret

# App URLs
APP_URL=http://localhost:3000
API_URL=http://localhost:8000
```

### Step 2: Set Up OAuth Applications

#### GitHub OAuth
1. Go to: https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in:
   - **Application name:** Q-IDE
   - **Homepage URL:** http://localhost:3000
   - **Authorization callback URL:** http://localhost:3000/auth/oauth/callback
4. Copy Client ID and Client Secret to `.env`

#### Google OAuth
1. Go to: https://console.cloud.google.com/
2. Create new project: "Q-IDE"
3. Enable APIs: Google+ API
4. Create OAuth 2.0 credentials (Web application)
5. Add authorized redirect URIs: http://localhost:3000/auth/oauth/callback
6. Copy credentials to `.env`

#### Microsoft OAuth (Optional)
1. Go to: https://portal.azure.com/
2. Azure Active Directory → App registrations → New registration
3. Set redirect URI: http://localhost:3000/auth/oauth/callback
4. Create client secret
5. Copy to `.env`

### Step 3: Update Backend (`main.py`)

Add these lines to your FastAPI app:

```python
from backend.unified_auth_routes import router as auth_router

# Add after your other route registrations:
app.include_router(auth_router)
```

### Step 4: Update Frontend (`App.tsx`)

Add the sign-in hub to your app:

```tsx
import { UnifiedSignInHub } from './components/UnifiedSignInHub';

function App() {
  return (
    <div>
      {/* Your other routes */}
      <UnifiedSignInHub />
    </div>
  );
}
```

### Step 5: Install Dependencies

```bash
pip install requests  # For OAuth and API calls
```

### Step 6: Test

```bash
# Backend
python backend/main.py

# Frontend
npm start
```

Visit: http://localhost:3000/auth

You should see the sign-in hub with GitHub, Google, and Microsoft options.

---

## API Reference

### OAuth Endpoints

#### Initialize OAuth
```
POST /auth/oauth/init
Content-Type: application/json

{
  "provider": "github"  // "github" | "google" | "microsoft"
}

Response:
{
  "session_id": "abc123...",
  "auth_url": "https://github.com/login/oauth/authorize?...",
  "state": "xyz789..."
}
```

#### Handle OAuth Callback
```
POST /auth/oauth/callback
Content-Type: application/json

{
  "session_id": "abc123...",
  "code": "code_from_provider",
  "state": "xyz789..."
}

Response:
{
  "success": true,
  "user_id": "user123",
  "email": "user@example.com",
  "name": "John Doe"
}
```

### Profile Endpoints

#### Get User Profile
```
GET /auth/profile/{user_id}

Response:
{
  "user_id": "user123",
  "email": "user@example.com",
  "name": "John Doe",
  "avatar_url": "https://...",
  "github_username": "johndoe",
  "github_repos": ["repo1", "repo2"],
  "connected_services": {
    "github": true,
    "google": false,
    "github_copilot": true,
    "openai": true
  },
  "created_at": "2024-01-15T10:30:00",
  "last_login": "2024-01-20T14:45:00"
}
```

### Credential Endpoints

#### Add Credential
```
POST /auth/credentials/add?user_id=user123
Content-Type: application/json

{
  "service": "openai",  // "openai" | "anthropic" | "github_copilot" | etc.
  "api_key": "sk-...",
  "is_active": true
}

Response:
{
  "success": true,
  "message": "openai credential added"
}
```

#### Get Active Credentials
```
GET /auth/credentials/active/{user_id}

Response:
{
  "user_id": "user123",
  "active_services": ["openai", "github_copilot", "google_gemini"],
  "count": 3
}
```

### Service Endpoints

#### Get Available Services
```
GET /auth/services/available

Response:
{
  "github_oauth": {
    "name": "GitHub OAuth",
    "description": "Sign in with GitHub account",
    "category": "authentication",
    "free": true
  },
  "github_copilot": {
    "name": "GitHub Copilot",
    "description": "AI-powered code completion",
    "category": "coding",
    "cost": "paid",
    "requires": ["github_oauth"]
  },
  ...
}
```

#### Get Service Status
```
GET /auth/services/status/{user_id}

Response:
{
  "github": {
    "connected": true,
    "username": "johndoe",
    "repos_count": 15
  },
  "copilot": {
    "connected": true,
    "configured": true
  },
  "google": {
    "connected": false
  },
  "llm_services": {
    "openai": true,
    "anthropic": true,
    "google_gemini": false
  }
}
```

### GitHub Repository Endpoints

#### Get User's Repositories
```
GET /auth/github/repos/{user_id}

Response:
{
  "repos": ["owner/repo1", "owner/repo2", ...],
  "count": 15,
  "username": "johndoe"
}
```

#### Get Repository Content
```
GET /auth/github/repos/{user_id}/{repo_name}/content?path=src/main.py

Response: Repository content (JSON or raw file)
```

---

## User Workflows

### Workflow 1: First-Time Sign-In

```
1. User visits Q-IDE
2. Sees "Sign In Hub" with GitHub, Google, Microsoft buttons
3. Clicks "Sign in with GitHub"
4. OAuth popup opens
5. User logs in to GitHub
6. Popup closes automatically
7. User's profile appears with:
   - Avatar ✓
   - Email ✓
   - GitHub username ✓
   - List of repositories ✓
8. User can now add Copilot API key (if subscribed)
```

### Workflow 2: Add LLM Model

```
1. User signs in (already connected)
2. Scrolls to "LLM Models" section
3. Clicks "Add API Key" for OpenAI
4. Modal appears asking for API key
5. User pastes API key from OpenAI
6. Clicks "Save"
7. ✅ OpenAI is now active and available
8. Q-IDE can now use OpenAI for code generation
```

### Workflow 3: Add GitHub Copilot

```
1. User is already signed in with GitHub ✓
2. Has GitHub Copilot subscription (paid)
3. Goes to /auth/github/repos/{user_id}/copilot
4. Follows link to create GitHub Copilot API token
5. Creates Personal Access Token on GitHub
6. Pastes token into Q-IDE UI
7. ✅ Copilot is now active
8. Can use Copilot in code editor
```

### Workflow 4: Use Local Models (Ollama)

```
1. User wants free offline models
2. Installs Ollama from ollama.ai
3. Runs: ollama run llama2 (downloads ~4GB, runs locally)
4. In Q-IDE, adds Ollama credential:
   - Service: "ollama_local"
   - Endpoint: "http://localhost:11434"
   - Model: "llama2"
5. ✅ Ollama is configured locally
6. Can use Llama2 without API keys or internet
```

---

## Available Services

### Authentication (Free)
- ✅ **GitHub OAuth** - Sign in + repo access
- ✅ **Google OAuth** - Sign in + Gmail
- ✅ **Microsoft OAuth** - Sign in + Azure

### Code Assistance
- 💻 **GitHub Copilot** - $10-20/mo
  - Requires: GitHub account + subscription
  - API: Requires token
- 💻 **Cody (Sourcegraph)** - $20/mo (optional)

### AI Models (Paid, Free Tier Available)
- 🤖 **OpenAI (GPT-4)** - $0.03-0.06 per 1K tokens
  - Free tier: $5 credits
  - https://platform.openai.com
- 🤖 **Claude (Anthropic)** - $0.003 per 1K tokens
  - Free tier: 10,000 daily requests
  - https://console.anthropic.com
- 🤖 **Google Gemini** - **100% FREE**
  - https://ai.google.dev
  - No credit card required

### AI Models (Free, Local)
- 🖥️ **Ollama** - Run Llama2, Mistral, Neural Chat
  - Download: ollama.ai
  - Models: 4GB-40GB each
  - Speed: Depends on GPU
- 🖥️ **GPT4All** - Optimized local models
  - Download: gpt4all.io
  - Models: 3GB-8GB each
  - No GPU required

---

## Security Considerations

### OAuth Tokens
- Stored securely in backend (not exposed to frontend)
- Can be revoked on provider's website
- Expire automatically

### API Keys
- Encrypted before storage
- Never logged or exposed
- User can delete anytime

### Data Privacy
- User profiles stored locally by default
- No data sent to third parties
- Full control over what's shared

### Best Practices
- Don't commit `.env` file to git
- Use strong, unique API keys
- Revoke tokens if compromised
- Use environment variables for secrets

---

## Troubleshooting

### OAuth Popup Not Opening
**Problem:** OAuth popup blocked by browser
**Solution:**
```
1. Check browser privacy settings
2. Allow popups from localhost:3000
3. Try different browser
4. Check console for errors
```

### "Invalid Session" Error
**Problem:** OAuth session expired
**Solution:**
```
1. Sessions expire after 15 minutes
2. Click sign-in button again
3. Complete OAuth flow
```

### API Key Not Working
**Problem:** "Invalid API Key" error
**Solution:**
1. Verify key is correct (no extra spaces)
2. Check key hasn't expired
3. Create new key from provider's website
4. Verify API has sufficient credits
5. Check scopes/permissions are correct

### Can't Find OAuth Credentials
**Problem:** Don't know where to get OAuth app ID
**Solution:**
- GitHub: https://github.com/settings/developers
- Google: https://console.cloud.google.com/
- Microsoft: https://portal.azure.com/

### Repositories Not Loading
**Problem:** GitHub repos list empty
**Solution:**
1. Check GitHub OAuth is connected ✓
2. Verify account has repositories
3. Check token scopes include "repo"
4. Try refreshing page

---

## Integration Examples

### Using Copilot in Code

```python
from backend.unified_auth_service import auth_service

user_id = "user123"
credentials = auth_service.get_active_credentials(user_id)

if 'github_copilot' in credentials:
    copilot_key = credentials['github_copilot']
    # Use Copilot API
```

### Using OpenAI for Generation

```python
import openai

user_id = "user123"
credentials = auth_service.get_active_credentials(user_id)

if 'openai' in credentials:
    openai.api_key = credentials['openai']
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Generate a React component"}]
    )
```

### Using Ollama Local

```python
import requests

# Ollama runs on localhost:11434
response = requests.post(
    'http://localhost:11434/api/generate',
    json={
        'model': 'llama2',
        'prompt': 'Generate a Python function'
    }
)
```

---

## Next Steps

1. **Deploy OAuth Apps** (GitHub, Google)
2. **Set Environment Variables** (.env)
3. **Update Backend & Frontend** (2 files)
4. **Test Sign-In** locally
5. **Add User Guides** for your users

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review API reference for endpoint usage
3. Check browser console for errors
4. Verify OAuth apps are configured correctly
5. Ensure environment variables are set

---

**You now have a production-ready unified authentication system!** 🎉

