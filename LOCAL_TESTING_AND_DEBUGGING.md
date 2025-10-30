# 🧪 Q-IDE Local Testing & Debugging Guide

**Purpose**: Set up Q-IDE for local testing and debugging on your PC  
**Platform**: Windows (PowerShell)  
**Status**: Ready to test immediately  
**Time**: 15 minutes to full setup

---

## 🚀 Quick Start: Get Running in 5 Minutes

### Option 1: Fastest Start (Recommended)
```powershell
# Navigate to project
cd c:\Quellum-topdog-ide

# Start everything with one command
.\START.bat
```

**What happens:**
- ✅ Backend starts on `http://localhost:8000`
- ✅ Frontend starts on `http://localhost:1431`
- ✅ Database initializes
- ✅ LLM auto-configuration runs
- ✅ All logs stream to terminal

### Option 2: Manual Control (Better for Debugging)

#### Terminal 1: Start Backend
```powershell
cd c:\Quellum-topdog-ide\backend
python -m pip install -r requirements.txt
python main.py
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

#### Terminal 2: Start Frontend
```powershell
cd c:\Quellum-topdog-ide\frontend
pnpm install
pnpm run dev
```

**Expected output:**
```
VITE v5.0.0 ready in 523 ms

➜  Local:   http://localhost:1431/
```

---

## 📊 Monitoring & Debugging

### Check Backend Status
```powershell
# Quick health check
curl http://localhost:8000/health

# Should return:
# {"status":"ok","timestamp":"2025-10-28T..."}
```

### View Backend Logs
```powershell
# Stream all backend logs
cd c:\Quellum-topdog-ide\backend
python main.py --log-level debug

# Or from separate terminal
cat backend/logs/app.log -f  # Follow mode
```

### View Frontend Logs
```powershell
# Check browser console in DevTools (F12)
# Or view dev server logs in terminal running:
pnpm run dev

# Errors show here in red
```

### Check Database Status
```powershell
cd c:\Quellum-topdog-ide\backend

# View database
python -c "from sqlalchemy import inspect; engine = create_engine('sqlite:///./data/q_ide.db'); inspector = inspect(engine); print('Tables:', inspector.get_table_names())"

# Or use SQLite CLI
sqlite3 data/q_ide.db ".tables"
sqlite3 data/q_ide.db ".schema users"
```

---

## 🧪 Running Tests

### Frontend Tests (React Components)

```powershell
cd c:\Quellum-topdog-ide\frontend

# Run all tests
pnpm test

# Run specific test file
pnpm test App.test.tsx

# Run with coverage report
pnpm test -- --coverage

# Watch mode (auto-rerun on changes)
pnpm test -- --watch

# Debug a specific test
pnpm test -- --debug --testNamePattern="test name"
```

### Backend Tests (Python)

```powershell
cd c:\Quellum-topdog-ide\backend

# Run all tests
python -m pytest -v

# Run specific test file
python -m pytest tests/test_auth.py -v

# Run with coverage
python -m pytest --cov=. tests/ -v

# Run specific test function
python -m pytest tests/test_auth.py::test_login -v

# Run with verbose output
python -m pytest -vv tests/

# Run in watch mode (requires pytest-watch)
ptw tests/
```

### End-to-End Tests (Playwright)

```powershell
cd c:\Quellum-topdog-ide\frontend

# First, ensure backend and frontend are running
# (in separate terminals)

# Run all E2E tests
pnpm exec playwright test

# Run specific test
pnpm exec playwright test e2e/editor.spec.ts

# Run in headed mode (see the browser)
pnpm exec playwright test --headed

# Debug mode (step through tests)
pnpm exec playwright test --debug

# Run with single worker (slower but more reliable)
pnpm exec playwright test --workers=1
```

---

## 🐛 Debugging Techniques

### Backend Debugging

#### Method 1: Using Python Debugger
```powershell
cd c:\Quellum-topdog-ide\backend

# Add breakpoint in your code:
# import pdb; pdb.set_trace()

# Run with debugger active
python -m pdb main.py

# Commands:
# (Pdb) continue      - Resume execution
# (Pdb) next          - Next line
# (Pdb) step          - Step into function
# (Pdb) print var     - Print variable
# (Pdb) list          - Show code
# (Pdb) break 42      - Set breakpoint on line 42
```

#### Method 2: Using VS Code Debugger
1. Open VS Code
2. Open backend folder
3. Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["main:app", "--reload"],
      "jinja": true,
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      },
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```
4. Press F5 to start debugging
5. Set breakpoints by clicking in the margin

#### Method 3: Enhanced Logging
```python
# In backend/logger_utils.py
import logging

logger = logging.getLogger(__name__)

# Use throughout your code:
logger.debug("Debug info: %s", variable)
logger.info("User logged in: %s", user_id)
logger.warning("Unusual activity: %s", event)
logger.error("Operation failed: %s", error, exc_info=True)
```

### Frontend Debugging

