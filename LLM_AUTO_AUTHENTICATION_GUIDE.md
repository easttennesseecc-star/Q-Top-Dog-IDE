# 🚀 LLM Auto-Authentication System

## Overview

Q-IDE now has an **automatic LLM credential detection and setup system** that runs on startup.

### How It Works

```
Q-IDE Starts
    ↓
Backend checks assigned LLMs
    ↓
Backend checks which have credentials
    ↓
If missing → Frontend shows prompt
    ↓
User chooses action:
├─ Add credentials now (go to Auth tab)
├─ Use alternatives (switch to ready LLMs)
└─ Proceed anyway (use smart fallbacks)
```

---

## What It Does

### On Startup (Backend)

1. **Checks Role Assignments**
   - Reads `~/.q-ide/llm_roles.json`
   - Gets all LLMs currently assigned to roles

2. **Checks Credentials**
   - For each assigned LLM, checks `~/.q-ide/llm_credentials.json`
   - Determines if API key exists

3. **Identifies Issues**
   - Makes list of LLMs that are assigned but missing credentials
   - Prepares setup information (URLs, alternatives, etc.)

4. **Logs Status**
   ```
   ✓ Q-IDE startup
   ✓ 3 LLMs authenticated and ready
   ⚠ 1 LLM needs credentials (GPT-4 assigned to Code Generation)
   ✓ Frontend will prompt user
   ```

### On Frontend Load

1. **Shows Modal If Needed**
   - Displays only if credentials are missing
   - Shows which LLMs need setup
   - Shows setup links and alternatives

2. **Gives User Options**
   ```
   Option 1: Add Credentials Now
   → Takes user to LLM Setup → Auth tab
   
   Option 2: Use Alternative LLMs  
   → Shows free/local alternatives
   
   Option 3: Proceed Without Setup
   → Continues with smart fallback responses
   ```

3. **Auto-Closes After Action**
   - Modal closes and user continues
   - Settings remembered for next session

---

## Backend Endpoints

### 1. Get Startup Status
```
GET /llm_config/startup_auth_status

Response:
{
  "assigned_llms": {"q_assistant": "gemini-pro", "coding": "gpt-4"},
  "authenticated_llms": ["gemini-pro"],
  "missing_credentials": ["gpt-4"],
  "needs_setup": [
    {
      "llm_id": "gpt-4",
      "name": "OpenAI GPT-4",
      "provider": "openai",
      "assigned_role": "Code Generation",
      "setup_url": "https://platform.openai.com/account/api-keys",
      "alternatives": ["gemini-pro", "claude-3", "ollama"]
    }
  ],
  "startup_prompt": {
    "status": "needs_setup",
    "message": "⚠️ 1 LLM needs credentials",
    "action_options": [...]
  }
}
```

### 2. Get Missing Credentials Detail
```
GET /llm_config/missing_credentials

Response:
{
  "has_issues": true,
  "missing_count": 1,
  "authenticated_count": 2,
  "details": [{...missing LLM info...}],
  "user_prompt": {...startup prompt...}
}
```

### 3. Get Auto-Setup Candidates
```
GET /llm_config/auto_setup_candidates

Response:
{
  "available_now": [
    {
      "llm_id": "gemini-pro",
      "name": "Google Gemini Pro",
      "status": "ready",
      "action": "assign_immediately"
    }
  ],
  "free_options": [
    {
      "llm_id": "ollama",
      "name": "Ollama",
      "status": "free_available",
      "action": "setup_free"
    }
  ],
  "total_options": 2
}
```

### 4. Handle User Action
```
POST /llm_config/handle_missing_credentials

Request:
{
  "action": "add_credentials" | "use_alternatives" | "proceed"
}

Response for "add_credentials":
{
  "success": true,
  "action": "redirect_to_auth",
  "message": "Go to LLM Setup → Auth tab to add credentials",
  "url": "/llm_setup_auth"
}

Response for "use_alternatives":
{
  "success": true,
  "action": "show_alternatives",
  "message": "These LLMs are ready to use",
  "alternatives": [{...}],
  "next_step": "Choose one and assign in Roles tab"
}

Response for "proceed":
{
  "success": true,
  "action": "use_fallbacks",
  "message": "Proceeding with smart fallback responses",
  "note": "Add credentials later in LLM Setup → Auth tab"
}
```

---

## Frontend Component: LLMStartupAuth.tsx

### Props
```typescript
interface LLMStartupAuthProps {
  onClose?: () => void;              // Close modal
  onAction?: (action: string, result: any) => void;  // Handle user action
}
```

### Behavior

1. **On Mount**
   - Fetches `/llm_config/startup_auth_status`
   - Shows loading spinner while fetching
   - Displays prompt if credentials needed

2. **On Action**
   - Posts user choice to backend
   - Shows loading state
   - Auto-closes after 1 second
   - Calls `onAction` callback with result

3. **Display**
   - Shows missing LLMs with emoji icons
   - Shows setup links for each LLM
   - Shows action options in buttons
   - Includes helpful info box

---

## Integration Points

### 1. Backend Startup (main.py)
```python
@app.on_event("startup")
async def startup_event():
    # ... existing code ...
    
    # Check LLM authentication status
    auth_status = check_all_llm_authentication()
    prompt = get_startup_auth_prompt()
    
    if auth_status.all_ready:
        logger.info(f"✓ All LLMs authenticated")
    else:
        logger.warning(f"⚠ {len(auth_status.missing_credentials)} LLM(s) need credentials")
        logger.info("  → Frontend will prompt user")
    
    app.llm_auth_prompt = prompt
```

