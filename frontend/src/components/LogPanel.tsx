import React, { useEffect, useRef } from 'react'

export default function LogPanel({ lines }: { lines: string[] }) {
  const bottomRef = useRef<HTMLDivElement | null>(null)
  useEffect(() => {
    // Auto-scroll to bottom when lines change
    try {
      const el = bottomRef.current as any
      if (el && typeof el.scrollIntoView === 'function') {
        el.scrollIntoView({ behavior: 'smooth', block: 'end' })
      }
    } catch (e) {
      // jsdom may not implement scrollIntoView — ignore in tests
    }
  }, [lines])

  return (
    <div aria-live="polite" className="w-full max-h-40 overflow-auto bg-gradient-to-b from-[#071826] to-[#03121a] p-3 rounded text-xs text-gray-200 log-mono">
      {lines.length === 0 && <div className="text-cyan-200/70">No logs yet</div>}
      {lines.map((l, i) => (
        <div key={i} className="whitespace-pre-wrap" data-testid={`log-line-${i}`}>
          {l}
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
