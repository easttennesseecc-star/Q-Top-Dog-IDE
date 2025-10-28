import React, { useState } from 'react';
import useBackground, { BackgroundSetting, PARTICLE_PRESETS } from '../hooks/useBackground';
import BackgroundPreviewModal from './BackgroundPreviewModal';
import MediaManager from './MediaManager';
// JSZip is optional; require dynamically to avoid breaking environments without it
async function importJSZip() {
  try {
    const mod = await import('jszip');
    return (mod as any).default || mod;
  } catch (e) {
    return null;
  }
}
import { saveBlob, deleteBlob, listBlobIds } from '../lib/idbStorage';

const PRESETS: { key: BackgroundSetting['kind']; label: string }[] = [
  { key: 'gradient', label: 'Subtle Gradient' },
  { key: 'animated', label: 'Animated Gradient' },
  { key: 'particles', label: 'Particles / Floaters' },
  { key: 'image', label: 'Blurred Photo' },
];

export default function BackgroundSettings() {
  const [setting, setSetting] = useBackground();
  const [localImagePreview, setLocalImagePreview] = useState<string | null>(setting.imagePreviewUrl ?? null);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [mediaManagerOpen, setMediaManagerOpen] = useState(false);
  const [exportInProgress, setExportInProgress] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);
  const [importInProgress, setImportInProgress] = useState(false);
  const [pruneInProgress, setPruneInProgress] = useState(false);
  const [pruneProgress, setPruneProgress] = useState(0);

  function chooseKind(kind: BackgroundSetting['kind']) {
    const next: BackgroundSetting = { ...setting, kind };
    if (kind !== 'image') {
      next.imageBlobId = undefined;
      next.imagePreviewUrl = undefined;
    }
    if (kind !== 'video') {
      next.videoBlobId = undefined;
    }
    setSetting(next);
  }

  async function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    // guard large uploads (warn at 5 MB)
    const maxWarn = 5 * 1024 * 1024; // 5 MB
    if (f.size > maxWarn) {
      const ok = confirm(`The file is ${(f.size/1024/1024).toFixed(2)} MB which may be large for browser storage. Continue and attempt to store?`);
      if (!ok) return;
    }
    // If user picked a video
    if (f.type.startsWith('video/')) {
      // store video blob directly in IndexedDB
      const vidId = await saveBlob(f);
      // clear any previous image blob
      if (setting.videoBlobId && setting.videoBlobId !== vidId) await deleteBlob(setting.videoBlobId);
      setLocalImagePreview(null);
      setSetting({ ...setting, kind: 'video', videoBlobId: vidId, imagePreviewUrl: undefined });
      return;
    }

    // For images: compress to reasonable max dim and quality, then store blob in IndexedDB
    const img = document.createElement('img');
    const reader = new FileReader();
    reader.onload = () => {
      img.src = String(reader.result ?? '');
      img.onload = async () => {
        const maxDim = 1920; // max width/height for stored image
        let { width, height } = img;
        let scale = 1;
        if (width > maxDim || height > maxDim) scale = Math.min(maxDim / width, maxDim / height);
        const cw = Math.round(width * scale);
        const ch = Math.round(height * scale);
        const c = document.createElement('canvas');
        c.width = cw;
        c.height = ch;
        const ctx = c.getContext('2d');
        if (!ctx) {
          // fallback: store raw data URL in preview only
          setLocalImagePreview(img.src);
          setSetting({ ...setting, kind: 'image', imagePreviewUrl: img.src });
          return;
        }
        ctx.drawImage(img, 0, 0, cw, ch);
        const quality = 0.82; // reasonable quality
        c.toBlob(async (blob) => {
          if (!blob) {
            setLocalImagePreview(img.src);
            setSetting({ ...setting, kind: 'image', imagePreviewUrl: img.src });
            return;
          }
          const id = await saveBlob(blob);
          // delete previous stored blob if present
          if (setting.imageBlobId && setting.imageBlobId !== id) await deleteBlob(setting.imageBlobId);
          const objUrl = URL.createObjectURL(blob);
          setLocalImagePreview(objUrl);
          setSetting({ ...setting, kind: 'image', imageBlobId: id, imagePreviewUrl: objUrl, particleCount: setting.particleCount });
        }, 'image/jpeg', quality);
      };
    };
    reader.readAsDataURL(f);
  }

  // show current stored blob size for UI
  const [storedSize, setStoredSize] = useState<number>(0);
  React.useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const id = setting.imageBlobId ?? setting.videoBlobId;
        if (!id) { if (mounted) setStoredSize(0); return; }
        const idb = await import('../lib/idbStorage');
        const s = await idb.getBlobSize(id);
        if (mounted) setStoredSize(s);
      } catch (_) { if (mounted) setStoredSize(0); }
    })();
    return () => { mounted = false; };
  }, [setting.imageBlobId, setting.videoBlobId]);

  function exportSettings() {
    // Export metadata + blobs as a zip (if JSZip available), otherwise export metadata JSON
    (async () => {
      setExportInProgress(true);
      setExportProgress(0);
      const JSZip = await importJSZip();
      const payload = JSON.stringify(setting, null, 2);
      if (!JSZip) {
        const blob = new Blob([payload], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'topdog-background.json';
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
        setExportInProgress(false);
        setExportProgress(100);
        return;
      }
      const zip = new JSZip();
      zip.file('metadata.json', payload);
      // include blobs
      const blobIds: string[] = [];
      if (setting.imageBlobId) blobIds.push(setting.imageBlobId);
      if (setting.videoBlobId) blobIds.push(setting.videoBlobId);
      let added = 0;
      for (const id of blobIds) {
        try {
          const b = await (await import('../lib/idbStorage')).getBlob(id);
          if (b) zip.file(`blobs/${id}`, b);
        } catch (e) {
          console.warn('exportSettings: failed to include blob', id, e);
        }
        added++;
        setExportProgress(Math.round((added / Math.max(1, blobIds.length)) * 50));
      }
      const content = await zip.generateAsync({ type: 'blob' }, (meta: any) => {
        const pct = 50 + Math.round((meta.percent || 0) / 2);
        setExportProgress(pct);
      });
      const url = URL.createObjectURL(content);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'topdog-background.zip';
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      setExportInProgress(false);
      setExportProgress(100);
    })();
  }

  function importSettings(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    (async () => {
      setImportInProgress(true);
      setExportProgress(0);
      const JSZip = await importJSZip();
      if (f.name.endsWith('.zip') && JSZip) {
        try {
          const data = await f.arrayBuffer();
          const zip = await JSZip.loadAsync(data);
          const meta = await zip.file('metadata.json')?.async('string');
          if (!meta) { alert('Invalid zip - missing metadata.json'); setImportInProgress(false); return; }
          const j = JSON.parse(meta);
          // if there are blobs, store and replace the ids
          const idb = await import('../lib/idbStorage');
          const blobIds: string[] = [];
          if (j.imageBlobId && zip.file(`blobs/${j.imageBlobId}`)) blobIds.push(j.imageBlobId);
          if (j.videoBlobId && zip.file(`blobs/${j.videoBlobId}`)) blobIds.push(j.videoBlobId);
          let processed = 0;
          for (const bid of blobIds) {
            const b = await zip.file(`blobs/${bid}`)!.async('blob');
            const newId = await idb.saveBlob(b);
            if (j.imageBlobId === bid) j.imageBlobId = newId;
            if (j.videoBlobId === bid) j.videoBlobId = newId;
            processed++;
            setImportInProgress(true);
            setExportProgress(Math.round((processed / blobIds.length) * 90));
          }
          setSetting(j);
        } catch (err) { console.error(err); alert('Failed to import zip'); }
        setImportInProgress(false);
        setExportProgress(100);
        return;
      }
      // fallback: try plain JSON
      const r = new FileReader();
      r.onload = () => {
        try {
          const j = JSON.parse(String(r.result));
          setSetting(j);
        } catch (err) {
          alert('Invalid settings file');
        }
        setImportInProgress(false);
        setExportProgress(100);
      };
      r.readAsText(f);
    })();
  }

  async function pruneUnusedBlobs() {
    setPruneInProgress(true);
    setPruneProgress(0);
    try {
      const all = await listBlobIds();
      const used = new Set<string>();
      if (setting.imageBlobId) used.add(setting.imageBlobId);
      if (setting.videoBlobId) used.add(setting.videoBlobId);
      const unused = all.filter(id => !used.has(id));
      for (let i = 0; i < unused.length; i++) {
        await deleteBlob(unused[i]);
        setPruneProgress(Math.round(((i + 1) / Math.max(1, unused.length)) * 100));
      }
      alert(`Pruned ${unused.length} blobs.`);
    } catch (e) {
      console.error(e);
      alert('Prune failed');
    }
    setPruneInProgress(false);
    setPruneProgress(100);
  }

  function resetToDefault() {
    setSetting({ kind: 'gradient', particleCount: 12 });
    setLocalImagePreview(null);
    window.dispatchEvent(new Event('topdog:background'));
  }

  return (
    <div className="space-y-4">
      <div className="bg-black/10 border border-white/5 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-cyan-200 mb-2">Background Presets</h4>
        <div className="flex gap-2 flex-wrap">
          {PRESETS.map(p => (
            <button
              key={p.key}
              className={`tab-button ${setting.kind === p.key ? 'active' : ''}`}
              onClick={() => chooseKind(p.key as any)}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

        {setting.kind === 'particles' && (
        <div className="bg-black/10 border border-white/5 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-cyan-200 mb-2">Particles</h4>
            <label className="text-xs text-slate-300/80">Particle density</label>
            <input
              aria-label="Particle density"
              type="range"
              min={6}
              max={300}
              value={setting.particleCount ?? 12}
              onChange={(e) => { setSetting({ ...setting, particleCount: Number(e.target.value) }); window.dispatchEvent(new Event('topdog:background')); }}
            />
            <div className="mt-2 flex gap-2" role="radiogroup" aria-label="Particle performance presets">
              <button
                className={`btn-secondary ${setting.particleCount === PARTICLE_PRESETS.low.count ? 'active' : ''}`}
                onClick={() => { setSetting({ ...setting, particleCount: PARTICLE_PRESETS.low.count }); window.dispatchEvent(new Event('topdog:background')); }}
                aria-pressed={setting.particleCount === PARTICLE_PRESETS.low.count}
              >{PARTICLE_PRESETS.low.label}</button>
              <button
                className={`btn-secondary ${setting.particleCount === PARTICLE_PRESETS.medium.count ? 'active' : ''}`}
                onClick={() => { setSetting({ ...setting, particleCount: PARTICLE_PRESETS.medium.count }); window.dispatchEvent(new Event('topdog:background')); }}
                aria-pressed={setting.particleCount === PARTICLE_PRESETS.medium.count}
              >{PARTICLE_PRESETS.medium.label}</button>
              <button
                className={`btn-secondary ${setting.particleCount === PARTICLE_PRESETS.high.count ? 'active' : ''}`}
                onClick={() => { setSetting({ ...setting, particleCount: PARTICLE_PRESETS.high.count }); window.dispatchEvent(new Event('topdog:background')); }}
                aria-pressed={setting.particleCount === PARTICLE_PRESETS.high.count}
              >{PARTICLE_PRESETS.high.label}</button>
            </div>
          <div className="text-xs text-slate-300/70 mt-1">Lower values = better perf on low-end machines.</div>
        </div>
      )}

      {(setting.kind === 'image' || setting.kind === 'video') && (
        <div className="bg-black/10 border border-white/5 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-cyan-200 mb-2">Upload Photo</h4>
          <input onChange={onFile} type="file" accept="image/*,video/*" />
          {localImagePreview && (
            <div className="mt-3 rounded overflow-hidden border border-white/5 w-40 h-24">
              <img src={localImagePreview} alt="preview" style={{ width: '100%', height: '100%', objectFit: 'cover', filter: 'brightness(.8) saturate(.92) blur(.6px)' }} />
            </div>
          )}
          {storedSize > 0 && (
            <div className="mt-2 text-xs text-slate-300/70">Stored blob size: {(storedSize/1024/1024).toFixed(2)} MB</div>
          )}
          <div className="mt-2 text-xs text-slate-300/70">Uploaded images or videos are stored locally in your browser (IndexedDB). Videos autoplay muted.</div>
        </div>
      )}
      <div className="flex gap-2">
        <button onClick={() => setPreviewOpen(true)} className="btn-secondary">Preview Presets</button>
        <button onClick={() => setMediaManagerOpen(true)} className="btn-secondary">Manage Media</button>
        <button onClick={() => { setSetting({ ...setting, lowPowerMode: !setting.lowPowerMode }); }} className={`btn-secondary ${setting.lowPowerMode ? 'active' : ''}`}>Low power: {setting.lowPowerMode ? 'On' : 'Off'}</button>
        <button onClick={exportSettings} className="btn-secondary">Export</button>
  {exportInProgress && <div className="text-xs text-slate-300 ml-2" role="status" aria-live="polite">Exporting... {exportProgress}%</div>}
        <label className="btn-secondary cursor-pointer">
          Import
          <input onChange={importSettings} type="file" accept="application/json,.zip" className="hidden" />
        </label>
  {importInProgress && <div className="text-xs text-slate-300 ml-2" role="status" aria-live="polite">Importing... {exportProgress}%</div>}
        <button onClick={pruneUnusedBlobs} className="btn-secondary">Prune unused blobs</button>
  {pruneInProgress && <div className="text-xs text-slate-300 ml-2" role="status" aria-live="polite">Pruning... {pruneProgress}%</div>}
        <button onClick={resetToDefault} className="btn-primary">Reset to default</button>
      </div>

      <BackgroundPreviewModal open={previewOpen} onClose={() => setPreviewOpen(false)} />
    </div>
  );
}
