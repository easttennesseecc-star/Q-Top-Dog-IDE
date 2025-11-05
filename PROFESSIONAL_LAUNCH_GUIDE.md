# 🚀 Top Dog TOPDOG - PROFESSIONAL LAUNCH GUIDE

**Status**: ✅ Ready to Launch  
**Version**: Production Release  
**Last Updated**: October 28, 2025

---

## 📌 THE SIMPLEST WAY TO LAUNCH Top Dog

### ⚡ Single-Click Launch (Recommended)

**Option 1: Direct File**
1. Open File Explorer
2. Navigate to `c:\Quellum-topdog-ide\`
3. **Double-click `Top Dog.bat`**
4. Watch the startup sequence
5. Your browser opens automatically to the application

**Option 2: Desktop Shortcut (Even Better!)**
1. Run `CREATE_SHORTCUT.bat` (in the root directory)
2. A shortcut appears on your Desktop
3. **Double-click `Top Dog Topdog.lnk`** anytime to launch
4. Application starts automatically

---

## 🎯 WHAT HAPPENS WHEN YOU LAUNCH

When you click `Top Dog.bat` or the desktop shortcut, the launcher:

1. **Stops any running servers** - Cleans up old processes
2. **Starts backend server** - FastAPI on port 8000
3. **Starts frontend server** - Vite dev server on port 1431
4. **Opens your browser** - Automatically navigates to http://127.0.0.1:1431
5. **Shows status message** - Confirms everything started successfully

**Total startup time**: ~15 seconds

---

## 💻 ACCESSING Top Dog

Once launched, you can access Top Dog at:

| Component | URL | Purpose |
|-----------|-----|---------|
| **Application** | http://127.0.0.1:1431 | Main Top Dog interface |
| **Backend API** | http://127.0.0.1:8000 | REST API endpoints |
| **API Documentation** | http://127.0.0.1:8000/docs | Interactive API docs (Swagger UI) |
| **Alternative Docs** | http://127.0.0.1:8000/redoc | ReDoc API documentation |

---

## 🔧 TROUBLESHOOTING

### Issue: "Command not found" or "Python not installed"

**Solution**: Make sure Python and Node.js are installed
```powershell
python --version
node --version
pnpm --version
```

If any are missing, install them and try again.

### Issue: Port 8000 or 1431 already in use

**Solution**: The launcher will try to stop old processes, but if ports are still blocked:

```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with the actual process ID)
taskkill /PID <PID> /F
```

Then try launching again.

### Issue: Browser doesn't open automatically

**Solution**: Manually open your browser and go to:
```
http://127.0.0.1:1431
```

### Issue: Services start but application doesn't respond

**Solution**: Give it more time to fully initialize (~15-20 seconds)

1. Check if both server windows are still running
2. Close Top Dog browser tab and refresh (F5)
3. Check backend logs:
   ```powershell
   Get-Content backend\logs\app.log -Tail 50
   ```

---

## 📋 ALL AVAILABLE LAUNCHERS

### Quick Reference

| Launcher | Method | When to Use | Result |
|----------|--------|------------|--------|
| **Top Dog.bat** | Double-click | Standard launch | Both servers start, browser opens |
| **Desktop Shortcut** | Desktop icon | Daily use | Same as Top Dog.bat but on Desktop |
| **START_DEBUG.ps1** | PowerShell | Debugging | Full debug output with troubleshooting |
| **DIAGNOSE.ps1** | PowerShell | System check | Validates all requirements |

### Detailed Instructions

**1. Standard Launch (Top Dog.bat)**
```powershell
cd c:\Quellum-topdog-ide
.\Top Dog.bat
```

**2. Create Desktop Shortcut**
```powershell
cd c:\Quellum-topdog-ide
.\CREATE_SHORTCUT.bat
```
Then use the shortcut on your Desktop.

**3. Debug Launch (with full output)**
```powershell
cd c:\Quellum-topdog-ide
.\START_DEBUG.ps1
```

**4. System Diagnostics**
```powershell
cd c:\Quellum-topdog-ide
.\DIAGNOSE.ps1
```

---

## 🔍 MONITORING Top Dog

### Keep Servers Running
Two console windows will appear when you launch Top Dog:
- **Top Dog Backend** - Shows API server logs
- **Top Dog Frontend** - Shows Vite dev server output

✅ **DO NOT CLOSE** these windows while using Top Dog  
✅ Keep them open in the background  
✅ You can minimize them if you prefer

### View Backend Logs Live
```powershell
Get-Content c:\Quellum-topdog-ide\backend\logs\app.log -Wait -Tail 0
```

### Monitor Frontend Output
Frontend logs appear in the "Top Dog Frontend" console window

### Check API Health
```powershell
curl http://127.0.0.1:8000/health
```

---

## 🚦 STARTUP SEQUENCE EXPLAINED

```
Launch Top Dog.bat
    ↓
