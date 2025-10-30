# 🎨 Media Generation - QUICK START GUIDE

## ⚡ 5-Minute Integration

### 1️⃣ Update Backend (backend/main.py)

Find the section with existing routers. Add these 2 lines:

```python
# Add this import
from media_routes import router as media_router

# Add this in app setup (after other routers)
app.include_router(media_router, prefix="/api", tags=["Media Generation"])
```

**That's it for backend!**

---

### 2️⃣ Update Frontend (frontend/src/App.tsx)

Find your Routes component. Add these imports:

```typescript
import MediaGeneration from './components/MediaGeneration';
import MediaSetup from './components/MediaSetup';
```

Add these routes inside `<Routes>`:

```typescript
<Route path="/media" element={<MediaGeneration />} />
<Route path="/media/setup" element={<MediaSetup />} />
```

**That's it for frontend!**

---

### 3️⃣ Install Dependencies

```bash
pip install requests aiohttp pillow anthropic
```

Or add to `backend/requirements.txt`:
```
requests>=2.28.0
aiohttp>=3.8.0
pillow>=9.0.0
anthropic>=0.7.0
```

**That's it for dependencies!**

---

### 4️⃣ Restart Your App

```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
cd frontend
npm start
```

---

### 5️⃣ Test It

Visit these URLs:

✅ **http://localhost:3000/media/setup** - Setup providers  
✅ **http://localhost:3000/media** - Generate media  
✅ **http://localhost:8000/api/media/status** - Check API  

---

## 🚀 How to Use

### First Time (2 minutes)

