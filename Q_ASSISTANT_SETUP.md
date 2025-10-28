# Q Assistant LLM Setup Guide

## Overview

**Q Assistant** is now fully integrated with the LLM configuration system. Here's how to set it up to actually use an LLM for responses.

## What Changed

Previously, Q Assistant didn't have an assigned LLM. Now:

✅ **Q Assistant checks for assigned LLM** on startup
✅ **Displays which LLM is being used** in the header
✅ **Prevents chat if no LLM is configured** with helpful error message
✅ **Auto-selects best available LLM** if none explicitly assigned
✅ **Supports both cloud and local LLMs**

## Quick Start

### Step 1: Choose an LLM

**Option A: Cloud Provider (Recommended)**
- OpenAI GPT-4 (best quality, costs $)
- Google Gemini (good quality, free tier)
- Anthropic Claude (excellent reasoning)
- xAI Grok (real-time knowledge)
- Perplexity (research focused)

**Option B: Local LLM (Free, Private)**
- Ollama (easiest setup)
- LLaMA C++
- GPT4All

### Step 2: Configure the LLM

**For Cloud Providers:**

1. Open Q-IDE frontend → **LLM Setup** panel (bottom right)
2. Click **Providers** tab
3. Click setup button for your chosen provider
4. Follow instructions to get API key
5. Paste key in the panel
6. Click "Save Key"

**For Local LLMs:**

1. Install Ollama from https://ollama.ai
2. Run: `ollama pull mistral` (or other model)
3. In Q-IDE, LLM Pool will auto-detect it

### Step 3: Assign to Q Assistant

Q Assistant uses the **"Coding"** role. To assign an LLM:

1. Go to **LLM Setup** → **Roles** tab
2. Find "Code Generation" row
3. Select your configured LLM
4. Click "Assign"

Now Q Assistant will use that LLM for responses!

### Step 4: Test

1. Restart frontend (or refresh page)
2. Notification should show: "✓ Q Assistant using: [LLM Name]"
3. Try typing a message
4. If backend API isn't wired up yet, it shows: "[Q Assistant (GPT-4)] I'm ready to help!"

## Backend Implementation

### New Endpoint: `GET /llm_config/q_assistant`

Returns the LLM assigned to Q Assistant:

```bash
curl http://127.0.0.1:8000/llm_config/q_assistant
```

**Response (Configured):**
```json
{
  "status": "configured",
  "llm": {
    "id": "gpt-4",
    "name": "OpenAI GPT-4",
    "type": "cloud",
    "source": "openai",
    "assigned_role": "coding",
    "has_credentials": true,
    "endpoint": "https://api.openai.com/v1/chat/completions"
  },
  "ready": true
}
```

**Response (Not Configured):**
```json
{
  "status": "not_configured",
  "llm": null,
  "message": "Q Assistant needs an LLM. Configure one via the LLM Setup panel.",
  "instructions": "1. Go to LLM Setup → Providers\n2. Choose...",
  "ready": false
}
```

## Frontend Implementation

### New Component Features

**QAssistantChat.tsx:**
- Loads LLM config on mount
- Shows LLM name in header with pulsing indicator
- Prevents chat if no LLM configured
- Shows helpful error message

```tsx
const [llmConfig, setLLMConfig] = useState<QAssistantLLMConfig | null>(null);

// Loads on mount
useEffect(() => {
  const loadLLMConfig = async () => {
    const res = await fetch('/llm_config/q_assistant');
    if (res.ok) {
      const config = await res.json() as QAssistantLLMConfig;
      setLLMConfig(config);
    }
  };
  loadLLMConfig();
}, []);

// Guards message sending
if (!llmConfig?.ready) {
  setToast({
    message: "Q Assistant is not configured. Please set up an LLM first.",
    type: "error"
  });
  return;
}
```

### Visual Indicators

Header now shows:
- **LLM Name Badge**: Green pulsing indicator with LLM name
- **Status Line**: "Using [LLM Name]" or "LLM not configured"

## Files Modified

### Backend
- **llm_config.py**: Added `get_q_assistant_llm()` function
- **llm_config_routes.py**: Added `GET /llm_config/q_assistant` endpoint

### Frontend
- **QAssistantChat.tsx**: 
  - Added LLM config type
  - Load config on mount
  - Guard send with config check
  - Display LLM name in header

## Next Steps

1. **Wire Backend LLM Calls** (TODO)
   - Modify `/api/chat` endpoint to use selected LLM
   - Call actual LLM API (OpenAI, Anthropic, etc.)
   - Stream responses back to frontend

2. **Add More Roles**
   - Assign different LLMs to different roles
   - Use appropriate LLM for each task type

3. **LLM Switching**
   - Allow switching LLM at runtime
   - Show LLM performance stats
   - Fall back to other LLMs if one fails

4. **Local LLM Integration**
   - Auto-detect local LLMs via LLM Pool
   - Connect to Ollama/llama-cpp directly
   - Use local LLMs without internet

## Configuration Locations

**Stored Locally At:**
- `~/.q-ide/llm_roles.json` - Role assignments
- `~/.q-ide/llm_keys.json` - API keys (for cloud providers)

## Troubleshooting

**"LLM not configured" message:**
- Go to LLM Setup → Providers
- Add API key for your chosen provider
- Assign to "Code Generation" role

**"Q Assistant using: [name]" but messages don't work:**
- Backend chat API not yet connected
- Implementation in progress
- Check console for errors

**Wrong LLM being used:**
- Check Roles tab in LLM Setup
- Verify "Code Generation" role assignment
- Refresh page to reload config

**Can't see LLM name in header:**
- Page may be loading
- Try refreshing
- Check browser console for errors

## Configuration Format

**Q Assistant uses this role mapping:**

```
Q Assistant Role: "coding" (Code Generation)
├─ Falls back to: Best available LLM from pool
├─ Supports: Cloud providers + local LLMs
└─ Data: Stored in ~/.q-ide/llm_roles.json
```

Example `~/.q-ide/llm_roles.json`:
```json
{
  "coding": "gpt-4",
  "analysis": "gemini-pro",
  "research": "claude-3",
  "documentation": "gpt-4",
  "optimization": "gpt-4",
  "creative": "claude-3",
  "local": "ollama"
}
```

When "coding" role has no assignment → auto-selects best LLM from pool.

## API Integration Example

Once backend chat endpoint is fully wired:

```python
# backend/main.py
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    # Get Q Assistant's assigned LLM
    llm_config = get_q_assistant_llm()
    
    if not llm_config:
        return {"error": "No LLM configured"}
    
    # Route to appropriate LLM
    if llm_config["type"] == "cloud":
        # Call OpenAI, Gemini, Claude, etc.
        response = call_cloud_llm(
            llm_config["source"],
            llm_config["endpoint"],
            request.message
        )
    else:
        # Call local LLM via Ollama or similar
        response = call_local_llm(
            llm_config["id"],
            request.message
        )
    
    return {"response": response}
```

---

## Summary

✅ Q Assistant now knows which LLM to use
✅ Visual indicator in header shows assigned LLM
✅ Auto-selects best available if none assigned
✅ Prevents chat if no LLM configured
✅ Supports both cloud and local LLMs
✅ Full REST API for configuration

**Next: Wire the backend to actually call the assigned LLM!**
