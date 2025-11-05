import { useState, useEffect, useRef } from "react";
import { Toast } from "./Toast";

type QAssistantLLMConfig = {
  status: "configured" | "not_configured" | "needs_credentials";
  llm?: {
    id: string;
    name: string;
    type: string;
    source: string;
    assigned_role?: string;
  } | null;
  ready?: boolean;
  message?: string;
  warning?: string;
  instructions?: string;
};

// Voice/BT integration hooks
const useSpeechRecognition = () => {
  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const recognitionRef = useRef<any>(null);
  useEffect(() => {
    if (!('webkitSpeechRecognition' in window)) return;
    const SpeechRecognition = (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    recognition.onresult = (event: any) => {
      let interim = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          setTranscript(event.results[i][0].transcript);
        } else {
          interim += event.results[i][0].transcript;
        }
      }
    };
    recognition.onstart = () => setListening(true);
    recognition.onend = () => setListening(false);
    recognitionRef.current = recognition;
  }, []);
  const start = () => recognitionRef.current && recognitionRef.current.start();
  const stop = () => recognitionRef.current && recognitionRef.current.stop();
  return { listening, transcript, start, stop, setTranscript };
};

const useSpeechSynthesis = () => {
  const speak = (text: string) => {
    if ('speechSynthesis' in window) {
      const utter = new window.SpeechSynthesisUtterance(text);
      utter.rate = 1.05;
      utter.pitch = 1.1;
      utter.lang = 'en-US';
      window.speechSynthesis.speak(utter);
    }
  };
  return { speak };
};

type QAssistantChatProps = {
  activePanel?: string | null;
  setActivePanel?: (p: string | null) => void;
  showViewer?: boolean;
  edition?: 'dev' | 'regulated';
};

