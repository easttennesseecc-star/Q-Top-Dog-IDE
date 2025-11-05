# OAuth Client Configuration Guide

**Top Dog - Professional OAuth Sign-In Setup**

This guide helps you configure OAuth credentials for professional sign-in experience in Top Dog.

---

## 🎯 Overview

Top Dog supports OAuth sign-in with:
- **Google** - Use your Google account
- **GitHub** - Use your GitHub account  
- **OpenAI** - Use your OpenAI account
- **Anthropic** - Use your Anthropic account

Each provider requires OAuth client credentials (Client ID and Secret).

---

## 📋 Prerequisites

- Top Dog backend running on `http://localhost:8000`
- Top Dog frontend running on `http://localhost:1431`
- Administrator access to each OAuth provider's console

---

## 🔵 Google OAuth Setup

### Step 1: Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API:
   - Go to "APIs & Services" → "Library"
   - Search for "Google+ API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Web application"
   - Name it "Top Dog"
   - Add authorized redirect URIs:
     ```
     http://localhost:8000/llm_auth/callback?provider=google
     http://localhost:1431
     ```
   - Click "Create"
5. Copy your **Client ID** and **Client Secret**

### Step 2: Store Credentials

In project root `.env` file:
```bash
QIDE_GOOGLE_CLIENT_ID=your_client_id_here
QIDE_GOOGLE_CLIENT_SECRET=your_client_secret_here
```

### Step 3: Verify Configuration

- Restart backend: `python backend/main.py`
- Frontend: `npm start`
- In Auth tab, "Sign in with Google" button should be enabled

---

## ⚫ GitHub OAuth Setup

### Step 1: Create GitHub OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Fill in details:
   - **Application name**: Top Dog
   - **Homepage URL**: `http://localhost:1431`
   - **Authorization callback URL**: `http://localhost:8000/llm_auth/callback?provider=github`
4. Click "Register application"
5. Copy your **Client ID** and generate **Client Secret**

### Step 2: Store Credentials

In project root `.env` file:
```bash
QIDE_GITHUB_CLIENT_ID=your_client_id_here
QIDE_GITHUB_CLIENT_SECRET=your_client_secret_here
```

### Step 3: Verify Configuration

- Restart backend
- Frontend should show "Sign in with GitHub" enabled

---

## 🚀 OpenAI OAuth Setup

### Step 1: Create OpenAI OAuth Credentials