#### Method 1: Browser DevTools (F12)
1. Press `F12` to open DevTools
2. **Console tab**: See logs and errors
3. **Elements tab**: Inspect HTML/CSS
4. **Network tab**: Monitor API calls
5. **Application tab**: Check local storage, cookies
6. **Performance tab**: Measure performance

#### Method 2: VS Code Debugger for React
1. Install "Debugger for Chrome" extension
2. Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Launch Chrome",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:1431",
      "webRoot": "${workspaceFolder}/frontend/src",
      "sourceMapPathPrefix": "webpack:///"
    }
  ]
}
```
3. Press F5 and set breakpoints in your code

#### Method 3: React DevTools
1. Install "React Developer Tools" browser extension
2. Open DevTools (F12)
3. Go to "Components" tab
4. Inspect React components
5. View props and state in real-time

---

## 🔍 Common Debugging Scenarios

### Backend API Returning 500 Error

```powershell
# 1. Check the error in logs
cd c:\Quellum-topdog-ide\backend
Get-Content logs/app.log -Tail 50

# 2. Add debug logging
# In your route handler:
@app.post("/api/endpoint")
async def endpoint(data: dict):
    logger.debug("Received data: %s", data)
    try:
        result = process(data)
        logger.info("Success: %s", result)
        return result
    except Exception as e:
        logger.error("Failed: %s", str(e), exc_info=True)
        raise

# 3. Test the endpoint directly
curl -X POST http://localhost:8000/api/endpoint -H "Content-Type: application/json" -d '{"test":"data"}'

# 4. Check database connection
python -c "from sqlalchemy import create_engine; e = create_engine('sqlite:///./data/q_ide.db'); print(e.connect())"
```

### Frontend Component Not Rendering

```typescript
// Add debug logging in your component
export function MyComponent({ data }) {
  console.log("MyComponent rendered with:", data);
  
  useEffect(() => {
    console.log("useEffect triggered");
    return () => console.log("useEffect cleanup");
  }, [data]);
  
  if (!data) {
    console.warn("No data provided to MyComponent");
    return null;
  }
  
  return (
    <div>
      {console.log("Rendering content") || (
        // Your JSX here
      )}
    </div>
  );
}
```

### API Call Failing

```powershell
# 1. Check if backend is running
curl http://localhost:8000/health

# 2. Check CORS configuration in backend
# Look for CORS_ORIGINS in backend/main.py
# Make sure localhost:1431 is included

# 3. Monitor network requests in DevTools
# Open DevTools → Network tab
# Make the request
# Look for red (failed) requests
# Click to see response and error details

# 4. Check browser console for CORS errors
# Should show something like:
# Access to XMLHttpRequest at 'http://localhost:8000/...' 
# from origin 'http://localhost:1431' has been blocked by CORS policy

# 5. Test API directly from command line
curl http://localhost:8000/api/users
curl -X POST http://localhost:8000/api/login -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"test"}'
```

### LLM Not Responding

```powershell
# 1. Check if LLM is configured
curl http://localhost:8000/api/llm/status

# 2. Check LLM logs
cat backend/logs/llm.log -f

# 3. Test LLM directly
python -c "
from backend.llm_client import LLMClient
client = LLMClient()
response = client.chat('Hello, are you working?')
print(response)
"

# 4. If using OpenAI, verify API key
echo $env:OPENAI_API_KEY  # Should show your key

# 5. If using local model (Ollama)
# Check if Ollama is running
curl http://localhost:11434/api/version
# If not running, start it:
ollama serve
```

---

## 📝 Viewing & Collecting Logs

### All Log Files

```powershell
# Backend logs
Get-ChildItem c:\Quellum-topdog-ide\backend\logs\

# View main app log
Get-Content c:\Quellum-topdog-ide\backend\logs\app.log -Tail 100

# View error log
Get-Content c:\Quellum-topdog-ide\backend\logs\error.log -Tail 100

# View LLM log
Get-Content c:\Quellum-topdog-ide\backend\logs\llm.log -Tail 100

# Stream logs live
Get-Content c:\Quellum-topdog-ide\backend\logs\app.log -Wait -Tail 0

# Search logs for errors
Select-String "ERROR" c:\Quellum-topdog-ide\backend\logs\*.log

# Create diagnostic bundle
$date = Get-Date -Format "yyyy-MM-dd_HHmmss"
Copy-Item c:\Quellum-topdog-ide\backend\logs -Destination "c:\Quellum-topdog-ide\logs_backup_$date" -Recurse
Write-Host "Logs backed up to: logs_backup_$date"
```

### Browser Console Logs

```javascript
// In browser DevTools console:

// Get all logs
localStorage.getItem('logs')

// Clear logs
localStorage.clear()

// Export logs
copy(localStorage.getItem('logs'))
// Paste in text file to save

