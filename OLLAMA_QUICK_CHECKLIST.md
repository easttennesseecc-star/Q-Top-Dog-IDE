# ✅ Ollama Setup Checklist - Do These 7 Steps

**Objective**: Get Ollama running with Q-IDE auto-detecting it  
**Total Time**: 15-20 minutes  
**Difficulty**: ⭐ (very easy)

---

## Checklist

### [ ] Step 1: Download Ollama (2 min)
```
□ Go to: https://ollama.ai
□ Click "Download" button
□ Select "Windows"
□ File downloads: ollama-windows-amd64.exe
```

**Status**: ⏳ Not started
**Time**: 2 minutes

---

### [ ] Step 2: Install Ollama (5 min)
```
□ Find ollama-windows-amd64.exe in Downloads
□ Double-click it
□ Click "Yes" for admin permissions
□ Follow installer (click "Next", "Finish", etc.)
□ Wait for "Installation complete"
□ Ollama starts automatically
```

**Status**: ⏳ Not started
**Time**: 5 minutes total install time

---

### [ ] Step 3: Verify Installation (2 min)
```
□ Check system tray (bottom-right corner)
□ Look for Ollama icon (colorful circle)
□ Icon is visible and showing "running"

OR

□ Open PowerShell
□ Run: ollama --version
□ See version number like "0.1.X"
```

**Status**: ⏳ Not started
**Time**: 1-2 minutes

---

### [ ] Step 4: Download a Model (5-10 min)
```
□ Open PowerShell
□ Run: ollama pull llama2
□ Wait for download to complete
□ See "success" message
□ Takes 2-10 minutes depending on internet
```

**Pro tip**: Keep PowerShell window open, don't close it yet

**Status**: ⏳ Not started
**Time**: 5-10 minutes (mostly waiting)

---

### [ ] Step 5: Verify Model Downloaded (1 min)
```
□ In PowerShell, run: ollama list
□ See output:
  NAME            ID              SIZE    MODIFIED
  llama2:latest   2c26f67f5051    4.0GB   10 seconds ago

□ llama2 appears in the list
```

**Status**: ⏳ Not started
**Time**: 1 minute

---

### [ ] Step 6: Refresh Q-IDE (2 min)
```
□ Go to Q-IDE in browser
□ Press F5 to refresh
□ Wait 3-5 seconds
□ Page reloads
□ Check LLM Pool tab
```

**Status**: ⏳ Not started
**Time**: 2 minutes

---

### [ ] Step 7: Verify Auto-Detection (1 min)
```
□ Look at LLM Pool Management tab
□ See green section: "✨ Auto-Selected Best Options"
□ Ollama or llama2 appears in green box
□ Shows priority score (65 pts)
□ Available LLMs shows: 1 (not 0)

If you see this → ✅ SUCCESS!
```

**Status**: ⏳ Not started
**Time**: 1 minute

---

## Quick Reference Commands

```powershell
# Check if Ollama is installed
ollama --version

# Download a model
ollama pull llama2

# List downloaded models
ollama list

# Start Ollama (if not running)
ollama serve

# Test Ollama directly (optional)
ollama run llama2
# Type a question and see it respond
# Type 'quit' to exit
```

---

## Expected Results

### Before (Current State)
```
LLM Pool Management
├─ Error ⚠️
├─ Available LLMs: 0 ← Problem
├─ "No available assistants found"
└─ Nothing in the list
```

### After (What You'll See)
```
LLM Pool Management
├─ Ready ✅ ← Changed!
├─ Available LLMs: 1 ← Changed!
├─ Green section appears:
│  ✨ Auto-Selected Best Options
│  ├─ llama2 (Priority: 65)
│  └─ [Click to select]
└─ Success! ✅
```

---

## Progress Tracker

Track your progress as you go:

```
□ Downloaded Ollama installer
□ Installed Ollama on Windows
□ Verified Ollama is running
□ Downloaded llama2 model
□ Verified model in list
□ Refreshed Q-IDE in browser
□ Saw Ollama auto-detect in Q-IDE
□ ✅ ALL DONE!
```

---

## Troubleshooting Quick Links

If you get stuck:

| Problem | Solution |
|---------|----------|
| "ollama command not found" | Restart PowerShell or computer |
| Model download is slow | Normal (2-10 min). Check internet speed. |
| Q-IDE still shows "0 available" | Close/reopen Q-IDE, press F5, wait 5 sec |
| Ollama not in system tray | Check Services (Ctrl+Alt+Delete) or restart |
| "Disk space" error | Need 5GB free. Delete files or try smaller model. |

---

## Next Steps After This Works

### Immediate (Required for Q-IDE to work)
```
□ Select Ollama from the green box in Q-IDE
□ Click to confirm
□ Open Q Assistant chat
□ Ask: "What model are you using?"
□ You should get a response
```

### Soon (Optional but recommended)
```
□ Get Google API key for backup
□ Add it to Q-IDE via Providers tab
□ Have both Ollama + Google available
```

### Later (When ready for collaboration)
```
□ Start working on collaboration features
□ Use Q Assistant for code generation
□ Pair programming setup
□ Real-time code review
```

---

## Time Estimate

```
Step 1: Download        2 min   ⏱️
Step 2: Install         5 min   ⏱️
Step 3: Verify install  2 min   ⏱️
Step 4: Download model  7 min   ⏱️ (mostly waiting)
Step 5: Verify model    1 min   ⏱️
Step 6: Refresh Q-IDE   2 min   ⏱️
Step 7: Verify detect   1 min   ⏱️
                      ─────────
TOTAL:                 20 min

Most of this is waiting for downloads/installs
Actual work: ~5-7 minutes
```

---

## You Got This! 🚀

Follow each step in order. It's designed to be very simple and straightforward.

**Expected outcome after 20 minutes:**
- ✅ Ollama installed locally
- ✅ llama2 model cached
- ✅ Q-IDE auto-detects it
- ✅ Ready to use Q Assistant
- ✅ Ready for next phase!

---

**Start with Step 1 now. Come back here to check off each step as you complete it.**
