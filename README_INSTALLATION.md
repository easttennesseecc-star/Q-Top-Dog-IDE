# Q-IDE TOPDOG - Installation & Launch Guide

## System Requirements

- **Windows 10/11**
- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **4GB RAM minimum**
- **500MB free disk space**

---

## ONE-CLICK SETUP

### Step 1: Prerequisites Installation
Before running the installer, make sure you have:
1. **Python 3.11+** installed and added to PATH
2. **Node.js 18+** installed and added to PATH

**How to verify:**
```
python --version    (should show 3.11 or higher)
node --version      (should show 18 or higher)
```

If these commands don't work, Python/Node are not in PATH. Reinstall them and check "Add to PATH".

---

### Step 2: Install Q-IDE

**Option A: Double-Click Install (Easiest)**
1. Navigate to: `c:\Quellum-topdog-ide\`
2. Double-click `INSTALL.bat`
3. Wait for the installer to complete
4. It will show `[OK]` messages as dependencies install

**Option B: Command Line Install**
```powershell
cd c:\Quellum-topdog-ide
.\INSTALL.bat
```

**What the installer does:**
- ✅ Checks Python and Node.js are installed
- ✅ Installs pnpm if needed
- ✅ Installs backend Python dependencies (pip install -r requirements.txt)
- ✅ Installs frontend Node dependencies (pnpm install)
- ✅ Runs integration tests to verify setup
- ✅ Shows `[SUCCESS]` when complete

---

### Step 3: Launch Q-IDE

**Option A: Double-Click Launch (Easiest)**
1. Navigate to: `c:\Quellum-topdog-ide\`
2. Double-click `START.bat`
3. Two new windows will open (Backend and Frontend)
4. Wait 3-5 seconds for servers to start

**Option B: Command Line Launch**
```powershell
cd c:\Quellum-topdog-ide
.\START.bat
```

---

## What Happens When You Launch

When you run `START.bat`, here's what you'll see:

```
================================================================================
                    Q-IDE TOPDOG - APPLICATION LAUNCHER
================================================================================

[INFO] Cleaning up old processes...
[OK] Old processes cleaned up

[OK] Backend starting in new window...
[OK] Frontend starting in new window...

================================================================================
                         APPLICATION STARTED!
================================================================================

[INFO] Backend API:  http://localhost:8000
[INFO] Frontend UI:  http://localhost:5173
[INFO] API Docs:     http://localhost:8000/docs

The backend and frontend are running in separate windows.
Keep both windows open while using the application.
```

Two new **Command Prompt windows** will open:
- **"Q-IDE Backend"** - Shows: `INFO: Application startup complete`
- **"Q-IDE Frontend"** - Shows: `VITE ready in XXX ms`

---

## Accessing the Application

Once launched, open your browser and go to:

### **Frontend UI**
```
http://localhost:5173
```

### **Backend API Documentation** 
```
http://localhost:8000/docs
```

---

## Troubleshooting

### "Python is not installed or not in PATH"
- **Solution:** Reinstall Python from https://www.python.org/downloads/
- Make sure to check the box: ☑ "Add Python to PATH"

### "Node.js is not installed or not in PATH"
- **Solution:** Reinstall Node.js from https://nodejs.org/
- Make sure to check: ☑ "Add to PATH"

### Backend window closes immediately
- **Solution:** Open PowerShell and run:
  ```powershell
  cd c:\Quellum-topdog-ide\backend
  python main.py
  ```
- Look for error messages - copy them exactly

### Frontend window closes immediately
- **Solution:** Open PowerShell and run:
  ```powershell
  cd c:\Quellum-topdog-ide\frontend
  pnpm run dev
  ```
- Look for error messages - copy them exactly

### Port 8000 or 5173 already in use
- **Solution:** In a PowerShell window:
  ```powershell
  Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force
  Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
  ```
- Then run `START.bat` again

### Tests fail during installation
- **Solution:** This might not be critical. Test the app anyway by running `START.bat`
- If the app doesn't work, run manual tests:
  ```powershell
  cd c:\Quellum-topdog-ide
  python test_q_assistant_integration.py
  ```

---

## What This System Does

**Q-IDE** is an AI-powered development IDE with:

- **5 LLM Roles**: Q Assistant (orchestrator) → Code Writer → Test Auditor → Verification Overseer → Release Manager
- **Cost-Optimized**: Simple SVG image generation ($0 vs expensive APIs)
- **Build Pipeline**: 8-phase project management system
- **Real-time Chat**: Stream responses from AI agents
- **Scope Enforcement**: Q Assistant can only plan/coordinate, never write code

---

## File Structure

```
c:\Quellum-topdog-ide\
├── INSTALL.bat                 ← Run this to install
├── START.bat                   ← Run this to launch
├── README_INSTALLATION.md      ← This file
├── backend/
│   ├── main.py                 ← Backend entry point
│   ├── requirements.txt         ← Python dependencies
│   └── [other backend files]
└── frontend/
    ├── package.json            ← Node dependencies
    ├── vite.config.ts          ← Frontend config
    └── [other frontend files]
```

---

## Support

If something doesn't work:

1. **Check the console/terminal windows** - they show exact error messages
2. **Run tests manually:**
   ```powershell
   cd c:\Quellum-topdog-ide
   python test_q_assistant_integration.py
   ```
3. **Verify dependencies are installed:**
   ```powershell
   pip list                    # Check Python packages
   pnpm list --depth=0         # Check Node packages
   ```

---

## Next Steps After Launching

1. Open http://localhost:5173 in your browser
2. Navigate to "LLM Setup" to configure your LLM provider
3. Start creating projects with the Q Assistant
4. Watch as the system orchestrates the full 5-LLM pipeline

---

**Ready? Double-click `INSTALL.bat` to get started!**
