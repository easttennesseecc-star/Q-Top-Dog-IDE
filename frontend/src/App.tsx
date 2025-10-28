import { useEffect, useState, useRef, type ReactNode } from "react";
import "./App.css";
import { Toast } from "./components/Toast";
import { UserProfileMenu } from "./components/UserProfileMenu";
import QAssistantChat from "./components/QAssistantChat";
import BuildQueue from "./components/BuildQueue";
import { CommandPalette } from "./components/CommandPalette";
import IntegrationsPanel from "./components/IntegrationsPanel";
import BuildHealthIndicator from "./components/BuildHealthIndicator";
import LLMPoolPanel from "./components/LLMPoolPanel";
import LLMConfigPanel from "./components/LLMConfigPanel";
import LLMStartupAuth from "./components/LLMStartupAuth";
import PhoneLinkPanel from "./components/PhoneLinkPanel";
import BackgroundManager from "./components/BackgroundManager";
import { schedulePrune } from './lib/idbStorage';
// HMR ping - no-op comment to trigger live reloads when needed
import React from 'react';
const BackgroundSettings = React.lazy(() => import('./components/BackgroundSettings'));
const OAuthCallback = React.lazy(() => import('./components/OAuthCallback'));

type SelectedTab = "viewer" | "builds" | "extensions" | "settings" | "learning" | "llm" | "config" | "phone";

