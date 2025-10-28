import React, { useState } from 'react';

type PluginState = 'idle' | 'installing' | 'updating' | 'error';

// Example plugin data (replace with real API later)
const examplePlugins = [
  {
    id: 'theme-darkplus',
    name: 'Dark+ Theme',
    description: 'A beautiful dark theme for Q-IDE.',
    installed: true,
    enabled: true,
    icon: '🌑',
    author: 'Q-IDE Team',
    version: '1.0.0',
  },
  {
    id: 'python-tools',
    name: 'Python Tools',
    description: 'Linting, formatting, and more for Python.',
    installed: false,
    enabled: false,
    icon: '🐍',
    author: 'Q-IDE Team',
    version: '0.9.2',
  },
  {
    id: 'git-integration',
    name: 'Git Integration',
    description: 'Seamless Git support inside Q-IDE.',
    installed: false,
    enabled: false,
    icon: '🔗',
    author: 'Q-IDE Team',
    version: '1.1.0',
  },
];


export default function PluginMarketplace({ onClose }: { onClose: () => void }) {
  const [settingsOpen, setSettingsOpen] = useState<string|null>(null);
  const [detailsOpen, setDetailsOpen] = useState<string|null>(null);
  const [tab, setTab] = useState<'marketplace' | 'installed'>('marketplace');
  const [search, setSearch] = useState('');
  const [plugins, setPlugins] = useState(examplePlugins.map(p => ({...p, state: 'idle'})));
  const [errorMsg, setErrorMsg] = useState<string|null>(null);

  const filtered = plugins.filter(p =>
    (tab === 'installed' ? p.installed : true) &&
    (p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.description.toLowerCase().includes(search.toLowerCase()))
  );

  const handleInstall = (id: string) => {
    setPlugins(ps => ps.map(p => p.id === id ? { ...p, state: 'installing' } : p));
    setTimeout(() => {
      // Simulate error for demo
      if (id === 'git-integration') {
        setPlugins(ps => ps.map(p => p.id === id ? { ...p, state: 'error' } : p));
        setErrorMsg('Failed to install Git Integration. Please try again.');
      } else {
        setPlugins(ps => ps.map(p => p.id === id ? { ...p, installed: true, enabled: true, state: 'idle' } : p));
      }
    }, 1200);
  };
  const handleUninstall = (id: string) => {
    setPlugins(ps => ps.map(p => p.id === id ? { ...p, installed: false, enabled: false, state: 'idle' } : p));
  };
  const handleToggleEnabled = (id: string) => {
    setPlugins(ps => ps.map(p => p.id === id ? { ...p, enabled: !p.enabled } : p));
  };
  const handleUpdate = (id: string) => {
    setPlugins(ps => ps.map(p => p.id === id ? { ...p, state: 'updating' } : p));
    setTimeout(() => {
      setPlugins(ps => ps.map(p => p.id === id ? { ...p, version: (parseFloat(p.version)+0.1).toFixed(1), state: 'idle' } : p));
    }, 1000);
  };
  const handleOpenSettings = (id: string) => setSettingsOpen(id);
  const handleOpenDetails = (id: string) => setDetailsOpen(id);
  const handleCloseModal = () => { setSettingsOpen(null); setDetailsOpen(null); setErrorMsg(null); };

  // Settings form state (simulate per-plugin settings)
  const [settings, setSettings] = useState<{[id: string]: {autoUpdate: boolean, config: string}}>({});
  const handleSettingsChange = (id: string, key: string, value: any) => {
    setSettings(s => ({...s, [id]: {...(s[id]||{autoUpdate:true,config:''}), [key]: value}}));
  };
  const handleSaveSettings = (id: string) => {
    setSettings(s => ({...s, [id]: {...(s[id]||{autoUpdate:true,config:''})}}));
    setSettingsOpen(null);
  };

  return (
    <div className="w-[440px] max-w-full h-full bg-[#22272e]/80 border-l border-cyan-900/40 flex flex-col animate-fade-in-right z-40 backdrop-blur-xl shadow-2xl panel-elevated" role="dialog" aria-modal="true" aria-label="Plugin Marketplace">
      <div className="flex items-center gap-2 p-4 border-b border-cyan-900/40 bg-gradient-to-r from-[#1e2128]/90 to-[#23272e]/80 shadow-md">
        <span className="text-cyan-300 font-extrabold text-2xl tracking-wide drop-shadow-lg">🧩 Marketplace</span>
        <button className="ml-auto px-3 py-1.5 rounded-lg bg-cyan-900/40 text-cyan-100 hover:bg-cyan-700/60 text-sm font-semibold shadow transition-all duration-150" onClick={onClose} aria-label="Close marketplace">✕</button>
      </div>
      <div className="flex gap-2 px-4 py-3 border-b border-cyan-900/30 bg-[#23272e]/80">
        <button onClick={() => setTab('marketplace')} className={`px-4 py-1.5 rounded-lg font-semibold shadow-sm transition-all duration-150 ${tab === 'marketplace' ? 'bg-cyan-700 text-white shadow-cyan-700/30' : 'bg-[#181a20]/80 text-cyan-200 hover:bg-cyan-800/30'}`}>Marketplace</button>
        <button onClick={() => setTab('installed')} className={`px-4 py-1.5 rounded-lg font-semibold shadow-sm transition-all duration-150 ${tab === 'installed' ? 'bg-cyan-700 text-white shadow-cyan-700/30' : 'bg-[#181a20]/80 text-cyan-200 hover:bg-cyan-800/30'}`}>Installed</button>
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search plugins..."
          className="ml-auto px-3 py-1.5 rounded-lg bg-[#181a20]/80 text-cyan-200 border border-cyan-900/30 focus:border-cyan-400 text-base w-48 shadow-inner outline-none"
          aria-label="Search plugins"
        />
      </div>
      {errorMsg && (
        <div className="bg-red-900/40 text-red-200 px-4 py-2 text-sm text-center">{errorMsg} <button className="ml-2 underline" onClick={()=>setErrorMsg(null)}>Dismiss</button></div>
      )}
  <div className="flex-1 overflow-y-auto p-3">
        {filtered.length === 0 ? (
          <div className="text-gray-400 text-sm text-center mt-8">No plugins found.</div>
        ) : (
          filtered.map(plugin => (
            <div key={plugin.id} className="flex items-center gap-6 p-5 mb-6 rounded-2xl bg-gradient-to-br from-[#23272e]/90 to-[#1e2128]/80 border border-cyan-900/40 shadow-lg relative group transition-all duration-200 hover:scale-[1.025] hover:shadow-2xl focus-within:ring-2 focus-within:ring-cyan-400" tabIndex={0} aria-label={`Plugin ${plugin.name}`}> 
              <span className="text-4xl mr-4 select-none cursor-pointer drop-shadow-lg" onClick={()=>handleOpenDetails(plugin.id)} title="View details" aria-label="View plugin details">{plugin.icon}</span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3 mb-2">
                  <span className="font-bold text-cyan-200 text-lg truncate cursor-pointer underline decoration-dotted hover:text-cyan-300 transition" title={plugin.name} onClick={()=>handleOpenDetails(plugin.id)}>{plugin.name}</span>
                  {plugin.installed && (
                    <span className={`ml-2 px-2 py-0.5 rounded-lg text-xs font-bold shadow ${plugin.enabled ? 'bg-cyan-800/80 text-cyan-100' : 'bg-gray-700/80 text-gray-300'}`}
                      title={plugin.enabled ? 'Enabled' : 'Disabled'}>
                      {plugin.enabled ? 'Enabled' : 'Disabled'}
                    </span>
                  )}
                  {plugin.state === 'installing' && <span className="ml-2 text-xs text-cyan-400 animate-pulse">Installing...</span>}
                  {plugin.state === 'updating' && <span className="ml-2 text-xs text-cyan-400 animate-pulse">Updating...</span>}
                  {plugin.state === 'error' && <span className="ml-2 text-xs text-red-400">Error</span>}
                </div>
                <div className="text-base text-gray-300 mb-1 truncate" title={plugin.description}>{plugin.description}</div>
                <div className="text-xs text-cyan-400">By {plugin.author} • v{plugin.version}</div>
              </div>
              {plugin.installed ? (
                <div className="flex flex-col gap-2 items-end min-w-[130px]">
                  <button className="px-3 py-1.5 rounded-lg bg-red-900/40 text-red-100 hover:bg-red-700/60 text-xs font-semibold mb-1 shadow transition-all duration-150" onClick={() => handleUninstall(plugin.id)} title="Uninstall this plugin" aria-label={`Uninstall ${plugin.name}`}>Uninstall</button>
                  <button className={`px-3 py-1.5 rounded-lg text-xs font-semibold mb-1 shadow transition-all duration-150 ${plugin.enabled ? 'bg-cyan-900/40 text-cyan-200 hover:bg-cyan-700/60' : 'bg-gray-700/60 text-gray-300 hover:bg-gray-600/80'}`} onClick={() => handleToggleEnabled(plugin.id)} title={plugin.enabled ? 'Disable plugin' : 'Enable plugin'} aria-label={plugin.enabled ? `Disable ${plugin.name}` : `Enable ${plugin.name}`}>{plugin.enabled ? 'Disable' : 'Enable'}</button>
                  <button className="px-3 py-1.5 rounded-lg bg-cyan-700 text-white hover:bg-cyan-600 text-xs font-semibold mb-1 shadow transition-all duration-150" onClick={() => handleUpdate(plugin.id)} title="Update plugin" aria-label={`Update ${plugin.name}`}>Update</button>
                  <button className="px-3 py-1.5 rounded-lg bg-gray-800/80 text-cyan-200 hover:bg-gray-700/80 text-xs font-semibold shadow transition-all duration-150" onClick={() => handleOpenSettings(plugin.id)} title="Plugin settings" aria-label={`Settings for ${plugin.name}`}>Settings</button>
                </div>
              ) : (
                <button className="px-3 py-1.5 rounded-lg bg-cyan-900/40 text-cyan-200 hover:bg-cyan-700/60 text-xs font-semibold min-w-[90px] shadow transition-all duration-150" onClick={() => handleInstall(plugin.id)} title="Install this plugin" aria-label={`Install ${plugin.name}`} disabled={plugin.state==='installing'}>{plugin.state==='installing' ? 'Installing...' : 'Install'}</button>
              )}

              {/* Settings Modal Overlay */}
              {settingsOpen === plugin.id && (
                <div className="fixed inset-0 z-50 flex items-center justify-center" style={{background:'rgba(24,28,40,0.75)'}}>
                  <div className="bg-[#23272e] rounded-2xl shadow-2xl p-8 min-w-[340px] max-w-[95vw] border-2 border-cyan-800 relative">
                    <div className="flex items-center justify-between mb-6">
                      <span className="text-cyan-300 font-bold text-xl">{plugin.name} Settings</span>
                      <button className="px-2 py-1 rounded bg-cyan-900/30 text-cyan-200 hover:bg-cyan-700/40 text-xs" onClick={handleCloseModal} aria-label="Close settings">✕</button>
                    </div>
                    <form onSubmit={e => {e.preventDefault(); handleSaveSettings(plugin.id);}}>
                      <div className="mb-4">
                        <label className="flex items-center gap-2 text-cyan-200 text-sm mb-2">
                          <input type="checkbox" checked={(settings[plugin.id]?.autoUpdate ?? true)} onChange={e => handleSettingsChange(plugin.id, 'autoUpdate', e.target.checked)} className="accent-cyan-600" />
                          Enable auto-update
                        </label>
                        <label className="block text-cyan-200 text-sm mb-1">Custom config:</label>
                        <input type="text" value={settings[plugin.id]?.config ?? ''} onChange={e => handleSettingsChange(plugin.id, 'config', e.target.value)} className="w-full rounded bg-[#181a20] border border-cyan-900/30 px-2 py-1 text-cyan-100" placeholder="e.g. --flag=value" />
                      </div>
                      <div className="flex gap-3 justify-end">
                        <button type="submit" className="px-4 py-1.5 rounded bg-cyan-700 text-white hover:bg-cyan-600 text-sm font-semibold">Save</button>
                        <button type="button" className="px-4 py-1.5 rounded bg-gray-800 text-cyan-200 hover:bg-gray-700 text-sm font-semibold" onClick={handleCloseModal}>Cancel</button>
                      </div>
                    </form>
                  </div>
                </div>
              )}

              {/* Details Modal Overlay */}
              {detailsOpen === plugin.id && (
                <div className="fixed inset-0 z-50 flex items-center justify-center" style={{background:'rgba(24,28,40,0.85)'}}>
                  <div className="bg-[#23272e] rounded-2xl shadow-2xl p-8 min-w-[340px] max-w-[95vw] border-2 border-cyan-800 relative">
                    <div className="flex items-center justify-between mb-6">
                      <span className="text-cyan-300 font-bold text-xl">{plugin.name} Details</span>
                      <button className="px-2 py-1 rounded bg-cyan-900/30 text-cyan-200 hover:bg-cyan-700/40 text-xs" onClick={handleCloseModal} aria-label="Close details">✕</button>
                    </div>
                    <div className="mb-4">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-4xl select-none">{plugin.icon}</span>
                        <div>
                          <div className="font-bold text-cyan-200 text-lg">{plugin.name}</div>
                          <div className="text-xs text-cyan-400">By {plugin.author}</div>
                        </div>
                      </div>
                      <div className="text-gray-300 mb-2">{plugin.description}</div>
                      <div className="text-xs text-cyan-400 mb-2">Version: {plugin.version}</div>
                      <div className="text-xs text-gray-400">Plugin ID: {plugin.id}</div>
                    </div>
                    <div className="flex gap-3 justify-end">
                      <button className="px-4 py-1.5 rounded bg-cyan-700 text-white hover:bg-cyan-600 text-sm font-semibold" onClick={handleCloseModal}>Close</button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
