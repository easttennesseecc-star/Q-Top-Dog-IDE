# 🚀 ONE-CLICK OLLAMA INSTALLER

## Quick Start - 3 Steps to Working AI Models

### **Step 1: Find the Installer**
Look in your Top Dog folder for:
```
INSTALL_OLLAMA_AUTO.bat
```

### **Step 2: Double-Click It**
That's it! The installer will:
- ✅ Request admin permissions (Windows will ask - click "Yes")
- ✅ Download Ollama (~50 MB)
- ✅ Install it automatically 
- ✅ Download llama2 model (~4 GB) - this takes 5-15 minutes
- ✅ Start the Ollama service
- ✅ Optionally offer Google Gemini setup

### **Step 3: Wait 15-20 Minutes**
⏱️ **Don't close the window!** The installer will:
1. Download files (2-3 min)
2. Install (2-5 min)  
3. Download model (5-15 min depending on your internet)
4. Verify everything (1 min)

---

## What Happens During Installation

### 📥 Download Phase (2-3 minutes)
```
STEP 1: DOWNLOADING OLLAMA
[████████████████░░░░░░] 75%
Downloading Ollama from: https://ollama.ai/download/OllamaSetup.exe
```

### ⚙️ Install Phase (2-5 minutes)
```
STEP 2: INSTALLING OLLAMA
[*] Starting Ollama installer...
[*] This will take 2-5 minutes
[*] Please wait...
```

### 🧠 Model Download Phase (5-15 minutes)
```
STEP 4: DOWNLOADING YOUR FIRST MODEL
[*] Downloading llama2 model (~4 GB)
[*] This will take 5-15 minutes depending on your internet speed
[*] DO NOT CLOSE THIS WINDOW

Progress:
 0% [         ] downloading...
```

This is **normal** - it's downloading the actual AI model. Your Top Dog will use this model locally.

### 🎯 Final Step - Optional Gemini Setup
```
WOULD YOU LIKE TO SET UP GOOGLE GEMINI TOO?

Google Gemini benefits:
 ✓ Free tier available (60 requests/min)
 ✓ Higher quality responses than local models
 ✓ Cloud-based (no local resources needed)

Do you want to set up Google Gemini now? (Y/N): 
```

- **Type `Y`**: Browser opens directly to Google API key signup
- **Type `N`**: Skip for now (you can add Gemini later)

---

## After Installation Completes

### ✅ Top Dog will show:
```
============================================================================
INSTALLATION COMPLETE! 🎉
============================================================================

Summary:
 ✓ Ollama downloaded and installed
 ✓ llama2 model cached locally
 ✓ Ollama service running
 ✓ Top Dog can now auto-detect it

Next steps:
 1. Go back to Top Dog
 2. Press F5 to refresh (important!)
 3. Go to "LLM Pool Management" tab
 4. Should see green box: "Auto-Selected Best Options"
 5. Ollama/llama2 should be listed
 6. Click to select it
 7. Done!
```

---

## Verify Installation in Top Dog

### **After you see the installation complete message:**

1. **Go back to Top Dog** in your browser
2. **Press F5** to refresh the page (this is important!)
3. **Wait 3-5 seconds** for it to load
4. **Look for green box** that says "Auto-Selected Best Options"
5. **You should see:**
   ```
   Ollama
   │
   ├─ llama2
   │  Provider: Ollama (Local)
   │  Status: ✅ Available
   ```

6. **Click the checkbox** to select it
7. **Boom!** You now have AI in Top Dog! 🎉

---

## Google Gemini Setup (Optional but Recommended)

### If you said **YES** during installation:
- ✅ Browser opened to Google API page
- ✅ Sign in with your Google account
- ✅ Click "Create API Key" (free tier)
- ✅ Copy the blue key
- ✅ Go to Top Dog → **Providers** tab
- ✅ Select **Google** → Paste key → Save
- ✅ Now you have **both** Ollama + Gemini!

### If you said **NO** during installation:
- Can do it anytime later
- Just visit: https://makersuite.google.com/app/apikey
- Follow same steps above

---

## Troubleshooting

### ❓ "Installation failed with error"
→ Check internet connection and try again

### ❓ "Ollama not in PATH after installation"
→ **Restart your computer** (installer might not be 100% done yet)

### ❓ "Model download seems stuck"
→ **Don't worry!** Big files take time. Look for progress output. If nothing for 5 min, check internet connection

### ❓ "Top Dog doesn't show Ollama after refresh"
→ Try these in order:
   1. **Restart Top Dog** (close browser tab, reopen)
   2. **Wait 10 seconds** then refresh F5
   3. **Check Ollama is running**: Open PowerShell and type `ollama list`
   4. **Restart computer** (Ollama service might need restart)

### ❓ "I want to use Gemini instead of Ollama"
→ Easy! You can have **both** and switch anytime:
   1. Get free API key from Google (2 min)
   2. Add to Top Dog via Providers tab
   3. In LLM Pool, you'll see both - pick whichever you want

---

## Next Steps After Installation

### 🎯 **Immediate (Right Now)**
- [ ] Run **INSTALL_OLLAMA_AUTO.bat** (double-click)
- [ ] Wait for "Installation Complete!" message
- [ ] Refresh Top Dog (F5)
- [ ] Verify Ollama appears in LLM Pool
- [ ] Select Ollama as your AI model

### 💡 **Soon (This Week)**
- [ ] Test Q Assistant with Ollama
- [ ] Optionally add Google Gemini (2-3 min setup)
- [ ] Try different models if you want

### 🚀 **Later (Once System Working)**
- We'll implement collaboration features
- Pair programming mode
- Real-time code review
- Multi-user presence

---

## Reference Guides

If you need more detailed info:
- **`OLLAMA_SETUP_COMPLETE_GUIDE.md`** - Detailed 7-step walkthrough (if something goes wrong)
- **`OLLAMA_QUICK_CHECKLIST.md`** - Quick checklist to track progress
- **`GET_MODELS_WORKING_NOW.md`** - General troubleshooting for all model types
- **`LLM_SETUP_TROUBLESHOOTING_QUICK_FIX.md`** - Comprehensive troubleshooting

---

## Questions?

The installer handles everything automatically. If you get stuck:

1. **Check the detailed guides above**
2. **Look at the error message** in the installer window
3. **Try the troubleshooting section** above
4. **Restart your computer** (fixes 80% of issues)

---

## Summary

| Step | Action | Time |
|------|--------|------|
| 1 | Find `INSTALL_OLLAMA_AUTO.bat` | - |
| 2 | Double-click it | - |
| 3 | Click "Yes" to admin prompt | 1 sec |
| 4 | Watch it download Ollama | 2-3 min |
| 5 | Watch it install | 2-5 min |
| 6 | Watch it download model | 5-15 min |
| 7 | Choose Gemini or Skip | 30 sec |
| **Total** | | **15-25 min** |

---

## You're Ready! 🚀

Just double-click `INSTALL_OLLAMA_AUTO.bat` and let it do its thing!

**Next message you see:** "Installation Complete! 🎉"

**Then:** Refresh Top Dog, select Ollama, and start building with AI! 🎉

