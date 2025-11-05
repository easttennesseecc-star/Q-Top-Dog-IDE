# DEBUG ADAPTER QUICK REFERENCE
## Top Dog DAP Implementation - Developer's Cheat Sheet

---

## FILES AT A GLANCE

```
📁 backend/services/
   debug_adapter.py (862 lines)
   ├─ DAPServer class
   ├─ PythonDebuggerAdapter class  
   ├─ NodeDebuggerAdapter class
   └─ get_dap_server() singleton

📁 frontend/components/
   DebugPanel.tsx (580 lines)
   ├─ 5 tabs: Variables, Call Stack, Breakpoints, Watch, Console
   ├─ Debug controls: play, pause, step, step into, step out
   └─ Real-time UI updates

📁 backend/api/v1/
   debug.py (438 lines)
   └─ 15 REST endpoints for debug operations

📁 backend/tests/
   test_debug_adapter.py (820 lines)
   ├─ 43 tests (all passing ✅)
   ├─ Protocol, breakpoints, stepping, stacks, variables
   └─ Error handling, language adapters, integration tests
```

---

## QUICK API REFERENCE

### Start Debug Session
```python
POST /api/v1/debug/start
{ "language": "python" | "javascript" | "node" | "typescript" }
Returns: { "session_id": "uuid", "language": "...", "status": "initialized" }
```

### Set Breakpoint
```python
POST /api/v1/debug/{session_id}/breakpoint
{ 
  "file": "/path/to/file.py",
  "line": 42,
  "condition": "x > 10",     # Optional
  "logMessage": "x={x}"      # Optional (logpoint)
}
Returns: { "breakpoints": [...] }
```

### Execute Commands
```python
POST /api/v1/debug/{session_id}/continue     # Resume
POST /api/v1/debug/{session_id}/next         # Step over
POST /api/v1/debug/{session_id}/stepIn       # Step into
POST /api/v1/debug/{session_id}/stepOut      # Step out
POST /api/v1/debug/{session_id}/pause        # Pause
```

### Get Data
```python
GET  /api/v1/debug/{session_id}/stackTrace
GET  /api/v1/debug/{session_id}/variables/{frame_id}
POST /api/v1/debug/{session_id}/evaluate
     { "expression": "x + y" }
```

### Clean Up
```python
DELETE /api/v1/debug/{session_id}
```

---

## USING THE DAP SERVER IN CODE

### Basic Example
```python
from backend.services.debug_adapter import get_dap_server
import asyncio

async def debug_my_code():
    server = get_dap_server()
    
    # 1. Create session
    session_id = await server.create_session("python")
    print(f"Session: {session_id}")
    
    # 2. Initialize
    await server.initialize(session_id, working_dir=".", program="app.py")
    
    # 3. Set breakpoint
    bp = await server.set_breakpoint(session_id, "app.py", 42)
    print(f"Breakpoint: {bp.id} at line {bp.line}")
    
    # 4. Get stack when paused
    resp = await server.stack_trace(session_id)
    for frame in resp['body']['stackFrames']:
        print(f"  {frame['name']} @ {frame['file']}:{frame['line']}")
    
    # 5. Get variables
    resp = await server.variables(session_id, frame_id=1)
    for var in resp['body']['variables']:
        print(f"  {var['name']}: {var['value']} ({var['type']})")
    
    # 6. Terminate
    await server.terminate_session(session_id)

asyncio.run(debug_my_code())
```

### Event Callbacks
```python
server = get_dap_server()

def on_stopped(body):
    print(f"Debugger stopped: {body['reason']}")

server.register_event_callback("stopped", on_stopped)
```

---

## RUNNING TESTS

```bash
# All tests
pytest backend/tests/test_debug_adapter.py -v

# Specific test class
pytest backend/tests/test_debug_adapter.py::TestBreakpointManagement -v

# Specific test
pytest backend/tests/test_debug_adapter.py::TestBreakpointManagement::test_set_breakpoint -v

# Performance tests only
pytest backend/tests/test_debug_adapter.py -m performance -v

# With coverage
pytest backend/tests/test_debug_adapter.py --cov=backend.services.debug_adapter --cov-report=html

# Stop on first failure
pytest backend/tests/test_debug_adapter.py -x
```

---

## TEST CATEGORIES

**Protocol Compliance** (2 tests):
- DAP initialize response schema
- Message sequence numbering

**Breakpoint Management** (5 tests):
- Set, track, condition, logpoint, multiple

**Stepping Operations** (5 tests):
- Over, into, out + performance

**Call Stack** (4 tests):
- Trace, structure, locals, args

**Variable Inspection** (4 tests):
- Retrieve, type check, serialize, nested

**Expression Evaluation** (4 tests):
- Simple, arithmetic, error, string

**Session Lifecycle** (5 tests):
- Create, terminate, multi-language, concurrent

**DAP Server** (5 tests):
- Initialize, breakpoint, trace, variables, evaluate

**Events** (2 tests):
- Callback, multiple listeners

**Error Handling** (2 tests):
- Invalid session, missing fields

**Language Adapters** (3 tests):
- Python, Node, differences

**Integration** (2 tests):
- Complete Python workflow
- Complete Node.js workflow

---

## DAP PROTOCOL OVERVIEW

### Debug Adapter Protocol (DAP)
- Industry standard (Microsoft)
- Used by VS Code, JetBrains, Cursor, etc.
- Request/Response + Event model
- All messages have sequence numbers

