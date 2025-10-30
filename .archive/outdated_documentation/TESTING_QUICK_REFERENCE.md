# 🚀 Q-IDE Testing & Debugging - Quick Reference

**Last Updated**: October 28, 2025  
**Status**: Ready to Test ✅

---

## 🎯 START HERE (Choose One)

### Option A: Quickest Start (Recommended)
```powershell
cd c:\Quellum-topdog-ide
.\START_DEBUG.ps1
```
✅ Starts both backend & frontend  
✅ Opens browser automatically  
✅ Shows live debug logs  

### Option B: Traditional Scripts
```powershell
# Batch file (START_DEBUG.bat)
cd c:\Quellum-topdog-ide
.\START_DEBUG.bat

# Or classic batch
.\START.bat
```

### Option C: Manual Control (Advanced)

Terminal 1: Backend
```powershell
cd c:\Quellum-topdog-ide\backend
python main.py --log-level debug
```

Terminal 2: Frontend
```powershell
cd c:\Quellum-topdog-ide\frontend
pnpm run dev
```

---

## 🔍 Accessing Q-IDE

- **Frontend**: http://localhost:1431
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: `backend/data/q_ide.db`

---

## 🧪 Running Tests

### Frontend Tests
```powershell
cd c:\Quellum-topdog-ide\frontend

pnpm test                  # Run all tests
pnpm test -- --coverage    # With coverage report
pnpm test -- --watch       # Watch mode (auto-rerun)
```

### Backend Tests
```powershell
cd c:\Quellum-topdog-ide\backend

python -m pytest -v                    # Run all tests
python -m pytest tests/ --cov=. -v     # With coverage
python -m pytest tests/test_auth.py -v # Specific file
```

### Full Test Suite
```powershell
# Run all tests (frontend + backend)
cd c:\Quellum-topdog-ide

# Frontend
cd frontend
pnpm test

# Backend
cd ..\backend
python -m pytest -v
```

---

## 🐛 Debugging

### View Logs Live
```powershell
# Backend logs
Get-Content c:\Quellum-topdog-ide\backend\logs\app.log -Wait -Tail 0

# Search for errors
Select-String "ERROR" c:\Quellum-topdog-ide\backend\logs\app.log

# Frontend: Open browser DevTools (F12)
```

### Debug with VS Code

1. Open VS Code
2. Create `.vscode/launch.json` in backend folder:
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
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```
3. Press F5 to start debugging

### Browser DevTools (F12)
- **Console**: Frontend errors & logs
- **Network**: API calls & responses
- **Elements**: HTML/CSS inspection
- **Application**: Storage & cookies
- **Performance**: Load times & metrics

---

## 🔧 Common Issues & Fixes

### Port Already in Use
```powershell
# Kill backend process
Get-Process | Where-Object {$_.Name -eq 'python'} | Stop-Process -Force

# Kill frontend process
Get-Process | Where-Object {$_.Name -eq 'node'} | Stop-Process -Force

# Or specify different ports
# Backend: python main.py --port 8001
# Frontend: pnpm run dev -- --port 1432
```

### Module Not Found
```powershell
# Backend
cd backend
pip install -r requirements.txt --force-reinstall

# Frontend
cd frontend
pnpm install --force
```

### Database Locked/Corrupted
```powershell
# Safe to delete - recreated on startup
rm backend/data/q_ide.db

# Restart backend
cd backend
python main.py
```

### CORS Errors
```powershell
# Backend must allow frontend origin
# Check: backend/main.py line with CORSMiddleware
# Should include: "http://localhost:1431"

# Restart backend after fixing
```

---

## 📊 System Check

Run diagnostic tool:
```powershell
cd c:\Quellum-topdog-ide
.\DIAGNOSE.ps1
```

Checks:
- ✅ Python 3.9+
- ✅ Node.js & pnpm
- ✅ Project files
- ✅ Dependencies
- ✅ Ports available
- ✅ Database
- ✅ Environment variables

---

## 📝 Testing Checklist

Before pushing to production:

- [ ] Backend tests pass: `pytest -v`
- [ ] Frontend tests pass: `pnpm test`
- [ ] No console errors (F12)
- [ ] No backend errors (logs)
- [ ] API responses valid (Network tab)
- [ ] Database working
- [ ] All features tested manually
- [ ] Code builds without warnings

---

## 🚀 Quick Command Reference

| Command | Purpose |
|---------|---------|
| `.\START_DEBUG.ps1` | Start with debug logs |
| `.\DIAGNOSE.ps1` | Run system diagnostics |
| `curl http://localhost:8000/health` | Check backend |
| `Get-Content backend/logs/app.log -Wait` | Live logs |
| `pnpm test` | Frontend unit tests |
| `pytest -v` | Backend unit tests |
| `pnpm exec playwright test --headed` | E2E tests with browser |
| `sqlite3 backend/data/q_ide.db ".tables"` | View database tables |

---

## 📚 Documentation

- **Full Guide**: `LOCAL_TESTING_AND_DEBUGGING.md`
- **Test Guide**: `TESTING.md`
- **Architecture**: `SYSTEM_ARCHITECTURE.md`
- **API Docs**: `http://localhost:8000/docs` (when running)

---

## 💡 Pro Tips

1. **Watch Mode**: Auto-reload on code changes
   ```powershell
   pnpm run dev    # Frontend auto-reloads
   python main.py  # Backend auto-reloads with --reload
   ```

2. **Quick Reset**: Clean database
   ```powershell
   rm backend/data/q_ide.db
   # Recreated on next startup
   ```

3. **Debug-Only Build**: Disable optimizations
   ```powershell
   $env:DEBUG = "true"
   pnpm run dev
   ```

4. **Monitor Performance**: Real-time metrics
   ```javascript
   // In browser console (F12)
   console.memory  // Heap usage
   performance.now()  // Current timestamp
   ```

5. **Export Test Results**: Create report
   ```powershell
   pytest --html=report.html --self-contained-html
   # Opens: report.html
   ```

---

## 🎓 Learning Path

1. **Start Here**: `.\START_DEBUG.ps1`
2. **Explore**: Open http://localhost:1431
3. **Check Logs**: `Get-Content backend/logs/app.log -Wait`
4. **Run Tests**: `pytest -v` & `pnpm test`
5. **Debug**: Press F12 in browser, set breakpoints
6. **Check Docs**: http://localhost:8000/docs

---

## 🆘 Getting Help

1. **Check Logs**:
   - Backend: `backend/logs/app.log`
   - Frontend: Browser console (F12)

2. **Run Diagnostics**:
   ```powershell
   .\DIAGNOSE.ps1
   ```

3. **Test Endpoints**:
   ```powershell
   curl http://localhost:8000/health
   curl http://localhost:8000/docs
   ```

4. **View Full Guide**:
   - `LOCAL_TESTING_AND_DEBUGGING.md`
   - `TESTING.md`

---

## ✅ Ready to Debug!

Everything is set up. Choose a start method above and begin testing! 🚀

**Questions?** See `LOCAL_TESTING_AND_DEBUGGING.md` for comprehensive guide.