### 2. Frontend App Component (App.tsx)
```typescript
const [showStartupAuthPrompt, setShowStartupAuthPrompt] = useState(true);

// ... in JSX ...
{showStartupAuthPrompt && (
  <LLMStartupAuth
    onClose={() => setShowStartupAuthPrompt(false)}
    onAction={(action, result) => {
      if (action === 'add_credentials') {
        setTab('config');  // Go to LLM Setup tab
      }
    }}
  />
)}
```

---

## User Experience Flow

### Scenario 1: All LLMs Ready ✓

```
User opens Q-IDE
    ↓
Backend: "All 3 LLMs authenticated"
    ↓
Frontend: No prompt shown
    ↓
User starts building immediately
```

### Scenario 2: One LLM Missing Credentials ⚠

```
User opens Q-IDE
    ↓
Backend: "GPT-4 assigned but no credentials"
    ↓
Frontend: Shows modal
  "⚠️ 1 LLM needs credentials"
  "GPT-4 assigned to Code Generation"
  [Add Credentials Now] [Use Alternatives] [Proceed]
    ↓
User clicks "Add Credentials Now"
    ↓
Modal closes, goes to LLM Setup → Auth tab
    ↓
User enters API key
    ↓
(Next time Q-IDE starts, no prompt shown)
```

### Scenario 3: Multiple Missing, Some Alternatives

```
User opens Q-IDE
    ↓
Backend: "GPT-4 and Claude missing, but Gemini ready"
    ↓
Frontend: Shows modal with all missing
    ↓
User clicks "Use Alternatives"
    ↓
"Gemini Pro is ready to use"
"Ollama is free and available"
"Choose one in Roles tab"
    ↓
User goes to Roles tab, reassigns
    ↓
(No more prompts until next missing LLM)
```

---

## Configuration Files

### llm_roles.json
```json
{
  "q_assistant": {
    "name": "Q Assistant",
    "description": "...",
    "model_name": "gemini-pro",
    "status": "active"
  },
  "coding": {
    "name": "Code Generation",
    "description": "...",
    "model_name": "gpt-4",
    "status": "active"
  }
}
```

### llm_credentials.json (encrypted)
```json
{
  "gemini-pro": "AIzaSy...",
  "gpt-4": "sk-proj-...",
  "claude-3": "sk-ant-..."
}
```

---

## Advanced Features

### Auto-Setup Candidates

The system automatically detects:
1. **Ready LLMs** - Have credentials, can be used now
2. **Free Options** - Free tiers (Gemini free tier, Ollama)
3. **Local Options** - Ollama, no internet needed

### Alternative LLMs

For each missing LLM, system suggests alternatives:

```
Missing: GPT-4
Suggested: Gemini Pro, Claude 3, Ollama
(In order of preference based on LLM type)
```

### Smart Fallbacks

If user chooses "Proceed":
- `simple_q_assistant.py` kicks in
- Uses intelligent response routing
- Helps user describe app requirements
- Continues building with smart responses
- Can add credentials anytime

---

## Troubleshooting

### Prompt Keeps Showing

**Problem:** Credentials saved but prompt still shows
**Solution:** 
- Restart Q-IDE backend
- Check credentials were actually saved (Auth tab shows ✓)
- Try different LLM

### Missing LLM Not Shown

**Problem:** Assigned LLM not in missing list
**Solution:**
- LLM doesn't have credentials but that's okay
- System auto-detected a working alternative
- Check roles tab for current assignment

### Can't Find Setup Link

**Problem:** Clicking provider link doesn't work
**Solution:**
- Copy link manually and paste in browser
- Check internet connection
- Try different LLM first

---

## Files Modified/Created

### New Files
- `backend/llm_auto_auth.py` - Auto-authentication logic (290 lines)
- `frontend/src/components/LLMStartupAuth.tsx` - Startup prompt UI (200 lines)

### Modified Files
- `backend/llm_config_routes.py` - Added 5 new endpoints
- `backend/main.py` - Added auto-auth check to startup
- `frontend/src/App.tsx` - Integrated LLMStartupAuth component

---

## API Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/llm_config/startup_auth_status` | GET | Full status on startup |
| `/llm_config/missing_credentials` | GET | List missing credentials |
| `/llm_config/auto_setup_candidates` | GET | Available alternatives |
| `/llm_config/handle_missing_credentials` | POST | Handle user action |

---

## Next Steps

1. **User Opens Q-IDE**
   - Startup auth check runs automatically
   - If needed, modal shows

2. **User Chooses Action**
   - Add credentials → Goes to Auth tab
   - Use alternatives → Reassigns in Roles tab
   - Proceed → Continues with fallbacks

3. **User Continues Building**
   - Q Assistant ready to help
   - Can add credentials anytime
   - No restart needed

---

## Summary

✅ **Automatic detection** of missing LLM credentials on startup
✅ **User-friendly modal** showing what needs setup
✅ **Multiple options** (add credentials, use alternatives, proceed)
✅ **Smart defaults** with alternative LLM suggestions
✅ **No restart needed** to add credentials
✅ **Complete control** - user always in charge

**Result:** Users get a smooth onboarding experience and never get stuck with missing credentials!
