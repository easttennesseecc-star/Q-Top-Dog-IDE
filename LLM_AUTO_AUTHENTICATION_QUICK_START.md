# 🎯 LLM Auto-Authentication - Quick Start

## What It Does

When Top Dog starts:

✅ Checks which LLMs are assigned to roles
✅ Checks if credentials exist for those LLMs
✅ If missing → Shows helpful modal to user
✅ User can: add credentials, use alternatives, or proceed

---

## The User Experience

### If Everything is Ready
```
User opens Top Dog
    ↓
Backend: "All LLMs authenticated ✓"
    ↓
No modal shown
    ↓
User builds immediately
```

### If Something's Missing
```
User opens Top Dog
    ↓
Backend: "GPT-4 is assigned but missing credentials ⚠"
    ↓
Modal pops up:
┌────────────────────────────────────────┐
│ ⚠️ LLM Setup Required                 │
│ 1 LLM needs credentials               │
│                                        │
│ GPT-4 (assigned to Code Generation)   │
│ [Get Key →] (link to OpenAI)          │
│                                        │
│ What do you want to do?               │
│ [Add Credentials Now] ← User clicks   │
│ [Use Alternative LLMs]                │
│ [Proceed Without Setup]               │
└────────────────────────────────────────┘
    ↓
User clicks "Add Credentials Now"
    ↓
Modal closes, Top Dog opens Auth tab
    ↓
User pastes API key, clicks Save
    ↓
Next time Top Dog starts, no modal shown
```

---

## The Three Options

### 1️⃣ Add Credentials Now
```
→ Takes you to LLM Setup → Auth tab
→ Shows all LLM providers
→ You can paste your API keys
→ Changes take effect immediately
→ No restart needed
```

### 2️⃣ Use Alternative LLMs
```
→ Shows LLMs that are ready to use
→ Shows free options (Gemini free tier, Ollama)
→ You go to Roles tab
→ Switch to a different LLM
→ Instant switch, ready to use
```

### 3️⃣ Proceed Without Setup
```
→ Closes the modal
→ Q Assistant uses smart fallbacks
→ Can answer basic questions
→ Still guided building experience
→ Add credentials anytime (no restart)
```

---

## Architecture

### Backend (auto_auth.py)
```
Startup
  ↓
Check role assignments (llm_roles.json)
  ↓
Check credentials (llm_credentials.json)
  ↓
Identify missing
  ↓
Return status + setup info
```

### Frontend (LLMStartupAuth.tsx)
```
Load
  ↓
Fetch startup status
  ↓
Show modal if needed
  ↓
User picks action
  ↓
Handle action
  ↓
Auto-close
```

---

## Endpoints

### Frontend Calls
```typescript
// On app load
GET /llm_config/startup_auth_status
// → Get what's missing and what to do

// When user clicks action
POST /llm_config/handle_missing_credentials
{action: "add_credentials" | "use_alternatives" | "proceed"}
// → Backend handles it
```

### Backend Returns
```typescript
// If all ready
{status: "ready", message: "✓ All LLMs ready"}

// If missing
{
  status: "needs_setup",
  message: "⚠️ 1 LLM needs credentials",
  missing_llms: [
    {
      name: "GPT-4",
      assigned_role: "Code Generation",
      setup_url: "https://platform.openai.com/...",
      alternatives: ["gemini", "claude", "ollama"]
    }
  ],
  action_options: [
    {option: "add_credentials", label: "Add Credentials Now"},
    {option: "use_alternatives", label: "Use Alternative LLMs"},
    {option: "proceed", label: "Proceed Without Setup"}
  ]
}
```

---

## Integration

### Backend: main.py
```python
@app.on_event("startup")
async def startup_event():
    # Check LLMs on startup
    auth_status = check_all_llm_authentication()
    if not auth_status.all_ready:
        logger.warning(f"⚠ {len(auth_status.missing_credentials)} LLM(s) need credentials")
```

