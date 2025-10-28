import React from 'react'

export default function ConfirmModal({
  title,
  message,
  confirmLabel = 'Yes',
  cancelLabel = 'No',
  onConfirm,
  onCancel,
  confirmAriaLabel,
}: {
  title?: string
  message: string
  confirmLabel?: string
  cancelLabel?: string
  onConfirm: () => void
  onCancel: () => void
  confirmAriaLabel?: string
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: 'rgba(0,0,0,0.55)' }} role="dialog" aria-modal="true">
      <div className="bg-[#23272e] rounded-2xl shadow-2xl p-6 min-w-[320px] max-w-[95vw] border-2 border-cyan-800">
        {title && <div className="text-lg font-bold mb-3">{title}</div>}
        <div className="text-sm text-cyan-200 mb-4">{message}</div>
        <div className="flex justify-end gap-3">
          <button aria-label="decline-confirm" className="px-4 py-1.5 rounded bg-gray-800 text-cyan-200" onClick={onCancel}>{cancelLabel}</button>
          <button aria-label={confirmAriaLabel ?? 'confirm'} className="px-4 py-1.5 rounded bg-red-700 text-white" onClick={onConfirm}>{confirmLabel}</button>
        </div>
      </div>
    </div>
  )
}
