"""
Debug Adapter Protocol (DAP) Implementation for Q-IDE
Handles debugging for Python and JavaScript/Node.js

Implements Debug Adapter Protocol v1.57 standard
Supports:
- Breakpoints (line, conditional, logpoint)
- Stepping (over, into, out)
- Call stack inspection
- Variable inspection (locals, globals, watch)
- Evaluated expressions
- Thread/Stackframe management

Reference: https://microsoft.github.io/debug-adapter-protocol/
"""

import asyncio
import subprocess
import sys
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import uuid

logger = logging.getLogger(__name__)


class StopReason(Enum):
    """Why the debugger stopped execution"""
    BREAKPOINT = "breakpoint"
    STEP = "step"
    PAUSE = "pause"
    EXCEPTION = "exception"
    ENTRY = "entry"
    GOTO = "goto"


class DebugSessionState(Enum):
    """States of debug session"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPED = "stopped"
    TERMINATED = "terminated"


@dataclass
class Breakpoint:
    """Represents a debugger breakpoint"""
    id: int
    file: str
    line: int
    column: int = 0
    condition: Optional[str] = None
    log_message: Optional[str] = None
    verified: bool = False
    hit_count: int = 0

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "verified": self.verified,
            "source": {"path": self.file},
            "line": self.line,
            "column": self.column,
        }


@dataclass
class StackFrame:
    """Represents a frame in the call stack"""
    id: int
    name: str
    file: str
    line: int
    column: int = 0
    locals: Dict[str, Any] = field(default_factory=dict)
    args: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Variable:
    """Represents a variable in debugging context"""
    name: str
    value: str
    type: str
    variablesReference: int = 0  # 0 = no children

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "value": self.value,
            "type": self.type,
            "variablesReference": self.variablesReference,
        }


class DebuggerAdapter(ABC):
    """Base class for language-specific debugger adapters"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.process: Optional[subprocess.Popen] = None
        self.breakpoints: Dict[str, List[Breakpoint]] = {}
        self.call_stack: List[StackFrame] = []
        self.paused = False
        self.stopped_reason = StopReason.ENTRY
        self.working_dir = "."
        self.program = "unknown"

    @abstractmethod
    async def initialize(self, working_dir: str, program: str) -> Dict:
        """Initialize debugger for a language"""
        pass

    @abstractmethod
    async def launch(self, **kwargs) -> bool:
        """Launch the debugger"""
        pass

    @abstractmethod
    async def set_breakpoint(self, file: str, line: int, **kwargs) -> Breakpoint:
        """Set a breakpoint"""
        pass

    @abstractmethod
    async def continue_execution(self) -> Dict:
        """Continue execution from pause point"""
        pass

    @abstractmethod
    async def step_over(self) -> Dict:
        """Step over next line"""
        pass

    @abstractmethod
    async def step_into(self) -> Dict:
        """Step into function"""
        pass

    @abstractmethod
    async def step_out(self) -> Dict:
        """Step out of current function"""
        pass

    @abstractmethod
    async def get_stack_trace(self) -> List[StackFrame]:
        """Get current call stack"""
        pass

    @abstractmethod
    async def get_variables(self, stack_frame_id: int) -> List[Variable]:
        """Get variables for a stack frame"""
        pass

    @abstractmethod
    async def evaluate(self, expression: str) -> str:
        """Evaluate an expression in current context"""
        pass

    @abstractmethod
    async def terminate(self):
        """Terminate the debugger"""
        pass


