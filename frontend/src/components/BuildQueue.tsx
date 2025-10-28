import React, { useState } from 'react'
import ConfirmModal from './ConfirmModal'
import LogPanel from './LogPanel'

type Build = { id: string; status: string; log?: string }

export default function BuildQueue({ builds, logsMap, onClose, onSelect, onCancel, onCopy }: { builds: Build[]; logsMap: Record<string, string[]>; onClose: () => void; onSelect?: (id: string) => void; onCancel?: (id: string) => void; onCopy?: (id: string) => void }) {
  const [confirming, setConfirming] = useState<string | null>(null)

  const handleCancel = async (id: string) => {
    // Allow parent to handle cancel if provided; otherwise call backend cancel endpoint
    if (onCancel) return onCancel(id)
    try {
      await fetch(`/build/${id}/cancel`, { method: 'POST' })
    } catch (e) {
      // best-effort; UI may show error elsewhere
      console.error('cancel build failed', e)
    }
  }

  const handleCopyId = (id: string) => {
    const text = id
    if (navigator?.clipboard?.writeText) {
      navigator.clipboard.writeText(text).then(() => onCopy && onCopy(id)).catch(() => { if (onCopy) onCopy(id) })
    } else {
      // fallback for older envs / tests
      try {
        const ta = document.createElement('textarea')
        ta.value = text
        ta.style.position = 'fixed'
        ta.style.left = '-9999px'
        document.body.appendChild(ta)
        ta.select()
        document.execCommand('copy')
        document.body.removeChild(ta)
        if (onCopy) onCopy(id)
      } catch (e) {
        // ignore
      }
    }
  }

  return (
    <div className="build-panel panel-elevated glass">
      <div className="flex items-center justify-between mb-3">
        <div className="text-lg font-semibold">Build Queue</div>
        <div>
          <button aria-label="close-build-panel" className="px-3 py-1 rounded-md bg-gray-700 text-white" onClick={onClose}>Close</button>
        </div>
      </div>
      <div>
        {builds.length === 0 && <div className="text-sm text-cyan-200">No builds queued</div>}
        {builds.map(b => (
          <div key={b.id} className="mb-3 border-b border-cyan-900/20 pb-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <button onClick={() => onSelect && onSelect(b.id)} className="font-bold text-sm text-left" aria-label={`select-build-${b.id}`}>
                  Build {b.id.slice(0,6)}
                </button>
                <button aria-label={`copy-buildid-${b.id}`} title="Copy build id" className="tab-button text-xs px-2 py-1 rounded-md bg-[#1b2228] text-cyan-200" onClick={() => handleCopyId(b.id)}>Copy</button>
                <button aria-label={`cancel-build-${b.id}`} title="Cancel build" className="tab-button text-xs px-2 py-1 rounded-md bg-red-800 text-red-100" onClick={() => setConfirming(b.id)}>Cancel</button>
              </div>
              <div className="text-xs text-cyan-200/80">{b.status}</div>
            </div>
            <div className="mt-2">
              <LogPanel lines={logsMap[b.id] ?? (b.log ? b.log.split('\n') : [])} />
            </div>
          </div>
        ))}
        {/* Confirmation modal */}
        {confirming && (
          <ConfirmModal
            title="Confirm cancel"
            message="Are you sure you want to cancel this build?"
            confirmLabel="Yes, cancel"
            cancelLabel="No"
            onCancel={() => setConfirming(null)}
            onConfirm={() => { const id = confirming; setConfirming(null); handleCancel(id!) }}
            confirmAriaLabel={`confirm-cancel-${confirming}`}
          />
        )}
      </div>
    </div>
  )
}
