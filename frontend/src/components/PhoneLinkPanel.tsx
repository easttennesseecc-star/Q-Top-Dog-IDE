import React, { useEffect, useRef, useState } from 'react'

// Minimal, serverless WebRTC pairing: copy/paste SDP between desktop and phone.
// 1) Desktop: Create Offer -> copy SDP
// 2) Phone (phone-link.html): Paste Offer -> Create Answer -> copy SDP back
// 3) Desktop: Paste Answer -> Connect. Audio from phone plays locally.

export default function PhoneLinkPanel({ onClose }: { onClose: () => void }) {
  const [pc, setPc] = useState<RTCPeerConnection | null>(null)
  const [offer, setOffer] = useState<string>("")
  const [answer, setAnswer] = useState<string>("")
  const remoteAudioRef = useRef<HTMLAudioElement>(null)
  const [status, setStatus] = useState<string>('Idle')

  useEffect(() => {
    const cfg: RTCConfiguration = { iceServers: [{ urls: ['stun:stun.l.google.com:19302'] }] }
    const peer = new RTCPeerConnection(cfg)
    peer.oniceconnectionstatechange = () => setStatus(peer.iceConnectionState)
    peer.ontrack = (e) => {
      const stream = e.streams?.[0]
      if (stream && remoteAudioRef.current) {
        remoteAudioRef.current.srcObject = stream
      }
    }
    setPc(peer)
    return () => { try { peer.close() } catch {} }
  }, [])

  async function createOffer() {
    if (!pc) return
    setStatus('Creating offer…')
    const data = pc.createDataChannel('ping')
    data.onopen = () => data.send('hello')
    const desc = await pc.createOffer({ offerToReceiveAudio: true })
    await pc.setLocalDescription(desc)
    // Wait for ICE gathering complete for a fuller SDP
    await new Promise<void>(resolve => {
      if (pc.iceGatheringState === 'complete') return resolve()
      const check = () => {
        if (pc.iceGatheringState === 'complete') {
          pc.removeEventListener('icegatheringstatechange', check)
          resolve()
        }
      }
      pc.addEventListener('icegatheringstatechange', check)
      setTimeout(resolve, 1500)
    })
    setOffer(JSON.stringify(pc.localDescription))
    setStatus('Offer ready')
  }

  async function applyAnswer() {
    if (!pc) return
    try {
      const desc = JSON.parse(answer)
      await pc.setRemoteDescription(desc)
      setStatus('Answer applied; connecting…')
    } catch (e:any) {
      setStatus('Invalid answer: ' + (e?.message || String(e)))
    }
  }

  return (
    <div className="p-4 bg-[#0a0f1a]/95 border border-cyan-700/40 rounded-xl text-cyan-100 w-[520px]">
      <div className="flex items-center justify-between mb-3">
        <div className="text-lg font-semibold">Phone Link (Bluetooth alternative)</div>
        <button onClick={onClose} className="px-2 py-1 rounded bg-cyan-700 text-white text-xs">Close</button>
      </div>
      <div className="text-xs text-cyan-300/70 mb-3">Use this when direct Bluetooth mic is unavailable. Pair your phone via browser-to-browser WebRTC without servers.</div>
      <div className="space-y-3">
        <div>
          <div className="font-semibold mb-1">Step 1 — Create Offer</div>
          <button onClick={createOffer} className="px-3 py-1 rounded bg-cyan-600 text-[#06121a] text-sm">Create Offer</button>
          <textarea className="mt-2 w-full h-28 bg-[#0d1422] border border-cyan-800 rounded p-2 text-xs" value={offer} readOnly placeholder="Offer will appear here" />
          <div className="text-xs text-cyan-300/60 mt-1">Copy this offer and paste it into your phone at: /phone-link.html</div>
        </div>
        <div>
          <div className="font-semibold mb-1">Step 2 — Paste Answer</div>
          <textarea className="w-full h-28 bg-[#0d1422] border border-cyan-800 rounded p-2 text-xs" value={answer} onChange={e=>setAnswer(e.target.value)} placeholder="Paste the SDP answer from your phone here" />
          <button onClick={applyAnswer} className="mt-2 px-3 py-1 rounded bg-cyan-600 text-[#06121a] text-sm">Apply Answer</button>
        </div>
        <div className="text-xs text-cyan-300/70">Status: {status}</div>
        <audio ref={remoteAudioRef} autoPlay playsInline className="hidden" />
      </div>
    </div>
  )
}
