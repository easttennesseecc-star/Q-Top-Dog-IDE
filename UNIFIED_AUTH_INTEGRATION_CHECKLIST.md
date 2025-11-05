# ✅ Unified Authentication Integration Checklist

## Pre-Setup (Before You Start)

- [ ] You have GitHub account (free)
- [ ] You have Google account (free)
- [ ] You have VS Code or IDE open
- [ ] You have `.env` file in project root
- [ ] You can access https://localhost:3000 locally
- [ ] Node.js and Python installed

---

## OAuth Setup (10 minutes)

### GitHub OAuth

- [ ] Go to: https://github.com/settings/developers
- [ ] Click: "New OAuth App" (or "Developer settings" → "OAuth Apps")
- [ ] Fill in Application Details:
  - [ ] Application name: `Top Dog`
  - [ ] Homepage URL: `http://localhost:3000`
  - [ ] Application description: `Local IDE with AI integration`
  - [ ] Authorization callback URL: `http://localhost:3000/auth/oauth/callback`
- [ ] Click: "Register application"
- [ ] Copy to `.env`:
  ```
  GITHUB_OAUTH_CLIENT_ID=your_client_id_here
  GITHUB_OAUTH_CLIENT_SECRET=your_client_secret_here
  ```
- [ ] Do NOT commit this file to git!

### Google OAuth

- [ ] Go to: https://console.cloud.google.com/
- [ ] Create new project:
  - [ ] Click: "Select a project" (top left)
  - [ ] Click: "New project"
  - [ ] Name: `Top Dog`
  - [ ] Click: "Create"
- [ ] Enable APIs:
  - [ ] Search for: "Google+ API"
  - [ ] Click: "Enable"
  - [ ] Search for: "Google Sign-In API"
  - [ ] Click: "Enable"
- [ ] Create OAuth 2.0 credentials:
  - [ ] Go to: Credentials (left menu)
  - [ ] Click: "Create credentials" → "OAuth 2.0 client ID"
  - [ ] Choose: "Web application"
  - [ ] Add Authorized redirect URIs:
    - [ ] `http://localhost:3000/auth/oauth/callback`
    - [ ] `http://localhost:3000/auth/callback`
  - [ ] Click: "Create"
- [ ] Copy to `.env`:
  ```
  GOOGLE_OAUTH_CLIENT_ID=your_client_id_here
  GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret_here
  ```

---

## Code Integration (5 minutes)

### Backend Setup

- [ ] Copy file: `backend/unified_auth_service.py`
- [ ] Copy file: `backend/unified_auth_routes.py`
- [ ] Open: `backend/main.py`
- [ ] Add to imports (top of file):
  ```python
  from backend.unified_auth_routes import router as auth_router
  ```
- [ ] Add after other route registrations:
  ```python
  app.include_router(auth_router)
  ```
- [ ] Save file

### Frontend Setup

- [ ] Copy file: `frontend/src/components/UnifiedSignInHub.tsx`
- [ ] Open: `frontend/src/App.tsx`
- [ ] Add to imports:
  ```tsx
  import UnifiedSignInHub from './components/UnifiedSignInHub';
  ```
- [ ] Add to your JSX (preferably in a route or main container):
  ```tsx
  <UnifiedSignInHub />
  ```
- [ ] Save file

### Environment Configuration

- [ ] Create file `.env` in project root (if not exists)
- [ ] Add:
  ```bash
  # OAuth Credentials (from above steps)
  GITHUB_OAUTH_CLIENT_ID=your_client_id
  GITHUB_OAUTH_CLIENT_SECRET=your_client_secret
  GOOGLE_OAUTH_CLIENT_ID=your_client_id
  GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret
  
  # App Configuration
  APP_URL=http://localhost:3000
  API_URL=http://localhost:8000
  ```
- [ ] Save and close
- [ ] Add `.env` to `.gitignore` (IMPORTANT!)
  ```
  .env
  .env.local
  *.key
  ```