// Monitor API calls in real-time
(function() {
  const originalFetch = window.fetch;
  window.fetch = function(...args) {
    console.log('API Call:', args[0], args[1]);
    return originalFetch.apply(this, args)
      .then(r => {
        console.log('Response:', r.status, r);
        return r;
      });
  };
})();
```

---

## 🧪 Test Coverage

### Generate Coverage Reports

```powershell
# Backend coverage
cd c:\Quellum-topdog-ide\backend
python -m pytest --cov=. --cov-report=html tests/

# View report
Invoke-Item htmlcov\index.html

# Frontend coverage
cd c:\Quellum-topdog-ide\frontend
pnpm test -- --coverage

# View report
Invoke-Item coverage\lcov-report\index.html
```

### Coverage Goals
- Backend: 85%+ coverage
- Frontend: 80%+ coverage
- Overall: 85%+ coverage

---

## 📊 Performance Testing

### Backend Performance

```powershell
cd c:\Quellum-topdog-ide\backend

# Test with Apache Bench (if installed)
ab -n 100 -c 10 http://localhost:8000/health

# Or use Python requests
python -c "
import requests
import time
import statistics

times = []
for i in range(100):
    start = time.time()
    r = requests.get('http://localhost:8000/health')
    times.append(time.time() - start)

print(f'Average: {statistics.mean(times):.3f}s')
print(f'Min: {min(times):.3f}s')
print(f'Max: {max(times):.3f}s')
print(f'Stdev: {statistics.stdev(times):.3f}s')
"
```

### Frontend Performance

```javascript
// In browser console:

// Measure page load
console.log('Load time:', window.performance.timing.loadEventEnd - window.performance.timing.navigationStart, 'ms');

// Measure specific operation
console.time('operation');
// ... do something ...
console.timeEnd('operation');

// Monitor memory
console.memory  // Shows heap usage

// Profile render performance
console.profile('render');
// ... trigger a re-render ...
console.profileEnd('render');
```

---

## 🔧 Troubleshooting Common Issues

### "Port Already in Use"
```powershell
# Kill process on port 8000 (backend)
Get-Process | Where-Object {$_.Name -eq 'python'} | Stop-Process -Force

# Kill process on port 1431 (frontend)
netstat -ano | findstr :1431
# Note the PID from output, then:
taskkill /PID <PID> /F

# Or restart your terminals
```

### "Module Not Found"
```powershell
# Backend
cd c:\Quellum-topdog-ide\backend
pip install -r requirements.txt --force-reinstall

# Frontend
cd c:\Quellum-topdog-ide\frontend
pnpm install --force
pnpm prune
```

### "LLM Not Working"
```powershell
# Check LLM configuration
python -c "
import os
print('OpenAI key:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')
print('Gemini key:', 'SET' if os.getenv('GOOGLE_API_KEY') else 'NOT SET')
"

# If using local Ollama, verify it's running
curl http://localhost:11434/api/version
```

### "Database Locked"
```powershell
# Close any open database connections
cd c:\Quellum-topdog-ide\backend

# Backup and reset database
cp data/q_ide.db data/q_ide.db.backup
rm data/q_ide.db

# Restart backend to recreate tables
python main.py
```

### "CORS Errors"
```powershell
# Check CORS config in backend/main.py
# Make sure this line includes localhost:1431:

# CORSMiddleware(
#     app,
#     allow_origins=["http://localhost:1431", "http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Restart backend after changes
```

---

## 🚀 Quick Commands Cheat Sheet

```powershell
# Start everything
cd c:\Quellum-topdog-ide; .\START.bat

# Backend only
cd c:\Quellum-topdog-ide\backend; python main.py

# Frontend only
cd c:\Quellum-topdog-ide\frontend; pnpm run dev

# Run all tests
cd c:\Quellum-topdog-ide\backend; python -m pytest -v
cd c:\Quellum-topdog-ide\frontend; pnpm test

# Check health
curl http://localhost:8000/health

# View logs
Get-Content c:\Quellum-topdog-ide\backend\logs\app.log -Tail 50 -Wait

# Reset database
rm c:\Quellum-topdog-ide\backend\data\q_ide.db

# Kill processes
Get-Process | Where-Object {$_.Name -eq 'python'} | Stop-Process
Get-Process | Where-Object {$_.Name -eq 'node'} | Stop-Process
```

---

## 📚 Resources

- [FastAPI Debugging](https://fastapi.tiangolo.com/tutorial/debugging/)
- [React DevTools](https://react-devtools-tutorial.vercel.app/)
- [pytest Documentation](https://docs.pytest.org/)
- [Playwright Testing](https://playwright.dev/docs/intro)
- [VS Code Debugging](https://code.visualstudio.com/docs/editor/debugging)

---

**Next Steps**:
1. Run `.\START.bat` to start the application
2. Open browser to `http://localhost:1431`
3. Run tests with `pnpm test` (frontend) and `pytest -v` (backend)
4. Use DevTools (F12) to debug frontend
5. Check logs in `backend/logs/` for backend issues

**Ready to debug!** 🧪🚀
