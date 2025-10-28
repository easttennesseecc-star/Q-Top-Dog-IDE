# 🚀 Q-IDE Quick Start - 3 Steps to Building Apps with AI

## Step 1: Prerequisites (5 minutes)

Your PC needs:
- **Python 3.11+** - Download from https://www.python.org/downloads/
- **Node.js 18+** - Download from https://nodejs.org/

**Important:** When installing, check ✅ **"Add to PATH"**

Verify installation (open Command Prompt):
```
python --version
node --version
```

Should show version numbers, not "command not found"

---

## Step 2: Install Q-IDE (5 minutes)

### Option A: Click & Go (Easiest)
1. Open `c:\Quellum-topdog-ide\` folder
2. Double-click **`INSTALL.bat`**
3. Wait for green [OK] messages
4. You'll see: `[SUCCESS] Installation complete!`

### Option B: Manual Install
```powershell
cd c:\Quellum-topdog-ide
pip install -r backend/requirements.txt
cd frontend
pnpm install
```

**That's it! Dependencies installed.**

---

## Step 3: Launch & Use (1 minute)

### Start the App

Double-click: **`START.bat`**

This opens **two windows**:
- **Backend** - Shows: `INFO: Application startup complete`
- **Frontend** - Shows: `VITE ready in XXX ms`

### Open in Browser

```
http://localhost:1431
```

You'll see: "Welcome to Q-IDE! Set up your AI team"

---

## Now What?

### First Time Setup (3-5 minutes)

1. **Click** "Start Setup"
2. **Choose** an LLM provider:
   - OpenAI (GPT-4, GPT-3.5) - **RECOMMENDED**
   - Anthropic (Claude) - EXCELLENT
   - Google (Gemini) - Good & Free
   - Mistral - Fast & Cheap

3. **Sign up** (all have free $5 credits):
   - OpenAI: https://platform.openai.com/account/api-keys
   - Anthropic: https://console.anthropic.com/account/keys
   - Google: https://makersuite.google.com/app/apikey
   - Mistral: https://console.mistral.ai/

4. **Paste** your API key into Q-IDE

5. **Click** "Complete Setup"

Q-IDE automatically:
- ✅ Tests your API
- ✅ Assigns best models to roles
- ✅ Shows cost estimate
- ✅ Ready to build!

### Build Your First App (10-30 minutes)

1. **Click** "Create New Project"
2. **Describe** what you want to build
   - Example: "A project management tool with tasks, teams, and real-time updates"
3. **Q-IDE Orchestrates:**
   - 🎯 Q Assistant extracts requirements
   - 💻 Code Writer generates implementation
   - ✅ Test Auditor creates tests
   - 🔍 Verification Overseer checks quality
   - 📦 Release Manager creates docs
4. **Get** your complete codebase
5. **Download** and run!

---

## Cost Estimate

| Plan | Monthly | Best For |
|------|---------|----------|
| **Free Trial** | $0 (using free $5 credits) | Learning & Prototypes |
| **Starter** | $5-10 | Real projects, tight budget |
| **Professional** | $20-50 | Complex apps, best quality |

---

## Troubleshooting

### "Python/Node not found"
1. Reinstall Python/Node
2. **IMPORTANT:** Check ✅ "Add to PATH"
3. Restart your PC
4. Try again

### Setup Wizard doesn't appear
1. Check backend is running (first window shows `Application startup complete`)
2. Refresh browser (Ctrl+R or Cmd+R)
3. Check http://localhost:1431 in address bar

### API Key rejected
1. Make sure it's the correct key format
2. Try creating a new key on provider website
3. Copy exactly - no extra spaces!

### Slow performance
- If using free tier: Expected (rate limited)
- Upgrade to paid to get faster responses

---

## Useful Endpoints

### Setup Wizard
```
http://localhost:1431/setup
```

### API Documentation  
```
http://localhost:8000/docs
```
(Has "Try it out" button for testing)

### View Logs
```
c:\Quellum-topdog-ide\logs\
```

---

## Your AI Team

Once setup is complete, you have:

| Role | Job | Best Model |
|------|-----|-----------|
| 🎯 **Q Assistant** | Plan projects, extract requirements | GPT-4 or Claude-3-Opus |
| 💻 **Code Writer** | Write production-ready code | Claude-3-Sonnet or GPT-4 |
| ✅ **Test Auditor** | Write comprehensive tests | GPT-3.5-Turbo or Claude-3 |
| 🔍 **Verification Overseer** | Check for mistakes/hallucinations | Claude-3 or Gemini |
| 📦 **Release Manager** | Generate documentation & deploy | Any capable model |

**All automatically assigned based on your available APIs!**

---

## Next Steps After Launch

1. ✅ Verify Python/Node installed
2. ✅ Run `INSTALL.bat`
3. ✅ Run `START.bat`
4. ✅ Open http://localhost:1431
5. ✅ Complete Setup Wizard
6. ✅ Create your first project
7. ✅ Describe your app idea
8. 🎉 Get your codebase!

---

## Common Commands

```powershell
# Check if backend is running
curl http://localhost:8000/docs

# Check if frontend is running
curl http://localhost:1431

# Stop all services
Get-Process python* | Stop-Process -Force
Get-Process node | Stop-Process -Force

# View backend logs
Get-Content c:\Quellum-topdog-ide\logs\* -Tail 50

# Restart everything
.\START.bat
```

---

## Still Need Help?

### Check Documentation
- `README_INSTALLATION.md` - Detailed install guide
- `LLM_AUTO_ASSIGNMENT_GUIDE.md` - How AI assignment works
- `LLM_AUTO_ASSIGNMENT_SYSTEM_READY.md` - Technical reference

### API Documentation
Visit: http://localhost:8000/docs (after running START.bat)

### Test System
```powershell
cd c:\Quellum-topdog-ide
python test_q_assistant_integration.py
```
(Should show "7/7 tests passed")

---

## Ready? 

**Double-click `INSTALL.bat` to begin! 🚀**

Questions? All endpoints have built-in documentation at:
http://localhost:8000/docs
