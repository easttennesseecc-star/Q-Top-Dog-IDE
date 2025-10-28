# Q-IDE STANDALONE DEPLOYMENT GUIDE

## What You Have Now

✅ **Q-IDE is working on your PC** with both servers running
- Backend running on http://127.0.0.1:8000
- Frontend running on http://127.0.0.1:1431

## How to Install It on Any PC

### Option 1: Create a Portable Package (Recommended)

This creates a **self-contained folder** that you can copy to any PC.

**Step 1: Create the Package**
1. Open Command Prompt in `c:\Quellum-topdog-ide\`
2. Run: `STANDALONE_INSTALLER.bat`
3. This creates a `Q-IDE_STANDALONE` folder with everything needed

**What it copies:**
- ✅ All backend Python files
- ✅ All frontend React files  
- ✅ All configuration files
- ✅ Smart SETUP.bat for dependency installation
- ✅ Smart LAUNCH_Q-IDE.bat launcher
- ✅ Full documentation

**Step 2: Deploy to Another PC**
1. Copy the entire `Q-IDE_STANDALONE` folder to the other PC
2. Double-click `SETUP.bat` (one time only)
   - Checks for Python 3.11+ and Node.js
   - Installs all dependencies automatically
3. Double-click `LAUNCH_Q-IDE.bat` to start using Q-IDE

### Option 2: Manual Copy (If you prefer)

Simply copy these folders to another PC:
```
Q-IDE-Root/
├── backend/
├── frontend/
├── SETUP.bat         (install dependencies)
├── LAUNCH_Q-IDE.bat  (start servers)
└── README.txt
```

Then on the new PC:
1. Run `SETUP.bat` to install dependencies
2. Run `LAUNCH_Q-IDE.bat` to launch

## System Requirements (On Target PC)

- **OS:** Windows 10 or higher
- **Python:** 3.11+ (from https://www.python.org/)
- **Node.js:** 18+ (from https://nodejs.org/)
- **RAM:** 4GB minimum
- **Disk Space:** 500MB minimum
- **Internet:** For downloading/installing dependencies

## First-Time Setup on New PC

```
User gets Q-IDE_STANDALONE folder
       ↓
Double-clicks SETUP.bat
       ↓
Script checks for Python & Node.js
       ↓
If missing → Shows download links
       ↓
If present → Installs dependencies
       ↓
"Setup Complete - Ready to Launch!"
       ↓
Double-clicks LAUNCH_Q-IDE.bat
       ↓
Both servers start
       ↓
Browser opens to Q-IDE interface
       ↓
User sees Setup Wizard
       ↓
Ready to build apps!
```

## What SETUP.bat Does

```batch
✓ Checks Python is installed and accessible
✓ Checks Node.js is installed and accessible
✓ Installs/updates pnpm (Node package manager)
✓ Installs Python dependencies (pip install -r requirements.txt)
✓ Installs Node dependencies (pnpm install)
✓ Runs integration tests to verify everything works
✓ Shows completion status
```

**Time to complete:** ~5-10 minutes (depending on internet speed)

## What LAUNCH_Q-IDE.bat Does

```batch
✓ Stops any previously running servers
✓ Verifies Python and pnpm are available
✓ Starts Backend server on port 8000
  → Waits 5 seconds for startup
✓ Starts Frontend server on port 1431
  → Waits 6 seconds for startup
✓ Opens browser to http://127.0.0.1:1431
✓ Shows status with all URLs
```

**Time to launch:** ~20 seconds

## Important Notes

### For Python/Node.js Installation:

When installing Python:
- ☑️ **MUST CHECK:** "Add Python to PATH"

When installing Node.js:
- ☑️ **MUST CHECK:** "Add to PATH"

Without these, the scripts won't find them.

### Ports Used

- **8000** - Backend API (FastAPI)
- **1431** - Frontend UI (React/Vite)

If these ports are in use by other apps, the servers won't start. Close other apps or use different ports.

### Running Multiple Instances

You can run multiple copies of Q-IDE on the same PC:
- Each copy must use different ports
- Edit `LAUNCH_Q-IDE.bat` to change the port numbers

## Troubleshooting on Target PC

### "Python is not installed or not in PATH"

**Solution:**
1. Download Python from https://www.python.org/downloads/
2. Run the installer
3. **CHECK the box:** "Add Python to PATH"
4. Click "Install Now"
5. Restart the computer
6. Run SETUP.bat again

### "Node.js is not installed or not in PATH"

**Solution:**
1. Download Node.js from https://nodejs.org/
2. Run the installer
3. **CHECK the box:** "Add to PATH"
4. Click "Install" and follow prompts
5. Restart the computer
6. Run SETUP.bat again

### Servers won't start

**Solution:**
1. Close any existing Q-IDE windows
2. Open a PowerShell window
3. Run:
   ```powershell
   taskkill /F /IM python.exe
   taskkill /F /IM node.exe
   ```
4. Wait 5 seconds
5. Run LAUNCH_Q-IDE.bat again

### "Connection refused" errors

**Solution:**
1. Wait 10-15 seconds for servers to fully start
2. If ports still show as in use:
   ```powershell
   Get-Process python* | Stop-Process -Force
   Get-Process node | Stop-Process -Force
   ```
3. Try again

## Distribution Options

### Option A: Zip File (Easiest for Email/Cloud)
```powershell
# Create a zip file for easy sharing
Compress-Archive -Path "C:\path\to\Q-IDE_STANDALONE" -DestinationPath "Q-IDE_STANDALONE.zip"
```
Then email or upload the .zip file.

### Option B: USB Drive
Simply copy the `Q-IDE_STANDALONE` folder to a USB drive and it will work on any Windows PC.

### Option C: Network Share
Place the `Q-IDE_STANDALONE` folder on a shared network drive for your team.

## Uninstalling from Target PC

Simply delete the `Q-IDE_STANDALONE` folder. It doesn't install anything system-wide except dependencies (Python/Node), which can be kept for other projects.

## Advanced: Customizing for Your Organization

You can pre-configure the following before distribution:

1. **Pre-load LLM settings** - Edit `backend/llm_config.json`
2. **Custom branding** - Modify frontend colors in `frontend/src/`
3. **Auto-API-Key** - Store in environment variable (not recommended)

See `docs/` folder for more advanced customization options.

---

## Summary

**You now have:**
- ✅ Working Q-IDE on your development PC
- ✅ Automatic standalone packaging via STANDALONE_INSTALLER.bat
- ✅ Easy one-click setup (SETUP.bat) for target PCs
- ✅ Easy one-click launch (LAUNCH_Q-IDE.bat)
- ✅ Portable across any Windows machine

**Next Steps:**
1. Run `STANDALONE_INSTALLER.bat` to create the package
2. Copy `Q-IDE_STANDALONE` to the target PC
3. Run `SETUP.bat` then `LAUNCH_Q-IDE.bat`
4. Enjoy Q-IDE on unlimited PCs!
