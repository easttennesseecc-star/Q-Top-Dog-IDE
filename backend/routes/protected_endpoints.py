"""
API Protection Layer - Example Protected Endpoints
Shows how to apply tier validation to your FastAPI endpoints

Apply these patterns to your actual routes:
- /api/code/execute (requires 'code_execution' feature)
- /api/webhooks/* (requires 'webhooks' feature)  
- /api/llm/custom (requires 'custom_llms' feature)
- /api/team/* (requires 'pro_team' minimum tier)
"""

from fastapi import APIRouter, Header, Depends, HTTPException
from pydantic import BaseModel
from backend.middleware.tier_validator import require_tier_access
from backend.services.rate_limiter import RateLimiter
from datetime import datetime

router = APIRouter(prefix="/api", tags=["Protected APIs"])

rate_limiter = RateLimiter()


# ============================================================================
# EXAMPLE 1: CODE EXECUTION - Requires PRO tier or higher
# ============================================================================

class CodeExecutionRequest(BaseModel):
    code: str
    language: str = "python"
    timeout: int = 30


@router.post("/code/execute")
async def execute_code(
    request: CodeExecutionRequest,
    tier_info = Depends(lambda user_id = Header(None, alias="X-User-ID"): 
        require_tier_access(feature='code_execution', user_id=user_id))
):
    """
    Execute code in the IDE
    
    ✅ Allowed on: PRO, PRO-PLUS, PRO-TEAM, TEAMS-*, ENTERPRISE-*
    ❌ Blocked on: FREE
    
    Usage:
        POST /api/code/execute
        Headers: X-User-ID: user123
        Body: {
            "code": "print('hello')",
            "language": "python"
        }
    """
    
    # Check rate limit
    rate_check = rate_limiter.check_limit(tier_info['user_id'])
    if not rate_check['allowed']:
        return {
            'status': 'error',
            'code': 'RATE_LIMIT_EXCEEDED',
            'message': rate_check['error'],
            'limit': rate_check.get('limit'),
            'used': rate_check.get('used'),
            'remaining': rate_check.get('remaining')
        }
    
    # TODO: Actually execute code here
    return {
        'status': 'success',
        'result': f'Executed {request.language} code',
        'tier': tier_info['tier_name'],
        'api_calls_remaining': rate_check['remaining']
    }


# ============================================================================
# EXAMPLE 2: CUSTOM LLMS - Requires PRO-PLUS tier or higher
# ============================================================================

class CustomLLMRequest(BaseModel):
    model_name: str
    api_key: str
    provider: str


@router.post("/llm/custom")
async def register_custom_llm(
    request: CustomLLMRequest,
    tier_info = Depends(lambda user_id = Header(None, alias="X-User-ID"): 
        require_tier_access(feature='custom_llms', user_id=user_id))
):
    """
    Register a custom LLM model
    
    ✅ Allowed on: PRO-PLUS, PRO-TEAM, TEAMS-*, ENTERPRISE-*
    ❌ Blocked on: FREE, PRO
    
    Usage:
        POST /api/llm/custom
        Headers: X-User-ID: user123
        Body: {
            "model_name": "gpt-4",
            "provider": "openai",
            "api_key": "sk-..."
        }
    """
    
    rate_check = rate_limiter.check_limit(tier_info['user_id'])
    if not rate_check['allowed']:
        return {'status': 'error', 'message': rate_check['error']}
    
    # TODO: Store custom LLM config
    return {
        'status': 'success',
        'message': f'Custom LLM {request.model_name} registered',
        'tier': tier_info['tier_name']
    }


# ============================================================================
# EXAMPLE 3: WEBHOOKS - Requires PRO tier or higher
# ============================================================================

class WebhookRequest(BaseModel):
    url: str
    events: list
    description: str = ""