export default function QAssistantChat({ activePanel, setActivePanel: _setActivePanel, showViewer = true, edition }: QAssistantChatProps) {
  // Resolve backend base URL from runtime injection or build-time envs
  const backendBase = (
    (window as any).__VITE_BACKEND_URL ||
    (import.meta as any)?.env?.VITE_BACKEND_URL ||
    (import.meta as any)?.env?.VITE_API_URL ||
    (process as any)?.env?.REACT_APP_BACKEND_URL ||
    ""
  ) as string;
  const toApi = (path: string) => `${backendBase.replace(/\/$/, "")}${path.startsWith("/") ? path : "/" + path}`;

  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hi! I'm your Q Assistant. How can I help you today?" }
  ]);
  const [snapshots, setSnapshots] = useState(() => [
    { id: 1, title: 'UI Variant 1', status: 'pending' as 'pending' | 'approved' | 'requested' },
    { id: 2, title: 'UI Variant 2', status: 'pending' as 'pending' | 'approved' | 'requested' },
    { id: 3, title: 'UI Variant 3', status: 'pending' as 'pending' | 'approved' | 'requested' },
  ]);
  const [toast, setToast] = useState<{ message: string; type?: 'success'|'error'|'info' } | null>(null);
  const [inflight, setInflight] = useState<Record<number, boolean>>({});
  const [buildQueue, setBuildQueue] = useState<number[]>([]);
  const [input, setInput] = useState("");
  const [micOnly, setMicOnly] = useState(false);
  const { listening, transcript, start, stop, setTranscript } = useSpeechRecognition();
  const { speak } = useSpeechSynthesis();
  const [bluetoothConnected] = useState(false); // Placeholder
  const [streaming, setStreaming] = useState(false);
  const [llmConfig, setLLMConfig] = useState<QAssistantLLMConfig | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  // Load Q Assistant LLM configuration on mount
  useEffect(() => {
    const loadLLMConfig = async () => {
      try {
        const res = await fetch(toApi('/llm_config/q_assistant'));
        if (res.ok) {
          const config = await res.json() as QAssistantLLMConfig;
          setLLMConfig(config);
          
          // Show notification if LLM is configured
          if (config.status === "configured" && config.llm) {
            setToast({
              message: `✓ Q Assistant using: ${config.llm.name}`,
              type: "info"
            });
          } else if (config.status === "not_configured") {
            setToast({
              message: `⚠ Q Assistant needs an LLM. Go to LLM Setup to configure one.`,
              type: "info"
            });
          }
        }
      } catch (e) {
        console.error("Failed to load LLM config:", e);
      }
    };
    
    loadLLMConfig();
  }, []);

  useEffect(() => {
    if (chatEndRef.current) {
      if (typeof (chatEndRef.current as any).scrollIntoView === 'function') {
        (chatEndRef.current as any).scrollIntoView({ behavior: "smooth" });
      }
    }
  }, [messages]);

  // Keyboard shortcuts and global handlers
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      // Ctrl/Cmd+K -> focus textarea
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        textareaRef.current?.focus();
      }
      // Ctrl/Cmd+M -> toggle mic
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'm') {
        e.preventDefault();
        if (listening) stop(); else start();
      }
      // Escape -> stop listening
      if (e.key === 'Escape') {
        if (listening) stop();
      }
      // Ctrl/Cmd+Enter -> send
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        if (listening && transcript.trim()) {
          stop();
          sendMessage(transcript);
        } else {
          sendMessage();
        }
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [listening, transcript]);

  const sendMessage = async (msgOverride?: string) => {
    const userMsg = msgOverride !== undefined ? msgOverride : input;
    if (!userMsg.trim()) return;
    
    // Check if LLM is configured - if not, show helpful message
    if (!llmConfig?.ready) {
      const helpMessage = llmConfig?.message || "Q Assistant needs an LLM configured.\n\nGo to: LLM Setup (Ctrl+Shift+P) → Choose a provider → Add API key → Assign to 'Coding' role";
      setToast({
        message: helpMessage,
        type: "error"
      });
      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: `⚠️ ${helpMessage}` 
      }]);
      return;
    }
    
    // Clear input immediately for better UX
    setInput("");
    setTranscript("");
    
    // Add user message
    setMessages(prev => [...prev, { role: "user", content: userMsg }]);
    
    // Set streaming immediately for feedback
    setStreaming(true);
    
    try {
      // Connect to backend streaming endpoint
      const response = await fetch(toApi('/api/chat/'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
          ...(edition ? { 'X-Edition': edition } : {}),
        },
        body: JSON.stringify({ 
          message: userMsg,
          conversation_id: "default",
          include_history: true
        })
      });
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || 'Chat service error');
      }
      
      // Read server-sent events stream
      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');
      
      const decoder = new TextDecoder();
      let assistantResponse = "";
      let buffer = "";
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines[lines.length - 1]; // Keep incomplete line
        
        for (let i = 0; i < lines.length - 1; i++) {
          const line = lines[i].trim();
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.slice(6));
              
              if (event.type === 'chunk' && event.data) {
                assistantResponse += event.data;
                
                // Update UI with streaming text
                setMessages(msgs => {
                  const msgsNoStreaming = msgs.filter(m => !(m.role === "assistant" && (m as any).streaming));
                  return [...msgsNoStreaming, { role: "assistant", content: assistantResponse, streaming: true }];
                });
              } else if (event.type === 'verification') {
                // Show lightweight verification summary inline as a system note
                const v = event as any;
                const ow = v.overwatch ? `Overwatch: ${v.overwatch}` : 'Overwatch';
                const summary = typeof v.result_raw === 'string' ? v.result_raw.slice(0, 280) : '';
                setMessages(msgs => [...msgs, { role: 'assistant', content: `\n[${ow}] ${summary}` }]);
              } else if (event.type === 'blocked') {
                // Blocked by verification policy
                const reason = event.reason || 'Response blocked by policy';
                setMessages(msgs => [...msgs, { role: 'assistant', content: `⛔ ${reason}` }]);
              } else if (event.type === 'done') {
                // Stream complete
                setMessages(msgs => {
                  const msgsNoStreaming = msgs.filter(m => !(m.role === "assistant" && (m as any).streaming));
                  const finalMsg = { role: "assistant", content: assistantResponse };
                  
                  // Auto-speak final message
                  if (assistantResponse.length > 0) {
                    speak(assistantResponse.slice(0, 500)); // Speak first 500 chars to avoid too long synthesis
                  }
                  
                  return [...msgsNoStreaming, finalMsg];
                });
              } else if (event.type === 'error') {
                throw new Error(event.error || 'Stream error');
              }
            } catch (e) {
              // Skip invalid JSON lines
            }
          }
        }
      }
      
      if (assistantResponse.length === 0) {
        throw new Error('No response from LLM');
      }
      
    } catch (error: any) {
      const errorMsg = error?.message || "I encountered an error. Please try again.";
      setMessages(prev => [...prev, { role: "assistant", content: `❌ ${errorMsg}` }]);
      setToast({
        message: errorMsg,
        type: "error"
      });
    } finally {
      setStreaming(false);
    }
  };

  // Snapshot actions (optimistic)
  const approveSnapshot = (id: number) => {
    // optimistic update: mark approved locally and add to inflight
    setSnapshots(prev => prev.map(s => s.id === id ? { ...s, status: 'approved' } : s));
    setInflight(prev => ({ ...prev, [id]: true }));
    setBuildQueue(q => [...q, id]);
    // persist to backend
    fetch(toApi(`/snapshots/${id}/approve`), { method: 'POST' })
      .then(res => res.json())
      .then((body) => {
        if (body.status !== 'ok') throw new Error(body.message || 'Server error');
        // persisted, remove inflight marker and queue item
        setInflight(prev => { const c = { ...prev }; delete c[id]; return c; });
        setBuildQueue(q => q.filter(x => x !== id));
        setToast({ message: `Snapshot ${id} approved and persisted`, type: 'success' });
      })
      .catch(err => {
        // rollback optimistic update
        setSnapshots(prev => prev.map(s => s.id === id ? { ...s, status: 'pending' } : s));
        setInflight(prev => { const c = { ...prev }; delete c[id]; return c; });
        setBuildQueue(q => q.filter(x => x !== id));
        setToast({ message: `Failed to persist approval: ${err.message}`, type: 'error' });
      });
  };

  const requestChangeSnapshot = (id: number) => {
    setSnapshots(prev => prev.map(s => s.id === id ? { ...s, status: 'requested' } : s));
    setInflight(prev => ({ ...prev, [id]: true }));
    // persist
    fetch(toApi(`/snapshots/${id}/request-change`), { method: 'POST' })
      .then(res => res.json())
      .then((body) => {
        if (body.status !== 'ok') throw new Error(body.message || 'Server error');
        setInflight(prev => { const c = { ...prev }; delete c[id]; return c; });
        setToast({ message: `Change requested for snapshot ${id}`, type: 'info' });
      })
      .catch(err => {
        setSnapshots(prev => prev.map(s => s.id === id ? { ...s, status: 'pending' } : s));
        setInflight(prev => { const c = { ...prev }; delete c[id]; return c; });
        setToast({ message: `Failed to persist request: ${err.message}`, type: 'error' });
      });
  };

  const MicIcon = ({ active = false, size = 16 }: { active?: boolean; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill={active ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <rect x="9" y="3" width="6" height="11" rx="3" />
      <path d="M5 12a7 7 0 0 0 14 0M12 19v2" />
    </svg>
  );

  return (
    <div className="flex-1 flex flex-col overflow-y-auto p-4 relative panel-elevated glass">
      {/* LLM Model and Bluetooth status */}
      {/* Polished header: big title + status badges */}
      <div className="flex items-center justify-between mb-3 w-full">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-3">
            <div className="rounded-full bg-white/5 border border-white/10 w-10 h-10 flex items-center justify-center text-cyan-300 font-extrabold text-base shadow">Q</div>
            <div className="flex flex-col leading-tight select-none">
              <div className="text-sm font-bold text-white">Q Assistant <span className="text-cyan-300/80">v1.0</span></div>
              <div className="text-[11px] text-slate-300/80">
                {llmConfig?.ready ? `Using ${llmConfig?.llm?.name}` : "LLM not configured"}
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {llmConfig?.llm && (
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md border border-cyan-500/50 bg-cyan-500/10 text-cyan-200">
              <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></div>
              <span className="text-xs font-medium">{llmConfig.llm.name}</span>
            </div>
          )}
          <div className={"flex items-center gap-2 px-2.5 py-1 rounded-md cursor-default border " + (bluetoothConnected ? "border-cyan-500/50 bg-cyan-500/10 text-cyan-200" : "border-white/10 bg-white/5 text-slate-200")} aria-live="polite">
              <span className="text-xs font-medium">Bluetooth</span>
              {/* Build queue badge */}
              {buildQueue.length > 0 && (
                <span className="ml-1 inline-flex items-center justify-center px-1.5 py-0.5 rounded-full text-[10px] bg-yellow-500 text-black" aria-label="build-queue">{buildQueue.length}</span>
              )}
          </div>

          <button
            onClick={() => { if (listening) stop(); else start(); }}
            aria-pressed={listening}
            className={"flex items-center gap-2 px-3 py-1 rounded-full font-semibold focus:outline-none border " + (listening ? "border-cyan-500/60 bg-cyan-500/10 text-cyan-200" : "border-white/10 bg-white/5 text-slate-100 hover:bg-white/10")}
            title={listening ? 'Stop Voice Input' : 'Start Voice Input'}
          >
            <MicIcon active={listening} />
            <span className="text-xs">{listening ? 'Listening' : 'Voice'}</span>
          </button>
        </div>
      </div>
      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto mb-2" style={{ maxHeight: 260 }}>
        {messages.map((msg, i) => (
          <div key={i} className={`mb-2 ${msg.role === "assistant" ? "text-slate-100 text-left" : "text-cyan-200 text-right"} text-sm animate-fade-in-up`}>{msg.content}</div>
        ))}
        <div ref={chatEndRef} />
      </div>
      {/* Input row: voice and expanded text area (with mic-only mode & keyboard shortcuts) */}
      <div className="flex flex-col gap-2 mt-auto w-full">
        <div className="flex gap-2 items-end">
          <button
            className={"rounded-full w-10 h-10 flex items-center justify-center font-bold border " + (listening ? "border-cyan-500/50 bg-cyan-500/10 text-cyan-200" : "border-white/10 bg-white/5 text-slate-100 hover:bg-white/10")}
            onClick={listening ? stop : start}
            title={listening ? "Stop Listening" : "Start Voice Input"}
            aria-pressed={listening}
            aria-label={listening ? 'Stop voice input' : 'Start voice input'}
            disabled={streaming}
          >
            <MicIcon active={listening} />
          </button>

          {micOnly ? (
            <div className="flex-1 rounded-lg bg-black/20 border border-white/10 px-3 py-6 text-sm text-slate-100 flex items-center justify-center">
              <button
                className={"w-full rounded-lg bg-cyan-500 hover:bg-cyan-400 py-3 font-semibold text-[#071018] focus:outline-none focus:ring-2 focus:ring-cyan-400"}
                onClick={() => {
                  if (listening) {
                    stop();
                    if (transcript.trim()) sendMessage(transcript);
                  } else {
                    start();
                  }
                }}
                aria-pressed={listening}
                aria-label={listening ? 'Stop recording and send' : 'Start recording'}
              >
                {listening ? 'Stop & Send' : 'Tap to Record (mic-only)'}
              </button>
            </div>
          ) : (
            <textarea
              ref={textareaRef}
              className="flex-1 rounded-lg bg-white/5 border border-cyan-400/30 px-4 py-3 text-base text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:bg-white/10 focus:border-cyan-300 resize-none min-h-[56px] max-h-[220px] font-medium"
              placeholder={listening ? "Speak now..." : "Ask Q Assistant anything..."}
              value={listening ? transcript : input}
              onChange={e => listening ? setTranscript(e.target.value) : setInput(e.target.value)}
              onKeyDown={e => {
                // Enter to send, Shift+Enter for newline
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  if (listening && transcript.trim()) {
                    stop();
                    sendMessage(transcript);
                  } else {
                    sendMessage();
                  }
                }
              }}
              aria-label="Message to Q Assistant"
              tabIndex={0}
              role="textbox"
              onClick={() => textareaRef.current?.focus()}
            />
          )}

          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2">
              <button
                className="ml-2 rounded-lg bg-cyan-500 text-[#071018] font-semibold px-4 py-2 text-sm hover:bg-cyan-400 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-cyan-400"
                onClick={() => listening && transcript.trim() ? (stop(), sendMessage(transcript)) : sendMessage()}
                disabled={streaming || (!input.trim() && !transcript.trim())}
                aria-label="Send message"
              >
                <span className="inline-flex items-center gap-2">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
                    <path d="M2 21L23 12L2 3V10L17 12L2 14V21Z" fill="#071018" />
                  </svg>
                  Send
                </span>
              </button>

              <button
                className={"rounded px-3 py-2 text-sm border border-white/10 bg-white/5 text-slate-100 hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-cyan-500"}
                onClick={() => setMicOnly(m => !m)}
                aria-pressed={micOnly}
                aria-label={micOnly ? 'Disable mic-only mode' : 'Enable mic-only mode'}
                title={micOnly ? 'Disable mic-only mode' : 'Enable mic-only mode'}
              >
                {micOnly ? 'Mic-only: On' : 'Mic-only: Off'}
              </button>
            </div>
            <div className="text-xs text-slate-300/80 flex items-center justify-between">
              <div>Press Enter to send • Shift+Enter for new line • Ctrl+K focus • Ctrl+M toggle mic</div>
              <div aria-live="polite">{streaming ? 'Assistant responding…' : (listening ? 'Recording…' : 'Ready')}</div>
            </div>
          </div>
        </div>
      </div>
  {showViewer !== false && (
  <div className="mt-3 animate-fade-in-up bg-white/5 border border-white/10 rounded-xl p-4 text-sm text-slate-100 shadow-xl min-h-[180px] flex flex-col items-start justify-center gap-2 relative overflow-hidden w-full">
        {activePanel === 'runway' && (
          <div className="w-full">
            <span className="font-semibold text-cyan-200 text-sm mb-2 block">Runway AI Media</span>
            <div className="text-slate-300/80 text-sm mb-2">Generate images, video, or audio with AI</div>
            <div className="w-full flex flex-col gap-2 mb-2">
              <input className="rounded bg-[#0f1114] border border-white/10 px-2 py-1 text-xs text-slate-100 focus:outline-none" placeholder="Describe what you want to generate..." disabled />
              <button className="rounded bg-cyan-500 text-[#071018] font-semibold px-3 py-1 text-xs hover:bg-cyan-400 disabled:opacity-60" disabled>Generate (coming soon)</button>
            </div>
            <div className="text-slate-300/70 text-xs mt-2">Runway integration coming soon.<br/>AI-powered media tools will appear here.</div>
          </div>
        )}
        {activePanel === 'editor' && (
          <div className="w-full">
            <span className="font-semibold text-cyan-200 text-sm mb-2 block">Editor</span>
            <div className="w-full min-h-[120px]">
              {/* Editor panel placeholder */}
              <span className="text-slate-300/80 text-sm">Your code editor will appear here.</span>
            </div>
          </div>
        )}
        {activePanel === 'workflow' && (
          <div className="w-full">
            <span className="font-semibold text-cyan-200 text-sm mb-2 block">Workflow Builder</span>
            <div className="w-full min-h-[120px] flex items-center justify-center text-sm text-slate-300/80 select-none">
              Drag, drop, and automate your coding workflows here soon.
            </div>
          </div>
        )}
        {activePanel === 'plugins' && (
          <div className="w-full">
            <span className="font-semibold text-cyan-200 text-sm mb-2 block">Plugin Marketplace</span>
            <div className="w-full min-h-[120px] flex items-center justify-center text-sm text-slate-300/80 select-none">
              Plugin Marketplace coming soon.
            </div>
          </div>
        )}
        {!activePanel && (
          <>
            <div className="w-full flex items-center justify-between mb-3">
              <div>
                <span className="font-semibold text-cyan-200">Assistant Viewing Window</span>
                <div className="text-slate-300/80 text-xs">Snapshots, build options, and approval controls</div>
              </div>
              <div className="text-[11px] text-slate-300/70">Tip: Approve builds or request changes from a snapshot card</div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 w-full">
              {snapshots.map(s => (
                <div key={s.id} className="relative rounded-lg bg-white/5 border border-white/10 p-3 shadow motion-reduce:transition-none transition-transform transform hover:-translate-y-0.5" data-testid={`snapshot-${s.id}`}>
                  <div className="h-28 bg-black/20 rounded-md mb-3 flex items-center justify-center text-slate-200/90 font-medium">Snapshot {s.id}</div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <div className="text-slate-100 font-semibold text-sm">{s.title}</div>
                      <div className={`text-[11px] px-2 py-0.5 rounded border ${s.status === 'approved' ? 'border-green-500/50 bg-green-500/10 text-green-300' : s.status === 'requested' ? 'border-yellow-500/50 bg-yellow-500/10 text-yellow-200' : 'border-cyan-400/40 bg-cyan-500/10 text-cyan-200'}`} aria-label={`status-${s.id}`}>{s.status === 'pending' ? 'Pending' : s.status === 'approved' ? 'Approved' : 'Change requested'}</div>
                    </div>
                    <div className="text-slate-300/80 text-xs mb-3">A quick preview of the assistant output and suggested UI changes for this build.</div>
                    <div className="flex items-center gap-2">
                      <button onClick={() => approveSnapshot(s.id)} disabled={!!inflight[s.id]} className="rounded-md bg-cyan-500 text-[#071018] font-semibold px-3 py-1 text-sm hover:bg-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-400 disabled:opacity-50" aria-label={`Approve snapshot ${s.id}`}>
                        Approve
                      </button>
                      <button onClick={() => requestChangeSnapshot(s.id)} disabled={!!inflight[s.id]} className="rounded-md bg-white/10 text-slate-100 font-semibold px-3 py-1 text-sm hover:bg-white/15 focus:outline-none focus:ring-2 focus:ring-cyan-400 disabled:opacity-50" aria-label={`Request change for snapshot ${s.id}`}>
                        Request Change
                      </button>
                      <button className="ml-auto text-xs text-slate-300/70 hover:text-slate-200" aria-label={`More options for snapshot ${s.id}`}>⋯</button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            {toast && <Toast message={toast.message} type={toast.type as any} onClose={() => setToast(null)} />}

            <div className="mt-3 text-slate-300/70 text-[11px] italic select-none">(Interactive build & review workflow integrated here — clicking Approve will schedule a build.)</div>
          </>
        )}
      </div>
      )}
    </div>
  );
}
