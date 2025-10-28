import { useEffect } from 'react'

export type BuildInfo = { id: string; status: string; log?: string }

// Polls /build/{bid} every second and calls onUpdate with the returned build object.
// Optionally calls onChunk with incremental log diffs (new text appended since last poll).
// Stops polling when status is not 'running' or 'queued'.
export function useBuildPoll(
  bid: string | null,
  onUpdate: (b: BuildInfo) => void,
  onChunk?: (chunk: string, build?: BuildInfo) => void,
) {
  useEffect(() => {
    if (!bid) return
    let cancelled = false
    let lastLog: string | null = null
    const poll = async () => {
      try {
        const res = await fetch(`/build/${bid}`)
        if (!res.ok) return
        const j = await res.json()
        if (j?.build) {
          const build: BuildInfo = j.build
          // detect incremental log chunks and call onChunk if provided
          const newLog = build.log || ''
          if (onChunk) {
            if (lastLog === null && newLog) {
              // first time seeing a log: send entire content as first chunk
              onChunk(newLog, build)
            } else if (lastLog !== null && newLog.startsWith(lastLog) && newLog.length > lastLog.length) {
              const diff = newLog.slice(lastLog.length)
              onChunk(diff, build)
            } else if (lastLog !== null && newLog !== lastLog) {
              // non-prefix change — send full newLog
              onChunk(newLog, build)
            }
          }
          lastLog = newLog
          onUpdate(build)
          const s = j.build.status
          if (s && s !== 'running' && s !== 'queued') {
            // finished — nothing more to do
            return
          }
        }
      } catch (e) {
        // swallow errors; upstream can decide to stop polling by clearing bid
      }
    }

    // Start interval
    const id = setInterval(() => {
      if (cancelled) return
      void poll()
    }, 1000)

    // Run one immediate poll quickly so UI updates faster
    void poll()

    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [bid, onUpdate])
}
