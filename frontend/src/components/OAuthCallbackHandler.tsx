/*
 * OAuth Callback Handler
 * Q-IDE - Intelligent Development Environment
 * Copyright (c) 2025 Quellum Technologies. All rights reserved.
 * Licensed under the MIT License
 * 
 * Handles OAuth provider callbacks and communicates with parent window
 * This component runs in the OAuth popup window after provider redirect
 */

import React, { useEffect, useState } from 'react';

interface CallbackProps {
  provider?: string;
  code?: string;
  state?: string;
  error?: string;
  error_description?: string;
}

export default function OAuthCallbackHandler() {
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
  const [message, setMessage] = useState('Processing OAuth callback...');
  const [provider, setProvider] = useState<string>('');

  useEffect(() => {
    // Get query parameters
    const params = new URLSearchParams(window.location.search);
    const provider = params.get('provider') || params.get('state')?.split('_')[0] || 'unknown';
    const code = params.get('code');
    const state = params.get('state');
    const error = params.get('error');
    const errorDescription = params.get('error_description');

    setProvider(provider);

    // Check if there's an error from OAuth provider
    if (error) {
      setStatus('error');
      setMessage(`Authentication failed: ${errorDescription || error}`);
      
      // Notify parent window
      if (window.opener) {
        window.opener.postMessage({
          type: 'oauth_error',
          provider,
          error: errorDescription || error,
        }, window.location.origin);
      }
      return;
    }

    // If no code, something went wrong
    if (!code || !state) {
      setStatus('error');
      setMessage('Invalid callback parameters received');
      
      if (window.opener) {
        window.opener.postMessage({
          type: 'oauth_error',
          provider,
          error: 'Invalid callback parameters',
        }, window.location.origin);
      }
      return;
    }

    // Process the callback
    processCallback(provider, code, state);
  }, []);

  async function processCallback(provider: string, code: string, state: string) {
    try {
      setMessage(`Exchanging authorization code with ${provider}...`);

      // Call backend callback endpoint
      const response = await fetch(
        `/llm_auth/callback?code=${encodeURIComponent(code)}&state=${encodeURIComponent(state)}&provider=${encodeURIComponent(provider)}`
      );

      const data = await response.json();

      if (data.success) {
        setStatus('success');
        setMessage(`✅ Successfully authenticated with ${provider}!`);
        
        // Notify parent window of success
        if (window.opener) {
          window.opener.postMessage({
            type: 'oauth_success',
            provider,
            user_id: data.user_id,
            user_email: data.user_email,
          }, window.location.origin);
        }

        // Close this window after a short delay
        setTimeout(() => {
          window.close();
        }, 2000);
      } else {
        setStatus('error');
        setMessage(`Authentication failed: ${data.error || 'Unknown error'}`);
        
        if (window.opener) {
          window.opener.postMessage({
            type: 'oauth_error',
            provider,
            error: data.error || 'Authentication failed',
          }, window.location.origin);
        }
      }
    } catch (err) {
      setStatus('error');
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      setMessage(`Error: ${errorMsg}`);
      
      if (window.opener) {
        window.opener.postMessage({
          type: 'oauth_error',
          provider,
          error: errorMsg,
        }, window.location.origin);
      }
    }
  }

  const statusColors = {
    processing: '#4285F4',
    success: '#34A853',
    error: '#EA4335',
  };

  return (
    <div className="oauth-callback-container">
      <div className="oauth-callback-content">
        <div 
          className="oauth-callback-icon"
          style={{ color: statusColors[status] }}
        >
          {status === 'processing' && '⏳'}
          {status === 'success' && '✅'}
          {status === 'error' && '❌'}
        </div>
        
        <h1 className="oauth-callback-title">
          {status === 'processing' && 'Signing In...'}
          {status === 'success' && 'Successfully Authenticated!'}
          {status === 'error' && 'Authentication Failed'}
        </h1>
        
        <p className="oauth-callback-message">{message}</p>
        
        {status === 'processing' && (
          <div className="oauth-callback-spinner">
            <div className="spinner"></div>
          </div>
        )}
        
        {status === 'success' && (
          <p className="oauth-callback-note">
            This window will close automatically in a moment...
          </p>
        )}
        
        {status === 'error' && (
          <button 
            className="oauth-callback-button"
            onClick={() => window.close()}
          >
            Close Window
          </button>
        )}
      </div>

      <style>{`
        .oauth-callback-container {
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
        }

        .oauth-callback-content {
          background: white;
          border-radius: 16px;
          padding: 40px;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
          text-align: center;
          max-width: 400px;
          width: 90%;
        }

        .oauth-callback-icon {
          font-size: 64px;
          margin-bottom: 20px;
          display: block;
        }

        .oauth-callback-title {
          font-size: 24px;
          font-weight: 600;
          margin: 0 0 15px 0;
          color: #1f2937;
        }

        .oauth-callback-message {
          font-size: 16px;
          color: #666;
          margin: 0 0 30px 0;
          line-height: 1.5;
        }

        .oauth-callback-note {
          font-size: 14px;
          color: #999;
          margin: 20px 0 0 0;
          font-style: italic;
        }

        .oauth-callback-spinner {
          display: flex;
          justify-content: center;
          margin: 30px 0;
        }

        .spinner {
          width: 40px;
          height: 40px;
          border: 4px solid #e5e7eb;
          border-top-color: #667eea;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .oauth-callback-button {
          background: #667eea;
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 8px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.3s;
        }

        .oauth-callback-button:hover {
          background: #5568d3;
        }

        .oauth-callback-button:active {
          transform: scale(0.98);
        }
      `}</style>
    </div>
  );
}
