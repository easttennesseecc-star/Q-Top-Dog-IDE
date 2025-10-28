# OAuth 2.0 Setup Guide for Q-IDE

Complete step-by-step guide to set up Google OAuth and GitHub OAuth for Q-IDE development and production.

## Prerequisites

- Q-IDE Backend running (`python -m uvicorn backend.main:app --reload`)
- Q-IDE Frontend running (Vite dev server on port 1431)
- OAuth app credentials from Google Cloud Console and GitHub
- Python 3.11+

## Part 1: Google OAuth Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click **Create Project**
3. Enter project name: `Q-IDE` (or your preference)
4. Click **Create**

### Step 2: Enable Google+ API

1. In the sidebar, go to **APIs & Services** → **Library**
2. Search for "Google+ API"
3. Click on it and press **Enable**

### Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Select **Web application**
4. Under **Authorized redirect URIs**, add:
   - `http://127.0.0.1:8000/auth/google/callback` (development)
   - `https://your-domain.com/auth/google/callback` (production)
5. Click **Create**
6. Copy the **Client ID** and **Client Secret**

### Step 4: Set Environment Variables

Create or update `.env` file in the backend directory:

```bash
# .env (backend/.env)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
BACKEND_URL=http://127.0.0.1:8000
```

Or set as system environment variables:

**Windows (PowerShell):**
```powershell
$env:GOOGLE_CLIENT_ID = "your-client-id.apps.googleusercontent.com"
$env:GOOGLE_CLIENT_SECRET = "your-client-secret"
$env:BACKEND_URL = "http://127.0.0.1:8000"
```

**Linux/Mac (bash):**
```bash
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-client-secret"
export BACKEND_URL="http://127.0.0.1:8000"
```

### Step 5: Test Google OAuth

1. Start the backend:
   ```bash
   python -m uvicorn backend.main:app --reload
   ```

