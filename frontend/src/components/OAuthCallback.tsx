import React, { useEffect, useState } from 'react';

/**
 * OAuthCallback Component
 * Handles OAuth callback redirects from LLM providers
 * Extracts authorization code and exchanges it for a token
 */
export default function OAuthCallback() {
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
  const [message, setMessage] = useState('Processing OAuth callback...');

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Extract query parameters from URL
        const params = new URLSearchParams(window.location.search);
        const code = params.get('code');
        const state = params.get('state');
        const error = params.get('error');
        const error_description = params.get('error_description');

        // Handle OAuth errors
        if (error) {
          setStatus('error');
          setMessage(`OAuth Error: ${error}${error_description ? ` - ${error_description}` : ''}`);
          
          // Notify parent window of error
          if (window.opener) {
            window.opener.postMessage(
              { type: 'oauth_error', provider: state, error, error_description },
              window.location.origin
            );
          }
          return;
        }

        // Validate we have the authorization code
        if (!code || !state) {
          setStatus('error');
          setMessage('Missing authorization code or provider information');
          return;
        }

        // Exchange the code for a token
        const response = await fetch('/llm_auth/oauth/exchange', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            provider: state,
            code: code,
            redirect_uri: `${window.location.origin}/oauth/callback`,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to exchange authorization code');
        }

        const data = await response.json();

        // Success!
        setStatus('success');
        setMessage(`Successfully authenticated with ${state}!`);

        // Notify parent window of success
        if (window.opener) {
          window.opener.postMessage(
            { type: 'oauth_success', provider: state, token: data },
            window.location.origin
          );
          // Close popup after a short delay
          setTimeout(() => {
            window.close();
          }, 1500);
        }
      } catch (err) {
        setStatus('error');
        setMessage(`Error: ${err instanceof Error ? err.message : 'Unknown error occurred'}`);

        // Notify parent window of error
        if (window.opener) {
          window.opener.postMessage(
            {
              type: 'oauth_error',
              error: err instanceof Error ? err.message : 'Unknown error',
            },
            window.location.origin
          );
        }
      }
    };

    handleCallback();
  }, []);

  return (
    <div className="min-h-screen bg-[#1a1f26] flex items-center justify-center">
      <div className="p-8 bg-[#23272e] rounded-lg border border-cyan-900/20 text-center max-w-md">
        <div className="mb-4">
          {status === 'processing' && (
            <div className="inline-block animate-spin">
              <div className="w-12 h-12 border-4 border-cyan-900/30 border-t-cyan-400 rounded-full"></div>
            </div>
          )}
          {status === 'success' && (
            <div className="text-4xl">✓</div>
          )}
          {status === 'error' && (
            <div className="text-4xl">✕</div>
          )}
        </div>

        <h1 className={`text-xl font-bold mb-2 ${
          status === 'success' ? 'text-green-400' :
          status === 'error' ? 'text-red-400' :
          'text-cyan-300'
        }`}>
          {status === 'processing' ? 'Authenticating...' :
           status === 'success' ? 'Authentication Successful' :
           'Authentication Failed'}
        </h1>

        <p className={`text-sm mb-4 ${
          status === 'success' ? 'text-green-300' :
          status === 'error' ? 'text-red-300' :
          'text-cyan-200'
        }`}>
          {message}
        </p>

        {status === 'error' && (
          <button
            onClick={() => window.close()}
            className="px-4 py-2 bg-cyan-700 hover:bg-cyan-600 text-white rounded text-sm"
          >
            Close
          </button>
        )}

        {status === 'processing' && (
          <p className="text-xs text-gray-400">
            This window will close automatically when complete.
          </p>
        )}
      </div>
    </div>
  );
}
