# 🎯 Top Dog PROFESSIONAL SETUP GUIDE

## Install Top Dog Like a Professional Application

Follow these steps to set up Top Dog as a professional desktop application on Windows.

---

## Step 1: Initial Installation

Run the installer once:

```
Double-click: INSTALL.bat
```

This installs all dependencies (Python packages, Node packages, etc.)

**Time:** ~5-10 minutes

---

## Step 2: Create Desktop Shortcut (Recommended)

Create a professional desktop shortcut for Top Dog:

```
Double-click: CREATE_DESKTOP_SHORTCUT.bat
```

This adds a "Top Dog Topdog" shortcut to your Desktop.

**After this:**
- You'll have a desktop icon for Top Dog
- Can launch it like any professional Windows application
- Just double-click the icon anytime

---

## Step 3: First Launch

**Option A: Using Desktop Shortcut (Recommended)**
- Double-click the "Top Dog Topdog" icon on your Desktop

**Option B: Using Professional Launcher**
- Double-click: `LAUNCH_Q-IDE_PROFESSIONAL.bat`

Both will:
1. Clean up old processes
2. Verify system requirements
3. Start backend server (port 8000)
4. Start frontend server (port 1431)
5. Open Top Dog in your browser automatically
6. Show progress bars and status updates

**Time to launch:** ~20 seconds

---

## What You'll See

### The Professional Launcher
```
╔════════════════════════════════════════════════════════════════════════════╗
║                    🚀 Top Dog TOPDOG LAUNCHING                              ║
║                   Advanced AI Development Environment                      ║
║                          Please wait...                                    ║
╚════════════════════════════════════════════════════════════════════════════╝

[▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 5%
Cleaning up old processes...

[██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 10%
Verifying system requirements...

... (progress continues) ...

[████████████████████████████████████████████████████████████████████████████] 100%
✓ Top Dog TOPDOG SUCCESSFULLY LAUNCHED!
```

### Browser Opens
Then your browser automatically opens to Top Dog:
```
http://127.0.0.1:1431
```

You'll see the Top Dog interface with the Setup Wizard.

---

## Complete First-Time Setup

### 1. Choose Your LLM Provider

In the Setup Wizard, select one of:
- **OpenAI** - Most popular, $5 free credits
- **Anthropic (Claude)** - Highly accurate, $5 free credits
- **Google Gemini** - Fast and powerful, $5 free credits
- **Mistral** - Cost-effective, free trial available

### 2. Get API Key

Click the link for your chosen provider to:
1. Create an account
2. Get $5 in free credits
3. Generate an API key

### 3. Enter API Key

Paste your API key into Top Dog.

### 4. System Auto-Assigns Models

Top Dog automatically:
- Discovers all available models from your provider
- Scores them for each role (planning, coding, testing, etc.)
- Assigns the best models
- Shows monthly cost estimate

### 5. Ready to Build!

The wizard shows: *"Your AI team is ready! What do you want to build?"*

---

## Everyday Usage

**To start Top Dog anytime:**
- Double-click the **"Top Dog Topdog"** icon on your Desktop

**To stop Top Dog:**
- Close the two black terminal windows (Backend and Frontend)
- Close the browser window

---

## Launchers Available

| File | Purpose | Complexity |
|------|---------|-----------|
| Desktop Shortcut | Recommended - easiest | Very Simple |
| `LAUNCH_Q-IDE_PROFESSIONAL.bat` | Professional launcher with progress | Simple |
| `🚀_LAUNCH_Top Dog.bat` | Full verification launcher | Medium |
| `START.bat` | Original launcher | Medium |
| `RUN_Top Dog.bat` | Ultra-simple no-checks launcher | Very Simple |

**Recommended:** Use the Desktop Shortcut after running `CREATE_DESKTOP_SHORTCUT.bat`

---

## System Requirements

