import { useEffect, useState } from 'react'

type Build = { id: string; status: string; log?: string }

export default function BuildHealthIndicator() {
	const [status, setStatus] = useState<'ok'|'warn'|'error'|'idle'>('idle')
	const [lastId, setLastId] = useState<string | null>(null)

	useEffect(() => {
		let stopped = false
		async function load() {
			try {
				const res = await fetch('/llm/learning/builds')
				const j = await res.json()
				if (stopped) return
				const builds: Build[] = j?.builds ?? []
				if (builds.length === 0) { setStatus('idle'); setLastId(null); return }
				const mostRecent = builds[0]
				setLastId(mostRecent.id)
				if (mostRecent.status === 'success') setStatus('ok')
				else if (mostRecent.status === 'queued' || mostRecent.status === 'running') setStatus('warn')
				else setStatus('error')
			} catch {
				if (!stopped) setStatus('warn')
			}
		}
		load()
		const t = setInterval(load, 3000)
		return () => { stopped = true; clearInterval(t) }
	}, [])

	const color = status === 'ok' ? 'bg-emerald-500/80 shadow-emerald-400/40'
		: status === 'warn' ? 'bg-amber-500/80 shadow-amber-400/40'
		: status === 'error' ? 'bg-rose-600/80 shadow-rose-400/40'
		: 'bg-slate-500/60 shadow-slate-400/20'

	const label = status === 'ok' ? 'Healthy'
		: status === 'warn' ? 'Building…'
		: status === 'error' ? 'Issues'
		: 'Idle'

	return (
		<div className="flex items-center gap-2 select-none" title={lastId ? `Last build ${lastId.slice(0,8)}` : 'No builds yet'}>
			<div className={`w-2.5 h-2.5 rounded-full shadow-[0_0_14px] ${color}`} />
			<span className="text-xs font-mono text-cyan-300/80">{label}</span>
		</div>
	)
}

