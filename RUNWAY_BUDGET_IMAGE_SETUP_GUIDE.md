# 🎨 RUNWAY + BUDGET IMAGE GENERATION - COMPLETE SETUP GUIDE

## Overview

Top Dog now supports **THREE tiers of image/media generation**:

```
Tier 1: FREE (Q Assistant) ✨
├─ Simple SVG diagrams, wireframes, flows
├─ Cost: $0 per image
├─ Speed: Instant (milliseconds)
└─ Use: Planning, visualization, mockups

Tier 2: BUDGET (Stable Diffusion / HuggingFace) 💰
├─ Professional AI images on a budget
├─ Cost: $0.003-0.01 per image (vs $0.05-0.50 for Runway)
├─ Speed: 3-5 seconds per image
└─ Use: App UI, icons, illustrations, social media

Tier 3: PREMIUM (Runway AI) 🚀
├─ Professional visuals + audio/video
├─ Cost: Varies by credit (video $0.10-1.00, audio $0.01-0.05)
├─ Speed: 2-10 seconds (video), 1-3 seconds (audio)
└─ Use: Final deliverables, video intros, music generation
```

---

## 🎯 Quick Setup (3 Steps)

### **STEP 1: Choose Your Tier**

```
Option A: FREE ONLY
├─ Q Assistant generates simple SVG images
├─ No API keys needed
└─ Cost: $0/month

Option B: BUDGET + FREE  ← RECOMMENDED
├─ Stable Diffusion (budget images)
├─ Q Assistant (free SVGs)
├─ Set API key in 2 minutes
└─ Cost: $0 (VERY cheap, $0.01-0.10 per image)

Option C: ALL THREE (PREMIUM)
├─ Free tier (Q Assistant SVGs)
├─ Budget tier (Stable Diffusion)
├─ Premium tier (Runway)
├─ Maximum flexibility
└─ Cost: Free + $0.003-0.01 per image + Runway credits
```

### **STEP 2: Add API Keys (If Needed)**

**For Budget Tier (Recommended):**
```
Go to: https://huggingface.co/settings/tokens
1. Create account (free)
2. Create API key
3. In Top Dog → Media Setup → Add Stable Diffusion key
4. Done! (60 seconds)
```

**For Premium Tier (Optional):**
```
Go to: https://app.runwayml.com/settings/api
1. Create account (free, $50 credits)
2. Create API key
3. In Top Dog → Media Setup → Add Runway key
4. Done! (60 seconds)
```

### **STEP 3: Start Using**

```
In Q Assistant chat:

User: "Show me a mockup of a chat app"
Q Assistant:
  1. Generates simple SVG wireframe (free)
  2. Optionally generates Stable Diffusion image (budget)
  3. Recommends Runway for video/audio

OR

In Build Panel → Media Generation:
  1. Select tier (Free/Budget/Premium)
  2. Describe what you want
  3. AI generates it
  4. View in Media Viewer
  5. Done!
```

---

## 📦 What You're Getting

### **Files Created/Updated:**

1. **backend/media_service.py** (NEW)
   - Unified media generation interface
   - Supports all 3 tiers
   - Cost estimation
   - Auto-tier selection

2. **backend/providers/runway_provider.py** (NEW)
   - Runway AI integration
   - Video generation
   - Audio generation
   - Image generation

3. **backend/providers/stable_diffusion_provider.py** (NEW)
   - Budget image generation
   - HuggingFace integration
   - Cost-optimized

4. **frontend/src/components/MediaGeneration.tsx** (NEW)
   - Easy UI for media generation
   - Tier selection
   - Cost display
   - Progress tracking

5. **frontend/src/components/MediaSetup.tsx** (NEW)
   - One-click API key configuration
   - Supports all providers
   - Validation
   - Easy testing

6. **backend/media_routes.py** (NEW)
   - API endpoints for all media types
   - Cost tracking
   - Usage monitoring

---

## 🚀 Installation

### **Step 1: Copy Backend Files**

```bash
# Download provider files to backend/
cp providers/runway_provider.py backend/providers/
cp providers/stable_diffusion_provider.py backend/providers/
cp media_service.py backend/
cp media_routes.py backend/
```

