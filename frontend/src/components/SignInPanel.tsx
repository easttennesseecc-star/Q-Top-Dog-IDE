import React, { useState, useEffect } from 'react';
import { GoogleSignIn } from './GoogleSignIn';
import { AccountLinkingPanel } from './AccountLinkingPanel';

interface SignInPanelProps {
  onSignInSuccess?: () => void;
}

export const SignInPanel: React.FC<SignInPanelProps> = ({ onSignInSuccess }) => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [user, setUser] = useState<any>(null);

  // Restore session from localStorage on mount
  useEffect(() => {
    const savedSessionId = localStorage.getItem('oauth_session_id');
    const savedUser = localStorage.getItem('oauth_user');
    if (savedSessionId) {
      setSessionId(savedSessionId);
      if (savedUser) {
        setUser(JSON.parse(savedUser));
      }
    }
  }, []);

  const handleGoogleSuccess = (googleUser: any) => {
    setSessionId(googleUser.session_id);
    setUser(googleUser);
    localStorage.setItem('oauth_session_id', googleUser.session_id);
    localStorage.setItem('oauth_user', JSON.stringify(googleUser));
    onSignInSuccess?.();
  };

  const handleSignOut = () => {
    setSessionId(null);
    setUser(null);
    localStorage.removeItem('oauth_session_id');
    localStorage.removeItem('oauth_user');
  };

  if (user && sessionId) {
    return (
      <div className="flex flex-col gap-6 p-6 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-xl border border-slate-700/50 shadow-2xl">
        <div className="flex items-center justify-between pb-4 border-b border-slate-700/30">
          <div className="flex items-center gap-4">
            {user.picture && (
              <div className="relative">
                <img 
                  src={user.picture} 
                  alt={user.name} 
                  className="w-14 h-14 rounded-full border-2 border-cyan-400/50 shadow-lg"
                />
                <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 border-2 border-slate-900 rounded-full"></div>
              </div>
            )}
            <div>
              <p className="font-semibold text-white text-lg">{user.name}</p>
              <p className="text-sm text-cyan-300/80">{user.email}</p>
            </div>
          </div>
          <button
            onClick={handleSignOut}
            className="px-4 py-2 text-sm bg-red-600/20 text-red-300 rounded-lg hover:bg-red-600/40 border border-red-500/50 transition-all duration-200"
          >
            🚪 Sign Out
          </button>
        </div>

        <AccountLinkingPanel sessionId={sessionId} />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-5 p-6 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-xl border border-slate-700/50 shadow-2xl backdrop-blur-sm">
      <div>
        <h2 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-blue-400 mb-2">🔐 Sign In to Q</h2>
        <p className="text-sm text-slate-300">
          Connect with your Google account to unlock integrated tools, OAuth flows, and AI-powered assistance.
        </p>
      </div>
      <div className="bg-slate-800/50 border border-slate-700/30 rounded-lg p-4 space-y-2 text-xs text-slate-400">
        <div className="flex items-start gap-2">
          <span className="text-cyan-400 mt-1">✓</span>
          <span>Seamless OAuth integration with Google & GitHub</span>
        </div>
        <div className="flex items-start gap-2">
          <span className="text-cyan-400 mt-1">✓</span>
          <span>Secure token storage and session management</span>
        </div>
        <div className="flex items-start gap-2">
          <span className="text-cyan-400 mt-1">✓</span>
          <span>Link multiple accounts for enhanced functionality</span>
        </div>
      </div>
      <GoogleSignIn onSuccess={handleGoogleSuccess} />
    </div>
  );
};