- **Windows 10 or Higher** (Home, Pro, Enterprise editions all work)
- **Python 3.11+** (Already checked during INSTALL.bat)
- **Node.js 18+** (Already checked during INSTALL.bat)
- **4GB RAM** (Recommended for best performance)
- **500MB Free Disk Space** (Minimum)
- **Internet Connection** (For downloading LLM models)

---

## Troubleshooting

### "Launcher closes immediately"

Check that Python and Node are properly installed:

1. Open PowerShell
2. Run: `python --version`
3. Run: `node --version`

If either shows "not found":
- Download Python: https://www.python.org/downloads/
- Download Node.js: https://nodejs.org/
- During install: ☑️ CHECK "Add to PATH"
- Restart your computer
- Try again

### "Connection refused" error in browser

Wait an additional 10 seconds, then refresh the browser (press F5).

### "Port 8000 already in use"

1. The launcher automatically cleans up old processes
2. If you still see this error, manually:

```powershell
taskkill /F /IM python.exe
taskkill /F /IM node.exe
```

Then try launching again.

### Both servers started but Top Dog won't load

1. Try manually opening browser to: http://127.0.0.1:1431
2. If that doesn't work, wait another 5 seconds and refresh
3. If still nothing, check the backend terminal window for error messages

---

## Advanced: Customize Launch Behavior

### Change Default Browser

Edit `LAUNCH_Q-IDE_PROFESSIONAL.bat` and change:
```batch
start http://127.0.0.1:1431
```
To your preferred browser, e.g.:
```batch
start chrome http://127.0.0.1:1431
start firefox http://127.0.0.1:1431
start msedge http://127.0.0.1:1431
```

### Change Port Numbers

Edit `LAUNCH_Q-IDE_PROFESSIONAL.bat`:
- Change `8000` to `9000` for backend
- Change `1431` to `3000` for frontend

Then update the browser URL accordingly.

### Skip Backend Verification

Edit `LAUNCH_Q-IDE_PROFESSIONAL.bat` and comment out the Python check:
```batch
REM python --version >nul 2>&1
```

---

## Architecture Overview

```
Top Dog Topdog
├── Desktop Shortcut (recommended entry point)
├── LAUNCH_Q-IDE_PROFESSIONAL.bat (professional launcher)
├── Backend Server (Python/FastAPI)
│   ├── Port 8000
│   ├── LLM orchestration
│   └── 50+ API endpoints
├── Frontend Server (React/Vite)
│   ├── Port 1431
│   ├── Web interface
│   └── Real-time chat
└── Browser
    └── Top Dog UI (http://127.0.0.1:1431)
```

---

## What Top Dog Does

Top Dog is an **AI-powered development IDE** that:

1. **Plans Your App**
   - Q Assistant analyzes your requirements
   - Creates detailed architecture

2. **Generates Code**
   - Code Writer produces complete code
   - Full-stack implementation

3. **Tests Everything**
   - Test Auditor writes comprehensive tests
   - 90%+ code coverage

4. **Verifies Quality**
   - Verification Overseer checks everything
   - Security, performance, best practices

5. **Prepares Deployment**
   - Release Manager creates deployment files
   - Ready for production

---

## Next Steps

1. ✅ Run `INSTALL.bat` (if you haven't already)
2. ✅ Run `CREATE_DESKTOP_SHORTCUT.bat` to add desktop shortcut
3. ✅ Double-click the "Top Dog Topdog" icon on your Desktop
4. ✅ Complete the Setup Wizard
5. ✅ Describe your app idea
6. ✅ Watch Top Dog build it!

---

## Your App Idea: iOS & Android App

You want to build an app for both iOS and Android products.

**Top Dog will:**
- Propose cross-platform technology (React Native, Flutter, or native)
- Generate complete source code
- Create test suites
- Provide deployment instructions
- Estimate development costs

**Result:** Production-ready iOS + Android app! 🎯

---

## Support

For issues or questions, open an issue on GitHub or check the documentation in the `docs/` folder.

---

**Ready? Double-click the "Top Dog Topdog" icon and start building!** 🚀
