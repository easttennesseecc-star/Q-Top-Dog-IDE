# 🚀 Top Dog TOPDOG - START HERE

## The Simplest Way to Launch Top Dog

### ⚡ JUST DOUBLE-CLICK ONE OF THESE:

**Option 1: Quick Launch**
```
Double-click: Top Dog.bat
```
✅ Fastest way to start  
✅ Servers start automatically  
✅ Browser opens automatically  

**Option 2: Desktop Shortcut (Recommended)**
```
1. Run: CREATE_SHORTCUT.bat
2. Double-click shortcut on Desktop
3. Done!
```
✅ Most professional  
✅ Easiest to access  
✅ Just like any desktop app  

---

## What Happens When You Launch

1. ✅ Old processes are cleaned up
2. ✅ Backend server starts (FastAPI on port 8000)
3. ✅ Frontend server starts (Vite on port 1431)
4. ✅ Browser opens automatically
5. ✅ Top Dog is ready to use!

**Total time: ~15 seconds**

---

## 🌐 Where to Find Top Dog

Once launched, Top Dog will be at:
- **Main App**: http://127.0.0.1:1431
- **Backend API**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs

---

## ⚠️ IMPORTANT

Keep the two server windows (Backend and Frontend) open while using Top Dog.
- You can minimize them
- You can move them
- But do NOT close them
- Top Dog stops working if you close them

---

## 🆘 Something Not Working?

1. **Check Requirements**
   - Python 3.9+: `python --version`
   - Node.js: `node --version`

2. **Run Diagnostics**
   ```
   .\DIAGNOSE.ps1
   ```

3. **View Logs**
   ```
   Get-Content backend\logs\app.log -Tail 50
   ```

4. **Read Full Guide**
   ```
   See: PROFESSIONAL_LAUNCH_GUIDE.md
   ```

---

## 📋 All Launch Options

| Option | File | Usage |
|--------|------|-------|
| **Standard** | Top Dog.bat | Double-click to start |
| **Desktop Shortcut** | CREATE_SHORTCUT.bat | Run once, then use shortcut |
| **Debug** | START_DEBUG.ps1 | Full troubleshooting output |
| **System Check** | DIAGNOSE.ps1 | Verify your setup |

---

## 🎓 QUICK COMMANDS

```powershell
# Standard launch
.\Top Dog.bat

# Create desktop shortcut
.\CREATE_SHORTCUT.bat

# Launch with debug output
.\START_DEBUG.ps1

# Check system requirements
.\DIAGNOSE.ps1

# View backend logs
Get-Content backend\logs\app.log -Wait -Tail 0

# Stop all services
taskkill /F /IM python.exe
taskkill /F /IM node.exe
```

---

## ✅ READY TO GO!

That's it! Pick an option above and launch Top Dog.

**Enjoy building! 🚀**

---

### For more details, see:
- `PROFESSIONAL_LAUNCH_GUIDE.md` - Complete user guide
- `PROFESSIONAL_LAUNCHER_COMPLETE.md` - Technical summary
- `LOCAL_TESTING_AND_DEBUGGING.md` - Debugging guide