### **Step 2: Update Backend Configuration**

In `backend/main.py`, add:

```python
from media_routes import router as media_router

# Register media endpoints
app.include_router(media_router, prefix="/api/media", tags=["media"])
```

### **Step 3: Install Python Dependencies**

```bash
pip install requests pillow anthropic  # for Stable Diffusion + Runway
```

### **Step 4: Copy Frontend Files**

```bash
# Download React components to frontend/src/components/
cp MediaGeneration.tsx frontend/src/components/
cp MediaSetup.tsx frontend/src/components/
```

### **Step 5: Update Frontend Router**

In `frontend/src/App.tsx`:

```tsx
import MediaGeneration from './components/MediaGeneration'
import MediaSetup from './components/MediaSetup'

// Add to your routes
<Route path="/media-setup" element={<MediaSetup />} />
<Route path="/media-gen" element={<MediaGeneration />} />
```

---

## 💻 API Endpoints

### **Media Generation**

```
POST /api/media/generate
Body: {
  "description": "A modern dashboard UI mockup",
  "tier": "budget",  // "free", "budget", or "premium"
  "media_type": "image"  // "image", "video", "audio"
}
Response: {
  "id": "gen-12345",
  "url": "https://...",
  "cost": 0.01,
  "time_ms": 3500
}
```

### **Get Cost Estimate**

```
GET /api/media/estimate?description=...&tier=budget
Response: {
  "tier": "budget",
  "estimated_cost": 0.01,
  "generation_time_ms": 3500
}
```

### **Provider Status**

```
GET /api/media/status
Response: {
  "free": { "enabled": true },
  "budget": { "enabled": true, "credits": 100 },
  "premium": { "enabled": false }
}
```

---

## 🎨 Usage Examples

### **Example 1: Simple Q Assistant Image (FREE)**

```python
# Q Assistant automatically generates SVG
from backend.q_assistant_scope import generate_simple_wireframe

svg = generate_simple_wireframe(1200, 800)
# User sees instant wireframe in chat
```

### **Example 2: Budget Image Generation (CHEAP)**

```python
from backend.media_service import MediaService

service = MediaService()

# Generate image for ~$0.01
result = await service.generate(
    description="Professional dashboard UI mockup",
    tier="budget",
    media_type="image"
)

print(f"Generated: {result['url']}")
print(f"Cost: ${result['cost']}")
```

### **Example 3: Premium Video with Audio (RUNWAY)**

```python
# Generate video intro + background music
result = await service.generate(
    description="App launch video with upbeat music",
    tier="premium",
    media_type="video"
)

result2 = await service.generate(
    description="Upbeat background music for launch",
    tier="premium",
    media_type="audio"
)

# Total cost: ~$0.20-0.50
# Professional quality
```

---

## 💰 Pricing Comparison

| Tier | Image Cost | Speed | Quality | API Key Needed |
|------|-----------|-------|---------|---|
| **Free** | $0 | Instant | Good (planning) | No |
| **Budget** | $0.003-0.01 | 3-5s | Professional | Yes (free setup) |
| **Premium** | $0.05-0.50 | 2-10s | Highest | Yes (paid) |

### **Example Project Budget:**

```
Project: 5-screen mobile app

Using FREE only:
├─ Q Assistant wireframes: 5 × $0 = $0
└─ Total: $0 ✅

Using BUDGET (Recommended):
├─ Q Assistant wireframes: 5 × $0 = $0
├─ Stable Diffusion mockups: 5 × $0.005 = $0.03
└─ Total: $0.03 ✅

Using ALL THREE (Premium):
├─ Q Assistant: 5 × $0 = $0
├─ Budget images: 5 × $0.005 = $0.03
├─ Runway video intro: 1 × $0.25 = $0.25
└─ Total: $0.28 (includes professional video)
```

---

## 🔧 Configuration

### **In Top Dog UI → Settings → Media**