Cleanup old processes (1-2 seconds)
    ↓
Verify directories exist (instant)
    ↓
Start backend server (5 seconds to initialize)
    ↓
Start frontend server (6 seconds to build)
    ↓
Open browser to http://127.0.0.1:1431 (1 second)
    ↓
Show success message (instant)
    ↓
✓ Ready to use!
```

---

## 💡 PRO TIPS

### Tip 1: Minimize Server Windows
After launch, minimize the two server windows to keep your desktop clean. They'll keep running in the background.

### Tip 2: Restart Quickly
Close the two server windows to stop Top Dog, then run `Top Dog.bat` again to restart fresh.

### Tip 3: Multiple Instances
You can run Top Dog on different ports if needed:
```powershell
cd frontend
pnpm run dev -- --port 1432
```

### Tip 4: Faster Restarts
If you modify code, the servers will auto-reload:
- **Backend**: Auto-reloads FastAPI (uvicorn with --reload)
- **Frontend**: Hot Module Reload (Vite HMR)

Just save your file and the app updates instantly!

### Tip 5: Debug Mode
For detailed startup information:
```powershell
cd c:\Quellum-topdog-ide
.\START_DEBUG.ps1
```

---

## 🎓 WHAT'S RUNNING

### Backend (Port 8000)
- **Framework**: FastAPI (Python)
- **Database**: SQLite
- **Features**: REST API, LLM integration, OAuth, real-time updates
- **Location**: `backend/main.py`

### Frontend (Port 1431)
- **Framework**: React + TypeScript
- **Build Tool**: Vite
- **Features**: Code editor, AI interface, collaboration tools
- **Location**: `frontend/src/`

### Services
- **Backend Server**: Listening on `http://127.0.0.1:8000`
- **Frontend Server**: Listening on `http://127.0.0.1:1431`
- **Database**: SQLite at `backend/data/q_ide.db`

---

## 📞 GETTING HELP

### Something Not Working?

1. **Check the console windows** - They show detailed error messages
2. **Run diagnostics** - `.\DIAGNOSE.ps1` checks your system
3. **View logs** - `Get-Content backend\logs\app.log -Tail 50`
4. **Try fresh start** - Close both windows and run `Top Dog.bat` again

### For Debugging Sessions

See `LOCAL_TESTING_AND_DEBUGGING.md` for:
- Advanced debugging techniques
- Running test suites
- Viewing network requests
- Browser DevTools tips
- Common issues & solutions

---

## ✅ VERIFICATION CHECKLIST

Before reporting issues, verify:

- [ ] Python 3.9+ installed: `python --version`
- [ ] Node.js installed: `node --version`
- [ ] pnpm installed: `pnpm --version`
- [ ] Ports 8000 and 1431 are available
- [ ] Run `.\DIAGNOSE.ps1` shows all green checkmarks
- [ ] Backend window shows "Uvicorn running on..."
- [ ] Frontend window shows "VITE... ready in X ms"
- [ ] Browser opened to http://127.0.0.1:1431

---

## 🎉 READY TO LAUNCH!

**You're all set!** Choose your launch method:

### Easiest
```
Double-click Top Dog.bat (or the desktop shortcut)
```

### From Command Line
```powershell
cd c:\Quellum-topdog-ide
.\Top Dog.bat
```

### With Full Debug Output
```powershell
cd c:\Quellum-topdog-ide
.\START_DEBUG.ps1
```

---

## 📝 NOTES

- Top Dog launches exactly like any professional desktop application
- All servers run locally - no cloud dependencies
- Your data stays on your computer
- Perfect for development and testing
- Production deployment docs available in separate guides

**Enjoy building with Top Dog! 🚀**