### Frontend: App.tsx
```typescript
const [showStartupAuthPrompt, setShowStartupAuthPrompt] = useState(true);

<LLMStartupAuth
  onClose={() => setShowStartupAuthPrompt(false)}
  onAction={(action) => {
    if (action === 'add_credentials') setTab('config');
  }}
/>
```

---

## Real-World Scenarios

### Scenario A: Fresh Install
```
1. User downloads Top Dog
2. Opens it first time
3. No LLMs assigned yet
4. No modal shown (nothing to prompt about)
5. User goes to LLM Setup → Roles tab
6. Assigns Google Gemini to Q Assistant
7. Adds credentials in Auth tab
8. Next start: no modal (everything ready)
✓ Smooth onboarding
```

### Scenario B: Multiple LLMs
```
1. User has Gemini (working) and GPT-4 (missing creds)
2. Opens Top Dog
3. Modal shows: "GPT-4 missing credentials"
4. Also shows: "Gemini is ready to use"
5. User can:
   - Add GPT-4 credentials now
   - Use just Gemini for now
   - Switch roles to use Gemini everywhere
✓ Flexible options
```

### Scenario C: Lost Credentials
```
1. User deletes API key from provider
2. Opens Top Dog
3. Modal shows: "GPT-4 no longer authenticated"
4. Suggests: "Use Gemini (free tier) or Ollama (local)"
5. User either:
   - Generates new GPT-4 key and adds
   - Uses Gemini or Ollama
✓ Recovery path shown
```

---

## Status Messages

### Backend Logs
```
✓ Top Dog Backend starting up...
✓ Top Dog startup tasks running...
✓ Checking LLM authentication...
✓ All 3 LLMs authenticated and ready
  → Q Assistant: Gemini Pro
  → Code Generation: GPT-4
  → Code Review: Claude
✓ Backend ready on port 8000
```

### Or With Issues
```
✓ Top Dog Backend starting up...
✓ Checking LLM authentication...
⚠ 2 LLM(s) need credentials:
  - GPT-4 (assigned to Code Generation)
  - Claude (assigned to Code Review)
✓ Frontend will prompt user
✓ Backend ready on port 8000
```

---

## Files

### New
- `backend/llm_auto_auth.py` (290 lines)
- `frontend/src/components/LLMStartupAuth.tsx` (200 lines)

### Updated
- `backend/main.py` (+import, +startup check)
- `backend/llm_config_routes.py` (+5 endpoints)
- `frontend/src/App.tsx` (+import, +state, +component)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Modal keeps showing | Credentials might not be saved. Go to Auth tab and verify ✓ |
| Modal not showing but LLMs missing | Restart backend, or check llm_roles.json |
| Can't click "Add Credentials" link | Copy link to browser manually |
| Want to dismiss modal | Click X or "Proceed Without Setup" |
| Later want to add credentials | Go to LLM Setup → Auth tab (no modal needed) |

---

## Summary

### For Users:
- Opens Top Dog → Auto-check happens
- If LLMs missing → Helpful modal with options
- Choose your action → Continue building
- Can add/change credentials anytime

### For Developers:
- New `llm_auto_auth.py` module handles logic
- New endpoints in `llm_config_routes.py`
- New React component `LLMStartupAuth.tsx`
- Integrated into `main.py` startup event
- Integrated into `App.tsx` component tree

### Result:
✅ Smooth UX for missing credentials
✅ Users always know what's needed
✅ Multiple options always available
✅ No hard blocks or errors
✅ Helpful guidance throughout

---

## Reference

**Complete Guide:** `LLM_AUTO_AUTHENTICATION_GUIDE.md`
**Backend Code:** `backend/llm_auto_auth.py`
**Frontend Code:** `frontend/src/components/LLMStartupAuth.tsx`
**API Integration:** `backend/llm_config_routes.py`
