# 🚀 Unified Sign-In: Quick Start (5 Minutes)

## What You're Getting

```
ONE LOGIN BUTTON
    ↓
Choose Provider (GitHub, Google, Microsoft)
    ↓
Sign in with OAuth (browser popup)
    ↓
DONE! Access all your tools:
  ✓ GitHub & Copilot
  ✓ LLM Models (OpenAI, Claude, Gemini)
  ✓ Local Models (Ollama, GPT4All)
  ✓ Repository Access
```

---

## Installation (2 Steps)

### Step 1: Copy Files
```bash
# Backend auth service
copy backend/unified_auth_service.py
copy backend/unified_auth_routes.py

# Frontend component
copy frontend/src/components/UnifiedSignInHub.tsx
```

### Step 2: Integration

**In backend/main.py, add 2 lines:**
```python
from backend.unified_auth_routes import router as auth_router

app.include_router(auth_router)  # Add after other routes
```

**In frontend/App.tsx, add 3 lines:**
```tsx
import UnifiedSignInHub from './components/UnifiedSignInHub';

// In your JSX:
<UnifiedSignInHub />
```

### Step 3: Environment Variables

Create `.env`:
```bash
# GitHub
GITHUB_OAUTH_CLIENT_ID=abc123
GITHUB_OAUTH_CLIENT_SECRET=xyz789

# Google
GOOGLE_OAUTH_CLIENT_ID=ghi456
GOOGLE_OAUTH_CLIENT_SECRET=def012

# App URLs
APP_URL=http://localhost:3000
API_URL=http://localhost:8000
```

---

## Getting OAuth Credentials (3 Minutes Each)

### GitHub
1. Go: https://github.com/settings/developers
2. "New OAuth App"
3. Fill in:
   - App name: Q-IDE
   - Homepage: http://localhost:3000
   - Callback: http://localhost:3000/auth/oauth/callback
4. Copy Client ID & Secret → `.env`

### Google
1. Go: https://console.cloud.google.com/
2. Create project: "Q-IDE"
3. Enable Google+ API
4. OAuth 2.0 credentials → "Web application"
5. Redirect URI: http://localhost:3000/auth/oauth/callback
6. Copy credentials → `.env`

---

## Usage

### First-Time User
```
1. Visit: http://localhost:3000
2. Click "Sign in with GitHub"
3. GitHub OAuth popup
4. Approve access
5. Popup closes
6. ✅ You're signed in!
```

### Add Copilot
```
1. Already signed in with GitHub ✓
2. Have Copilot subscription?
   YES → Create token at https://github.com/settings/tokens/new
        Paste in Q-IDE UI
   NO → Skip or use free Gemini instead
```

### Add Free Model (Gemini)
```
1. Click "Add API Key" for Gemini
2. Go: https://ai.google.dev
3. Click "Get API Key"
4. Create free key (no card needed)
5. Paste in Q-IDE
6. ✅ Free AI model activated!
```

### Add Paid Model (OpenAI)
```
1. Go: https://platform.openai.com/api/keys
2. Create API key
3. Get $5 free credits first
4. Paste key in Q-IDE UI
5. ✅ GPT-4 ready to use!
```

### Use Local Model (Ollama)
```
1. Download: https://ollama.ai
2. Run: ollama run llama2
3. Wait for download (~4GB)
4. In Q-IDE: Add Ollama endpoint
5. ✅ Offline model ready!
```

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /auth/oauth/init | Start OAuth flow |
| POST | /auth/oauth/callback | Handle OAuth return |
| GET | /auth/profile/{id} | Get user profile |
| POST | /auth/credentials/add | Add API key |
| GET | /auth/services/status/{id} | See what's connected |
| GET | /auth/services/available | List all services |
| GET | /auth/github/repos/{id} | List GitHub repos |

---

## Services Available

### FREE Tier
- ✅ Google Gemini (100% free, no card)
- ✅ GitHub OAuth (free account)
- ✅ Ollama (local, no internet)
- ✅ GPT4All (local, no internet)

### PAID Tier (With Free Credits)
- 💰 OpenAI GPT-4: $5 free credits
- 💰 Claude: 100k daily requests free
- 💰 GitHub Copilot: $10/mo (or free with GitHub Pro)

### BEST FOR BUDGET
```
Option 1: Use Gemini (100% free)
  → https://ai.google.dev
  → No credit card
  → Great quality

Option 2: Use Ollama (free, local)
  → Download from ollama.ai
  → Run offline
  → Uses your GPU/CPU
  
Option 3: Mix them
  → Gemini for complex tasks
  → Ollama for repetitive work
  → Save money!
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| OAuth popup blocked | Allow popups in browser settings |
| "Invalid session" | Session expired, try again |
| API key rejected | Check for extra spaces, recreate key |
| Can't find GitHub token | Go to https://github.com/settings/tokens/new |
| Repos list empty | Check token has "repo" scope |
| Offline model slow | Install GPU support for Ollama |

---

## File Structure

```
backend/
  ├─ unified_auth_service.py     (Core auth engine)
  ├─ unified_auth_routes.py      (API endpoints)
  └─ main.py                     (Add 1 line here)

frontend/src/
  ├─ components/
  │  └─ UnifiedSignInHub.tsx     (Sign-in UI)
  └─ App.tsx                     (Add 3 lines here)

.env                            (Add credentials here)
```

---

## What Happens Behind the Scenes

### When You Click "Sign in with GitHub"

```
Q-IDE
  ↓ POST /auth/oauth/init
Backend
  ↓ Creates session
  ↓ Builds GitHub auth URL
  ↓
Returns auth URL to frontend
  ↓ Opens popup
User's Browser
  ↓ Redirects to GitHub.com
GitHub
  ↓ User logs in
  ↓ Grants permission
  ↓ Redirects back to Q-IDE
  ↓ POST /auth/oauth/callback
Q-IDE Backend
  ↓ Exchanges code for token
  ↓ Fetches user info
  ↓ Creates user profile
  ↓ Stores token securely
  ↓
Popup closes
User sees their profile ✅
```

### When You Add Copilot

```
User pastes API key
  ↓ POST /auth/credentials/add
Q-IDE Backend
  ↓ Stores key (encrypted)
  ↓ Marks service as "active"
  ↓
Returns success
User sees green checkmark ✅
Q-IDE can now use Copilot
```

---

## Security

✅ **OAuth tokens** encrypted at rest  
✅ **API keys** never logged  
✅ **User can revoke** anytime  
✅ **No data to third parties**  
✅ **Local-first** storage  

Never commit `.env` to git!

---

## Next Steps

1. Get OAuth credentials from GitHub, Google (5 min)
2. Set environment variables (1 min)
3. Copy the 3 files (1 min)
4. Update 2 files in your app (1 min)
5. Test sign-in (1 min)
6. **Total: ~15 minutes** ⚡

---

**You're ready to ship!** 🎉

