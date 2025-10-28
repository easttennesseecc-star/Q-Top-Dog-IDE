import React, { useState } from 'react';

interface GoogleSignInProps {
  onSuccess?: (user: { email: string; name: string; picture: string; session_id: string }) => void;
  onError?: (error: string) => void;
}

export const GoogleSignIn: React.FC<GoogleSignInProps> = ({ onSuccess, onError }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const BACKEND_URL = import.meta.env?.VITE_BACKEND_URL || 'http://127.0.0.1:8000';

  const handleGoogleSignIn = async () => {
    setLoading(true);
    setError(null);

    try {
      // Get the authorization URL from backend
      const startUrl = BACKEND_URL ? `${BACKEND_URL}/auth/google/start` : '/auth/google/start';
      const startResponse = await fetch(startUrl);
      const startData = await startResponse.json();

      if (!startData.auth_url) {
        throw new Error(startData.message || 'Failed to get Google auth URL');
      }

      // Open OAuth consent screen in a popup
      const popup = window.open(startData.auth_url, 'google-signin', 'width=500,height=600');

      // Listen for callback from the popup (backend redirects to a callback URL that posts to parent)
      const listener = (event: MessageEvent) => {
        if (event.origin !== window.location.origin) return;

        if (event.data?.type === 'google-signin-success') {
          window.removeEventListener('message', listener);
          popup?.close();
          onSuccess?.(event.data.user);
        } else if (event.data?.type === 'google-signin-error') {
          window.removeEventListener('message', listener);
          popup?.close();
          setError(event.data.error);
          onError?.(event.data.error);
        }
      };

      window.addEventListener('message', listener);

      // Clean up listener if popup closes without success
      const checkPopup = setInterval(() => {
        if (popup?.closed) {
          clearInterval(checkPopup);
          window.removeEventListener('message', listener);
        }
      }, 1000);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Sign-in failed';
      setError(message);
      onError?.(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-3">
      <button
        onClick={handleGoogleSignIn}
        disabled={loading}
        className="group relative w-full px-5 py-3 bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-lg font-semibold shadow-lg hover:shadow-blue-500/50 hover:from-blue-500 hover:to-blue-400 disabled:from-gray-600 disabled:to-gray-500 transition-all duration-200 disabled:cursor-not-allowed flex items-center justify-center gap-3"
      >
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
          <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
          <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
        </svg>
        {loading ? 'Signing in...' : 'Sign in with Google'}
      </button>
      {error && (
        <div className="p-3 bg-red-600/20 border border-red-500/50 rounded-lg text-red-300 text-sm flex items-start gap-2">
          <span className="text-lg mt-0.5">⚠️</span>
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};
