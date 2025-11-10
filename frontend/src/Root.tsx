import React, { useEffect, useState } from 'react';
import { ThemeProvider } from './components/ThemeContext';
import { AuthProvider } from './components/AuthContext';
import App from './App';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import { isAuthed, getToken, verifyToken, clearToken } from './services/authClient';
import { BrowserRouter, Routes, Route, Navigate, useParams } from 'react-router-dom';

// Supported tab list for deep-linking
const validTabs = new Set(['viewer','builds','extensions','settings','learning','llm','config','phone','billing','pricing','rules','medical','science']);

const AppWithParam: React.FC = () => {
  const { tab } = useParams();
  const t = (tab && validTabs.has(tab)) ? (tab as any) : 'viewer';
  return <App initialTab={t} />;
};

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [status, setStatus] = useState<'checking' | 'allowed' | 'denied'>('checking');
  useEffect(() => {
    const run = async () => {
      const tok = getToken();
      if (!tok) { setStatus('denied'); return; }
      const ok = await verifyToken(tok).catch(() => false);
      if (!ok) { clearToken(); setStatus('denied'); } else { setStatus('allowed'); }
    };
    run();
  }, []);
  if (status === 'checking') return <div className="min-h-screen grid place-items-center text-slate-300">Checking session…</div>;
  if (status === 'denied') return <Navigate to="/login" replace />;
  return <>{children}</>;
};

export const Root: React.FC = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
          <Route path="/" element={isAuthed() ? <Navigate to="/app/viewer" replace /> : <LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/oauth/callback" element={<App />} />
          <Route path="/auth/oauth/callback" element={<App />} />
          <Route path="/app" element={<ProtectedRoute><App initialTab="viewer" /></ProtectedRoute>} />
          <Route path="/app/:tab" element={<ProtectedRoute><AppWithParam /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to={isAuthed() ? "/app/viewer" : "/"} replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default Root;
