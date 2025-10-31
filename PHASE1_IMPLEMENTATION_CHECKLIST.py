"""
API Enforcement Checklist & Quick Reference

Use this to systematically apply tier protection to your endpoints
"""

# =============================================================================
# STEP 1: IMPORT STATEMENTS (Add to top of each route file)
# =============================================================================

IMPORTS_TO_ADD = """
from fastapi import Depends, Header
from middleware.tier_validator import require_tier_access
"""

# =============================================================================
# STEP 2: FIND THESE ENDPOINTS AND PROTECT THEM
# =============================================================================

ENDPOINTS_TO_PROTECT = {
    "Code Execution Endpoints": {
        "files": ["llm_chat_routes.py", "build_orchestration_routes.py"],
        "endpoints": [
            "POST /chat",
            "POST /execute",
            "POST /code/run"
        ],
        "feature": "code_execution",
        "minimum_tier": "pro",
        "reason": "Users need to pay to run code"
    },
    
    "Custom LLM Endpoints": {
        "files": ["llm_config_routes.py", "ai_workflow_routes.py"],
        "endpoints": [
            "POST /llm/register",
            "POST /llm/custom",
            "PUT /llm/{id}"
        ],
        "feature": "custom_llms",
        "minimum_tier": "pro_plus",
        "reason": "Custom LLM support is PRO-PLUS+ feature"
    },
    
    "Webhook Endpoints": {
        "files": ["webhook_routes.py", "integration_routes.py"],
        "endpoints": [
            "POST /webhooks",
            "PUT /webhooks/{id}",
            "DELETE /webhooks/{id}"
        ],
        "feature": "webhooks",
        "minimum_tier": "pro",
        "reason": "Webhooks are PRO+ feature"
    },
    
    "Team Collaboration": {
        "files": ["team_routes.py", "collaboration_routes.py"],
        "endpoints": [
            "POST /team/members",
            "PUT /team/members/{id}",
            "POST /workspaces/share"
        ],
        "feature": "team_members",
        "minimum_tier": "pro_team",
        "reason": "Team features start at PRO-TEAM"
    },
    
    "Audit & Compliance": {
        "files": ["audit_routes.py", "compliance_routes.py"],
        "endpoints": [
            "GET /audit-logs",
            "GET /compliance/export",
            "POST /data/backup"
        ],
        "feature": "audit_logs",
        "minimum_tier": "pro_team",
        "reason": "Audit logs are PRO-TEAM+ feature"
    },
    
    "Enterprise Features": {
        "files": ["enterprise_routes.py"],
        "endpoints": [
            "POST /sso/configure",
            "POST /deploy/on-premise",
            "GET /data-residency"
        ],
        "feature": "hipaa" or "on_premise",
        "minimum_tier": "enterprise_standard",
        "reason": "Enterprise-only features"
    }
}

# =============================================================================
# STEP 3: PROTECTION PATTERN
# =============================================================================

PROTECTION_PATTERN = """
# BEFORE:
@router.post("/endpoint")
async def endpoint_handler(request: Request):
    # implementation
    return result

# AFTER:
@router.post("/endpoint")
async def endpoint_handler(
    request: Request,
    user_id: str = Header(None, alias="X-User-ID"),
    tier_info = Depends(lambda: require_tier_access(
        feature='FEATURE_NAME',  # From FEATURE_REQUIREMENTS
        user_id=user_id
    ))
):
    # implementation
    return result
"""

# =============================================================================
# STEP 4: YOUR ACTUAL ROUTES TO CHECK
# =============================================================================

ROUTES_TO_CHECK = [
    {
        "file": "backend/llm_chat_routes.py",
        "protected_endpoints": [
            # Look for endpoints that should be code_execution
            "POST /chat with code execution",
            "POST /execute",
        ],
        "status": "TODO"
    },
    {
        "file": "backend/build_orchestration_routes.py",
        "protected_endpoints": [
            "POST /build/run",
        ],
        "status": "TODO"
    },
    {
        "file": "backend/routes/billing.py",
        "protected_endpoints": [
            # Billing endpoints might not need protection (accessible to all)
        ],
        "status": "NO CHANGES NEEDED"
    },
    {
        "file": "backend/routes/orchestration_workflow.py",
        "protected_endpoints": [
            # Check for team/collaboration features
        ],
        "status": "TODO"
    },
    {
        "file": "backend/routes/ai_workflow_routes.py",
        "protected_endpoints": [
            # Check what this exposes
        ],
        "status": "TODO"
    }
]

# =============================================================================
# STEP 5: TESTING SCRIPT
# =============================================================================

