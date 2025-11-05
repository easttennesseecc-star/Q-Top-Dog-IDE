# ⚡ GET MODELS WORKING NOW - Quick Action Guide

**Your Situation**: README says models auto-appear, but you see "0 Available"  
**Truth**: They will auto-appear once you install/configure them  
**Time to Fix**: 2-20 minutes (choose your path)

---

## 🚀 Option 1: Ollama (5 Minutes, FREE)

**Best for**: Testing, privacy, no API costs

### Installation
```
1. Go to: https://ollama.ai
2. Click "Download for Windows"
3. Run the installer
4. It will start automatically
```

### Get a Model (First Time Only)
```
1. Open PowerShell
2. Run: ollama pull llama2
3. Wait for download (~4 GB takes 2-5 minutes depending on internet)
4. Done!
```

### Verify in Top Dog
```
1. Refresh Top Dog (F5)
2. Go to LLM Pool Management tab
3. Should see green section: "✨ Auto-Selected Best Options"
4. Ollama should be listed
5. Click to select
6. Done! ✅
```

**Total time**: 10-15 minutes first time

---

## 🔑 Option 2: Google Gemini (2 Minutes, FASTEST)

**Best for**: Quickest path, no local installation

### Get API Key
```
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API key"
3. Copy it (blue button)
4. Done!
```

### Add to Top Dog
```
1. In Top Dog, find LLM Setup panel
2. Click "Providers" tab
3. Click [Setup] next to Google Gemini
4. Dialog appears
5. Paste your API key
6. Click [Save]
```

### Verify
```
1. Look for green section: "✨ Auto-Selected Best Options"
2. Google Gemini should be there
3. Done! ✅
```

**Total time**: 2-3 minutes

---

## 🎯 Option 3: Use Both (RECOMMENDED)

Do both Ollama AND Google:

**Benefits:**
- ✅ Ollama always available (no internet needed)
- ✅ Google as backup (higher quality)
- ✅ Top Dog auto-selects Ollama (faster locally)
- ✅ You can manually switch to Google if needed

**Time**: 15-20 minutes total

---

## 🧪 Test Which Option Works for You

Open PowerShell and run:

```powershell
# Test 1: Is Ollama installed?
ollama --version
# If this works, you're good for Option 1

# Test 2: Check Top Dog LLM Pool
curl http://localhost:8000/llm_pool
# If response shows more than just download suggestions, you're good

# Test 3: Check best LLMs
curl http://localhost:8000/llm_pool/best?count=3
# If "best" array is NOT empty, LLMs are detected
```

---

## 📊 Quick Comparison

| Factor | Ollama | Google | Both |
|--------|--------|--------|------|
| **Cost** | Free | Free tier | Free |
| **Setup time** | 10-15 min | 2-3 min | 15-20 min |
| **Speed** | Fast (local) | Fast (cloud) | Best of both |
| **Privacy** | 100% (local) | Cloud based | Mostly local |
| **Quality** | Good | Excellent | Excellent |
| **Need internet** | No | Yes | No (can use Ollama offline) |
| **Recommended** | ✅ Yes | ✅ Yes | ⭐⭐⭐ YES |

---

## ✅ How to Know It Worked

After you choose your option, you should see:

```
LLM Pool Management
├─ Ready ✅ (not Error)
├─ Available LLMs: 1+ (not 0)
├─ Green section appears:
│  ✨ Auto-Selected Best Options
│  ├─ Ollama (if you chose that)
│  └─ Google Gemini (if you chose that)
└─ You can click to select
```

If you don't see this, check the diagnostic guide.

---

## ❓ FAQ

**Q: Do I need BOTH Ollama AND a Google API key?**  
A: No, pick one. Both is better but not required.

**Q: Will Top Dog download models for me?**  
A: No, you download them via `ollama pull` command or get API key from provider.

**Q: Why isn't this automatic?**  
A: Models are huge (~4 GB), can't download without permission. You must choose what to install.

**Q: Can I use both?**  
A: Yes! Install Ollama + add Google API key. Top Dog will find both and auto-select the best one.

**Q: What if I see "0 available" even after installing Ollama?**  
A: Restart Top Dog or refresh the browser (F5). System scans on startup.

**Q: Is my API key sent to Top Dog servers?**  
A: NO! Top Dog stores it locally encrypted in `~/.Top Dog/llm_credentials.json`. Never sent externally (BYOK model).

**Q: Can I switch LLMs later?**  
A: Yes! Go to LLM Pool tab, click different option to select it.

**Q: What if Ollama is too slow?**  
A: Switch to Google (faster cloud) or add more VRAM to your GPU.

---

## 🎯 My Recommendation

**Start here (fastest path to working system):**

```
1. Go to: https://makersuite.google.com/app/apikey
2. Create API key (30 seconds)
3. Add to Top Dog: Providers → [Setup] → paste → [Save]
4. Refresh Top Dog (F5)
5. Should see Google Gemini in pool
6. Done in 2 minutes! ✅
```

**Later, add Ollama (for offline capability):**

```
1. Install Ollama from https://ollama.ai (5 min install)
2. Run: ollama pull llama2 (5-10 min download)
3. Refresh Top Dog (F5)
4. Should see both Ollama and Google in pool
5. Top Dog will auto-use Ollama (faster locally)
6. Perfect setup! ⭐
```

---

## Next Steps

Choose one and go:

- 👉 **Fastest**: Google Gemini (2 minutes) → [See Option 2 above](#-option-2-google-gemini-2-minutes-fastest)
- 👉 **Most Flexible**: Ollama (15 minutes) → [See Option 1 above](#-option-1-ollama-5-minutes-free)
- 👉 **Best Setup**: Both (20 minutes) → [See Option 3 above](#-option-3-use-both-recommended)

---

**Once you have ONE working, come back and tell me which you chose! Then we can start using Top Dog for collaboration features.**
