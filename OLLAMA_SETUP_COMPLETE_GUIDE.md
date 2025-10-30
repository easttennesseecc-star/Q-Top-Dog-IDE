# 🚀 Ollama Installation & Setup - Step by Step

**Objective**: Get Ollama running so Q-IDE auto-detects it  
**Time**: 15-20 minutes  
**Cost**: Free  
**Difficulty**: Very Easy

---

## Step 1: Download Ollama (2 minutes)

### Go to Ollama Website
```
1. Open your browser
2. Go to: https://ollama.ai
3. Look for big blue "Download" button
4. Click it
```

### Download for Windows
```
You'll see:
├─ macOS
├─ Linux  
└─ Windows ← Click this

The file will download:
ollama-windows-amd64.exe  (or similar name)
```

---

## Step 2: Install Ollama (3-5 minutes)

### Run the Installer
```
1. Go to Downloads folder
2. Find: ollama-windows-amd64.exe
3. Double-click it
4. Click "Yes" when asked for admin permissions
5. Follow prompts (mostly just "Next", "Finish")
```

### What Happens During Install
```
Installing...
├─ Ollama CLI tools
├─ Model cache directory
└─ Service setup

Status: "Installation complete"
       "Ollama has been installed"
```

### After Installation
```
✅ Ollama starts automatically
✅ Runs in background
✅ Ready to use immediately
```

---

## Step 3: Verify Ollama Is Running (1 minute)

### Method 1: Check System Tray (Easiest)
```
1. Look at bottom-right corner of screen
2. Find Ollama icon (looks like colorful circle)
3. If it's there and shows running → ✅ Good!
```

### Method 2: Check via PowerShell
```
Open PowerShell and run:
ollama --version

Should show something like:
ollama version is 0.1.X

If it works → ✅ Installed correctly
If "not found" → ❌ Not in PATH, try restart
```

### If Ollama Isn't Running
```
Option A: Restart your computer (forces start)

Option B: Manually start from PowerShell:
ollama serve

Option C: Check Services:
1. Press Windows + R
2. Type: services.msc
3. Look for "Ollama"
4. Right-click → Start
```

---

## Step 4: Download Your First Model (5-10 minutes)

### Open PowerShell
```
1. Right-click on desktop
2. Select "Open PowerShell here"
OR
1. Press Windows + X
2. Click "Windows PowerShell"
```

### Pull a Model
```
Run this command:
ollama pull llama2

What happens:
├─ Downloads model (~4 GB)
├─ Shows progress bar
├─ "pulling 6c59f80ead0..."
├─ "verifying sha256 digest..."
├─ "writing manifest..."
└─ "success"

This takes 2-10 minutes depending on your internet speed
```

### What This Command Does
```
ollama pull llama2
├─ "ollama" = run Ollama
├─ "pull" = download model
└─ "llama2" = which model to download

Result: llama2 model is downloaded and cached locally
        Takes up ~4 GB disk space
        Can be used offline anytime
```

---

## Step 5: Verify Model Was Downloaded (1 minute)

### Check Downloaded Models
```
In PowerShell, run:
ollama list

You should see:
NAME            ID              SIZE    MODIFIED
llama2:latest   2c26f67f5051    4.0GB   10 seconds ago
```

### If You Don't See It
```
Options:
1. Wait - download might still be in progress
2. Try again: ollama pull llama2
3. Check internet connection
4. Check disk space (need ~5 GB free)
```

---

## Step 6: Refresh Q-IDE (2 minutes)

### Refresh Your Browser
```
1. Go to Q-IDE window
2. Press F5 to refresh
3. Wait 3-5 seconds for page to load
```

### Check LLM Pool
```
After refresh, you should see:
├─ Go to "LLM Pool Management" tab
├─ Look for green section: "✨ Auto-Selected Best Options"
├─ Should see "Ollama" or "llama2" listed
└─ Shows a priority score (probably 65 pts)
```

### What You Should See
```
LLM Pool Management
├─ Ready ✅ (not Error)
├─ Available LLMs: 1 (not 0) ← THIS CHANGED!
├─ Green box at top:
│  ✨ Auto-Selected Best Options
│  └─ llama2 (via Ollama)
│     Score: 65 pts
│     [Click to select]
└─ Done! ✅
```

---

## Step 7: Select Ollama as Your LLM (1 minute)