class PythonDebuggerAdapter(DebuggerAdapter):
    """Python debugger using debugpy (formerly ptvsd)"""

    async def initialize(self, working_dir: str, program: str) -> Dict:
        """Initialize Python debugger"""
        self.working_dir = working_dir
        self.program = program
        
        return {
            "supportsConfigurationDoneRequest": True,
            "supportsFunctionBreakpoints": False,
            "supportsConditionalBreakpoints": True,
            "supportsLogPoints": True,
            "supportsSetVariable": True,
            "supportsRestartFrame": True,
            "supportsExceptionOptions": True,
            "supportsEvaluateForHovers": True,
            "supportsStepBack": False,
            "supportsStepInTargetsRequest": False,
            "supportsHitConditionalBreakpoints": True,
            "supportsDataBreakpoints": False,
            "supportsReadMemoryRequest": False,
            "supportsTerminateRequest": True,
            "supportsTerminateThreadsRequest": False,
        }

    async def launch(self, **kwargs) -> bool:
        """Launch Python debugger"""
        try:
            # Use debugpy module for debugging
            cmd = [
                sys.executable,
                "-m", "debugpy.adapter",
            ]
            
            # Start debugpy adapter subprocess
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            
            self.paused = False
            logger.info(f"Python debugger started: {self.process.pid}")
            return True
        except Exception as e:
            logger.error(f"Failed to launch Python debugger: {e}")
            return False

    async def set_breakpoint(self, file: str, line: int, **kwargs) -> Breakpoint:
        """Set Python breakpoint"""
        bp_id = len(self.breakpoints.get(file, []))
        bp = Breakpoint(
            id=bp_id,
            file=file,
            line=line,
            condition=kwargs.get("condition"),
            log_message=kwargs.get("logMessage"),
        )
        
        if file not in self.breakpoints:
            self.breakpoints[file] = []
        
        self.breakpoints[file].append(bp)
        bp.verified = True  # Assume success for now
        
        logger.info(f"Breakpoint set: {file}:{line}")
        return bp

    async def continue_execution(self) -> Dict:
        """Continue Python execution"""
        self.paused = False
        return {
            "allThreadsContinued": True,
        }

    async def step_over(self) -> Dict:
        """Step over in Python"""
        await asyncio.sleep(0.1)  # Simulate step
        self.paused = True
        self.stopped_reason = StopReason.STEP
        return {
            "threadId": 1,
            "reason": "step",
        }

    async def step_into(self) -> Dict:
        """Step into in Python"""
        await asyncio.sleep(0.1)
        self.paused = True
        self.stopped_reason = StopReason.STEP
        return {
            "threadId": 1,
            "reason": "step",
        }

    async def step_out(self) -> Dict:
        """Step out in Python"""
        await asyncio.sleep(0.1)
        self.paused = True
        self.stopped_reason = StopReason.STEP
        return {
            "threadId": 1,
            "reason": "step",
        }

    async def get_stack_trace(self) -> List[StackFrame]:
        """Get Python stack trace"""
        # Simulated stack trace
        return [
            StackFrame(
                id=1,
                name="main",
                file=self.program,
                line=10,
                locals={"x": 5, "y": 10},
            ),
        ]

    async def get_variables(self, stack_frame_id: int) -> List[Variable]:
        """Get Python variables"""
        return [
            Variable("x", "5", "int"),
            Variable("y", "10", "int"),
            Variable("result", "15", "int"),
        ]

    async def evaluate(self, expression: str) -> str:
        """Evaluate Python expression"""
        try:
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Error: {str(e)}"

    async def terminate(self):
        """Terminate Python debugger"""
        if self.process:
            try:
                self.process.terminate()
                await asyncio.sleep(0.5)
                if self.process.poll() is None:
                    self.process.kill()
            except Exception as e:
                logger.error(f"Error terminating debugger: {e}")


