# Phase 1 Implementation - Action Plan

## 🎯 Quick Start (1-2 Hours)

### Step 1: Identify Key Endpoints to Protect (15 min)

Your main monetizable endpoints:

```
backend/llm_chat_routes.py
├─ POST /api/chat/          ← CODE EXECUTION (PRO+)
├─ POST /api/chat/clear-history
└─ GET /api/chat/history/{id}

backend/build_orchestration_routes.py
├─ POST /api/build/execute  ← CODE EXECUTION (PRO+)
├─ POST /api/build/validate
└─ GET /api/build/status

backend/routes/billing.py
├─ GET /api/billing/usage   ← AUDIT LOGS (PRO-TEAM+)
├─ GET /api/billing/invoice
└─ POST /api/billing/upgrade

backend/routes/orchestration_workflow.py
├─ POST /api/workflows/     ← WEBHOOKS (PRO+)
└─ GET /api/workflows/{id}
```

### Step 2: Copy Tier Validator Import (5 min)

Add to each route file that needs protection:

```python
# At top of file, after existing imports
from middleware.tier_validator import require_tier_access
from fastapi import Header, Depends
```

### Step 3: Apply Pattern to Endpoints (45 min)

**Pattern for all protected endpoints:**

```python
@router.post("/your-endpoint")
async def your_function(
    request_body: YourModel = Body(...),
    user_id: str = Header(None, alias="X-User-ID"),
    tier_info = Depends(lambda: require_tier_access(
        feature='code_execution',  # Pick from list below
        user_id=user_id
    ))
):
    """Your docstring"""
    # Your existing code
    return {"result": "...", "tier": tier_info["tier_name"]}
```

**Features Available:**
- `code_execution` → minimum PRO tier
- `webhooks` → minimum PRO tier
- `custom_llms` → minimum PRO-PLUS tier
- `team_members` → minimum PRO-TEAM tier
- `audit_logs` → minimum PRO-TEAM tier
- `hipaa` → minimum ENTERPRISE-STANDARD tier
- `sso_saml` → minimum ENTERPRISE-PREMIUM tier
- `data_residency` → minimum ENTERPRISE-ULTIMATE tier
- `custom_integrations` → minimum PRO-PLUS tier

### Step 4: Test Endpoints (20 min)

```bash
# Test 1: Block FREE user (should get 403)
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-free" \
  -d '{"message":"Hello"}'

# Expected response:
# {
#   "detail": "Feature not available in tier",
#   "upgrade_url": "...",
#   "current_tier": "free",
#   "required_tier": "pro"
# }

# Test 2: Allow PRO user (should get 200)
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-pro" \
  -d '{"message":"Hello"}'

# Expected response: 200 OK with data

# Test 3: Check rate limit
for i in {1..25}; do
  curl -X GET http://localhost:8000/api/user/tier \
    -H "X-User-ID: test-free"
done

# After 20 requests: 429 Too Many Requests
```

---

## 📋 Specific Endpoints to Update

### 1. llm_chat_routes.py (Highest Priority)

**What to protect**: Chat endpoint
**Why**: Core IDE feature, high usage
**Feature**: `code_execution`

```python
from middleware.tier_validator import require_tier_access
from fastapi import Header, Depends

@router.post("/")
async def chat_stream(
    request: ChatRequest = Body(...),
    user_id: str = Header(None, alias="X-User-ID"),
    tier_info = Depends(lambda: require_tier_access(
        feature='code_execution',
        user_id=user_id
    ))
):
    """Stream response from Q Assistant"""
    # EXISTING CODE UNCHANGED - just add tier_info parameter above
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # ... rest of existing code
```

### 2. build_orchestration_routes.py

**What to protect**: Build/execute endpoints
**Why**: Core computation feature
**Feature**: `code_execution`

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
    """Execute a build"""
    # Your existing code
```

### 3. routes/orchestration_workflow.py

**What to protect**: Webhook endpoints
**Why**: Advanced automation feature
**Feature**: `webhooks`

```python
@router.post("/")
async def create_webhook(
    config: WebhookConfig = Body(...),
    user_id: str = Header(None, alias="X-User-ID"),
    tier_info = Depends(lambda: require_tier_access(
        feature='webhooks',
        user_id=user_id
    ))
):
    """Create webhook"""
    # Your existing code
```

### 4. routes/billing.py

**What to protect**: Audit/usage endpoints
**Why**: Compliance/audit feature
**Feature**: `audit_logs`

```python
@router.get("/usage")
async def get_usage(
    user_id: str = Header(None, alias="X-User-ID"),
    tier_info = Depends(lambda: require_tier_access(
        feature='audit_logs',
        user_id=user_id
    ))
):
    """Get usage statistics"""
    # Your existing code
```

---

## ✅ Checklist

- [ ] Identify which endpoints you're protecting first (pick 3-5 high-value ones)
- [ ] Add imports to those route files
- [ ] Apply pattern to each endpoint (copy-paste 3 lines)
- [ ] Test with FREE user (should block)
- [ ] Test with PRO user (should allow)
- [ ] Test rate limiting (20 calls for FREE)
- [ ] Check logs for errors
- [ ] Celebrate! Phase 1 is now live

---

## 🔧 Troubleshooting

### Issue: "X-User-ID header missing"
**Solution**: Make sure to include the header in all requests:
```bash
curl -H "X-User-ID: test-pro" ...
```

### Issue: "User not found in database"
**Solution**: Create test users:
```bash
sqlite3 backend/q_ide.db
INSERT INTO user_subscriptions (user_id, tier_name, is_trial, created_at)
VALUES ('test-pro', 'pro', 0, datetime('now'));
```

### Issue: 500 error in tier_info
**Solution**: Check that tier_validator.py is imported correctly:
```python
from middleware.tier_validator import require_tier_access
```

### Issue: Endpoint still works for FREE users
**Solution**: Make sure the Depends() dependency is properly added:
```python
# Wrong:
async def my_endpoint(user_id: str = Header(None)):

# Right:
async def my_endpoint(
    user_id: str = Header(None),
    tier_info = Depends(lambda: require_tier_access(...))
):
```

---

## ⏱️ Timeline

- **5-10 min**: Copy imports to 3 files
- **30-40 min**: Apply pattern to 5 endpoints
- **10-15 min**: Test with curl commands
- **5 min**: Verify no errors
- **Total: 1-2 hours**

## 🎯 Success = Phase 1 Live

When complete, you'll have:
- ✅ Free tier blocked from paid features
- ✅ Pro users can access features
- ✅ Rate limiting working (20 calls/day)
- ✅ Audit log entries for all requests
- ✅ Foundation ready for Phase 2 (React UI)

---

## 📚 Reference

- Implementation examples: `backend/routes/protected_endpoints.py`
- Middleware: `backend/middleware/tier_validator.py`
- Full guide: `PHASE1_API_ENFORCEMENT_GUIDE.md`
- Quick reference: `PHASE1_IMPLEMENTATION_CHECKLIST.py`

---

## Ready? 

Pick 3 endpoints to protect first (I recommend llm_chat_routes POST /api/chat as priority #1).

Then let me know and I can help with:
- Applying the pattern to specific files
- Testing the implementation
- Troubleshooting any issues
- Moving to Phase 2 (React components)