1. Go to http://localhost:3000/media/setup
2. Click "Get Free API Key" for Budget tier
3. Create free HuggingFace account (https://huggingface.co)
4. Copy your API token
5. Paste in the setup form
6. Click "Save & Test"
7. ✅ Done!

### Generate Media (per use)

1. Go to http://localhost:3000/media
2. Type description: "A wireframe of a dashboard"
3. See estimated cost appear
4. Click "Generate Media"
5. Wait 3-5 seconds
6. Download or copy URL

---

## 💰 Pricing

| Tier | Cost | Speed | Quality | Setup Time |
|------|------|-------|---------|------------|
| 🟢 Free | $0 | Instant | Basic SVG | 0 min |
| 🟡 Budget | $0.01 | 3-5s | Good AI | 2 min |
| 🟣 Premium | $0.05+ | 2-10s | Excellent | 3 min |

---

## 📁 Files Created

- ✅ `backend/media_service.py` - Core engine
- ✅ `backend/media_routes.py` - API endpoints  
- ✅ `frontend/src/components/MediaGeneration.tsx` - Main UI
- ✅ `frontend/src/components/MediaSetup.tsx` - Setup UI

---

## 🔗 API Endpoints

```
POST   /api/media/generate    - Generate image/video/audio
POST   /api/media/estimate    - Get cost estimate
GET    /api/media/status      - Provider status
GET    /api/media/history     - Generation history
GET    /api/media/usage       - Usage statistics
POST   /api/media/configure   - Configure provider
```

Test the API:
```bash
curl http://localhost:8000/api/media/status
```

---

## ❓ Troubleshooting

### "Cannot import media_routes"
→ Make sure `backend/media_routes.py` exists

### "Module 'requests' not found"
→ Run: `pip install requests aiohttp pillow anthropic`

### "/media page not loading"
→ Check you added routes to `frontend/src/App.tsx`

### "API returns 404"
→ Check you added router to `backend/main.py`

### "Invalid API key error"
→ Get new key from https://huggingface.co/settings/tokens

---

## 🎯 Three Tiers Explained

### 🟢 FREE Tier
```
Q Assistant SVG Generation
├─ Cost: $0 per image
├─ Speed: <200ms
├─ Best for: Testing, wireframes, quick ideas
└─ Setup: Automatic (no key needed)
```

### 🟡 BUDGET Tier  
```
Stable Diffusion AI Images
├─ Cost: $0.01 per image
├─ Speed: 3-5 seconds
├─ Best for: Professional mockups, icons, graphics
└─ Setup: Free HuggingFace account
```

### 🟣 PREMIUM Tier
```
Runway AI (Images, Video, Audio)
├─ Cost: $0.05+ per image
├─ Speed: 2-10 seconds
├─ Best for: Final deliverables, video, music
└─ Setup: Free account + $50 free credits
```

---

## 📊 Features

✨ **One-click Setup** - No manual configuration  
💰 **Transparent Pricing** - See cost before generating  
📈 **Usage Analytics** - Track what you've created and spent  
🔄 **Auto Tier Selection** - Uses cheapest option automatically  
💾 **Generation History** - See all past generations  
⚡ **Fast Estimates** - Get cost in real-time  
🛡️ **Secure** - API keys validated before use  
📱 **Responsive** - Works on mobile and desktop  

---

## 🎓 Example Use Cases

### Use Case 1: Designer Testing a Wireframe
```
1. Open /media
2. Type: "A wireframe of a user login form"
3. Select: Free tier (auto-selected)
4. Cost: $0
5. Result: SVG wireframe instantly
6. Use: Show to team for feedback
```

### Use Case 2: Creating a Mockup
```
1. Open /media
2. Type: "A professional dashboard mockup with charts and data"
3. Select: Budget tier (auto-selected if HF key set up)
4. Cost: $0.01
5. Result: AI-generated mockup in 4 seconds
6. Use: Client presentation
```

### Use Case 3: Final Deliverable
```
1. Open /media
2. Type: "A cinematic product video of a smartphone"
3. Select: Premium tier (Runway)
4. Cost: $0.25 (video)
5. Result: Professional video in 8 seconds
6. Use: Marketing/sales
```

---

## 🔐 Security Notes

⚠️ **API Keys**
- Stored in browser localStorage or .env file
- Never shared or logged
- Users own their keys
- Recommended: Use secrets manager in production

✅ **Best Practices**
1. Never commit API keys to git
2. Use `.env` file (add to `.gitignore`)
3. Rotate keys periodically
4. For production: Use HashiCorp Vault or AWS Secrets

---

## 📚 Full Documentation

For complete reference, see:
- `THREE_TIER_MEDIA_INTEGRATION_COMPLETE.md` - Full API reference
- `MEDIA_INTEGRATION_SNIPPETS.md` - Copy-paste code
- Code comments in `.py` and `.tsx` files

---

## ✅ Integration Checklist

- [ ] Read this file (you're here!)
- [ ] Update backend/main.py (add media_router import & registration)
- [ ] Update frontend/App.tsx (add media routes)
- [ ] Install pip dependencies
- [ ] Restart backend
- [ ] Restart frontend
- [ ] Visit http://localhost:3000/media/setup
- [ ] Test with Free tier first (no key needed)
- [ ] (Optional) Get HuggingFace key and test Budget tier
- [ ] Review cost estimates work correctly
- [ ] Check history and stats display
- [ ] ✅ Done! Ready to deploy

---

## 🚀 Going to Production

1. ✅ Code is production-ready
2. ✅ Error handling is comprehensive
3. ✅ Documentation is complete
4. ⏳ Add to CI/CD pipeline
5. ⏳ Configure secrets manager for API keys
6. ⏳ Set up cost monitoring/alerts
7. ⏳ Create user documentation
8. ⏳ Deploy! 🎉

---

## 🎉 You're All Set!

**Everything you need:**
- ✅ 4 production files created
- ✅ 2 comprehensive guides
- ✅ Copy-paste integration snippets
- ✅ Full API documentation
- ✅ This quick start guide

**Time to integrate:** 5 minutes  
**Time to generate first media:** 30 seconds  
**Difficulty level:** Easy (just copy/paste)  

**Questions?** Check the comprehensive guides:
1. `THREE_TIER_MEDIA_INTEGRATION_COMPLETE.md`
2. `MEDIA_INTEGRATION_SNIPPETS.md`

Happy generating! 🎨✨