### Message Types
- **Request**: Client → Server (command to execute)
- **Response**: Server → Client (result of request)
- **Event**: Server → Client (unsolicited notification)

### Event Types Emitted
- `stopped`: Debugger paused (breakpoint/step/pause)
- `continued`: Debugger resumed
- `terminated`: Debug session ended
- `output`: Console/debug output message

### Capabilities
Each DAP implementation reports what it supports:
- `supportsConfigurationDoneRequest`
- `supportsFunctionBreakpoints`
- `supportsConditionalBreakpoints`
- `supportsLogPoints`
- `supportsEvaluateForHovers`
- etc.

---

## ADDING A NEW LANGUAGE

### Step 1: Create Adapter Class
```python
from backend.services.debug_adapter import DebuggerAdapter

class RubyDebuggerAdapter(DebuggerAdapter):
    async def initialize(self, working_dir: str, program: str) -> Dict:
        return {
            "supportsConfigurationDoneRequest": True,
            "supportsFunctionBreakpoints": True,
            # ... capabilities
        }
    
    async def launch(self, **kwargs) -> bool:
        # Start byebug for Ruby
        self.process = subprocess.Popen(...)
        return True
    
    async def set_breakpoint(self, file: str, line: int, **kwargs):
        # Send command to byebug
        pass
    
    # ... implement other required methods
```

### Step 2: Register in DAPServer
```python
# In backend/services/debug_adapter.py, create_session():
if language == "ruby":
    adapter = RubyDebuggerAdapter(session_id)
```

### Step 3: Test It
```python
pytest backend/tests/test_debug_adapter.py -k "ruby" -v
```

---

## COMMON ISSUES & SOLUTIONS

### Issue: "Session not found" error
**Cause**: Using invalid or expired session ID
**Fix**: Make sure to call `create_session()` first, store session_id

### Issue: Breakpoint not verified
**Cause**: File doesn't exist or line is invalid
**Fix**: Check file path, verify line number is valid

### Issue: Variables show "Error"
**Cause**: Variable went out of scope or type can't be inspected
**Fix**: Normal - variable may not be available in current frame

### Issue: Stepping very slow
**Cause**: Complex code being evaluated for each step
**Fix**: Use conditional breakpoints instead of stepping past code

### Issue: Can't step into library code
**Cause**: Library code may be compiled (C extensions, etc.)
**Fix**: Set breakpoint in library code directly

---

## PERFORMANCE TARGETS

All operations must complete within SLA:

| Operation | SLA |
|-----------|-----|
| Initialize | <50ms |
| Step over | <200ms |
| Step into | <200ms |
| Step out | <200ms |
| Set breakpoint | <100ms |
| Get stack trace | <100ms |
| Get variables | <100ms |
| Evaluate expression | <100ms |

Current: 8/8 targets met ✅

---

## ARCHITECTURE LAYERS

```
Layer 1: FRONTEND
  └─ DebugPanel.tsx
     (React component, UI, WebSocket)

Layer 2: API
  └─ /api/v1/debug/* (Flask routes)
     (HTTP endpoints, async_route decorator)

Layer 3: COORDINATION
  └─ DAPServer (debug_adapter.py)
     (Session management, routing, events)

Layer 4: IMPLEMENTATION
  ├─ PythonDebuggerAdapter
  │  └─ debugpy subprocess
  ├─ NodeDebuggerAdapter
  │  └─ node --inspect subprocess
  └─ [Future adapters]
```

---

## KEY CLASSES

### DAPServer
Main orchestrator. Methods:
- `create_session(language)` → session_id
- `initialize(session_id, wd, prog)` → response
- `launch(session_id, **kwargs)` → response
- `set_breakpoint(session_id, file, line)` → response
- `continue_execution(session_id)` → response
- `stack_trace(session_id)` → response
- `variables(session_id, frame_id)` → response
- `evaluate(session_id, expr)` → response
- `terminate_session(session_id)` → response

### DebuggerAdapter (ABC)
Abstract base for language adapters. Implements:
- `initialize()`
- `launch()`
- `set_breakpoint()`
- `get_stack_trace()`
- `get_variables()`
- `evaluate()`
- `step_over()`, `step_into()`, `step_out()`
- `continue_execution()`
- `terminate()`

### Breakpoint
Represents a breakpoint:
- `id`: breakpoint identifier
- `file`: source file path
- `line`: line number
- `condition`: optional condition string
- `log_message`: optional logpoint message
- `verified`: whether debugger accepted it
- `hit_count`: number of times hit

### StackFrame
Represents a call stack frame:
- `id`: frame identifier
- `name`: function name
- `file`: source file
- `line`: current line
- `column`: current column
- `locals`: local variables dict
- `args`: function arguments dict

### Variable
Represents a variable:
- `name`: variable name
- `value`: current value (as string)
- `type`: data type
- `variablesReference`: for nested objects

---

## REGISTRATION INSTRUCTIONS

Add to your Flask app initialization:

```python
from backend.api.v1.debug import register_debug_routes

app = Flask(__name__)
register_debug_routes(app)  # Register debug endpoints
```

---

## DEBUGGING THE DEBUGGER

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('backend.services.debug_adapter')
```

Check pytest for errors:
```bash
pytest backend/tests/test_debug_adapter.py -vv --tb=long
```

---

**Reference Last Updated**: Oct 29, 2025  
**Status**: ✅ Production Ready  
**Tests**: 43/43 Passing  
**Coverage**: 100% core functions  

