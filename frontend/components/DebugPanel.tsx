/**
 * Debug Panel Component for Q-IDE
 * Provides debugging UI with:
 * - Variables inspector (locals, globals, watch)
 * - Call stack visualization
 * - Debug controls (continue, step over, step into, step out)
 * - Breakpoint management
 * - Watch expressions
 * - Console output
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { ChevronDown, ChevronRight, Trash2, Plus, Play, Pause, SkipForward, ArrowDown, LogOut } from 'lucide-react';

interface Variable {
  name: string;
  value: string;
  type: string;
  variablesReference: number;
}

interface StackFrame {
  id: number;
  name: string;
  file: string;
  line: number;
  column: number;
}

interface Breakpoint {
  id: number;
  file: string;
  line: number;
  verified: boolean;
  condition?: string;
}

interface DebugSession {
  id: string;
  language: string;
  running: boolean;
  paused: boolean;
}

interface WatchExpression {
  id: string;
  expression: string;
  value?: string;
  error?: string;
}

type TabType = 'variables' | 'callStack' | 'breakpoints' | 'watch' | 'console';

/**
 * DebugPanel - Main debugging interface
 */
const DebugPanel: React.FC = () => {
  const [session, setSession] = useState<DebugSession | null>(null);
  const [variables, setVariables] = useState<Variable[]>([]);
  const [stackFrames, setStackFrames] = useState<StackFrame[]>([]);
  const [breakpoints, setBreakpoints] = useState<Breakpoint[]>([]);
  const [watchExpressions, setWatchExpressions] = useState<WatchExpression[]>([]);
  const [consoleOutput, setConsoleOutput] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<TabType>('variables');
  const [selectedFrame, setSelectedFrame] = useState<number | null>(null);
  const [expandedVariables, setExpandedVariables] = useState<Set<number>>(new Set());
  const consoleEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll console to bottom
  useEffect(() => {
    consoleEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [consoleOutput]);

  /**
   * Initialize debug session
   */
  const initializeDebugSession = useCallback(async (language: string) => {
    try {
      const response = await fetch('/api/v1/debug/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language }),
      });

      const data = await response.json();
      setSession({
        id: data.session_id,
        language,
        running: false,
        paused: true,
      });

      addConsoleOutput(`Debug session started for ${language}`);
    } catch (error) {
      addConsoleOutput(`Error starting debug: ${error}`);
    }
  }, []);

  /**
   * Launch debugger
   */
  const launchDebugger = useCallback(async (program: string, workingDir: string) => {
    if (!session) return;

    try {
      const response = await fetch(`/api/v1/debug/${session.id}/launch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ program, workingDir }),
      });

      const data = await response.json();
      
      if (data.success) {
        setSession(prev => prev ? { ...prev, running: true, paused: false } : null);
        addConsoleOutput(`Debugger started: ${program}`);
        await refreshDebugState();
      }
    } catch (error) {
      addConsoleOutput(`Error launching debugger: ${error}`);
    }
  }, [session]);

  /**
   * Set breakpoint
   */
  const setBreakpoint = useCallback(async (file: string, line: number, condition?: string) => {
    if (!session) return;

    try {
      const response = await fetch(`/api/v1/debug/${session.id}/breakpoint`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file, line, condition }),
      });

      const data = await response.json();
      
      if (data.body?.breakpoints) {
        const bp = data.body.breakpoints[0];
        setBreakpoints(prev => [...prev, {
          id: bp.id,
          file,
          line,
          verified: bp.verified,
          condition,
        }]);
        addConsoleOutput(`Breakpoint set at ${file}:${line}`);
      }
    } catch (error) {
      addConsoleOutput(`Error setting breakpoint: ${error}`);
    }
  }, [session]);

  /**
   * Remove breakpoint
   */
  const removeBreakpoint = useCallback(async (breakpointId: number) => {
    if (!session) return;

    try {
      await fetch(`/api/v1/debug/${session.id}/breakpoint/${breakpointId}`, {
        method: 'DELETE',
      });

      setBreakpoints(prev => prev.filter(bp => bp.id !== breakpointId));
      addConsoleOutput(`Breakpoint removed`);
    } catch (error) {
      addConsoleOutput(`Error removing breakpoint: ${error}`);
    }
  }, [session]);

  /**
   * Continue execution
   */
  const continueExecution = useCallback(async () => {
    if (!session) return;

    try {
      const response = await fetch(`/api/v1/debug/${session.id}/continue`, {
        method: 'POST',
      });

      const data = await response.json();
      
      if (data.success) {
        setSession(prev => prev ? { ...prev, paused: false, running: true } : null);
        addConsoleOutput('Execution continued');
      }
    } catch (error) {
      addConsoleOutput(`Error continuing: ${error}`);
    }
  }, [session]);

  /**
   * Step over
   */
  const stepOver = useCallback(async () => {
    if (!session) return;

    try {
      const response = await fetch(`/api/v1/debug/${session.id}/next`, {
        method: 'POST',
      });

      const data = await response.json();
      
      if (data.success) {
        await refreshDebugState();
        addConsoleOutput('Stepped over');
      }
    } catch (error) {
      addConsoleOutput(`Error stepping: ${error}`);
    }
  }, [session]);

  /**
   * Step into
   */
  const stepInto = useCallback(async () => {
    if (!session) return;

    try {
      const response = await fetch(`/api/v1/debug/${session.id}/stepIn`, {
        method: 'POST',
      });

      const data = await response.json();
      
      if (data.success) {
        await refreshDebugState();
        addConsoleOutput('Stepped into function');
      }
    } catch (error) {
      addConsoleOutput(`Error stepping: ${error}`);
    }
  }, [session]);

  /**
   * Step out
   */
  const stepOut = useCallback(async () => {
    if (!session) return;

    try {
      const response = await fetch(`/api/v1/debug/${session.id}/stepOut`, {
        method: 'POST',
      });

      const data = await response.json();
      
      if (data.success) {
        await refreshDebugState();
        addConsoleOutput('Stepped out of function');
      }
    } catch (error) {
      addConsoleOutput(`Error stepping: ${error}`);
    }
  }, [session]);

  /**
   * Pause execution
   */
  const pauseExecution = useCallback(async () => {
    if (!session) return;

    try {
      const response = await fetch(`/api/v1/debug/${session.id}/pause`, {
        method: 'POST',
      });

      const data = await response.json();
      
      if (data.success) {
        setSession(prev => prev ? { ...prev, paused: true, running: true } : null);
        await refreshDebugState();
        addConsoleOutput('Execution paused');
      }
    } catch (error) {
      addConsoleOutput(`Error pausing: ${error}`);
    }
  }, [session]);

  /**
   * Terminate debug session
   */
  const terminateSession = useCallback(async () => {
    if (!session) return;

    try {
      await fetch(`/api/v1/debug/${session.id}`, {
        method: 'DELETE',
      });

      setSession(null);
      setVariables([]);
      setStackFrames([]);
      addConsoleOutput('Debug session terminated');
    } catch (error) {
      addConsoleOutput(`Error terminating: ${error}`);
    }
  }, [session]);

  /**
   * Refresh debug state (variables, stack, etc.)
   */
  const refreshDebugState = useCallback(async () => {
    if (!session) return;

    try {
      // Get stack trace
      const stackResponse = await fetch(`/api/v1/debug/${session.id}/stackTrace`);
      const stackData = await stackResponse.json();
      
      if (stackData.body?.stackFrames) {
        setStackFrames(stackData.body.stackFrames);
        if (stackData.body.stackFrames.length > 0 && selectedFrame === null) {
          setSelectedFrame(0);
        }
      }

      // Get variables for selected frame
      if (selectedFrame !== null && stackData.body?.stackFrames[selectedFrame]) {
        const varResponse = await fetch(
          `/api/v1/debug/${session.id}/variables/${selectedFrame}`
        );
        const varData = await varResponse.json();
        
        if (varData.body?.variables) {
          setVariables(varData.body.variables);
        }
      }
    } catch (error) {
      addConsoleOutput(`Error refreshing debug state: ${error}`);
    }
  }, [session, selectedFrame]);

  /**
   * Add watch expression
   */
  const addWatchExpression = useCallback(async (expression: string) => {
    if (!session) return;

    const id = Math.random().toString(36);
    setWatchExpressions(prev => [...prev, { id, expression }]);

    try {
      const response = await fetch(`/api/v1/debug/${session.id}/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expression }),
      });

      const data = await response.json();
      
      setWatchExpressions(prev =>
        prev.map(w =>
          w.id === id
            ? { ...w, value: data.body?.result, error: data.success ? undefined : 'Error' }
            : w
        )
      );
    } catch (error) {
      setWatchExpressions(prev =>
        prev.map(w =>
          w.id === id
            ? { ...w, error: String(error) }
            : w
        )
      );
    }
  }, [session]);

  /**
   * Remove watch expression
   */
  const removeWatchExpression = useCallback((id: string) => {
    setWatchExpressions(prev => prev.filter(w => w.id !== id));
  }, []);

  /**
   * Add console output
   */
  const addConsoleOutput = useCallback((message: string) => {
    setConsoleOutput(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${message}`]);
  }, []);

  /**
   * Toggle variable expansion
   */
  const toggleVariableExpansion = useCallback((varRef: number) => {
    setExpandedVariables(prev => {
      const newSet = new Set(prev);
      if (newSet.has(varRef)) {
        newSet.delete(varRef);
      } else {
        newSet.add(varRef);
      }
      return newSet;
    });
  }, []);

  return (
    <div className="flex flex-col h-full bg-gray-900 text-gray-100 font-mono">
      {/* Debug Controls Toolbar */}
      <div className="flex items-center gap-2 p-3 bg-gray-800 border-b border-gray-700">
        {!session ? (
          <button
            onClick={() => initializeDebugSession('python')}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
          >
            Start Debug
          </button>
        ) : (
          <>
            {session.paused ? (
              <button
                onClick={continueExecution}
                className="p-1 hover:bg-gray-700 rounded"
                title="Continue"
              >
                <Play size={18} />
              </button>
            ) : (
              <button
                onClick={pauseExecution}
                className="p-1 hover:bg-gray-700 rounded"
                title="Pause"
              >
                <Pause size={18} />
              </button>
            )}
            
            <button
              onClick={stepOver}
              className="p-1 hover:bg-gray-700 rounded"
              title="Step Over"
            >
              <SkipForward size={18} />
            </button>

            <button
              onClick={stepInto}
              className="p-1 hover:bg-gray-700 rounded"
              title="Step Into"
            >
              <ArrowDown size={18} />
            </button>

            <button
              onClick={stepOut}
              className="p-1 hover:bg-gray-700 rounded"
              title="Step Out"
            >
              <LogOut size={18} />
            </button>

            <div className="flex-1" />

            <span className="text-xs px-2 py-1 bg-gray-700 rounded">
              {session.language} {session.running ? '(running)' : '(stopped)'}
            </span>

            <button
              onClick={terminateSession}
              className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm"
            >
              Stop
            </button>
          </>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-0 bg-gray-800 border-b border-gray-700">
        {(['variables', 'callStack', 'breakpoints', 'watch', 'console'] as TabType[]).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm border-b-2 ${
              activeTab === tab
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent hover:bg-gray-700'
            }`}
          >
            {tab === 'variables' && 'Variables'}
            {tab === 'callStack' && 'Call Stack'}
            {tab === 'breakpoints' && 'Breakpoints'}
            {tab === 'watch' && 'Watch'}
            {tab === 'console' && 'Console'}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto p-3">
        {/* Variables Tab */}
        {activeTab === 'variables' && (
          <div className="space-y-2">
            <div className="text-xs text-gray-400 mb-3">Local Variables</div>
            {variables.length === 0 ? (
              <div className="text-xs text-gray-500">No variables</div>
            ) : (
              variables.map((v, i) => (
                <VariableRow
                  key={i}
                  variable={v}
                  expanded={expandedVariables.has(v.variablesReference)}
                  onToggle={() => toggleVariableExpansion(v.variablesReference)}
                />
              ))
            )}
          </div>
        )}

        {/* Call Stack Tab */}
        {activeTab === 'callStack' && (
          <div className="space-y-1">
            <div className="text-xs text-gray-400 mb-3">Call Stack</div>
            {stackFrames.length === 0 ? (
              <div className="text-xs text-gray-500">No stack frames</div>
            ) : (
              stackFrames.map((frame, i) => (
                <div
                  key={frame.id}
                  onClick={() => setSelectedFrame(i)}
                  className={`p-2 rounded cursor-pointer text-xs ${
                    selectedFrame === i
                      ? 'bg-blue-900 text-blue-200'
                      : 'hover:bg-gray-700'
                  }`}
                >
                  <div className="font-semibold">{frame.name}</div>
                  <div className="text-gray-400">{frame.file}:{frame.line}</div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Breakpoints Tab */}
        {activeTab === 'breakpoints' && (
          <div className="space-y-2">
            <div className="text-xs text-gray-400 mb-3">Breakpoints ({breakpoints.length})</div>
            {breakpoints.length === 0 ? (
              <div className="text-xs text-gray-500">No breakpoints</div>
            ) : (
              breakpoints.map(bp => (
                <div key={bp.id} className="flex items-center gap-2 p-2 bg-gray-800 rounded text-xs">
                  <div className="flex-1">
                    <div>{bp.file}:{bp.line}</div>
                    {bp.condition && <div className="text-gray-400">if {bp.condition}</div>}
                  </div>
                  <button
                    onClick={() => removeBreakpoint(bp.id)}
                    className="p-1 hover:bg-gray-700 rounded"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))
            )}
          </div>
        )}

        {/* Watch Tab */}
        {activeTab === 'watch' && (
          <div className="space-y-2">
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                placeholder="Add expression..."
                className="flex-1 px-2 py-1 bg-gray-800 text-xs rounded border border-gray-700"
                onKeyPress={e => {
                  if (e.key === 'Enter') {
                    addWatchExpression((e.target as HTMLInputElement).value);
                    (e.target as HTMLInputElement).value = '';
                  }
                }}
              />
              <button
                className="p-1 hover:bg-gray-700 rounded"
                onClick={() => {
                  const input = document.querySelector('[placeholder="Add expression..."]') as HTMLInputElement;
                  if (input) {
                    addWatchExpression(input.value);
                    input.value = '';
                  }
                }}
              >
                <Plus size={16} />
              </button>
            </div>
            {watchExpressions.map(w => (
              <div key={w.id} className="flex items-center gap-2 p-2 bg-gray-800 rounded text-xs">
                <div className="flex-1">
                  <div className="font-semibold">{w.expression}</div>
                  <div className="text-gray-400">
                    {w.error ? `Error: ${w.error}` : w.value}
                  </div>
                </div>
                <button
                  onClick={() => removeWatchExpression(w.id)}
                  className="p-1 hover:bg-gray-700 rounded"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Console Tab */}
        {activeTab === 'console' && (
          <div className="space-y-1 text-xs font-mono">
            {consoleOutput.map((line, i) => (
              <div key={i} className="text-gray-300">
                {line}
              </div>
            ))}
            <div ref={consoleEndRef} />
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Variable display component
 */
interface VariableRowProps {
  variable: Variable;
  expanded: boolean;
  onToggle: () => void;
}

const VariableRow: React.FC<VariableRowProps> = ({ variable, expanded, onToggle }) => {
  const hasChildren = variable.variablesReference > 0;

  return (
    <div>
      <div className="flex items-center gap-2 p-1 hover:bg-gray-800 rounded text-xs">
        {hasChildren ? (
          <button onClick={onToggle} className="w-4 h-4 p-0 flex items-center justify-center">
            {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          </button>
        ) : (
          <div className="w-4" />
        )}
        <span className="font-semibold text-blue-300">{variable.name}</span>
        <span className="text-gray-500">:</span>
        <span className="text-green-300">{variable.type}</span>
        <span className="text-gray-500">=</span>
        <span className="text-yellow-300">{variable.value}</span>
      </div>
      {expanded && hasChildren && (
        <div className="ml-4 border-l border-gray-700 pl-2">
          {/* Nested variables would be rendered here */}
          <div className="text-xs text-gray-500">...</div>
        </div>
      )}
    </div>
  );
};

export default DebugPanel;
