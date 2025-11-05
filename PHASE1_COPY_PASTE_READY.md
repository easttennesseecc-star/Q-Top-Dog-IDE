# 🚀 Phase 1 - Apply Pattern Now (Copy-Paste Ready)

## Your Next Actions: 3 Simple Steps

### STEP 1️⃣: Add Imports to Route Files (2 min)

Add these lines to the **top** of each route file you're protecting:

**File: `backend/llm_chat_routes.py`**
Add after existing imports (line ~15):
```python
from fastapi import Header, Depends
from middleware.tier_validator import require_tier_access
```

**File: `backend/build_orchestration_routes.py`**
Add after existing imports:
```python
from fastapi import Header, Depends
from middleware.tier_validator import require_tier_access
```

**File: `backend/routes/orchestration_workflow.py`**
Add after existing imports:
```python
from fastapi import Header, Depends
from middleware.tier_validator import require_tier_access
```

---

### STEP 2️⃣: Apply Pattern to Each Endpoint (30 sec per endpoint)

#### Priority 1: Chat Endpoint

**File: `backend/llm_chat_routes.py`, Line ~56**

**Before:**
```python
@router.post("/")
async def chat_stream(request: ChatRequest = Body(...)):
```

**After:**
```python
@router.post("/")
async def chat_stream(
    request: ChatRequest = Body(...),
    user_id: str = Header(None, alias="X-User-ID"),
    tier_info = Depends(lambda: require_tier_access(
        feature='code_execution',
        user_id=user_id
    ))
):
```

---

#### Priority 2: Build Execute Endpoint

**File: `backend/build_orchestration_routes.py`** (find the POST /execute endpoint)

**Before:**
```python
@router.post("/execute")
async def execute_build(config: BuildConfig = Body(...)):
```

**After:**
```python
@router.post("/execute")
async def execute_build(
    config: BuildConfig = Body(...),
    user_id: str = Header(None, alias="X-User-ID"),
    tier_info = Depends(lambda: require_tier_access(
        feature='code_execution',
        user_id=user_id
    ))
):
```

---

#### Priority 3: Webhook Endpoint

**File: `backend/routes/orchestration_workflow.py`** (find the POST / endpoint)

**Before:**
```python
@router.post("/")
async def create_workflow(config: WorkflowConfig = Body(...)):
```

**After:**
```python
@router.post("/")
async def create_workflow(
    config: WorkflowConfig = Body(...),
    user_id: str = Header(None, alias="X-User-ID"),
    tier_info = Depends(lambda: require_tier_access(
        feature='webhooks',
        user_id=user_id
    ))
):
```

---

### STEP 3️⃣: Test with Curl Commands (5 min)

Open PowerShell and run these commands:

```powershell
# Test 1: FREE user should be BLOCKED (403)
Write-Host "Test 1: FREE user (should block)" -ForegroundColor Cyan
curl -X POST http://localhost:8000/api/chat/ `
  -H "Content-Type: application/json" `
  -H "X-User-ID: test-free" `
  -d '{"message":"Hello"}'
# Expected: 403 Forbidden with upgrade_url

# Test 2: PRO user should be ALLOWED (200)
Write-Host "`nTest 2: PRO user (should allow)" -ForegroundColor Cyan
curl -X POST http://localhost:8000/api/chat/ `
  -H "Content-Type: application/json" `
  -H "X-User-ID: test-pro" `
  -d '{"message":"Hello"}'
# Expected: 200 OK with response

# Test 3: Check rate limit
Write-Host "`nTest 3: Rate limiting (20 calls max for FREE)" -ForegroundColor Cyan
for ($i=1; $i -le 25; $i++) {
  curl -s http://localhost:8000/api/user/tier `
    -H "X-User-ID: test-free" | ConvertFrom-Json | Select-Object tier_name, remaining_calls | Format-Table
  Start-Sleep -Milliseconds 100
}
# After call 20: Should show 429 Too Many Requests
```

---

## ✅ Verification Checklist

After applying the pattern:

- [ ] Imports added to all 3 route files
- [ ] Pattern applied to chat endpoint (POST /api/chat/)
- [ ] Pattern applied to build endpoint (POST /api/build/execute)
- [ ] Pattern applied to workflow endpoint (POST /api/workflows/)
- [ ] Test 1: FREE user blocked with 403
- [ ] Test 2: PRO user allowed with 200
- [ ] Test 3: Rate limiting works (20 calls max)
- [ ] No error logs in terminal

---

## 🎯 What Happens When You Run This

### For FREE Users:
```
curl -X POST http://localhost:8000/api/chat/ \
  -H "X-User-ID: test-free" \
  -d '{"message":"Hello"}'

Response (403):
{
  "detail": "Feature not available in tier",
  "current_tier": "free",
  "required_tier": "pro",
  "upgrade_url": "https://Top Dog.com/pricing",
  "upgrade_to": "pro",
  "feature": "code_execution"
}
```

### For PRO Users:
```
curl -X POST http://localhost:8000/api/chat/ \
  -H "X-User-ID: test-pro" \
  -d '{"message":"Hello"}'

Response (200 OK):
{
  "data": "...",
  "tier": "pro",
  "remaining_calls": 9999,
  "usage": {"today": 1}
}
```

---

## 🐛 If Something Goes Wrong

### Error: "X-User-ID header missing"
```
Solution: Add the header to your curl command:
curl -H "X-User-ID: test-pro" ...
```

### Error: "User not found"
```
Solution: Create test users first:
sqlite3 backend/q_ide.db
INSERT INTO user_subscriptions (user_id, tier_name, is_trial, created_at)
VALUES ('test-free', 'free', 0, datetime('now'));

INSERT INTO user_subscriptions (user_id, tier_name, is_trial, created_at)
VALUES ('test-pro', 'pro', 0, datetime('now'));
```

### Error: "Module not found: tier_validator"
```
Solution: Check import path:
# Should be:
from middleware.tier_validator import require_tier_access

# Not:
from tier_validator import require_tier_access
```

### Error: "Depends() not recognized"
```
Solution: Add import:
from fastapi import Depends, Header
```

---

## ⏱️ Total Time: 40 Minutes

- Add imports: 2 min
- Apply pattern to 3 endpoints: 15 min (5 min each)
- Test: 5 min
- Verify: 3 min
- **Total: ~25 min**

Then move to Phase 2 (React): 2-3 hours

---

## 📞 Need Help?

If you get stuck, let me know:
1. Which endpoint you're updating
2. What error you're seeing
3. I'll provide the exact fix

---

## 🎉 When Complete

You'll have Phase 1 LIVE:
- ✅ API enforcement working
- ✅ FREE users blocked from paid features
- ✅ Rate limiting enforced
- ✅ Ready for Phase 2 (React UI components)

**Next Phase**: Build React component to show tier info in UI (2-3 hours)