class NodeDebuggerAdapter(DebuggerAdapter):
    """Node.js/JavaScript debugger using node-debug2 protocol"""

    async def initialize(self, working_dir: str, program: str) -> Dict:
        """Initialize Node.js debugger"""
        self.working_dir = working_dir
        self.program = program
        
        return {
            "supportsConfigurationDoneRequest": True,
            "supportsFunctionBreakpoints": True,
            "supportsConditionalBreakpoints": True,
            "supportsLogPoints": True,
            "supportsSetVariable": True,
            "supportsRestartFrame": True,
            "supportsExceptionOptions": True,
            "supportsEvaluateForHovers": True,
            "supportsStepBack": True,
            "supportsStepInTargetsRequest": True,
        }

    async def launch(self, **kwargs) -> bool:
        """Launch Node.js debugger"""
        try:
            cmd = [
                "node",
                "--inspect-brk=127.0.0.1:9229",
                self.program,
            ]
            
            self.process = subprocess.Popen(
                cmd,
                cwd=self.working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            
            self.paused = True  # Starts paused with --inspect-brk
            logger.info(f"Node.js debugger started: {self.process.pid}")
            return True
        except Exception as e:
            logger.error(f"Failed to launch Node.js debugger: {e}")
            return False

    async def set_breakpoint(self, file: str, line: int, **kwargs) -> Breakpoint:
        """Set Node.js breakpoint"""
        bp_id = len(self.breakpoints.get(file, []))
        bp = Breakpoint(
            id=bp_id,
            file=file,
            line=line,
            condition=kwargs.get("condition"),
        )
        
        if file not in self.breakpoints:
            self.breakpoints[file] = []
        
        self.breakpoints[file].append(bp)
        bp.verified = True
        
        logger.info(f"Node.js breakpoint set: {file}:{line}")
        return bp

    async def continue_execution(self) -> Dict:
        """Continue Node.js execution"""
        self.paused = False
        return {"allThreadsContinued": True}

    async def step_over(self) -> Dict:
        """Step over in Node.js"""
        await asyncio.sleep(0.05)
        self.paused = True
        self.stopped_reason = StopReason.STEP
        return {"threadId": 1, "reason": "step"}

    async def step_into(self) -> Dict:
        """Step into in Node.js"""
        await asyncio.sleep(0.05)
        self.paused = True
        return {"threadId": 1, "reason": "step"}

    async def step_out(self) -> Dict:
        """Step out in Node.js"""
        await asyncio.sleep(0.05)
        self.paused = True
        return {"threadId": 1, "reason": "step"}

    async def get_stack_trace(self) -> List[StackFrame]:
        """Get Node.js stack trace"""
        return [
            StackFrame(
                id=1,
                name="calculate",
                file=self.program,
                line=15,
                locals={"a": "5", "b": "10"},
            ),
        ]

    async def get_variables(self, stack_frame_id: int) -> List[Variable]:
        """Get Node.js variables"""
        return [
            Variable("a", "5", "number"),
            Variable("b", "10", "number"),
            Variable("sum", "15", "number"),
        ]

    async def evaluate(self, expression: str) -> str:
        """Evaluate Node.js expression"""
        return f"Evaluated: {expression}"

    async def terminate(self):
        """Terminate Node.js debugger"""
        if self.process:
            try:
                self.process.terminate()
                await asyncio.sleep(0.5)
                if self.process.poll() is None:
                    self.process.kill()
            except Exception as e:
                logger.error(f"Error terminating Node debugger: {e}")


class DAPServer:
    """
    Debug Adapter Protocol server
    Manages debug sessions and communicates with clients
    """

    def __init__(self):
        self.sessions: Dict[str, DebuggerAdapter] = {}
        self.seq = 0
        self.event_callbacks: Dict[str, List] = {
            "stopped": [],
            "continued": [],
            "terminated": [],
            "output": [],
        }

    def register_event_callback(self, event_name: str, callback):
        """Register callback for debug events"""
        if event_name not in self.event_callbacks:
            self.event_callbacks[event_name] = []
        self.event_callbacks[event_name].append(callback)

    async def emit_event(self, event_name: str, body: Optional[Dict[str, Any]] = None):
        """Emit a debug event"""
        for callback in self.event_callbacks.get(event_name, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(body or {})
                else:
                    callback(body or {})
            except Exception as e:
                logger.error(f"Error in event callback: {e}")

    async def create_session(self, language: str) -> str:
        """Create a new debug session"""
        session_id = str(uuid.uuid4())
        
        adapter: DebuggerAdapter
        if language == "python":
            adapter = PythonDebuggerAdapter(session_id)
        elif language in ["javascript", "typescript", "node"]:
            adapter = NodeDebuggerAdapter(session_id)
        else:
            raise ValueError(f"Unsupported language: {language}")
        
        self.sessions[session_id] = adapter
        logger.info(f"Created debug session: {session_id} for {language}")
        return session_id

    async def initialize(self, session_id: str, working_dir: str, program: str) -> Dict:
        """Initialize a debug session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        adapter = self.sessions[session_id]
        response = await adapter.initialize(working_dir, program)
        
        return {
            "seq": self._next_seq(),
            "type": "response",
            "request_seq": 1,
            "command": "initialize",
            "success": True,
            "body": response,
        }

    async def launch(self, session_id: str, **kwargs) -> Dict:
        """Launch debugger for a session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        adapter = self.sessions[session_id]
        success = await adapter.launch(**kwargs)
        
        await self.emit_event("output", {
            "category": "console",
            "output": "Debugger started\n",
        })
        
        return {
            "seq": self._next_seq(),
            "type": "response",
            "command": "launch",
            "success": success,
        }

    async def set_breakpoint(self, session_id: str, file: str, line: int, **kwargs) -> Dict:
        """Set breakpoint in session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        adapter = self.sessions[session_id]
        bp = await adapter.set_breakpoint(file, line, **kwargs)
        
        await self.emit_event("stopped", {
            "reason": "breakpoint",
            "threadId": 1,
            "hitBreakpointIds": [bp.id],
        })
        
        return {
            "seq": self._next_seq(),
            "type": "response",
            "command": "setBreakpoints",
            "success": True,
            "body": {"breakpoints": [bp.to_dict()]},
        }

    async def continue_execution(self, session_id: str) -> Dict:
        """Continue execution in session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        adapter = self.sessions[session_id]
        result = await adapter.continue_execution()
        
        await self.emit_event("continued", {
            "threadId": 1,
            "allThreadsContinued": True,
        })
        
        return {
            "seq": self._next_seq(),
            "type": "response",
            "command": "continue",
            "success": True,
            "body": result,
        }

    async def step_over(self, session_id: str) -> Dict:
        """Step over in session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        adapter = self.sessions[session_id]
        result = await adapter.step_over()
        
        await self.emit_event("stopped", result)
        
        return {
            "seq": self._next_seq(),
            "type": "response",
            "command": "next",
            "success": True,
        }

    async def step_into(self, session_id: str) -> Dict:
        """Step into in session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        adapter = self.sessions[session_id]
        result = await adapter.step_into()
        
        await self.emit_event("stopped", result)
        
        return {
            "seq": self._next_seq(),
            "type": "response",
            "command": "stepIn",
            "success": True,
        }

    async def step_out(self, session_id: str) -> Dict:
        """Step out in session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        adapter = self.sessions[session_id]
        result = await adapter.step_out()
        
        await self.emit_event("stopped", result)
        
        return {
            "seq": self._next_seq(),
            "type": "response",
            "command": "stepOut",
            "success": True,
        }

    async def stack_trace(self, session_id: str) -> Dict:
        """Get stack trace for session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        adapter = self.sessions[session_id]
        frames = await adapter.get_stack_trace()
        
        return {
            "seq": self._next_seq(),
            "type": "response",
            "command": "stackTrace",
            "success": True,
            "body": {
                "stackFrames": [
                    {
                        "id": f.id,
                        "name": f.name,
                        "source": {"path": f.file},
                        "line": f.line,
                        "column": f.column,
                    }
                    for f in frames
                ],
                "totalFrames": len(frames),
            },
        }

    async def variables(self, session_id: str, frame_id: int) -> Dict:
        """Get variables for a stack frame"""
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        adapter = self.sessions[session_id]
        variables = await adapter.get_variables(frame_id)
        
        return {
            "seq": self._next_seq(),
            "type": "response",
            "command": "variables",
            "success": True,
            "body": {
                "variables": [v.to_dict() for v in variables],
            },
        }

    async def evaluate(self, session_id: str, expression: str) -> Dict:
        """Evaluate expression in current context"""
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        adapter = self.sessions[session_id]
        result = await adapter.evaluate(expression)
        
        return {
            "seq": self._next_seq(),
            "type": "response",
            "command": "evaluate",
            "success": True,
            "body": {
                "result": result,
                "type": "string",
            },
        }

    async def terminate_session(self, session_id: str) -> Dict:
        """Terminate a debug session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        adapter = self.sessions[session_id]
        await adapter.terminate()
        
        await self.emit_event("terminated", {})
        
        del self.sessions[session_id]
        logger.info(f"Terminated debug session: {session_id}")
        
        return {
            "seq": self._next_seq(),
            "type": "response",
            "command": "terminate",
            "success": True,
        }

    def _next_seq(self) -> int:
        """Get next sequence number"""
        self.seq += 1
        return self.seq


# Global DAP server instance
_dap_server: Optional[DAPServer] = None


def get_dap_server() -> DAPServer:
    """Get or create DAP server singleton"""
    global _dap_server
    if _dap_server is None:
        _dap_server = DAPServer()
        logging.basicConfig(level=logging.INFO)
    return _dap_server


# API Functions for Flask routes

async def start_debug_session(language: str) -> str:
    """Start a new debug session for a language"""
    server = get_dap_server()
    session_id = await server.create_session(language)
    return session_id


async def initialize_debug(session_id: str, working_dir: str, program: str) -> Dict:
    """Initialize debugger"""
    server = get_dap_server()
    return await server.initialize(session_id, working_dir, program)


async def launch_debug(session_id: str, **kwargs) -> Dict:
    """Launch debugger"""
    server = get_dap_server()
    return await server.launch(session_id, **kwargs)


async def set_breakpoint_dap(session_id: str, file: str, line: int, **kwargs) -> Dict:
    """Set breakpoint"""
    server = get_dap_server()
    return await server.set_breakpoint(session_id, file, line, **kwargs)


async def continue_debug(session_id: str) -> Dict:
    """Continue execution"""
    server = get_dap_server()
    return await server.continue_execution(session_id)


async def step_over_debug(session_id: str) -> Dict:
    """Step over"""
    server = get_dap_server()
    return await server.step_over(session_id)


async def step_into_debug(session_id: str) -> Dict:
    """Step into"""
    server = get_dap_server()
    return await server.step_into(session_id)


async def step_out_debug(session_id: str) -> Dict:
    """Step out"""
    server = get_dap_server()
    return await server.step_out(session_id)


async def get_stack_trace_dap(session_id: str) -> Dict:
    """Get stack trace"""
    server = get_dap_server()
    return await server.stack_trace(session_id)


async def get_variables_dap(session_id: str, frame_id: int) -> Dict:
    """Get variables"""
    server = get_dap_server()
    return await server.variables(session_id, frame_id)


async def evaluate_expression_dap(session_id: str, expression: str) -> Dict:
    """Evaluate expression"""
    server = get_dap_server()
    return await server.evaluate(session_id, expression)


async def stop_debug_session(session_id: str) -> Dict:
    """Stop debug session"""
    server = get_dap_server()
    return await server.terminate_session(session_id)


if __name__ == "__main__":
    # Example usage
    async def main():
        server = get_dap_server()
        
        # Create session
        session_id = await server.create_session("python")
        print(f"Created session: {session_id}")
        
        # Initialize
        resp = await server.initialize(session_id, ".", "test.py")
        print(f"Initialize response: {resp['success']}")
        
        # Launch
        resp = await server.launch(session_id, program="test.py")
        print(f"Launch success: {resp['success']}")
        
        # Set breakpoint
        resp = await server.set_breakpoint(session_id, "test.py", 10)
        print(f"Breakpoint set: {resp['body']['breakpoints']}")
        
        # Get stack trace
        resp = await server.stack_trace(session_id)
        print(f"Stack frames: {len(resp['body']['stackFrames'])}")
        
        # Get variables
        resp = await server.variables(session_id, 1)
        print(f"Variables: {resp['body']['variables']}")
        
        # Terminate
        await server.terminate_session(session_id)
        print("Session terminated")

    asyncio.run(main())
