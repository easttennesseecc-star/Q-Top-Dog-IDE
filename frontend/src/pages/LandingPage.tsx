import React from 'react';
import UnifiedSignInHub from '../components/UnifiedSignInHub';
import '../styles/theme.css';

/**
 * LandingPage
 * Public marketing + funnel entry. If user already authenticated (local token),
 * we could redirect to App; for now we show marketing + inline sign-in hub CTA.
 */
export const LandingPage: React.FC = () => {
  const hasSession = !!localStorage.getItem('q_ide_user_session');
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-200">
      {/* Top Nav */}
      <nav className="w-full flex items-center justify-between px-6 py-4 max-w-6xl mx-auto">
        <div className="text-lg font-extrabold tracking-tight text-cyan-300">Top Dog IDE</div>
        <div className="flex items-center gap-2">
          <a href="/login" className="text-xs px-3 py-1.5 rounded-md border border-cyan-400/30 hover:border-cyan-400 text-cyan-300">Sign in</a>
          <a href="/signup" className="text-xs px-3 py-1.5 rounded-md bg-cyan-600/20 border border-cyan-400/40 hover:bg-cyan-600/30 text-cyan-200">Sign up</a>
        </div>
      </nav>
      {/* Hero */}
      <header className="px-6 pt-6 pb-20 max-w-6xl mx-auto text-center">
        <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500">
          Top Dog IDE
        </h1>
        <p className="text-lg md:text-xl text-slate-300 max-w-3xl mx-auto mb-8">
          The AI-native development environment with integrated model orchestration, secure phone pairing, unified credential hub, and real-time build intelligence.
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          <a href="#features" className="px-6 py-3 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-semibold shadow-lg shadow-cyan-600/30 transition">Explore Features</a>
          <a href="/signup" className="px-6 py-3 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold shadow-lg shadow-blue-600/30 transition">Get Started – Free</a>
        </div>
      </header>

      {/* Trust Bar */}
      <section className="px-6 max-w-6xl mx-auto mb-24" id="features">
        <div className="grid md:grid-cols-3 gap-6">
          {[
            {title: 'Unified Model Access', desc: 'Switch seamlessly between local and hosted LLMs.'},
            {title: 'Secure Pairing', desc: 'Phone & device session security with OTP + revocation.'},
            {title: 'Production Ready', desc: 'Canary deploy workflow, quality gates & rollback alerts.'},
          ].map(f => (
            <div key={f.title} className="rounded-xl bg-slate-800/40 border border-slate-700/40 p-6 backdrop-blur">
              <h3 className="text-cyan-300 font-semibold mb-2 text-lg">{f.title}</h3>
              <p className="text-sm text-slate-300/80 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Sign-In Hub CTA */}
      <section id="signin" className="px-6 max-w-6xl mx-auto mb-24">
        <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 mb-6">Start Building</h2>
        <p className="text-slate-300 mb-4 max-w-2xl">Create a free account to enable repository access, model credentials, and secure device orchestration.</p>
        <p className="text-slate-400 text-sm mb-8">Already have an account? <a href="/login" className="text-cyan-300 hover:text-cyan-200">Sign in</a></p>
        {!hasSession ? (
          <UnifiedSignInHub />
        ) : (
          <div className="p-6 rounded-lg bg-green-900/20 border border-green-700/40">
            <p className="text-green-300 font-medium mb-2">You are already signed in.</p>
            <a href="/" className="inline-block px-5 py-2 rounded-md bg-green-600 hover:bg-green-500 text-white text-sm font-semibold">Enter App</a>
          </div>
        )}
      </section>

      {/* Footer */}
      <footer className="px-6 py-12 border-t border-slate-700/40 text-center text-xs text-slate-500">
        <p>&copy; {new Date().getFullYear()} Top Dog IDE. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default LandingPage;