1. Go to [OpenAI Platform](https://platform.openai.com/account/apps)
2. Click "Create new OAuth app"
3. Fill in details:
   - **Application name**: Top Dog
   - **Redirect URI**: `http://localhost:8000/llm_auth/callback?provider=openai`
4. Copy your **Client ID** and **Client Secret**

### Step 2: Store Credentials

In project root `.env` file:
```bash
QIDE_OPENAI_CLIENT_ID=your_client_id_here
QIDE_OPENAI_CLIENT_SECRET=your_client_secret_here
```

### Step 3: Verify Configuration

- Restart backend
- Frontend should show "Sign in with OpenAI" enabled

---

## 🧠 Anthropic OAuth Setup

### Step 1: Create Anthropic OAuth Credentials

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Navigate to "API Keys" or "OAuth Applications"
3. Create new OAuth application:
   - **Application name**: Top Dog
   - **Redirect URI**: `http://localhost:8000/llm_auth/callback?provider=anthropic`
4. Copy your **Client ID** and **Client Secret**

### Step 2: Store Credentials

In project root `.env` file:
```bash
QIDE_ANTHROPIC_CLIENT_ID=your_client_id_here
QIDE_ANTHROPIC_CLIENT_SECRET=your_client_secret_here
```

### Step 3: Verify Configuration

- Restart backend
- Frontend should show "Sign in with Anthropic" enabled

---

## 🛠️ Environment Configuration

### Option 1: .env File (Development)

Create `.env` in project root:

```bash
# Google OAuth
QIDE_GOOGLE_CLIENT_ID=xxxxxxxxxxxx.apps.googleusercontent.com
QIDE_GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxx

# GitHub OAuth
QIDE_GITHUB_CLIENT_ID=xxxxxxxxxxxxxxxx
QIDE_GITHUB_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OpenAI OAuth
QIDE_OPENAI_CLIENT_ID=xxxxxxxxxxxxxxxx
QIDE_OPENAI_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Anthropic OAuth
QIDE_ANTHROPIC_CLIENT_ID=xxxxxxxxxxxxxxxx
QIDE_ANTHROPIC_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Backend URL (for OAuth callbacks)
QIDE_BACKEND_URL=http://localhost:8000
```

### Option 2: Environment Variables (Production)

```bash
export QIDE_GOOGLE_CLIENT_ID=xxx
export QIDE_GOOGLE_CLIENT_SECRET=xxx
export QIDE_GITHUB_CLIENT_ID=xxx
export QIDE_GITHUB_CLIENT_SECRET=xxx
export QIDE_OPENAI_CLIENT_ID=xxx
export QIDE_OPENAI_CLIENT_SECRET=xxx
export QIDE_ANTHROPIC_CLIENT_ID=xxx
export QIDE_ANTHROPIC_CLIENT_SECRET=xxx
export QIDE_BACKEND_URL=https://api.Top Dog.com
```

### Option 3: Config File (Advanced)

Create `~/.Top Dog/oauth_config.json`:

```json
{
  "google": {
    "client_id": "xxx.apps.googleusercontent.com",
    "client_secret": "GOCSPX-xxx"
  },
  "github": {
    "client_id": "xxx",
    "client_secret": "xxx"
  },
  "openai": {
    "client_id": "xxx",
    "client_secret": "xxx"
  },
  "anthropic": {
    "client_id": "xxx",
    "client_secret": "xxx"
  }
}
```

---

## ✅ Verification Checklist

- [ ] Google Client ID and Secret set
- [ ] GitHub Client ID and Secret set
- [ ] OpenAI Client ID and Secret set (optional)
- [ ] Anthropic Client ID and Secret set (optional)
- [ ] Backend restarted after .env changes
- [ ] Frontend showing OAuth buttons in Auth tab
- [ ] Test Google sign-in works
- [ ] Test GitHub sign-in works
- [ ] Tokens stored in `~/.Top Dog/llm_credentials.json`
- [ ] Can refresh page and stay authenticated

---

## 🧪 Testing OAuth Flow

### Manual Test Steps

1. **Start Services**
   ```bash
   # Terminal 1: Backend
   cd backend
   python main.py
   
   # Terminal 2: Frontend  
   cd frontend
   npm start
   ```

2. **Access Top Dog**
   - Open browser: `http://localhost:1431`

3. **Test Google OAuth**
   - Click "LLM Config" → "Auth" tab
   - Click "Sign in with Google" button
   - Sign in with your Google account
   - Grant permission
   - See success message
   - Verify token saved: `cat ~/.Top Dog/llm_credentials.json | grep google`

4. **Test GitHub OAuth**
   - Click "Sign in with GitHub" button
   - Sign in with your GitHub account
   - Authorize Top Dog
   - See success message
   - Verify token saved: `cat ~/.Top Dog/llm_credentials.json | grep github`

5. **Test Other Providers**
   - Repeat for OpenAI and Anthropic

6. **Test Token Revocation**
   - In Auth tab, click "Sign out" on any provider
   - Should be prompted to sign back in
   - Token should be removed from storage

---

## 🐛 Troubleshooting

### OAuth Buttons Not Showing

**Problem:** Sign-in buttons greyed out or showing "OAuth not configured"

**Solutions:**
1. Check environment variables: `echo $QIDE_GOOGLE_CLIENT_ID`
2. Verify .env file exists in project root
3. Restart backend after setting env vars
4. Check browser console for errors
5. Check backend logs: `tail -f backend/logs/Top Dog-topdog.log`

### Popup Doesn't Open

**Problem:** Click "Sign in" but nothing happens

**Solutions:**
1. Check browser popup blocker settings
2. Whitelist `localhost:8000` in popup blocker
3. Check browser console for JavaScript errors
4. Verify backend is running: `curl http://localhost:8000/health`

### "Invalid Redirect URI"

**Problem:** OAuth provider says redirect URI is invalid

**Solutions:**
1. Check redirect URI exactly matches in OAuth provider console
2. For development: `http://localhost:8000/llm_auth/callback?provider=google`
3. For production: `https://api.Top Dog.com/llm_auth/callback?provider=google`
4. Make sure no trailing slashes unless expected

### Token Not Saving

**Problem:** Sign in succeeds but token not found in storage

**Solutions:**
1. Check `~/.Top Dog/` directory exists: `ls -la ~/.Top Dog/`
2. Create directory if missing: `mkdir -p ~/.Top Dog`
3. Check permissions: `ls -la ~/.Top Dog/llm_credentials.json`
4. Should be readable/writable: `chmod 0600 ~/.Top Dog/llm_credentials.json`
5. Check backend logs for storage errors

### Token Expired

**Problem:** Authenticated before but now getting "Unauthenticated"

**Solutions:**
1. OAuth tokens have expiration times
2. Click "Sign in" again to refresh token
3. System will automatically try refresh token if available
4. Some providers auto-extend tokens on use

### CORS Errors

**Problem:** Errors about "cross-origin requests blocked"

**Solutions:**
1. Check CORS middleware in backend/main.py
2. Frontend origin should be in `cors_origins` list
3. For localhost development, should be: `http://localhost:1431`
4. For production, add your domain

---

## 📱 Mobile/Remote Access

For accessing Top Dog from other machines:

1. Update redirect URI in OAuth providers:
   - Change `localhost` to actual hostname/IP
   - Example: `http://mycomputer.local:8000/llm_auth/callback`

2. Update backend environment:
   ```bash
   export QIDE_BACKEND_URL=http://mycomputer.local:8000
   ```

3. Update frontend CORS in main.py:
   ```python
   cors_origins = ["http://mycomputer.local:1431"]
   ```

---

## 🔒 Security Notes

1. **Never commit secrets** to version control
2. **Use .env file** for local development
3. **Use environment variables** for production
4. **Rotate secrets regularly** in OAuth provider consoles
5. **Monitor API usage** in provider dashboards
6. **Tokens are stored locally** in `~/.Top Dog/llm_credentials.json` with 0o600 permissions
7. **Users can revoke** tokens anytime in Top Dog Auth tab

---

## 🚀 Next Steps

1. ✅ Complete OAuth setup above
2. ✅ Test each OAuth provider
3. ✅ Verify tokens stored correctly
4. ⏳ Add to user onboarding documentation
5. ⏳ Set up deployment OAuth credentials
6. ⏳ Configure auto-refresh for production

---

## 💡 Pro Tips

- **Quick Restart**: `pkill -f "python main.py"` then `python main.py`
- **Check Tokens**: `jq . ~/.Top Dog/llm_credentials.json` (requires jq)
- **Clear Tokens**: `rm ~/.Top Dog/llm_credentials.json` to reset
- **Debug Logs**: `tail -f backend/logs/Top Dog-topdog.log` to see detailed logs
- **Test Endpoints**: `curl http://localhost:8000/llm_auth/providers` to check backend

---

## 📞 Support

For OAuth setup issues:
1. Check the troubleshooting section above
2. Review backend logs for detailed error messages
3. Verify provider console settings match exactly
4. Ensure .env file is in correct location
5. Try with different OAuth provider first to isolate issue

**Backend OAuth Implementation**: `backend/llm_oauth_auth.py`, `backend/llm_oauth_routes.py`
**Frontend OAuth Component**: `frontend/src/components/LLMOAuthPanel.tsx`
**Documentation**: This file

---

**Last Updated**: Top Dog Phase 13 - OAuth Integration
**Status**: ✅ Production Ready
