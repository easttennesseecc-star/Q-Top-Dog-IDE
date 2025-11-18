import React, { useEffect, useState } from 'react';
import { ThemeProvider } from './components/ThemeContext';
import { AuthProvider, useAuth } from './components/AuthContext';
import App from './App';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import OAuthCallback from './components/OAuthCallback';
import PricingPage from './pages/PricingPage';
import { isAuthed, getToken } from './services/authClient';
import { BrowserRouter, Routes, Route, Navigate, useParams } from 'react-router-dom';

// Supported tab list for deep-linking
const validTabs = new Set(['viewer','builds','extensions','settings','learning','llm','config','phone','billing','pricing','rules','medical','science']);

const AppWithParam: React.FC = () => {
  const { tab } = useParams();
  const t = (tab && validTabs.has(tab)) ? (tab as any) : 'viewer';
  return <App initialTab={t} />;
};

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { loading, isAuthed: authed } = useAuth();
  if (loading) return <div className="min-h-screen grid place-items-center text-slate-300">Checking session…</div>;
  if (!authed) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

// AuthGate: run once early; if no token, clear legacy oauth session artifacts.
const AuthGate: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { loading } = useAuth();
  const hasToken = !!getToken();
  useEffect(() => {
    if (!hasToken) {
      try {
        localStorage.removeItem('oauth_session_id');
        localStorage.removeItem('oauth_user');
      } catch (_) {
        // ignore
      }
    }
  }, [hasToken]);

  // While deciding, prefer showing marketing for a nicer first load if no token
  if (loading && !hasToken) return <LandingPage />;
  if (loading && hasToken) return <div className="min-h-screen grid place-items-center text-slate-300">Checking session…</div>;
  return <>{children}</>;
};

export const Root: React.FC = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <AuthGate>
            <Routes>
            <Route path="/" element={isAuthed() ? <Navigate to="/app/viewer" replace /> : <LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            {/* Public pricing page for SEO */}
            <Route path="/pricing" element={<PricingPage userId="public" currentTier="FREE" />} />
            {/* Explicit callback route uses dedicated component; not treated as fully authed */}
            <Route path="/oauth/callback" element={<OAuthCallback />} />
            <Route path="/auth/oauth/callback" element={<OAuthCallback />} />
            <Route path="/app" element={<ProtectedRoute><App initialTab="viewer" /></ProtectedRoute>} />
            <Route path="/app/:tab" element={<ProtectedRoute><AppWithParam /></ProtectedRoute>} />
            <Route path="*" element={<Navigate to={isAuthed() ? "/app/viewer" : "/"} replace />} />
            </Routes>
          </AuthGate>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default Root;
