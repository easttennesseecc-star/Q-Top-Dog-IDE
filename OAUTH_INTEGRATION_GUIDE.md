/*
 * OAuth Configuration Panel Snippet
 * Q-IDE - Intelligent Development Environment
 * Add this to LLMConfigPanel.tsx Auth Tab
 * 
 * Integrates professional OAuth sign-in alongside manual API key entry
 * Users can choose OAuth (recommended) or manual API key (fallback)
 */

// ============================================================================
// STEP 1: Add this to the imports at the top of LLMConfigPanel.tsx
// ============================================================================

import LLMOAuthPanel from './LLMOAuthPanel';
import './LLMOAuthPanel.css';


// ============================================================================
// STEP 2: Replace the Auth Tab section (around line 448) with this:
// ============================================================================

{activeTab === 'auth' && (
  <div className="space-y-6">
    {/* OAuth Sign-In Section */}
    <div className="border border-green-600/50 bg-green-900/10 rounded-lg p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-green-300 mb-2">✅ Recommended: OAuth Sign-In</h3>
        <p className="text-sm text-gray-400">
          Sign in with your OAuth provider for instant, secure authentication.
          No API keys to manage or copy-paste!
        </p>
      </div>
      
      {/* Embed OAuth Panel Component */}
      <LLMOAuthPanel />
    </div>

    {/* Divider */}
    <div className="flex items-center gap-4 py-4">
      <div className="flex-1 h-px bg-gray-600/30"></div>
      <span className="text-gray-400 text-sm">OR</span>
      <div className="flex-1 h-px bg-gray-600/30"></div>
    </div>

    {/* Manual API Key Section */}
    <div>
      <div>
        <h3 className="text-lg font-semibold mb-2 text-cyan-300">🔑 Manual: API Key Entry</h3>
        <p className="text-sm text-gray-400 mb-4">
          Alternatively, enter your API credentials manually. Your credentials are stored 
          locally and encrypted - never sent anywhere.
        </p>
      </div>

      {/* Existing credential input code */}
      <div className="space-y-3">
        {providers && Object.entries(providers)
          .filter(([_, p]) => p.type === 'cloud')
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([providerId, provider]) => {
            // ... rest of your existing credential input code ...
          })}
      </div>
    </div>
  </div>
)}


// ============================================================================
// STEP 3: Make sure you have these functions in your component
// ============================================================================

async function revokeAuth(providerId: string) {
  try {
    const res = await fetch(`/llm_auth/logout/${providerId}`, { method: 'POST' });
    if (res.ok) {
      setMessage({ 
        type: 'success', 
        text: `Logged out from ${providerId}` 
      });
      checkAuthStatus();
    }
  } catch (e) {
    console.error('Error revoking auth:', e);
    setMessage({ 
      type: 'error', 
      text: 'Failed to revoke authentication' 
    });
  }
}


// ============================================================================
// ENVIRONMENT SETUP REQUIRED
// ============================================================================

// For OAuth to work, you need to set environment variables:
//
// QIDE_GOOGLE_CLIENT_ID=your_google_client_id
// QIDE_GOOGLE_CLIENT_SECRET=your_google_client_secret
// QIDE_GITHUB_CLIENT_ID=your_github_client_id
// QIDE_GITHUB_CLIENT_SECRET=your_github_client_secret
// QIDE_OPENAI_CLIENT_ID=your_openai_client_id
// QIDE_OPENAI_CLIENT_SECRET=your_openai_client_secret
// QIDE_ANTHROPIC_CLIENT_ID=your_anthropic_client_id
// QIDE_ANTHROPIC_CLIENT_SECRET=your_anthropic_client_secret
// QIDE_BACKEND_URL=http://localhost:8000  (or your backend URL)
//
// Set these in:
// 1. .env file in project root
// 2. System environment variables
// 3. Docker environment variables
// 4. Deployment platform settings


// ============================================================================
// OAUTH CALLBACK SETUP REQUIRED
// ============================================================================

// Make sure the OAuth callback page is served. Add to main.py or config:
//
// 1. The callback handler will redirect to: /llm_auth/callback?code=...&state=...
// 2. The callback returns HTML that signals the parent window via postMessage
// 3. Frontend listens for postMessage and closes the popup
//
// The flow:
//   User clicks "Sign in with Google"
//   → Frontend opens OAuth popup to /llm_auth/login/google
//   → Backend generates OAuth URL, redirects to Google
//   → User signs in at Google
//   → Google redirects to /llm_auth/callback?code=...
//   → Backend exchanges code for token
//   → Backend stores token locally in ~/.q-ide/llm_credentials.json
//   → Frontend receives postMessage, closes popup
//   → Frontend refreshes auth status
//   → User can now use LLMs!


// ============================================================================
// TESTING THE OAUTH FLOW
// ============================================================================

// 1. Start backend: python main.py
// 2. Start frontend: npm start
// 3. In LLMConfigPanel, click Auth tab
// 4. Click "Sign in with Google"
// 5. OAuth popup opens
// 6. Sign in at Google
// 7. See success message
// 8. Token saved locally
// 9. Refresh page - should show "✓ Authenticated"


// ============================================================================
// TROUBLESHOOTING
// ============================================================================

// Issue: "OAuth not configured"
// Solution: Set QIDE_GOOGLE_CLIENT_ID env var and restart backend

// Issue: Popup doesn't open
// Solution: Check browser popup blocker settings

// Issue: "Invalid callback parameters"
// Solution: Make sure backend is receiving code and state from OAuth provider
//           Check backend logs for errors

// Issue: Token not saved
// Solution: Check ~/.q-ide/ directory permissions
//           Check backend logs for "token storage" errors

// Issue: Token expired
// Solution: Refresh token is automatically handled on first use
//           If refresh fails, user needs to sign in again