function App() {
  // Check if we're on the OAuth callback page
  const isOAuthCallback = window.location.pathname === '/oauth/callback';

  if (isOAuthCallback) {
    return (
      <React.Suspense fallback={<div className="min-h-screen bg-[#1a1f26] flex items-center justify-center text-cyan-200">Loading...</div>}>
        <OAuthCallback />
      </React.Suspense>
    );
  }

  const [tab, setTab] = useState<SelectedTab>("viewer");
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);
  const [showStartupAuthPrompt, setShowStartupAuthPrompt] = useState(true);
  const [isMicActive, setIsMicActive] = useState(false);
  const micRef = useRef<HTMLButtonElement>(null);
  const [builds, setBuilds] = useState<Array<{ id: string; status: string; log?: string }>>([]);
  const [logsMap, setLogsMap] = useState<Record<string, string[]>>({});

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Windows-standard Command Palette: Ctrl+Shift+P
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === "P" || e.key === "p")) {
        e.preventDefault();
        setCommandPaletteOpen((v) => !v);
        return;
      }
      // Mic toggle: Ctrl+M
      if ((e.ctrlKey || e.metaKey) && (e.key === "M" || e.key === "m")) {
        e.preventDefault();
        toggleMic();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isMicActive]);

  // Start maintenance tasks (prune orphaned blobs immediately and daily)
  useEffect(() => {
    const cancel = schedulePrune();
    return () => { try { cancel(); } catch (_) {} };
  }, []);

  // Load builds when Builds tab is selected (no mock data; pull from backend)
  useEffect(() => {
    if (tab !== "builds") return;
    let canceled = false;
    const load = async () => {
      try {
        const res = await fetch("/llm/learning/builds");
        const j = await res.json();
        if (canceled) return;
        const bs = (j?.builds ?? []) as Array<{ id: string; status: string; log?: string }>;
        setBuilds(bs);
        const map: Record<string, string[]> = {};
        for (const b of bs) map[b.id] = (b.log ?? "").split("\n");
        setLogsMap(map);
      } catch (_) {
        // keep previous state; optionally surface toast
      }
    };
    load();
    const t = setInterval(load, 2500);
    return () => { canceled = true; clearInterval(t); };
  }, [tab]);

  const toggleMic = () => {
    setIsMicActive(!isMicActive);
    setToast({
      message: isMicActive ? "Mic disabled" : "Mic listening...",
      type: "success",
    });
  };

  // Right rail button base (SVG icons only — no emoji)
  const railBtn = (active: boolean) => `w-10 h-10 rounded-md border ${active ? 'border-cyan-400/60 bg-cyan-500/10 text-cyan-200' : 'border-cyan-400/20 text-cyan-400/70 hover:text-cyan-200 hover:border-cyan-400/40'} grid place-items-center transition-colors`

  // Inline SVG icons (stroke-current, 1.6px)
  const Icon = {
    Builds: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
        <path d="M7 7h10v10H7z" />
        <path d="M3 3h4v4H3zM17 17h4v4h-4z" />
        <path d="M7 7l-3-3M20 20l-3-3" />
      </svg>
    ),
    Extensions: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
        <path d="M14 3h5v5h-5zM5 14h5v5H5z" />
        <path d="M9 5H5v4M19 15v4h-4" />
        <path d="M9 9l6 6" />
      </svg>
    ),
    Settings: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
        <circle cx="12" cy="12" r="3" />
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06-1.43 2.48- .08.02A8 8 0 0 1 12 20a8 8 0 0 1-6.28-3.12l-.08-.02L4.2 14.9l.06-.06A1.65 1.65 0 0 0 4.6 13H3v-2h1.6a1.65 1.65 0 0 0 .33-1.82l-.06-.06 1.43-2.48.08-.02A8 8 0 0 1 12 4c2.6 0 4.94 1.24 6.28 3.12l.08.02L19.8 9.1l-.06.06A1.65 1.65 0 0 0 19.4 11H21v2h-1.6z" />
      </svg>
    ),
    LLM: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
        <rect x="4" y="6" width="16" height="12" rx="2" />
        <path d="M8 10h8M8 14h5" />
      </svg>
    ),
    Learning: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
        <path d="M22 10L12 5 2 10l10 5 10-5z" />
        <path d="M6 12v5l6 3 6-3v-5" />
      </svg>
    ),
    Phone: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
        <rect x="7" y="2" width="10" height="20" rx="2" />
        <path d="M11 19h2" />
      </svg>
    ),
    Mic: (active: boolean) => (
      <svg width="18" height="18" viewBox="0 0 24 24" fill={active ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
        <rect x="9" y="3" width="6" height="11" rx="3" />
        <path d="M5 12a7 7 0 0 0 14 0M12 19v2" />
      </svg>
    ),
  } as const;

  return (
    <div className="w-full h-screen bg-[#0b0f16] text-slate-100 overflow-hidden dark flex flex-col">
  {/* Background manager (gradient / animated / image / particles) */}
  <BackgroundManager />

      <div className="relative w-full h-full flex flex-col z-10">
        {/* Header */}
        <div className="h-14 border-b border-white/5 bg-[#0b0f16]/90 backdrop-blur-xl flex items-center justify-between px-6 sticky top-0 z-20">
          <div className="flex items-center gap-2 select-none">
            <div className="header-glass flex items-center gap-3">
              <div className="text-xl font-extrabold tracking-tight text-cyan-300">Top Dog</div>
              <div className="text-[10px] text-cyan-400/60 font-mono px-2 py-0.5 rounded">v0.1.0</div>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <BuildHealthIndicator />
            <button
              ref={micRef}
              onClick={toggleMic}
              className={`w-9 h-9 grid place-items-center rounded-full transition-colors ${
                isMicActive
                  ? "bg-cyan-500/20 border border-cyan-400/60 text-cyan-200 mic-glow"
                  : "hover:bg-cyan-500/10 border border-cyan-400/30 text-cyan-300"
              }`}
              title="Mic - Click or Ctrl+M"
              aria-pressed={isMicActive}
            >
              {Icon.Mic(isMicActive)}
            </button>
            <button
              onClick={() => setCommandPaletteOpen(true)}
              className="px-3 py-1.5 text-xs border border-cyan-400/30 hover:border-cyan-400 text-cyan-400 hover:text-cyan-300 rounded-lg transition-all font-mono"
              title="Press Ctrl+Shift+P"
            >
              Ctrl+Shift+P
            </button>
            <UserProfileMenu />
          </div>
        </div>

        {/* Single tall panel: left = Q Assistant, right = viewer with tabs */}
        <div className="flex-1 overflow-hidden relative">
          <div className="w-full h-full grid grid-cols-1 md:grid-cols-2 gap-0">
            {/* Left: Q Assistant (chat only) */}
            <div className="h-full border-r border-white/5 p-4">
              <div className="h-full panel-elevated glass">
                <QAssistantChat activePanel={null} setActivePanel={() => {}} showViewer={false} />
              </div>
            </div>
            {/* Right: Viewer with tabs */}
            <div className="h-full flex flex-col panel-elevated glass overflow-hidden">
              <div className="h-10 flex items-stretch gap-1 border-b border-white/5 px-2">
                {([
                  { key: 'viewer', label: 'Viewer', icon: null },
                  { key: 'builds', label: 'Builds', icon: Icon.Builds },
                  { key: 'llm', label: 'LLM Pool', icon: Icon.LLM },
                  { key: 'config', label: 'LLM Setup', icon: Icon.Settings },
                  { key: 'extensions', label: 'Extensions', icon: Icon.Extensions },
                  { key: 'phone', label: 'Phone', icon: Icon.Phone },
                  { key: 'settings', label: 'Settings', icon: Icon.Settings },
                  { key: 'learning', label: 'Learning', icon: Icon.Learning },
                ] as Array<{key: SelectedTab; label: string; icon: ReactNode }>).map(t => (
                  <button key={t.key} onClick={()=>setTab(t.key)} className={`tab-button inline-flex items-center gap-2 text-xs ${tab===t.key ? 'active' : ''}`}>
                    {t.icon}
                    <span>{t.label}</span>
                  </button>
                ))}
              </div>
              <div className="flex-1 overflow-auto p-3">
                {tab === 'viewer' && (
                  <div className="h-full w-full rounded-lg border border-white/10 bg-white/5 grid place-items-center text-slate-300/80 text-sm select-none">
                    Nothing selected. Choose a tab to view tools here.
                  </div>
                )}
                {tab === 'builds' && (
                  <div className="h-full w-full">
                    <div className="mb-2 text-sm text-cyan-200 font-semibold">Build Queue</div>
                    <div className="bg-black/20 border border-white/5 rounded-lg p-3">
                      <BuildQueue builds={builds} logsMap={logsMap} onClose={() => setTab('viewer')} />
                    </div>
                  </div>
                )}
                {tab === 'extensions' && (
                  <div className="h-full w-full">
                    <IntegrationsPanel onClose={() => setTab('viewer')} />
                  </div>
                )}
                {tab === 'llm' && (
                  <div className="h-full w-full">
                    <div className="mb-2 text-sm text-cyan-200 font-semibold">LLM Pool (Local First)</div>
                    <LLMPoolPanel />
                  </div>
                )}
                {tab === 'config' && (
                  <div className="h-full w-full overflow-auto">
                    <div className="mb-2 text-sm text-cyan-200 font-semibold">LLM Configuration</div>
                    <LLMConfigPanel />
                  </div>
                )}
                {tab === 'phone' && (
                  <div className="h-full w-full">
                    <PhoneLinkPanel onClose={() => setTab('viewer')} />
                    <div className="mt-3 text-xs text-slate-300/70">
                      Open on your phone: <code>/phone-link.html</code>. Paste the offer, create the answer, then paste it back here.
                    </div>
                  </div>
                )}
                {tab === 'settings' && (
                  <div className="h-full w-full">
                    <div className="space-y-4">
                      <div className="bg-black/20 border border-white/5 rounded-lg p-4">
                        <h3 className="font-semibold text-cyan-200 mb-2">Appearance</h3>
                        <div className="text-sm text-slate-300/80">Theme: TopDog</div>
                      </div>
                      <div className="bg-black/20 border border-white/5 rounded-lg p-4">
                        <h3 className="font-semibold text-cyan-200 mb-2">Background</h3>
                        <div className="text-sm text-slate-300/80">
                          <div className="mb-2">Choose a background preset or upload a blurred photo.</div>
                          <div>
                            {/* Lazy-load the settings control */}
                            <React.Suspense fallback={<div className="text-sm text-slate-400">Loading background controls…</div>}>
                              <BackgroundSettings />
                            </React.Suspense>
                          </div>
                        </div>
                      </div>
                      <div className="bg-black/20 border border-white/5 rounded-lg p-4">
                        <h3 className="font-semibold text-cyan-200 mb-2">Backend</h3>
                        <p className="text-sm text-green-300/90">Connected</p>
                      </div>
                    </div>
                  </div>
                )}
                {tab === 'learning' && (
                  <div className="h-full w-full">
                    <h2 className="text-sm font-semibold text-cyan-200 mb-2">Learning Model</h2>
                    <p className="text-sm text-slate-300/80">Single learning model is not built yet. This panel will become active once it exists and will only be used for learning.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {commandPaletteOpen && (
        <CommandPalette
          open={commandPaletteOpen}
          onClose={() => setCommandPaletteOpen(false)}
          commands={[
            { label: "Viewer", action: () => { setTab('viewer'); setCommandPaletteOpen(false); } },
            { label: "Builds", action: () => { setTab('builds'); setCommandPaletteOpen(false); } },
            { label: "Extensions", action: () => { setTab('extensions'); setCommandPaletteOpen(false); } },
            { label: "Settings", action: () => { setTab('settings'); setCommandPaletteOpen(false); } },
            { label: "LLM Pool", action: () => { setTab('llm'); setCommandPaletteOpen(false); } },
            { label: "LLM Setup", action: () => { setTab('config'); setCommandPaletteOpen(false); } },
            { label: "Phone Link", action: () => { setTab('phone'); setCommandPaletteOpen(false); } },
            { label: "Learning Model", action: () => { setTab('learning'); setCommandPaletteOpen(false); } },
            { label: "Toggle Mic (Ctrl+M)", action: () => { toggleMic(); setCommandPaletteOpen(false); } },
          ]}
        />
      )}

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      {showStartupAuthPrompt && (
        <LLMStartupAuth
          onClose={() => setShowStartupAuthPrompt(false)}
          onAction={(action, result) => {
            if (action === 'add_credentials') {
              setTab('config');
            } else if (action === 'use_alternatives') {
              setToast({
                message: 'Check LLM Setup tab to assign available LLMs',
                type: 'success'
              });
            }
          }}
        />
      )}
    </div>
  );
}

export default App;