---

## Testing (5 minutes)

### Start Services

- [ ] Open Terminal 1:
  ```bash
  cd backend
  python main.py
  ```
  - [ ] Wait for: `Uvicorn running on http://127.0.0.1:8000`

- [ ] Open Terminal 2:
  ```bash
  cd frontend
  npm start
  ```
  - [ ] Wait for: React starts on http://localhost:3000

### Test Sign-In Flow

- [ ] Open browser: http://localhost:3000
- [ ] Look for: Sign-In Hub with GitHub, Google, Microsoft buttons
- [ ] Click: "Sign in with GitHub"
- [ ] Popup opens → Log in to GitHub (use your account)
- [ ] Approve permissions
- [ ] Popup closes
- [ ] Check: Your name and email appear in UI ✅
- [ ] Check: GitHub username shows ✅
- [ ] Check: Repository list populates ✅

### Test API Endpoints

In another terminal, test with curl:

```bash
# Get available services
curl http://localhost:8000/auth/services/available

# Expected: List of services with details
# Status: 200 OK ✅

# Health check
curl http://localhost:8000/auth/health

# Expected: {"status": "healthy", ...}
# Status: 200 OK ✅
```

---

## Add LLM Models (Optional, 2 minutes)

### Add Free Google Gemini

- [ ] Go to: https://ai.google.dev
- [ ] Click: "Get API Key"
- [ ] Create new project (or use existing)
- [ ] Copy API key
- [ ] In Top Dog UI:
  - [ ] Find: "Gemini (Free)" card
  - [ ] Click: "🔑 Add API Key (Free)"
  - [ ] Paste: Your Gemini API key
  - [ ] Click: "Save"
  - [ ] See: Green checkmark ✅

### Add OpenAI GPT-4 (Optional)

