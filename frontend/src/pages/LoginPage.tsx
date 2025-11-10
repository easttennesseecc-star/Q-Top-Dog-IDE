import React, { useState } from 'react';
import { login, storeToken } from '../services/authClient';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const resp = await login(email, password);
      if (!resp.success || !resp.data) {
        setError(resp.error || 'Invalid credentials');
      } else {
        storeToken(resp.data.token);
        window.location.href = '/app/viewer';
      }
    } catch (err: any) {
      setError(err?.message ?? 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen grid place-items-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-200 p-6">
      <form onSubmit={submit} className="w-full max-w-md bg-slate-900/70 border border-slate-700/40 rounded-xl p-6 space-y-4">
        <h1 className="text-2xl font-bold text-cyan-300">Welcome back</h1>
        <p className="text-sm text-slate-400">Sign in with your email to continue</p>
        {error && <div className="text-sm text-red-300 bg-red-900/20 border border-red-700/40 p-2 rounded">{error}</div>}
        <label className="block text-sm">
          <span className="block mb-1 text-slate-300">Email</span>
          <input type="email" required value={email} onChange={e=>setEmail(e.target.value)} className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500" placeholder="you@example.com" />
        </label>
        <label className="block text-sm">
          <span className="block mb-1 text-slate-300">Password</span>
          <input type="password" required value={password} onChange={e=>setPassword(e.target.value)} className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500" placeholder="••••••••" />
        </label>
  <button type="submit" disabled={loading} className="w-full py-2 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-semibold disabled:opacity-60">{loading? 'Signing in…':'Sign in'}</button>
        <div className="text-xs text-slate-400 text-center">No account? <a href="/signup" className="text-cyan-300 hover:text-cyan-200">Create one</a></div>
      </form>
    </div>
  );
};

export default LoginPage;
