// Centralized auth client for frontend
// Handles base URL resolution, token storage, and API calls

export type LoginResponse = {
  success: boolean;
  data?: { token: string; user_id: string; expires_at: string };
  error?: string;
};

export type RegisterResponse = {
  success: boolean;
  data?: any;
  error?: string;
};

const getBase = (): string => {
  const w = window as any;
  const fromWindow = w.__VITE_BACKEND_URL;
  const fromVite = (import.meta as any)?.env?.VITE_BACKEND_URL || (import.meta as any)?.env?.VITE_API_URL;
  const fromReact = (process as any)?.env?.REACT_APP_BACKEND_URL;
  return (fromWindow || fromVite || fromReact || '').replace(/\/$/, '');
};

const toApi = (p: string) => `${getBase()}${p.startsWith('/') ? p : '/' + p}`;

export const tokenKey = 'q_ide_access_token';
export const sessionKey = 'q_ide_user_session';

export const storeToken = (token: string) => {
  localStorage.setItem(tokenKey, token);
  localStorage.setItem(sessionKey, '1');
};

export const getToken = (): string | null => localStorage.getItem(tokenKey);
export const clearToken = () => {
  localStorage.removeItem(tokenKey);
  localStorage.removeItem(sessionKey);
};

export const isAuthed = (): boolean => !!getToken() || !!localStorage.getItem('oauth_session_id');

export async function login(email: string, password: string): Promise<LoginResponse> {
  const res = await fetch(toApi('/api/v1/auth/login'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const j = await res.json();
  return j as LoginResponse;
}

export async function register(email: string, username: string, password: string): Promise<RegisterResponse> {
  const res = await fetch(toApi('/api/v1/auth/register'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, username, password })
  });
  const j = await res.json();
  return j as RegisterResponse;
}

export async function verifyToken(token: string): Promise<boolean> {
  const res = await fetch(toApi('/api/v1/auth/verify-token'), {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
  });
  if (!res.ok) return false;
  const j = await res.json();
  return !!j?.success;
}
