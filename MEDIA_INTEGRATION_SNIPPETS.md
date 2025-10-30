# Integration Snippets - Copy & Paste Ready

## For backend/main.py

Add this import at the top with other route imports:

```python
from media_routes import router as media_router
```

Add this in your app setup section (after other `app.include_router()` calls):

```python
# Media Generation Routes
app.include_router(
    media_router,
    prefix="/api",
    tags=["Media Generation"]
)
```

**Full example location** (add after existing routers):
```python
# Near the end of main.py, in app setup section

# ... existing routers ...

# Add media router
app.include_router(
    media_router,
    prefix="/api", 
    tags=["Media Generation"]
)

# CORS and other middleware setup continues...
```

---

## For frontend/src/App.tsx

Add these imports:

```typescript
import MediaGeneration from './components/MediaGeneration';
import MediaSetup from './components/MediaSetup';
```

Add these routes in your Routes component:

```typescript
{/* Media Generation Routes */}
<Route path="/media" element={<MediaGeneration />} />
<Route path="/media/setup" element={<MediaSetup />} />
```

**Full example in Routes:**
```typescript
<Routes>
  {/* Existing routes... */}
  
  {/* Media Generation Routes */}
  <Route path="/media" element={<MediaGeneration />} />
  <Route path="/media/setup" element={<MediaSetup />} />
  
  {/* More routes... */}
</Routes>
```

---

## For Navigation Menu

Add navigation links to your main menu/navbar:

```typescript
<nav>
  {/* Existing links... */}
  
  {/* Media Generation Links */}
  <Link to="/media/setup" className="menu-item">
    🎨 Setup Media Providers
  </Link>
  <Link to="/media" className="menu-item">
    ✨ Generate Media
  </Link>
  
  {/* More links... */}
</nav>
```

---

## Python Dependencies

Add to `backend/requirements.txt`:

```
requests>=2.28.0
aiohttp>=3.8.0
pillow>=9.0.0
anthropic>=0.7.0
```

Or install directly:

```bash
pip install requests aiohttp pillow anthropic
```

---

## Environment Variables

Create/update `backend/.env`:

```env
# Media Providers (optional - users can configure via UI)
# STABLE_DIFFUSION_KEY=your_huggingface_key_here
# RUNWAY_API_KEY=your_runway_key_here

# Other existing vars...
```

---

## Optional: Update Q Assistant Chat Component

If you want to add media generation button to QAssistantChat, add this:

```typescript
// In frontend/src/components/QAssistantChat.tsx

// Add import
import { useNavigate } from 'react-router-dom';

// In component
const navigate = useNavigate();

// Find the media generation section and replace:
<button
  onClick={() => navigate('/media')}
  className="mt-2 w-full px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded font-medium transition-all"
>
  Generate with AI ✨
</button>
```

---

## Testing Locally

Start the app and test:

```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend  
cd frontend
npm start
```

Then visit:
1. http://localhost:3000/media/setup - Setup providers
2. http://localhost:3000/media - Generate media

---

## Verification Checklist

After integration, verify:

- [ ] Backend starts without import errors
- [ ] `GET http://localhost:8000/api/media/status` returns 200
- [ ] Frontend /media/setup page loads
- [ ] Frontend /media page loads
- [ ] Can see "Generate Media" button/menu item
- [ ] Navigation links work
- [ ] No console errors in DevTools

---

## Quick Reference

**Endpoints Created:**
- `POST /api/media/generate` - Generate image/video/audio
- `POST /api/media/estimate` - Estimate cost
- `GET /api/media/status` - Provider status
- `GET /api/media/history` - Generation history
- `GET /api/media/usage` - Usage statistics
- `POST /api/media/configure` - Configure provider

**Components Created:**
- `MediaGeneration.tsx` - Main UI for generating media
- `MediaSetup.tsx` - Configuration UI for API keys

**Services Created:**
- `media_service.py` - Business logic
- `media_routes.py` - API endpoints

---

## Rollback Instructions

If you need to remove media features:

1. Delete files:
   - `backend/media_service.py`
   - `backend/media_routes.py`
   - `frontend/src/components/MediaGeneration.tsx`
   - `frontend/src/components/MediaSetup.tsx`

2. Revert changes to:
   - `backend/main.py` (remove media_router import and registration)
   - `frontend/src/App.tsx` (remove media routes and imports)
   - `backend/requirements.txt` (remove new dependencies)

3. Restart both backend and frontend

That's it! All features removed cleanly.
