/*
 * LLM OAuth Authentication Component
 * Q-IDE - Intelligent Development Environment
 * Copyright (c) 2025 Quellum Technologies. All rights reserved.
 * Licensed under the MIT License
 * 
 * Professional OAuth sign-in experience with:
 * - Google, GitHub, OpenAI, Anthropic sign-in
 * - Seamless redirect-based OAuth flow
 * - Status display and management
 * - Token refresh handling
 */

import React, { useEffect, useState } from 'react';

interface OAuthProvider {
  id: string;
  name: string;
  configured: boolean;
  description: string;
  oauth_enabled: boolean;
  icon?: string;
  color?: string;
}

interface AuthStatus {
  authenticated: boolean;
  user_id?: string;
  user_email?: string;
  expires_at?: string;
  auth_method?: string;
}

interface OAuthProviderStatus {
  [key: string]: AuthStatus;
}

export default function LLMOAuthPanel() {
  const [providers, setProviders] = useState<OAuthProvider[]>([]);
  const [authStatus, setAuthStatus] = useState<OAuthProviderStatus>({});
  const [loading, setLoading] = useState(false);
  const [signingIn, setSigningIn] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);
  const [oauthWindow, setOAuthWindow] = useState<Window | null>(null);

  useEffect(() => {
    loadProviders();
    checkAuthStatus();
    
    // Listen for OAuth callback messages from popup
    const handleMessage = (event: MessageEvent) => {
      if (event.origin !== window.location.origin) return;
      
      if (event.data.type === 'oauth_success') {
        setMessage({
          type: 'success',
          text: `✅ Successfully authenticated with ${event.data.provider.toUpperCase()}!`
        });
        setSigningIn(null);
        
        // Close the OAuth window if still open
        if (oauthWindow && !oauthWindow.closed) {
          oauthWindow.close();
        }
        
        // Refresh auth status
        setTimeout(() => checkAuthStatus(), 1000);
      } else if (event.data.type === 'oauth_error') {
        setMessage({
          type: 'error',
          text: `❌ Authentication failed: ${event.data.error}`
        });
        setSigningIn(null);
      }
    };
    
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [oauthWindow]);

  async function loadProviders() {
    try {
      setLoading(true);
      const res = await fetch('/llm_auth/providers');
      const data = await res.json();
      setProviders(data.providers || []);
    } catch (e) {
      console.error('Error loading providers:', e);
      setMessage({ type: 'error', text: 'Failed to load OAuth providers' });
    } finally {
      setLoading(false);
    }
  }

  async function checkAuthStatus() {
    try {
      const res = await fetch('/llm_auth/status');
      const data = await res.json();
      setAuthStatus(data.providers || {});
    } catch (e) {
      console.error('Error checking auth status:', e);
    }
  }

  async function handleSignIn(provider: string) {
    setSigningIn(provider);
    
    try {
      // Get OAuth URL from backend
      const res = await fetch(`/llm_auth/login/${provider}`);
      const data = await res.json();
      
      if (!data.success) {
        if (data.client_required) {
          setMessage({
            type: 'info',
            text: `⚙️ ${provider.toUpperCase()} OAuth not configured. Using API key method instead.`
          });
        } else {
          setMessage({
            type: 'error',
            text: `Failed to initiate ${provider} sign-in`
          });
        }
        setSigningIn(null);
        return;
      }
      
      // Open OAuth URL in popup
      const width = 500;
      const height = 600;
      const left = window.screenX + (window.outerWidth - width) / 2;
      const top = window.screenY + (window.outerHeight - height) / 2;
      
      const oauthUrl = data.oauth_url;
      const popup = window.open(
        oauthUrl,
        `oauth_${provider}`,
        `width=${width},height=${height},left=${left},top=${top}`
      );
      
      if (popup) {
        setOAuthWindow(popup);
        
        // Monitor popup closure
        const checkPopup = setInterval(() => {
          if (popup.closed) {
            clearInterval(checkPopup);
            // After popup closes, check auth status
            setTimeout(() => checkAuthStatus(), 500);
          }
        }, 1000);
      } else {
        setMessage({
          type: 'error',
          text: 'Failed to open sign-in window. Please check popup blocker settings.'
        });
        setSigningIn(null);
      }
    } catch (e) {
      console.error('Error initiating sign-in:', e);
      setMessage({ type: 'error', text: 'Error initiating sign-in' });
      setSigningIn(null);
    }
  }

  async function handleLogout(provider: string) {
    try {
      const res = await fetch(`/llm_auth/logout/${provider}`, { method: 'POST' });
      
      if (res.ok) {
        setMessage({
          type: 'success',
          text: `✅ Logged out from ${provider.toUpperCase()}`
        });
        checkAuthStatus();
      } else {
        setMessage({
          type: 'error',
          text: `Failed to logout from ${provider}`
        });
      }
    } catch (e) {
      console.error('Error logging out:', e);
      setMessage({ type: 'error', text: 'Error logging out' });
    }
  }

  const getProviderIcon = (provider: string): string => {
    const icons: { [key: string]: string } = {
      google: '🔵',
      github: '⚫',
      openai: '🚀',
      anthropic: '🧠',
    };
    return icons[provider] || '🔐';
  };

  const getProviderColor = (provider: string): string => {
    const colors: { [key: string]: string } = {
      google: '#4285F4',
      github: '#333333',
      openai: '#00D084',
      anthropic: '#8B7355',
    };
    return colors[provider] || '#667eea';
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch {
      return dateString;
    }
  };

  return (
    <div className="llm-oauth-panel">
      <div className="oauth-header">
        <h2>🔐 Seamless OAuth Sign-In</h2>
        <p>Sign in with your OAuth providers for instant LLM access</p>
      </div>

      {message && (
        <div className={`oauth-message oauth-message-${message.type}`}>
          {message.text}
          <button 
            className="oauth-message-close"
            onClick={() => setMessage(null)}
          >
            ✕
          </button>
        </div>
      )}

      {loading && (
        <div className="oauth-loading">
          <div className="spinner"></div>
          <p>Loading OAuth providers...</p>
        </div>
      )}

      {!loading && (
        <>
          <div className="oauth-grid">
            {providers.map((provider) => {
              const status = authStatus[provider.id];
              const isAuthenticated = status?.authenticated || false;
              const icon = getProviderIcon(provider.id);
              const color = getProviderColor(provider.id);
              const isSigning = signingIn === provider.id;

              return (
                <div 
                  key={provider.id} 
                  className={`oauth-card ${isAuthenticated ? 'authenticated' : ''}`}
                  style={{
                    borderLeftColor: color,
                  }}
                >
                  <div className="oauth-card-header">
                    <span className="oauth-icon" style={{ fontSize: '28px' }}>
                      {icon}
                    </span>
                    <div className="oauth-card-title">
                      <h3>{provider.name}</h3>
                      <p>{provider.description}</p>
                    </div>
                    {isAuthenticated && (
                      <span className="oauth-badge">✓ Connected</span>
                    )}
                  </div>

                  {isAuthenticated ? (
                    <div className="oauth-card-authenticated">
                      <div className="oauth-user-info">
                        <p><strong>User ID:</strong> {status?.user_id}</p>
                        {status?.user_email && (
                          <p><strong>Email:</strong> {status.user_email}</p>
                        )}
                        {status?.expires_at && (
                          <p><strong>Expires:</strong> {formatDate(status.expires_at)}</p>
                        )}
                      </div>
                      <button
                        className="oauth-btn oauth-btn-logout"
                        onClick={() => handleLogout(provider.id)}
                        disabled={isSigning}
                      >
                        🚪 Sign Out
                      </button>
                    </div>
                  ) : (
                    <button
                      className="oauth-btn oauth-btn-signin"
                      onClick={() => handleSignIn(provider.id)}
                      disabled={isSigning || !provider.configured}
                      style={{
                        background: provider.configured
                          ? `linear-gradient(135deg, ${color}44 0%, ${color}22 100%)`
                          : '#f0f0f0',
                      }}
                    >
                      {isSigning ? (
                        <>
                          <span className="spinner-small"></span>
                          Signing in...
                        </>
                      ) : provider.configured ? (
                        `Sign in with ${provider.name}`
                      ) : (
                        'OAuth not configured'
                      )}
                    </button>
                  )}
                </div>
              );
            })}
          </div>

          <div className="oauth-info-box">
            <h4>🔒 How OAuth Sign-In Works</h4>
            <ol>
              <li>Click "Sign in with [Provider]" button</li>
              <li>A secure sign-in window will open</li>
              <li>Sign in with your provider credentials</li>
              <li>Grant Q-IDE permission to access your LLM services</li>
              <li>Automatically redirected back - you're all set!</li>
            </ol>
            <p style={{ marginTop: '15px', fontSize: '13px', color: '#666' }}>
              ✓ Your credentials are never stored in Q-IDE<br/>
              ✓ Only OAuth tokens are saved (revocable anytime)<br/>
              ✓ Secure, professional sign-in experience
            </p>
          </div>
        </>
      )}
    </div>
  );
}