2. Open Q-IDE frontend (http://localhost:1431)

3. Click **Sign In** button

4. Click **Sign in with Google** in the popup

5. You should be redirected to Google consent screen

6. After authorizing, the OAuth callback handler will:
   - Exchange authorization code for access token
   - Fetch your Google profile
   - Create/update user in Q-IDE
   - Return to popup with success message

7. Popup closes and you're signed in!

## Part 2: GitHub OAuth Setup

### Step 1: Register OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **New OAuth App** (in the left sidebar)
3. Fill in the form:
   - **Application name**: Q-IDE
   - **Homepage URL**: `http://127.0.0.1:1431` (dev) or `https://your-domain.com` (prod)
   - **Authorization callback URL**: `http://127.0.0.1:8000/auth/github/callback` (dev)

4. Click **Register application**

5. You'll see your **Client ID** and **Client Secret**

### Step 2: Set Environment Variables

Update your `.env` or system environment variables:

```bash
# .env (backend/.env)
GITHUB_CLIENT_ID=your-client-id
GITHUB_CLIENT_SECRET=your-client-secret
```

**Windows (PowerShell):**
```powershell
$env:GITHUB_CLIENT_ID = "your-client-id"
$env:GITHUB_CLIENT_SECRET = "your-client-secret"
```

**Linux/Mac (bash):**
```bash
export GITHUB_CLIENT_ID="your-client-id"
export GITHUB_CLIENT_SECRET="your-client-secret"
```

### Step 3: Test GitHub OAuth

1. Restart backend to pick up new environment variables

2. Open Q-IDE frontend

3. In the Account Linking panel, click **Connect GitHub**

4. You'll be redirected to GitHub consent screen

5. After authorizing, you'll see "GitHub account connected"

## Part 3: OAuth Callback Flow Explained

### Frontend OAuth Popup Flow

```javascript
// User clicks "Sign in with Google"
const startResponse = await fetch('/auth/google/start');
const { auth_url } = await startResponse.json();

// Frontend opens popup
const popup = window.open(auth_url, 'signin', 'width=500,height=600');

// Listen for callback message from popup
window.addEventListener('message', (event) => {
  if (event.data.type === 'oauth-success') {
    // Save session
    localStorage.setItem('q_ide_session', event.data.session_id);
    popup.close();
    // Update UI
  }
});
```

### Backend Callback Flow

1. **OAuth Provider redirects to `/auth/google/callback`**
   - Query params: `code=AUTH_CODE&state=STATE`

2. **Backend exchanges code for token**
   - Sends code to OAuth provider's token endpoint
   - Receives access token

3. **Backend fetches user profile**
   - Uses access token to get user info from OAuth provider
   - Extracts email, name, profile picture

4. **Backend creates/updates user**
   - Saves user to local auth data
   - Creates session for user

5. **Backend redirects to oauth-callback.html**
   - URL includes: `status=success`, `session_id`, `provider`, user info
   - Example: `/auth/google/callback?...` → redirect to `oauth-callback.html?status=success&session_id=...`

### OAuth Callback HTML Handler

The static page `frontend/public/oauth-callback.html` handles:

1. **Extract query parameters** from URL
2. **Parse status and session_id**
3. **Post message to parent window** with OAuth result
4. **Show spinner or error** based on result
5. **Auto-close** after success

```javascript
// Inside oauth-callback.html
const params = new URLSearchParams(window.location.search);
window.opener.postMessage({
  type: 'oauth-success',
  session_id: params.get('session_id'),
  provider: params.get('provider')
}, 'http://localhost:1431');
```

## Part 4: Troubleshooting

### Issue: "CORS error in browser console"

**Solution:** Backend CORS is configured for localhost:1431. Ensure:
- Frontend is running on http://localhost:1431
- Backend CORS includes this origin in `app.add_middleware(CORSMiddleware, ...)`

Current allowed origins:
```python
allow_origins=[
    "http://localhost:1431",
    "http://127.0.0.1:1431",
    "http://localhost:3000",
]
```

### Issue: "Invalid redirect URI"

**Solution:** OAuth provider redirect URI must match exactly. Check:
1. In OAuth app settings
2. In `BACKEND_URL` environment variable
3. Value used in redirect endpoints

Example:
- Google Console: `http://127.0.0.1:8000/auth/google/callback`
- GitHub Settings: `http://127.0.0.1:8000/auth/github/callback`
- Backend: `BACKEND_URL=http://127.0.0.1:8000`

### Issue: "Pop-up blocked by browser"

**Solution:** 
- Pop-up must be opened in response to user click (not async callback)
- Check browser pop-up blocker settings
- Some browsers require user approval per domain

### Issue: "Authorization code expired"

**Solution:**
- OAuth codes typically valid for 10 minutes
- If network is slow, try again
- Check backend logs: `tail -f backend.log`

### Issue: "Session not found when linking account"

**Solution:**
- For account linking, state parameter must contain valid session_id
- User must be signed in first before linking GitHub
- Check `/auth/status?session_id=YOUR_SESSION` endpoint

### Issue: "OAuth credentials not working in production"

**Solution:**
1. Update redirect URIs in OAuth app settings to production domain
2. Set `BACKEND_URL=https://your-domain.com`
3. Ensure SSL certificate is valid
4. Test: `curl https://your-domain.com/auth/google/start`

## Part 5: Production Deployment

### Before Going Live

1. **Update OAuth Redirect URIs** to production domain
   - Google Cloud Console: Add `https://your-domain.com/auth/google/callback`
   - GitHub: Update to `https://your-domain.com/auth/github/callback`

2. **Set Production Environment Variables**
   ```bash
   BACKEND_URL=https://your-domain.com
   GOOGLE_CLIENT_ID=production-client-id
   GOOGLE_CLIENT_SECRET=production-client-secret
   GITHUB_CLIENT_ID=production-client-id
   GITHUB_CLIENT_SECRET=production-client-secret
   ```

3. **Enable HTTPS**
   - Use Let's Encrypt or similar
   - OAuth requires secure connection

4. **Update CORS**
   ```python
   allow_origins=[
       "https://your-domain.com",
       "https://www.your-domain.com",
   ]
   ```

5. **Test OAuth Flow**
   ```bash
   # Verify redirect endpoints
   curl https://your-domain.com/auth/google/start
   curl https://your-domain.com/auth/github/start
   ```

### Security Best Practices

1. **Never commit credentials to git**
   - Use `.env` file with `.gitignore`
   - Use environment variables in production

2. **Validate OAuth tokens**
   - Backend verifies token with OAuth provider
   - Current implementation does this

3. **Use HTTPS in production**
   - OAuth requires secure redirects
   - Prevents token interception

4. **Implement CSRF protection**
   - Use `state` parameter (already implemented)
   - Validates OAuth provider response

5. **Secure session storage**
   - Frontend uses localStorage (consider secure HTTP-only cookie)
   - Backend stores sessions in `.dev_auth_data.json` (prod: use database)

## Part 6: Architecture Reference

### Endpoint Reference

| Endpoint | Purpose | Returns |
|----------|---------|---------|
| `GET /auth/google/start` | Initiate Google OAuth | `{auth_url: "..."}` |
| `GET /auth/google/callback` | Google redirects here | Redirects to `oauth-callback.html` |
| `GET /auth/github/start` | Initiate GitHub OAuth | `{auth_url: "..."}` |
| `GET /auth/github/callback` | GitHub redirects here | Redirects to `oauth-callback.html` |
| `GET /auth/status` | Get current session user | `{user: {...}, status: "ok"}` |
| `POST /auth/token/pat` | Create PAT token | `{token: "...", provider: "..."}` |
| `GET /auth/token/{provider}` | Get PAT token | `{token: "..."}` or `{status: "not_found"}` |
| `DELETE /auth/token/{provider}` | Delete PAT token | `{status: "ok"}` |

### File Structure

```
backend/
  main.py              # FastAPI app, OAuth endpoints, build endpoints, LLM endpoints
  auth.py              # OAuth utilities, session management, user creation
  llm_client.py        # Python client for LLM learning system
  llm_agent_example.py # Example coding agent with continuous learning
  .dev_auth_data.json  # Local auth storage (dev only)
  .dev_tokens.json     # PAT token storage (dev only)

frontend/
  src/
    components/
      GoogleSignIn.tsx        # Google OAuth popup handler
      SignInPanel.tsx         # Combined sign-in + account linking UI
      AccountLinkingPanel.tsx # Link/unlink OAuth providers
      IntegrationsPanel.tsx   # PAT token management
  public/
    oauth-callback.html       # Static OAuth callback handler
```

### Session & Auth Flow

```
User clicks "Sign In"
  ↓
Frontend opens popup
  ↓
Popup navigates to /auth/google/start
  ↓
Backend returns Google auth URL
  ↓
Popup redirects to Google consent screen
  ↓
User authorizes
  ↓
Google redirects to /auth/google/callback with code
  ↓
Backend exchanges code for token
  ↓
Backend fetches Google user profile
  ↓
Backend creates user & session
  ↓
Backend redirects to oauth-callback.html with session_id
  ↓
oauth-callback.html posts session to parent window
  ↓
Parent window receives message
  ↓
Parent closes popup & saves session to localStorage
  ↓
UI updates with user profile
```

## Part 7: Quick Reference Commands

### Start Development Environment

```bash
# Terminal 1: Start backend
cd C:\Quellum-topdog-ide\backend
python -m uvicorn main:app --reload

# Terminal 2: Start frontend
cd C:\Quellum-topdog-ide\frontend
npm run dev

# Browser: Open http://localhost:1431
```

### Set Environment Variables (Development)

**PowerShell:**
```powershell
$env:GOOGLE_CLIENT_ID = "your-client-id.apps.googleusercontent.com"
$env:GOOGLE_CLIENT_SECRET = "your-client-secret"
$env:GITHUB_CLIENT_ID = "your-client-id"
$env:GITHUB_CLIENT_SECRET = "your-client-secret"
$env:BACKEND_URL = "http://127.0.0.1:8000"
```

### Test OAuth Endpoints

```bash
# Test Google OAuth start
curl http://127.0.0.1:8000/auth/google/start

# Test GitHub OAuth start  
curl http://127.0.0.1:8000/auth/github/start

# Check current session
curl http://127.0.0.1:8000/auth/status?session_id=YOUR_SESSION_ID

# Create PAT token
curl -X POST http://127.0.0.1:8000/auth/token/pat \
  -H "Content-Type: application/json" \
  -d '{"provider":"github","token":"ghp_..."}'
```

### View Session Data

```bash
# View stored users and sessions
cat C:\Quellum-topdog-ide\.dev_auth_data.json

# View stored PAT tokens
cat C:\Quellum-topdog-ide\.dev_tokens.json
```

## Part 8: Integration with LLM Learning System

Once OAuth is set up, your coding LLM can:

1. **Authenticate with OAuth session**
   ```python
   from backend.llm_client import LLMClient
   
   session_id = "oauth-session-from-signin"
   client = LLMClient(session_id=session_id)
   ```

2. **Access authenticated endpoints**
   ```python
   # Get builds from authenticated session
   builds = client.get_builds()
   
   # Submit analysis reports
   client.submit_report(
       build_id="uuid",
       type="failure_analysis",
       analysis="...",
       recommendations=["..."],
       confidence=0.9
   )
   ```

3. **Link GitHub account** for more permissions
   ```python
   # In Account Linking panel
   # Click "Connect GitHub"
   # This links GitHub account to OAuth session
   # LLM can now access private repos with proper permissions
   ```

---

**Last Updated:** 2024
**Status:** Production Ready
