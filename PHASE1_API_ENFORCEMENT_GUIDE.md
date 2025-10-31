# Phase 1: API Enforcement Implementation Guide

## ✅ STATUS: READY TO DEPLOY

All tier validation middleware and protected endpoint examples have been created. Here's what to do next.

---

## 📋 What Was Created

### 1. Enhanced Tier Validator Middleware
**File**: `backend/middleware/tier_validator.py`

Features:
- ✅ Feature-based access control (code_execution, custom_llms, webhooks, etc.)
- ✅ Tier hierarchy comparison (FREE < PRO < PRO-PLUS < PRO-TEAM < TEAMS < ENTERPRISE)
- ✅ Trial expiry checking for FREE tier
- ✅ Rate limiting integration
- ✅ Clear error responses with upgrade CTAs

### 2. Protected Endpoint Examples
**File**: `backend/routes/protected_endpoints.py`

Includes examples for:
- ✅ Code Execution (requires PRO)
- ✅ Custom LLMs (requires PRO-PLUS)
- ✅ Webhooks (requires PRO)
- ✅ Team Features (requires PRO-TEAM)
- ✅ Audit Logs (requires PRO-TEAM)
- ✅ HIPAA Export (requires ENTERPRISE-STANDARD)
- ✅ User Tier Info (available to all)

### 3. Existing Services (Already Working)
- ✅ `backend/services/rate_limiter.py` - Rate limiting by tier quota
- ✅ `backend/services/trial_expiry_job.py` - FREE tier expiry checker
- ✅ `backend/database/tier_schema.py` - Database schema with 10 tiers
- ✅ SQLite database with all 10 tiers populated

---

## 🚀 Next Steps: Apply to Your Actual Endpoints

### Step 1: Identify Endpoints to Protect

Find these files in your project and protect the listed endpoints:

**File: `backend/llm_chat_routes.py`**
```python
# Endpoints to protect (if they exist):
- POST /chat               # Might need code_execution for live testing
- POST /chat/execute       # DEFINITELY needs code_execution
- GET /chat/history        # No protection (available to all)
```

**File: `backend/build_orchestration_routes.py`**
```python
# Endpoints to protect:
- POST /build/run          # Might need code_execution
- GET /build/{id}          # No protection needed
```

**File: `backend/routes/ai_workflow_routes.py`**
```python
# Endpoints to protect:
- POST /workflow/create    # Might need custom_llms
- PUT /workflow/{id}       # Might need team_members
```

**Your Webhook Endpoint (if you have one)**
```python
- POST /webhooks           # MUST protect with 'webhooks' feature
- PUT /webhooks/{id}       # MUST protect with 'webhooks' feature
- DELETE /webhooks/{id}    # MUST protect with 'webhooks' feature
```

---

### Step 2: Apply Tier Protection to an Endpoint

Here's the pattern (modify as needed):

#### BEFORE (No protection):
```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # Any user can call this, even FREE tier
    return {"response": "..."}
```

#### AFTER (With tier protection):
```python
from fastapi import APIRouter, Depends, Header
from middleware.tier_validator import require_tier_access

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    user_id: str = Header(None, alias="X-User-ID"),
    tier_info = Depends(lambda: require_tier_access(
        feature='code_execution',  # ← CHANGE THIS based on endpoint
        user_id=user_id
    ))
):
    # Now only PRO+ tier users can call this
    # FREE tier users get 403 with upgrade CTA
    
    # tier_info contains:
    # - tier_info['tier_name']  (e.g., "PRO")
    # - tier_info['tier_id']    (e.g., "pro")
    # - tier_info['user_id']    (e.g., "user123")
    
    return {"response": "...", "tier": tier_info['tier_name']}
```

#### What happens when FREE user hits it:
```json
{
    "detail": {
        "error": "Feature 'code_execution' requires pro tier or higher",
        "feature": "code_execution",
        "tier": "FREE",
        "upgrade_required": true,
        "upgrade_to": "pro",
        "upgrade_url": "/upgrade/pro"
    }
}
```

---

### Step 3: Feature Mapping

Use these features for your endpoints:

| Feature | Minimum Tier | Endpoints to Protect |
|---------|--------------|----------------------|
| `code_execution` | PRO ($20) | `/api/code/*`, `/execute`, `/run` |
| `webhooks` | PRO ($20) | `/api/webhooks/*` |
| `custom_llms` | PRO-PLUS ($45) | `/api/llm/custom`, `/api/llm/register` |
| `team_members` | PRO-TEAM ($75) | `/api/team/*`, `/api/collaboration/*` |
| `audit_logs` | PRO-TEAM ($75) | `/api/audit/*` |
| `custom_integrations` | PRO-PLUS ($45) | `/api/integrations/*` |
| `hipaa` | ENTERPRISE-STD ($5K) | `/api/data/export`, `/api/compliance/*` |
| `sso_saml` | ENTERPRISE-PREM ($15K) | `/api/auth/sso`, `/api/auth/saml` |
| `on_premise` | ENTERPRISE-ULT ($50K) | `/api/enterprise/deploy` |

---

### Step 4: Quick Copy-Paste Template

For each endpoint you want to protect:

```python
@router.post("/your-endpoint")
async def your_function(
    request: YourRequest,
    user_id: str = Header(None, alias="X-User-ID"),
    tier_info = Depends(lambda: require_tier_access(
        feature='PICK_FEATURE',  # ← FROM TABLE ABOVE
        user_id=user_id
    ))
):
    """
    Description of your endpoint
    
    ✅ Allowed on: PRO, PRO-PLUS, etc. (see feature requirements)
    ❌ Blocked on: FREE (and anything below minimum tier)
    """
    # Your existing code here
    # tier_info is available if you need tier name/id
    return {"result": "..."}
```

---

### Step 5: Import the Middleware in main.py

Add this to `backend/main.py` at the top of the file (after other imports):

```python
from middleware.tier_validator import tier_validator_middleware
from services.trial_expiry_job import start_trial_checker
```

Then add this middleware to the app (after other middleware):

```python
# Add BEFORE the routes are included
app.add_middleware(tier_validator_middleware)

# And start the trial expiry checker on startup
@app.on_event("startup")
async def startup_event():
    # ... existing startup code ...
    
    # Start trial expiry checker
    try:
        start_trial_checker(schedule_type='daily')
        logger.info("✅ Trial expiry checker started")
    except Exception as e:
        logger.error(f"Failed to start trial checker: {e}")
```

---

## 🧪 Testing Your Protected Endpoints

### Test 1: Call endpoint WITHOUT user header (should fail)

```bash
curl -X POST http://localhost:8000/api/code/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "print(1)"}'

# Expected: 401 Unauthorized
# Response: {"detail": "X-User-ID header required"}
```

### Test 2: Call with FREE tier user (should fail)

```bash
# First, create a test FREE user in database
# sqlite3 backend/q_ide.db
# INSERT INTO user_subscriptions (user_id, tier_id, trial_expiry, is_active) 
# VALUES ('test-free-user', 'free', datetime('now', '+7 days'), 1);

curl -X POST http://localhost:8000/api/code/execute \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-free-user" \
  -d '{"code": "print(1)"}'

# Expected: 403 Forbidden
# Response: {
#   "detail": {
#     "error": "Feature 'code_execution' requires pro tier or higher",
#     "upgrade_to": "pro",
#     "upgrade_url": "/upgrade/pro"
#   }
# }
```

### Test 3: Call with PRO tier user (should succeed)

```bash
# First, create a test PRO user in database
# sqlite3 backend/q_ide.db
# INSERT INTO user_subscriptions (user_id, tier_id, is_active) 
# VALUES ('test-pro-user', 'pro', 1);

curl -X POST http://localhost:8000/api/code/execute \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-pro-user" \
  -d '{"code": "print(1)"}'

# Expected: 200 OK
# Response: {"status": "success", "result": "...", "tier": "PRO"}
```

### Test 4: Test Rate Limiting

```bash
# Make 10,001 calls with a FREE user (limit = 20/day)
for i in {1..21}; do
  curl -X GET http://localhost:8000/api/user/tier \
    -H "X-User-ID: test-free-user"
  
  # After 20th call, should get rate limit error
done

# After 20 calls: 429 Too Many Requests
# Response: {
#   "status": "error",
#   "code": "RATE_LIMIT_EXCEEDED",
#   "message": "Daily API call limit exceeded",
#   "limit": 20,
#   "remaining": 0
# }
```

---

## 📊 Feature Protection Matrix

Here's what gets blocked for each tier:

```
FEATURE                 FREE  PRO   PRO-PLUS  PRO-TEAM  TEAMS  ENTERPRISE
────────────────────────────────────────────────────────────────────────
code_execution          ❌    ✅    ✅        ✅        ✅     ✅
webhooks                ❌    ✅    ✅        ✅        ✅     ✅
custom_llms             ❌    ❌    ✅        ✅        ✅     ✅
team_members            ❌    ❌    ❌        ✅(3)     ✅(5+) ✅(100+)
role_based_access       ❌    ❌    ❌        ✅        ✅     ✅
audit_logs              ❌    ❌    ❌        ✅        ✅     ✅
custom_integrations     ❌    ❌    ✅        ✅        ✅     ✅
hipaa                   ❌    ❌    ❌        ❌        ❌     ✅
sso_saml                ❌    ❌    ❌        ❌        ❌     ✅(PREM)
data_residency          ❌    ❌    ❌        ❌        ❌     ✅(ULT)
on_premise_deploy       ❌    ❌    ❌        ❌        ❌     ✅(ULT)
```

---

## 🔍 Debugging Tier Issues

### Issue 1: "No active subscription" error

**Cause**: User doesn't exist in `user_subscriptions` table

**Fix**:
```bash
# Add test user:
sqlite3 backend/q_ide.db
INSERT INTO user_subscriptions (user_id, tier_id, is_active) 
VALUES ('test-user-id', 'pro', 1);

# Or check existing:
SELECT * FROM user_subscriptions WHERE user_id = 'test-user-id';
```

### Issue 2: "FREE tier trial expired" error

**Cause**: FREE tier user's 7-day trial has passed

**Fix**:
```bash
# Update trial expiry to future date:
sqlite3 backend/q_ide.db
UPDATE user_subscriptions 
SET trial_expiry = datetime('now', '+7 days') 
WHERE user_id = 'test-free-user' AND tier_id = 'free';
```

### Issue 3: Rate limit not working

**Cause**: Trial expiry job not running, or usage not being tracked

**Fix**:
```bash
# Check if daily_usage_tracking has records:
sqlite3 backend/q_ide.db
SELECT * FROM daily_usage_tracking WHERE user_id = 'test-user' ORDER BY usage_date DESC LIMIT 5;

# If empty, manually add today's usage:
INSERT INTO daily_usage_tracking (user_id, usage_date, api_calls_used) 
VALUES ('test-user', date('now'), 0);
```

### Issue 4: Middleware not being called

**Cause**: Tier decorator not added, or import issue

**Fix**:
```python
# Make sure middleware is imported at the top of main.py:
from middleware.tier_validator import require_tier_access, tier_validator_middleware

# And middleware is added before routes:
app.add_middleware(tier_validator_middleware)

# And endpoint has the dependency:
@app.post("/code/execute")
async def execute(
    req: Request,
    tier_info = Depends(lambda uid=Header(None, alias="X-User-ID"): 
        require_tier_access(feature='code_execution', user_id=uid))
):
    pass
```

---

## ✅ Checklist: Ready to Deploy?

- [ ] Tier validator middleware is updated (`backend/middleware/tier_validator.py`)
- [ ] Protected endpoint examples exist (`backend/routes/protected_endpoints.py`)
- [ ] Database has 10 tiers populated (verify with `python scripts/verify_tiers.py`)
- [ ] Test users created in database (FREE, PRO, PRO-TEAM tiers)
- [ ] Middleware imported in `main.py`
- [ ] Trial expiry job started in `main.py`
- [ ] At least ONE endpoint protected as a test (e.g., `/api/user/tier`)
- [ ] Test endpoint works with correct tier and blocks FREE tier
- [ ] Rate limiting tested (call 21 times with FREE user)
- [ ] All error responses have `upgrade_url` for UI

---

## 📝 Next: Phase 2 - React Components

Once API enforcement is working, the next phase is creating React components to show:
- Current user tier
- Daily API usage bar
- Trial countdown (if FREE)
- "Upgrade Now" CTAs

File: `frontend/src/components/TierInfo.tsx`

---

## 🆘 Need Help?

Check these files:
1. **Understanding the flow**: See `backend/routes/protected_endpoints.py` - has full examples
2. **How features map to tiers**: See `backend/middleware/tier_validator.py` line ~16 (FEATURE_REQUIREMENTS)
3. **How tier hierarchy works**: See `backend/middleware/tier_validator.py` line ~12 (TIER_HIERARCHY)
4. **Database structure**: See `backend/database/tier_schema.py`
5. **Rate limiting logic**: See `backend/services/rate_limiter.py`
