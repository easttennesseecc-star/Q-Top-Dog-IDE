# 📋 QUICK REFERENCE CARD - Phase 1 Implementation

## 🎯 The Mission
Apply tier protection to your FastAPI endpoints so FREE users can't access paid features.

---

## ⚡ The 3-Step Pattern

### Step 1: Add Imports
```python
from fastapi import Header, Depends
from middleware.tier_validator import require_tier_access
```

### Step 2: Add to Function Signature
```python
user_id: str = Header(None, alias="X-User-ID"),
tier_info = Depends(lambda: require_tier_access(
    feature='code_execution',
    user_id=user_id
))
```

### Step 3: Your Code Runs
- FREE users: Blocked with 403 + upgrade URL
- PRO users: Proceeds with 200 OK
- Rate limiting: Automatic (20 calls/day for FREE)

---

## 📍 Where to Apply

| Endpoint | Feature | File |
|----------|---------|------|
| POST /api/chat/ | code_execution | llm_chat_routes.py |
| POST /api/build/execute | code_execution | build_orchestration_routes.py |
| POST /api/workflows/ | webhooks | orchestration_workflow.py |
| GET /api/billing/usage | audit_logs | billing.py |

---

## 🧪 Test Commands

### Test 1: Block FREE User
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "X-User-ID: test-free" \
  -d '{"message":"Hello"}'
# Expected: 403 Forbidden
```

### Test 2: Allow PRO User
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "X-User-ID: test-pro" \
  -d '{"message":"Hello"}'
# Expected: 200 OK
```

### Test 3: Check Rate Limit
```bash
for i in {1..25}; do
  curl -H "X-User-ID: test-free" \
    http://localhost:8000/api/user/tier
done
# After 20: 429 Too Many Requests
```

---

## ✅ Success Checklist

- [ ] Imports added to 3 files
- [ ] Pattern applied to 3-4 endpoints
- [ ] Test 1: FREE user blocked (403)
- [ ] Test 2: PRO user allowed (200)
- [ ] Test 3: Rate limit working
- [ ] No errors in backend logs
- [ ] Phase 1 COMPLETE! 🎉

---

## 📊 Features to Choose From

```
code_execution  → Minimum tier: PRO ($20)
webhooks        → Minimum tier: PRO ($20)
custom_llms     → Minimum tier: PRO-PLUS ($45)
team_members    → Minimum tier: PRO-TEAM ($75)
audit_logs      → Minimum tier: PRO-TEAM ($75)
hipaa           → Minimum tier: ENTERPRISE-STD ($5K)
sso_saml        → Minimum tier: ENTERPRISE-PREM ($15K)
```

---

## 🚨 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "X-User-ID header missing" | Add `-H "X-User-ID: test-pro"` to curl |
| "User not found" | Create test user: `INSERT INTO user_subscriptions...` |
| "Module not found" | Check import path: `from middleware.tier_validator...` |
| "Still allows FREE" | Verify `Depends()` added to function signature |
| "Rate limit broken" | Verify `rate_limiter.py` service running |

---

## 📚 Documentation Quick Links

| Need | Document |
|------|----------|
| Quick start | START_PHASE1_NOW.md |
| Code examples | PHASE1_COPY_PASTE_READY.md |
| Full reference | PHASE1_API_ENFORCEMENT_GUIDE.md |
| All 4 phases | MASTER_IMPLEMENTATION_CHECKLIST.md |
| Revenue info | PHASE1_EXECUTIVE_SUMMARY.md |
| Decision tree | IMPLEMENTATION_STATUS_DASHBOARD.md |

---

## ⏱️ Time Estimate

```
Add imports:     2 min
Apply pattern:   15 min
Test:            5 min
Debug (if any):  10-15 min
─────────────────────
TOTAL:           40 min
```

---

## 🎯 Result After 40 Minutes

✅ API enforcement live
✅ FREE users blocked from paid features
✅ PRO users can access features
✅ Rate limiting enforced
✅ Ready for Phase 2 (React)

---

## 📞 If You Get Stuck

1. Check the troubleshooting section in the guide
2. Verify the import path is correct
3. Ensure test users exist in DB
4. Check backend logs for errors
5. Message me with the error

---

## 🚀 Next: Phase 2

After Phase 1 complete:
- Build React components (2-3 hours)
- Show tier in UI
- Show usage bar
- Show upgrade prompts

---

## 💡 Pro Tips

✓ Start with 1 endpoint, test it, then do others
✓ Use exact copy-paste patterns provided
✓ Check backend terminal for error logs
✓ Verify database has test users
✓ Test each step before moving on

---

## 🎉 You Got This!

Phase 1 is just:
1. Copy imports
2. Copy function parameters
3. Test with curl
4. Done!

**No complicated logic. No deep changes. Just 3 lines of pattern. 40 minutes.**

---

**Ready?** → START_PHASE1_NOW.md