### Click to Select
```
1. In the green "Auto-Selected Best Options" box
2. Click on the Ollama/llama2 card
3. Confirmation dialog appears
4. Click [Confirm] or [Select]
```

### Verify Selection
```
After selecting:
├─ Notification: "LLM selected" ✅
├─ Ollama is now your active LLM
├─ Q Assistant will use it for responses
└─ Ready to start using Q-IDE!
```

---

## You're Done! 🎉

You now have:
```
✅ Ollama installed locally
✅ llama2 model downloaded
✅ Q-IDE auto-detected it
✅ Ollama selected as LLM
✅ Ready to use Q Assistant
```

---

## Testing It Works

### Test 1: Open Q Assistant
```
In Q-IDE:
1. Look for chat icon or "Q Assistant" button
2. Click it
3. Open chat panel
```

### Test 2: Ask a Question
```
Type in chat:
"Hello, what model are you using?"

Expected response:
"I'm running on Ollama with the Llama2 model..."

If you get a response: ✅ WORKING!
```

### Test 3: Ask for Code
```
Type:
"Generate a simple Python function to add two numbers"

Expected: 
Code response with Python function

If you get code: ✅ FULLY WORKING!
```

---

## Troubleshooting

### Issue: "Ollama not found" in PowerShell
```
Solution: Restart PowerShell or your computer
The PATH might not be updated yet after installation
```

### Issue: Model download is slow
```
Normal: 2-10 minutes depending on internet speed
If slower: Check your internet connection speed
Alternative: Use smaller model (mistral-7b is faster)
```

### Issue: Q-IDE still shows "0 available LLMs"
```
Solution:
1. Close and reopen Q-IDE completely
2. Or: Open new tab, go to http://localhost:5173
3. Wait 5 seconds
4. Refresh page (F5)
5. If still not showing, run: ollama list (verify model exists)
```

### Issue: Ollama is slow or using too much RAM
```
This is normal:
├─ Llama2 uses ~6 GB RAM when running
├─ First response takes longer to load model into memory
├─ Subsequent responses are faster

If too slow:
├─ Use smaller model: ollama pull mistral
└─ Or: Use API key option (Google Gemini) for faster cloud option
```

### Issue: "Not enough disk space"
```
Llama2 model: ~4 GB
Mistral model: ~5 GB (smaller, faster)
Neural-chat: ~3 GB (smaller, decent quality)

Solution:
1. Free up at least 5 GB disk space
2. Run: ollama pull llama2 (again)
3. Or choose smaller model
```

---

## Next Steps After Ollama Works

### Option A: Keep Using Ollama (Good!)
```
Pros:
├─ Free forever
├─ Runs locally (no internet needed)
├─ Private (no data sent anywhere)
└─ Good quality responses

Use when: You want to work offline
```

### Option B: Add Google Gemini Too (Better!)
```
When you're ready (later):
1. Get API key from: https://makersuite.google.com/app/apikey
2. Add to Q-IDE: Providers → [Setup] → paste
3. Q-IDE will have both Ollama + Google
4. Can switch between them

Pros:
├─ Ollama for offline (fast, local)
├─ Google for complex tasks (higher quality)
├─ Best of both worlds!
```

### Option C: Try Different Models
```
After Ollama works, try other models:
ollama pull mistral      # Faster, smaller, good
ollama pull neural-chat  # Compact, good quality
ollama pull orca-mini    # Fast, small
ollama pull openhermes   # Good reasoning

Switch in Q-IDE: Pool tab → select different one
```

---

## Summary

```
✅ Installed Ollama
✅ Downloaded llama2 model  
✅ Q-IDE auto-detected it
✅ Selected Ollama as LLM
✅ Tested with Q Assistant
✅ Ready to build with AI!
```

**You're now ready to:**
- 🤖 Use Q Assistant for code generation
- 💬 Have conversations with your AI
- 🔧 Start using Q-IDE for development
- 🚀 (Later) Build collaboration features

---

## Questions?

If anything doesn't work:
1. Check "Troubleshooting" section above
2. Make sure `ollama --version` works in PowerShell
3. Make sure `ollama list` shows your downloaded model
4. Try refreshing Q-IDE (F5) or restarting browser
5. If still stuck, restart your computer (forces everything to reload)

---

**Ready? Follow the steps above and you'll have Ollama + Q-IDE working in ~15 minutes!**