TESTING_COMMANDS = """
# Test 1: List all users in database
sqlite3 backend/q_ide.db
SELECT user_id, tier_id, is_active FROM user_subscriptions ORDER BY tier_id;

# Test 2: Create test users for testing
INSERT INTO user_subscriptions (user_id, tier_id, is_active) VALUES ('test-free', 'free', 1);
INSERT INTO user_subscriptions (user_id, tier_id, is_active) VALUES ('test-pro', 'pro', 1);
INSERT INTO user_subscriptions (user_id, tier_id, is_active) VALUES ('test-pro-team', 'pro_team', 1);

# Test 3: Test code execution endpoint with FREE user
curl -X POST http://localhost:8000/api/code/execute \\
  -H "X-User-ID: test-free" \\
  -H "Content-Type: application/json" \\
  -d '{"code": "print(1)"}'
# Expected: 403 Forbidden with upgrade CTA

# Test 4: Test with PRO user (should work)
curl -X POST http://localhost:8000/api/code/execute \\
  -H "X-User-ID: test-pro" \\
  -H "Content-Type: application/json" \\
  -d '{"code": "print(1)"}'
# Expected: 200 OK

# Test 5: Check that unprotected endpoints still work
curl -X GET http://localhost:8000/health
# Expected: 200 OK (no tier check needed)

# Test 6: Rate limit test
for i in {1..25}; do
  echo "Call $i"
  curl -s -X GET http://localhost:8000/api/user/tier \\
    -H "X-User-ID: test-free" | grep -o "RATE_LIMIT_EXCEEDED" && break
done
# After 20 calls (FREE tier limit): Should see RATE_LIMIT_EXCEEDED
"""

# =============================================================================
# STEP 6: FEATURES & MINIMUM TIERS QUICK REFERENCE
# =============================================================================

FEATURE_TIER_MAPPING = {
    'code_execution': {
        'minimum': 'pro',
        'price': '$20/mo',
        'blocked_on': ['free'],
        'allowed_on': ['pro', 'pro_plus', 'pro_team', 'teams_small', 'teams_medium', 'teams_large', 'enterprise_standard', 'enterprise_premium', 'enterprise_ultimate']
    },
    'webhooks': {
        'minimum': 'pro',
        'price': '$20/mo',
        'blocked_on': ['free'],
        'allowed_on': ['pro', 'pro_plus', 'pro_team', 'teams_small', 'teams_medium', 'teams_large', 'enterprise_standard', 'enterprise_premium', 'enterprise_ultimate']
    },
    'custom_llms': {
        'minimum': 'pro_plus',
        'price': '$45/mo',
        'blocked_on': ['free', 'pro'],
        'allowed_on': ['pro_plus', 'pro_team', 'teams_small', 'teams_medium', 'teams_large', 'enterprise_standard', 'enterprise_premium', 'enterprise_ultimate']
    },
    'team_members': {
        'minimum': 'pro_team',
        'price': '$75/mo (3 members)',
        'blocked_on': ['free', 'pro', 'pro_plus'],
        'allowed_on': ['pro_team', 'teams_small', 'teams_medium', 'teams_large', 'enterprise_standard', 'enterprise_premium', 'enterprise_ultimate']
    },
    'audit_logs': {
        'minimum': 'pro_team',
        'price': '$75/mo',
        'blocked_on': ['free', 'pro', 'pro_plus'],
        'allowed_on': ['pro_team', 'teams_small', 'teams_medium', 'teams_large', 'enterprise_standard', 'enterprise_premium', 'enterprise_ultimate']
    },
    'hipaa': {
        'minimum': 'enterprise_standard',
        'price': '$5,000/mo',
        'blocked_on': ['free', 'pro', 'pro_plus', 'pro_team', 'teams_small', 'teams_medium', 'teams_large'],
        'allowed_on': ['enterprise_standard', 'enterprise_premium', 'enterprise_ultimate']
    },
    'sso_saml': {
        'minimum': 'enterprise_premium',
        'price': '$15,000/mo',
        'blocked_on': ['free', 'pro', 'pro_plus', 'pro_team', 'teams_small', 'teams_medium', 'teams_large', 'enterprise_standard'],
        'allowed_on': ['enterprise_premium', 'enterprise_ultimate']
    },
    'on_premise': {
        'minimum': 'enterprise_ultimate',
        'price': '$50,000/mo',
        'blocked_on': ['free', 'pro', 'pro_plus', 'pro_team', 'teams_small', 'teams_medium', 'teams_large', 'enterprise_standard', 'enterprise_premium'],
        'allowed_on': ['enterprise_ultimate']
    }
}

# =============================================================================
# STEP 7: IMPLEMENTATION CHECKLIST
# =============================================================================