@router.post("/webhooks")
async def create_webhook(
    request: WebhookRequest,
    tier_info = Depends(lambda user_id = Header(None, alias="X-User-ID"): 
        require_tier_access(feature='webhooks', user_id=user_id))
):
    """
    Create a webhook
    
    ✅ Allowed on: PRO, PRO-PLUS, PRO-TEAM, TEAMS-*, ENTERPRISE-*
    ❌ Blocked on: FREE
    
    Usage:
        POST /api/webhooks
        Headers: X-User-ID: user123
        Body: {
            "url": "https://example.com/hook",
            "events": ["execution.complete", "error"],
            "description": "My webhook"
        }
    """
    
    rate_check = rate_limiter.check_limit(tier_info['user_id'])
    if not rate_check['allowed']:
        return {'status': 'error', 'message': rate_check['error']}
    
    # TODO: Create webhook
    return {
        'status': 'success',
        'webhook_id': 'wh_123',
        'tier': tier_info['tier_name'],
        'events_count': len(request.events)
    }


# ============================================================================
# EXAMPLE 4: TEAM FEATURES - Requires PRO-TEAM tier or higher
# ============================================================================

class TeamMemberRequest(BaseModel):
    email: str
    role: str  # 'admin' or 'viewer'


@router.post("/team/members")
async def add_team_member(
    request: TeamMemberRequest,
    tier_info = Depends(lambda user_id = Header(None, alias="X-User-ID"): 
        require_tier_access(feature='team_members', user_id=user_id))
):
    """
    Add a team member
    
    ✅ Allowed on: PRO-TEAM (3 members), TEAMS-* (5-100+), ENTERPRISE-* (500-∞)
    ❌ Blocked on: FREE, PRO, PRO-PLUS
    
    Usage:
        POST /api/team/members
        Headers: X-User-ID: user123
        Body: {
            "email": "colleague@example.com",
            "role": "admin"
        }
    """
    
    rate_check = rate_limiter.check_limit(tier_info['user_id'])
    if not rate_check['allowed']:
        return {'status': 'error', 'message': rate_check['error']}
    
    # TODO: Add team member
    return {
        'status': 'success',
        'member_added': request.email,
        'role': request.role,
        'tier': tier_info['tier_name']
    }


# ============================================================================
# EXAMPLE 5: AUDIT LOGS - Requires PRO-TEAM tier or higher
# ============================================================================

@router.get("/audit-logs")
async def get_audit_logs(
    limit: int = 100,
    tier_info = Depends(lambda user_id = Header(None, alias="X-User-ID"): 
        require_tier_access(feature='audit_logs', user_id=user_id))
):
    """
    Get audit logs (all actions on this account)
    
    ✅ Allowed on: PRO-TEAM, TEAMS-*, ENTERPRISE-*
    ❌ Blocked on: FREE, PRO, PRO-PLUS
    
    Usage:
        GET /api/audit-logs?limit=50
        Headers: X-User-ID: user123
    """
    
    rate_check = rate_limiter.check_limit(tier_info['user_id'])
    if not rate_check['allowed']:
        return {'status': 'error', 'message': rate_check['error']}
    
    # TODO: Fetch audit logs from database
    return {
        'status': 'success',
        'logs': [],
        'total': 0,
        'tier': tier_info['tier_name']
    }


# ============================================================================
# EXAMPLE 6: HIPAA COMPLIANCE - Requires ENTERPRISE-STANDARD tier or higher
# ============================================================================

@router.post("/data/export")
async def export_data_hipaa(
    format: str = "json",
    tier_info = Depends(lambda user_id = Header(None, alias="X-User-ID"): 
        require_tier_access(feature='hipaa', user_id=user_id))
):
    """
    Export data with HIPAA compliance
    
    ✅ Allowed on: ENTERPRISE-STANDARD, ENTERPRISE-PREMIUM, ENTERPRISE-ULTIMATE
    ❌ Blocked on: Everything else (requires HIPAA certification)
    
    Usage:
        POST /api/data/export?format=json
        Headers: X-User-ID: user123
    """
    
    rate_check = rate_limiter.check_limit(tier_info['user_id'])
    if not rate_check['allowed']:
        return {'status': 'error', 'message': rate_check['error']}
    
    # TODO: Generate HIPAA-compliant export
    return {
        'status': 'success',
        'export_id': 'exp_123',
        'format': format,
        'tier': tier_info['tier_name'],
        'hipaa_compliant': True
    }


# ============================================================================
# EXAMPLE 7: USAGE INFO - Available to all (shows tier info)
# ============================================================================

