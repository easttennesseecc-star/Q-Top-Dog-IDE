import React, { useEffect, useState } from 'react';
import { listBlobIds, getBlob, getBlobSize, deleteBlob } from '../lib/idbStorage';

export default function MediaManager({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [items, setItems] = useState<string[]>([]);
  useEffect(() => {
    if (!open) return;
    let mounted = true;
    (async () => {
      const ids = await listBlobIds();
      if (!mounted) return;
      setItems(ids);
    })();
    return () => { mounted = false; };
  }, [open]);

  if (!open) return null;
  // focus trap + aria
  const modalRef = React.useRef<HTMLDivElement | null>(null);
  React.useEffect(() => {
    if (!open) return;
    const prev = document.activeElement as HTMLElement | null;
    const el = modalRef.current;
    const focusable = el?.querySelectorAll<HTMLElement>('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])') ?? [];
    focusable?.[0]?.focus();
    function onKey(e: KeyboardEvent) { if (e.key === 'Escape') onClose(); }
    document.addEventListener('keydown', onKey);
    return () => { document.removeEventListener('keydown', onKey); prev?.focus(); };
  }, [open, onClose]);

  return (
    <div className="fixed inset-0 z-60 grid place-items-center" role="dialog" aria-modal="true" aria-labelledby="media-manager-title">
      <div className="absolute inset-0 bg-black/60" onClick={onClose} />
      <div ref={modalRef} className="relative w-[780px] max-w-[94%] bg-[#071021]/80 border border-white/6 rounded-lg p-4 glass panel-elevated">
        <div className="flex items-center justify-between mb-3">
          <h3 id="media-manager-title" className="text-lg font-semibold text-cyan-200">Stored Media</h3>
          <button onClick={onClose} aria-label="Close media manager" className="btn-secondary">Close</button>
        </div>
        <div className="space-y-3 max-h-[60vh] overflow-auto">
          {items.length === 0 && <div className="text-sm text-slate-300/70">No stored media found.</div>}
          {items.map(id => (
            <MediaRow key={id} id={id} onDelete={() => setItems(items.filter(x => x !== id))} />
          ))}
        </div>
      </div>
    </div>
  );
}

function MediaRow({ id, onDelete }: { id: string; onDelete: () => void }) {
  const [preview, setPreview] = useState<string | null>(null);
  const [size, setSize] = useState<number>(0);
  useEffect(() => {
    let mounted = true;
    (async () => {
      const b = await getBlob(id);
      if (!mounted) return;
      if (b) setPreview(URL.createObjectURL(b));
      const s = await getBlobSize(id);
      if (!mounted) return;
      setSize(s);
    })();
    return () => { mounted = false; if (preview) URL.revokeObjectURL(preview); };
  }, [id]);

  async function handleDelete() {
    if (!confirm('Delete this stored media? This cannot be undone.')) return;
    await deleteBlob(id);
    onDelete();
  }

  return (
    <div className="flex items-center gap-3 p-2 bg-black/5 rounded">
      <div className="w-28 h-16 bg-slate-900 rounded overflow-hidden">
        {preview && <img src={preview} alt="media" className="w-full h-full object-cover" />}
      </div>
      <div className="flex-1 text-sm text-slate-200">
        <div>ID: <code className="text-xs">{id}</code></div>
        <div className="text-xs text-slate-400">Size: {(size/1024).toFixed(1)} KB</div>
      </div>
      <div>
        <button onClick={handleDelete} className="btn-danger">Delete</button>
      </div>
    </div>
  );
}
