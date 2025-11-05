# 🚀 QUICK START - Phase 1 Implementation (40 min)

## What You're Doing
Adding tier protection to your FastAPI endpoints so FREE users can't access paid features.

## Files You Need (Open These)
1. `backend/llm_chat_routes.py` - Your chat endpoint
2. `backend/middleware/tier_validator.py` - Protection middleware  
3. `backend/routes/protected_endpoints.py` - Reference examples

## The Pattern (Copy-Paste This)

### Add to top of file (after imports):
```python
from fastapi import Header, Depends
from middleware.tier_validator import require_tier_access
```

### Add to endpoint function signature:
```python
async def your_function(
    request: YourModel = Body(...),
    user_id: str = Header(None, alias="X-User-ID"),
    tier_info = Depends(lambda: require_tier_access(
        feature='code_execution',  # Pick your feature
        user_id=user_id
    ))
):
```

That's it. The middleware does the rest.

---

## Features You Can Protect

| Feature | Min Tier | Price | Use Case |
|---------|----------|-------|----------|
| `code_execution` | PRO | $20 | Run code |
| `webhooks` | PRO | $20 | Automation |
| `custom_llms` | PRO-PLUS | $45 | Use own LLM |
| `team_members` | PRO-TEAM | $75 | Collaboration |
| `audit_logs` | PRO-TEAM | $75 | Compliance |

---

## Three Endpoints to Protect (Recommended Order)

### 1️⃣ Chat Endpoint
**File**: `backend/llm_chat_routes.py`, Line ~56

```python
@router.post("/")
async def chat_stream(
    request: ChatRequest = Body(...),
    user_id: str = Header(None, alias="X-User-ID"),
    tier_info = Depends(lambda: require_tier_access(feature='code_execution', user_id=user_id))
):
    # Your existing code - no changes needed
    ...
```

### 2️⃣ Build Execute Endpoint
**File**: `backend/build_orchestration_routes.py` (find POST /execute)

```python
@router.post("/execute")
async def execute_build(
    config: BuildConfig = Body(...),
    user_id: str = Header(None, alias="X-User-ID"),
    tier_info = Depends(lambda: require_tier_access(feature='code_execution', user_id=user_id))
):
    # Your existing code
    ...
```

### 3️⃣ Workflow Endpoint
**File**: `backend/routes/orchestration_workflow.py` (find POST /)

```python
@router.post("/")
async def create_workflow(
    config: WorkflowConfig = Body(...),
    user_id: str = Header(None, alias="X-User-ID"),
    tier_info = Depends(lambda: require_tier_access(feature='webhooks', user_id=user_id))
):
    # Your existing code
    ...
```

---

## Test Commands (PowerShell)

```powershell
# Test 1: FREE user should be blocked (403)
curl -X POST http://localhost:8000/api/chat/ `
  -H "Content-Type: application/json" `
  -H "X-User-ID: test-free" `
  -d '{"message":"Hello"}'

# Expected: 403 Forbidden with upgrade_url

---

# Test 2: PRO user should be allowed (200)
curl -X POST http://localhost:8000/api/chat/ `
  -H "Content-Type: application/json" `
  -H "X-User-ID: test-pro" `
  -d '{"message":"Hello"}'

# Expected: 200 OK with response
```

---

## ✅ Checklist

- [ ] Add imports to 3 route files
- [ ] Apply pattern to 3 endpoints
- [ ] Test 1: FREE user blocked
- [ ] Test 2: PRO user allowed
- [ ] No errors in terminal
- [ ] Phase 1 complete ✅

---

## If Something Breaks

**Error: "X-User-ID header missing"**
```
Add header to curl:
-H "X-User-ID: test-pro"
```

**Error: "User not found"**
```
Create test users in database:
sqlite3 backend/q_ide.db
INSERT INTO user_subscriptions (user_id, tier_name)
VALUES ('test-pro', 'pro');
```

**Error: "Module not found"**
```
Check import path - should be:
from middleware.tier_validator import require_tier_access
```

---

## 📊 What You Get

✅ FREE users see 403 + upgrade prompt
✅ PRO users can proceed
✅ All API calls logged
✅ Rate limiting enforced (20/day for FREE)
✅ Ready for Phase 2 (React UI)

---

## ⏱️ Time Estimate

- Add imports: 2 min
- Apply pattern: 15 min (5 min per endpoint)
- Test: 5 min
- Debug (if needed): 10-15 min
- **Total: 30-40 minutes**

---

## 🎯 Success = This Output

```
✅ Test 1 Result:
{
  "detail": "Feature not available in tier",
  "current_tier": "free",
  "required_tier": "pro",
  "upgrade_url": "https://Top Dog.com/pricing"
}

✅ Test 2 Result:
{
  "data": "Your chat response here...",
  "tier": "pro",
  "remaining_calls": 9999
}
```

---

## 🔄 Next Phase

After Phase 1 complete → Phase 2: React components (2-3 hrs)
- Show tier in UI
- Show usage bar
- Show upgrade buttons

---

## 📚 Full Resources

- `PHASE1_COPY_PASTE_READY.md` - Detailed copy-paste guide
- `PHASE1_API_ENFORCEMENT_GUIDE.md` - Complete reference
- `MASTER_IMPLEMENTATION_CHECKLIST.md` - All 4 phases

---

**Ready? Start with step 1 above! You got this! 🚀**