@router.get("/user/tier")
async def get_user_tier(
    user_id: str = Header(None, alias="X-User-ID")
):
    """
    Get current user's tier and usage information
    
    ✅ Available to: All authenticated users
    
    Returns:
    - Current tier name and ID
    - Daily API call limit and remaining
    - Trial status (if FREE)
    - Available features
    
    Usage:
        GET /api/user/tier
        Headers: X-User-ID: user123
    """
    
    if not user_id:
        raise HTTPException(status_code=401, detail="X-User-ID header required")
    
    # Get tier info
    await require_tier_access(user_id=user_id)
    
    # Get rate limit
    rate_check = rate_limiter.check_limit(user_id)
    
    # Get trial status
    tier_data = rate_limiter.get_user_tier(user_id)
    
    if not tier_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    trial_expires_in = None
    if tier_data['tier_id'] == 'free' and tier_data['trial_expiry']:
        trial_date = datetime.fromisoformat(tier_data['trial_expiry'])
        trial_expires_in = (trial_date - datetime.utcnow()).days
    
    return {
        'status': 'success',
        'tier': {
            'name': tier_data['name'],
            'tier_id': tier_data['tier_id'],
            'price': tier_data['price'],
            'renewal_date': tier_data.get('renewal_date')
        },
        'usage': {
            'daily_call_limit': rate_check['limit'],
            'api_calls_used_today': rate_check['used'],
            'api_calls_remaining_today': rate_check['remaining']
        },
        'trial': {
            'is_trial': tier_data['tier_id'] == 'free',
            'expires_in_days': trial_expires_in
        } if tier_data['tier_id'] == 'free' else None,
        'features': {
            'code_execution': tier_data['code_execution'],
            'custom_llms': tier_data['custom_llms'],
            'webhooks': tier_data['webhooks'],
            'team_members': tier_data['team_members'],
            'role_based_access': tier_data['role_based_access'],
            'audit_logs': tier_data['audit_logs'],
            'sso_saml': tier_data['sso_saml'],
            'hipaa': tier_data['hipaa_ready'],
            'data_residency': tier_data['data_residency'],
            'on_premise': tier_data['on_premise_deploy']
        }
    }


# ============================================================================
# ENDPOINT APPLICATION GUIDE
# ============================================================================

"""
HOW TO APPLY THIS TO YOUR EXISTING ENDPOINTS:

1. Find your endpoint in llm_chat_routes.py, build_orchestration_routes.py, etc.

2. Add the tier check dependency:

    # BEFORE:
    @app.post("/chat")
    async def chat_endpoint(request: ChatRequest):
        ...
    
    # AFTER:
    @app.post("/chat")
    async def chat_endpoint(
        request: ChatRequest,
        tier_info = Depends(lambda user_id = Header(None, alias="X-User-ID"): 
            require_tier_access(feature='code_execution', user_id=user_id))
    ):
        # Now tier_info contains user's tier data
        # And the endpoint will be blocked for FREE tier
        ...

3. Features to protect:

   Feature: 'code_execution'      → Endpoint: /api/code/*
   Feature: 'custom_llms'         → Endpoint: /api/llm/custom
   Feature: 'webhooks'            → Endpoint: /api/webhooks
   Feature: 'team_members'        → Endpoint: /api/team/*
   Feature: 'audit_logs'          → Endpoint: /api/audit/*
   Feature: 'custom_integrations' → Endpoint: /api/integrations
   Feature: 'hipaa'               → Endpoint: /api/data/export
   Feature: 'sso_saml'            → Endpoint: /api/auth/sso
   Feature: 'on_premise'          → Endpoint: /api/enterprise/deploy
   Feature: 'data_residency'      → Endpoint: /api/enterprise/residency

4. What happens when a FREE user hits a protected endpoint:

   Status: 403 Forbidden
   Response: {
       "detail": {
           "error": "Feature 'code_execution' requires pro tier or higher",
           "feature": "code_execution",
           "tier": "FREE",
           "current_tier_level": 0,
           "required_tier_level": 1,
           "upgrade_required": true,
           "upgrade_to": "pro",
           "upgrade_url": "/upgrade/pro"
       }
   }

5. Rate limiting is automatic - no additional code needed!
   Every API call increments the daily counter and checks limit.
"""