CHECKLIST = """
Phase 1: API Enforcement Implementation Checklist
═════════════════════════════════════════════════

PREPARATION:
  □ Read PHASE1_API_ENFORCEMENT_GUIDE.md completely
  □ Understand tier hierarchy: FREE < PRO < PRO-PLUS < ... < ENTERPRISE-ULT
  □ Understand feature requirements from FEATURE_TIER_MAPPING
  □ Test database connection and verify tiers exist

CODE CHANGES:
  □ Update backend/middleware/tier_validator.py (DONE ✓)
  □ Create backend/routes/protected_endpoints.py (DONE ✓)
  □ Import tier validation in each route file that needs protection
  
  Route-by-route:
    □ backend/llm_chat_routes.py - Add @require_tier for code execution
    □ backend/build_orchestration_routes.py - Protect /build/run
    □ backend/llm_config_routes.py - Protect custom LLM endpoints
    □ backend/routes/billing.py - No changes needed (available to all)
    □ backend/routes/orchestration_workflow.py - Check if needs protection
    □ backend/routes/ai_workflow_routes.py - Check if needs protection
    □ [Any webhook routes] - Protect with 'webhooks' feature
    □ [Any team routes] - Protect with 'team_members' feature

MAIN.PY:
  □ Import tier validator middleware
  □ Add tier_validator_middleware to app
  □ Import and start trial expiry checker
  □ Add trial checker to startup event

DATABASE:
  □ Create test FREE user: INSERT INTO user_subscriptions (user_id, tier_id, is_active) VALUES ('test-free', 'free', 1);
  □ Create test PRO user: INSERT INTO user_subscriptions (user_id, tier_id, is_active) VALUES ('test-pro', 'pro', 1);
  □ Verify both users exist: SELECT * FROM user_subscriptions;

TESTING:
  □ Test protected endpoint WITHOUT X-User-ID header (expect 401)
  □ Test protected endpoint WITH FREE user (expect 403 + upgrade CTA)
  □ Test protected endpoint WITH PRO user (expect 200 OK)
  □ Test rate limiting (call 21 times, FREE user)
  □ Test unprotected endpoint still works
  □ Check trial expiry (set FREE trial to past date, should block)
  □ Test feature-specific blocking (e.g., custom_llms blocks FREE and PRO)

DOCUMENTATION:
  □ Update API docs with tier requirements
  □ Document upgrade paths for each feature
  □ Document rate limits per tier
  □ Create migration guide for existing users

MONITORING:
  □ Set up logging for tier violations
  □ Track feature usage by tier
  □ Monitor upgrade conversion rate
  □ Alert on trial expiry failures

LAUNCH:
  □ All tests passing
  □ Rate limiting working
  □ Trial expiry job running
  □ Error messages are user-friendly
  □ Upgrade URLs in responses point to pricing page
  □ Ready for Phase 2 (React components)
"""

# =============================================================================
# STEP 8: EXAMPLE IMPLEMENTATION
# =============================================================================

EXAMPLE_IMPLEMENTATION = """
Here's a concrete example of protecting an endpoint:

FILE: backend/routes/my_code_routes.py
────────────────────────────────────────

# BEFORE (no tier protection):
from fastapi import APIRouter

router = APIRouter()

@router.post("/execute")
async def execute_code(request: CodeRequest):
    # Run the code
    result = run_code(request.code)
    return {"result": result}


# AFTER (with tier protection):
from fastapi import APIRouter, Depends, Header
from middleware.tier_validator import require_tier_access  # ← ADD THIS
from pydantic import BaseModel

router = APIRouter()

class CodeRequest(BaseModel):
    code: str

@router.post("/execute")
async def execute_code(
    request: CodeRequest,
    user_id: str = Header(None, alias="X-User-ID"),  # ← ADD THIS
    tier_info = Depends(lambda: require_tier_access(  # ← ADD THIS
        feature='code_execution',
        user_id=user_id
    ))
):
    # Run the code
    result = run_code(request.code)
    return {
        "result": result,
        "tier": tier_info['tier_name']  # Can access tier info if needed
    }


Now when a FREE user calls this endpoint:
  curl -X POST http://localhost:8000/execute \\
    -H "X-User-ID: test-free" \\
    -H "Content-Type: application/json" \\
    -d '{"code": "print(1)"}'

They get:
  Status: 403 Forbidden
  {
    "detail": {
      "error": "Feature 'code_execution' requires pro tier or higher",
      "upgrade_to": "pro",
      "upgrade_url": "/upgrade/pro"
    }
  }

A PRO user gets:
  Status: 200 OK
  {
    "result": "1",
    "tier": "PRO"
  }
"""

# =============================================================================
# PRINT THE CHECKLIST FOR USER
# =============================================================================

if __name__ == "__main__":
    print(CHECKLIST)
    print("\n\nQUICK START:\n")
    print("1. Review PHASE1_API_ENFORCEMENT_GUIDE.md")
    print("2. Run this script to see the full checklist")
    print("3. Identify which endpoints need protection")
    print("4. Apply the pattern shown in EXAMPLE_IMPLEMENTATION")
    print("5. Run the testing commands to verify")
    print("6. Mark items as complete in the checklist")