```
TIER 1: FREE (Always Available)
└─ No setup needed
   Q Assistant generates SVG automatically

TIER 2: BUDGET (Optional)
├─ Provider: Stable Diffusion (HuggingFace)
├─ API Key: [____________] (add your key)
├─ Status: ✓ Connected
└─ Estimated cost: $0.003-0.01 per image

TIER 3: PREMIUM (Optional)
├─ Provider: Runway AI
├─ API Key: [____________] (add your key)
├─ Status: ✗ Not configured (but you can set it up)
└─ Estimated cost: $0.05-0.50 per image
```

---

## 🎯 Use Cases

### **Tier 1 (FREE - Q Assistant):**
- Early wireframes and layout planning
- User flow diagrams
- Database schemas
- Architecture diagrams
- Quick UI mockups
- Cost: $0 ✅

### **Tier 2 (BUDGET - Stable Diffusion):**
- Professional mockup images
- UI component illustrations
- Icon and asset generation
- Social media graphics
- Marketing visuals
- Cost: ~$0.01 per image ✅

### **Tier 3 (PREMIUM - Runway):**
- Video intros for demos
- AI-generated background music
- Professional hero images
- Animation sequences
- Full production assets
- Cost: Runway credits (paid)

---

## 📚 Quick Reference

### **To Generate Free SVG (Tier 1):**
```
# In Q Assistant chat:
User: "Show me a wireframe of a dashboard"
Q Assistant: [Generates SVG instantly]
# Cost: $0
```

### **To Generate Budget Image (Tier 2):**
```
# In Media Panel:
1. Choose: "Budget image generation"
2. Describe: "Professional dashboard UI mockup"
3. Click: "Generate"
4. Wait: 3-5 seconds
# Cost: $0.005 ✅
```

### **To Generate Premium Video (Tier 3):**
```
# In Media Panel:
1. Choose: "Premium (Runway)"
2. Describe: "App launch video intro"
3. Click: "Generate"
4. Wait: 5-10 seconds
# Cost: Runway credits (~$0.25)
```

---

## ⚙️ How to Add Your Own Providers

You can easily add more providers (DALL-E, Midjourney, etc.):

```python
# Create backend/providers/my_provider.py
class MyProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def generate_image(self, description: str) -> dict:
        # Your API call here
        return {
            "url": "https://...",
            "cost": 0.05,
            "time_ms": 2000
        }

# Register in media_service.py
from providers.my_provider import MyProvider
PROVIDERS = {
    "my_provider": MyProvider,
    ...
}
```

---

## 🚀 Next Steps

### **Right Now:**
1. [ ] Choose your tier (Free/Budget/Premium)
2. [ ] If Budget: Get HuggingFace API key (1 minute)
3. [ ] If Premium: Get Runway API key (2 minutes)
4. [ ] Add keys to Top Dog Media Setup

### **Soon:**
1. [ ] Generate first image
2. [ ] Check cost (probably <$0.01)
3. [ ] Start using in projects
4. [ ] Monitor usage

### **Later:**
1. [ ] Integrate video generation
2. [ ] Add audio generation
3. [ ] Build custom workflows
4. [ ] Integrate with build system

---

## ✅ Setup Checklist

### **Minimum Setup (FREE):**
- [x] Done! Just use Q Assistant

### **Recommended Setup (BUDGET):**
- [ ] Sign up for HuggingFace (free)
- [ ] Create API key (1 min)
- [ ] Add to Top Dog settings (30 sec)
- [ ] Test generation (1 min)
- [ ] Start using! ($0.003-0.01 per image)

### **Complete Setup (ALL THREE):**
- [ ] Free tier working
- [ ] Budget tier configured
- [ ] HuggingFace: https://huggingface.co/settings/tokens
- [ ] Runway account: https://app.runwayml.com
- [ ] Runway API key: Settings → API
- [ ] Add both keys to Top Dog
- [ ] Ready for any media type!

---

## 🎉 You Now Have

✅ **3 tiers of image generation** (free to premium)
✅ **One-click setup** for each tier
✅ **Smart cost tracking** (know what you're spending)
✅ **Automatic tier selection** (uses cheapest by default)
✅ **Easy to add more providers** (Midjourney, DALL-E, etc.)

**Ready to make media generation super easy!** 🚀