- [ ] Go to: https://platform.openai.com/api/keys
- [ ] Sign in to OpenAI
- [ ] Create new API key
- [ ] (You'll get $5 free credits to start)
- [ ] Copy key
- [ ] In Top Dog UI:
  - [ ] Find: "ChatGPT / GPT-4" card
  - [ ] Click: "🔑 Add API Key"
  - [ ] Paste: Your OpenAI API key
  - [ ] Click: "Save"
  - [ ] See: Green checkmark ✅

### Add GitHub Copilot (Optional)

- [ ] You need: Active GitHub Copilot subscription ($10/month)
- [ ] Go to: https://github.com/settings/tokens/new
- [ ] Create new token with scopes:
  - [ ] `user:read`
  - [ ] `write:packages`
  - [ ] `read:packages`
- [ ] Copy token (shown only once!)
- [ ] In Top Dog UI:
  - [ ] Find: "⚡ Copilot" card
  - [ ] Click: "🔑 Add API Key"
  - [ ] Paste: Your Copilot token
  - [ ] Click: "Save"
  - [ ] See: Green checkmark ✅

---

## Deployment Checklist

### Before Going to Production

- [ ] `.env` file exists with all credentials
- [ ] `.env` is in `.gitignore`
- [ ] OAuth apps are registered for production URLs
  - [ ] Update: GitHub OAuth callback URL
  - [ ] Update: Google OAuth redirect URI
  - [ ] Update: APP_URL in `.env` to production domain
- [ ] Backend API is accessible from frontend
- [ ] SSL/HTTPS enabled (required for OAuth)
- [ ] API keys are using production credentials
- [ ] User profiles are persisting correctly
- [ ] GitHub repos are loading
- [ ] All LLM models can be switched

### Production Deployment

- [ ] Use environment-specific `.env` files:
  ```
  .env.local       (development)
  .env.production  (production)
  ```
- [ ] Set environment variable: `NODE_ENV=production`
- [ ] Use production OAuth credentials (not localhost)
- [ ] Enable HTTPS (required for OAuth)
- [ ] Set up proper CORS headers
- [ ] Monitor API error logs
- [ ] Monitor token refresh rates

---

## Troubleshooting

### OAuth Popup Doesn't Open

- [ ] Check: Browser popup blocker
  - [ ] Allow popups from `localhost:3000`
  - [ ] Try different browser
  - [ ] Try incognito/private mode
- [ ] Check: Console for errors (F12 → Console)
- [ ] Check: Backend is running on port 8000

### "Invalid Session" Error

- [ ] Sessions expire after 15 minutes
- [ ] Try: Click sign-in button again
- [ ] Try: Clear browser cookies and cache
  ```
  Browser Settings → Privacy → Clear browsing data
  ```

### GitHub OAuth Fails

- [ ] Verify: GitHub OAuth app is registered
- [ ] Verify: Client ID and Secret are correct in `.env`
- [ ] Verify: Callback URL matches exactly: `http://localhost:3000/auth/oauth/callback`
- [ ] Verify: Refresh `.env` and restart backend

### API Key Not Working

- [ ] Check: No extra spaces around the key
- [ ] Check: Key hasn't expired
- [ ] Check: API has credit/quota
- [ ] Check: Correct scopes selected when creating key

### Repositories Not Loading

- [ ] Check: GitHub OAuth is connected
- [ ] Check: Account has public repositories
- [ ] Check: GitHub token hasn't expired
- [ ] Try: Refresh browser (F5)
- [ ] Try: Clear localStorage:
  ```javascript
  // In browser console:
  localStorage.clear()
  location.reload()
  ```

### UI Not Appearing

- [ ] Check: Frontend is running on port 3000
- [ ] Check: No TypeScript errors (check console)
- [ ] Check: Component is imported in App.tsx
- [ ] Check: Component is rendered in JSX
- [ ] Try: Clear browser cache (Ctrl+Shift+Delete)

---

## Files Included

### Backend (2 files)
- ✅ `backend/unified_auth_service.py` (450 lines)
- ✅ `backend/unified_auth_routes.py` (400 lines)

### Frontend (1 file)
- ✅ `frontend/src/components/UnifiedSignInHub.tsx` (650 lines)

### Documentation (2 files)
- ✅ `UNIFIED_AUTH_SETUP_GUIDE.md` (Complete reference)
- ✅ `UNIFIED_SIGN_IN_QUICK_START.md` (Quick start)
- ✅ This file (Integration checklist)

---

## Support & Documentation

| Need | File |
|------|------|
| Quick start (5 min) | `UNIFIED_SIGN_IN_QUICK_START.md` |
| Full setup guide | `UNIFIED_AUTH_SETUP_GUIDE.md` |
| API reference | `UNIFIED_AUTH_SETUP_GUIDE.md` (API Reference section) |
| Troubleshooting | This file + guides above |

---

## Success Criteria

When everything is working:

✅ User can click "Sign in with GitHub"  
✅ OAuth popup opens  
✅ After login, user sees profile with avatar  
✅ User can see GitHub username and repos  
✅ User can add LLM API keys  
✅ All connected services show green checkmarks  
✅ User can switch between models in IDE  
✅ Profile persists on refresh  
✅ Can sign out and back in  
✅ Everything works offline (with local models)  

---

## Estimated Timeline

| Task | Time |
|------|------|
| GitHub OAuth setup | 5 min |
| Google OAuth setup | 5 min |
| Code integration | 5 min |
| Testing | 5 min |
| **Total** | **~20 minutes** ⚡ |

---

## Next Steps After Integration

1. ✅ Test locally (all checklist items above)
2. ✅ Deploy to staging environment
3. ✅ Test with production OAuth credentials
4. ✅ Deploy to production
5. ✅ Monitor user sign-ins
6. ✅ Gather feedback
7. ✅ Iterate on UX

---

**Ready to go live!** 🚀

