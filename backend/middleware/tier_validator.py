"""
Tier validation middleware for FastAPI
Protects endpoints that require specific tier permissions
Enhanced with feature-based access control and rate limiting
"""

import sqlite3
from datetime import datetime, date
from fastapi import HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from backend.database.tier_schema import MembershipTierSchema, TIER_CONFIGS
from typing import Dict, Any, Optional


# Tier hierarchy for comparison
TIER_HIERARCHY = {
    'free': 0,
    'pro': 1,
    'pro_plus': 2,
    'pro_team': 3,
    'teams_small': 4,
    'teams_medium': 5,
    'teams_large': 6,
    'enterprise_standard': 7,
    'enterprise_premium': 8,
    'enterprise_ultimate': 9,
}

# Feature to minimum tier mapping
FEATURE_REQUIREMENTS = {
    'code_execution': 'pro',           # CODE_EXECUTION unlock at PRO
    'custom_llms': 'pro_plus',         # CUSTOM_LLMs unlock at PRO-PLUS
    'webhooks': 'pro',                 # WEBHOOKS at PRO+
    'api_keys': 'pro',                 # API keys at PRO+
    'debug_logs': 'pro',               # Debug logs at PRO+
    'data_persistence': 'free',        # Available to all
    'concurrent_sessions': 'free',     # Available to all
    'team_members': 'pro_team',        # Team features at PRO-TEAM+
    'role_based_access': 'pro_team',   # RBAC at PRO-TEAM+
    'shared_workspaces': 'pro_team',   # Shared workspaces at PRO-TEAM+
    'audit_logs': 'pro_team',          # Audit logs at PRO-TEAM+
    'custom_integrations': 'pro_plus', # Custom integrations at PRO-PLUS+
    'hipaa': 'enterprise_standard',    # HIPAA at ENTERPRISE-STANDARD+
    'soc2': 'enterprise_standard',     # SOC2 at ENTERPRISE-STANDARD+
    'sso_saml': 'enterprise_premium',  # SSO/SAML at ENTERPRISE-PREMIUM+
    'data_residency': 'enterprise_ultimate',      # Data residency at ENTERPRISE-ULTIMATE
    'on_premise': 'enterprise_ultimate',          # On-premise at ENTERPRISE-ULTIMATE
}


class TierValidator:
    """Enhanced tier validation with feature-based access control"""
    
    def __init__(self):
        self.db_path = MembershipTierSchema.get_db_path()
    
    def get_user_tier(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's subscription tier with all features"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT mt.*, us.trial_expiry, us.is_active, us.subscription_date
                FROM membership_tiers mt
                JOIN user_subscriptions us ON mt.tier_id = us.tier_id
                WHERE us.user_id = ?
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return None
            
            return dict(result)
            
        except Exception as e:
            print(f"Error getting tier: {e}")
            return None
    
    def check_feature_access(self, user_id: str, feature: str) -> Dict[str, Any]:
        """Check if user can access a specific feature"""
        
        tier = self.get_user_tier(user_id)
        
        if not tier:
            return {
                'allowed': False,
                'error': 'No active subscription',
                'feature': feature,
                'upgrade_required': True
            }
        
        # Check if subscription is active
        if not tier['is_active']:
            return {
                'allowed': False,
                'error': 'Subscription inactive',
                'feature': feature,
                'tier': tier['name']
            }
        
        # Check FREE tier trial expiry
        if tier['tier_id'] == 'free' and tier['trial_expiry']:
            if datetime.fromisoformat(tier['trial_expiry']) < datetime.utcnow():
                return {
                    'allowed': False,
                    'error': 'FREE tier trial expired',
                    'feature': feature,
                    'tier': tier['name'],
                    'upgrade_required': True,
                    'upgrade_to': 'pro'
                }
        
        # Check feature availability
        if feature not in FEATURE_REQUIREMENTS:
            return {
                'allowed': False,
                'error': f'Unknown feature: {feature}',
                'feature': feature
            }
        
        required_tier = FEATURE_REQUIREMENTS[feature]
        required_level = TIER_HIERARCHY.get(required_tier, 0)
        current_level = TIER_HIERARCHY.get(tier['tier_id'], 0)
        
        if current_level < required_level:
            return {
                'allowed': False,
                'error': f'Feature "{feature}" requires {required_tier} tier or higher',
                'feature': feature,
                'tier': tier['name'],
                'current_tier_level': current_level,
                'required_tier_level': required_level,
                'upgrade_required': True,
                'upgrade_to': required_tier,
                'upgrade_url': f'/upgrade/{required_tier}'
            }
        
        # Feature is allowed
        return {
            'allowed': True,
            'feature': feature,
            'tier': tier['name'],
            'tier_id': tier['tier_id']
        }
    
    def check_rate_limit(self, user_id: str) -> Dict[str, Any]:
        """Check if user has exceeded daily rate limit"""
        try:
            tier = self.get_user_tier(user_id)
            
            if not tier:
                return {
                    'allowed': False,
                    'error': 'No active subscription',
                    'limit': 0,
                    'remaining': 0
                }
            
            today = date.today().isoformat()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = """
                SELECT api_calls_used
                FROM daily_usage_tracking
                WHERE user_id = ? AND usage_date = ?
            """
            cursor.execute(query, (user_id, today))
            result = cursor.fetchone()
            
            used = result[0] if result else 0
            limit = tier['daily_call_limit']
            
            conn.close()
            
            if used >= limit:
                return {
                    'allowed': False,
                    'error': 'Daily API call limit exceeded',
                    'tier': tier['name'],
                    'limit': limit,
                    'used': used,
                    'remaining': 0,
                    'reset_at': f'{today}T23:59:59Z'
                }
            
            # Increment usage
            self._increment_usage(user_id, today)
            
            return {
                'allowed': True,
                'tier': tier['name'],
                'limit': limit,
                'used': used + 1,
                'remaining': limit - used - 1
            }
            
        except Exception as e:
            return {
                'allowed': False,
                'error': f'Rate limit check failed: {str(e)}'
            }
    
    def _increment_usage(self, user_id: str, usage_date: str):
        """Increment daily usage counter"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Ensure record exists
            cursor.execute(
                "SELECT id FROM daily_usage_tracking WHERE user_id = ? AND usage_date = ?",
                (user_id, usage_date)
            )
            
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO daily_usage_tracking (user_id, usage_date, api_calls_used) VALUES (?, ?, 0)",
                    (user_id, usage_date)
                )
            
            # Increment
            cursor.execute(
                "UPDATE daily_usage_tracking SET api_calls_used = api_calls_used + 1 WHERE user_id = ? AND usage_date = ?",
                (user_id, usage_date)
            )
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error incrementing usage: {e}")


# Singleton instance
_validator = TierValidator()


async def require_tier_access(
    tier_id: Optional[str] = None,
    feature: Optional[str] = None,
    action: Optional[str] = None,
    user_id: Optional[str] = Header(None, alias="X-User-ID")
) -> dict:
    """
    Enhanced dependency for tier validation
    
    Args:
        tier_id: Required exact tier (e.g., 'pro')
        feature: Required feature access (e.g., 'code_execution')
        action: Legacy action name (maps to feature)
        user_id: User ID from header
    
    Returns:
        User subscription and tier info
    
    Raises:
        HTTPException if validation fails
    """
    
    if not user_id:
        raise HTTPException(status_code=401, detail="X-User-ID header required")
    
    try:
        tier = _validator.get_user_tier(user_id)
        
        if not tier:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "No active subscription",
                    "upgrade_url": "/upgrade/pro"
                }
            )
        
        if not tier['is_active']:
            raise HTTPException(
                status_code=403,
                detail="Subscription is inactive or expired"
            )
        
        # Check FREE tier trial expiry
        if tier['tier_id'] == 'free' and tier['trial_expiry']:
            if datetime.fromisoformat(tier['trial_expiry']) < datetime.utcnow():
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "FREE tier trial expired",
                        "upgrade_url": "/upgrade/pro",
                        "expired_at": tier['trial_expiry']
                    }
                )
        
        # Map action to feature if needed
        if action and not feature:
            action_to_feature = {
                'code_execution': 'code_execution',
                'custom_llm': 'custom_llms',
                'webhook': 'webhooks',
                'hipaa': 'hipaa',
                'custom_integration': 'custom_integrations',
                'on_premise': 'on_premise',
            }
            feature = action_to_feature.get(action, action)
        
        # Check feature access
        if feature:
            check = _validator.check_feature_access(user_id, feature)
            if not check['allowed']:
                raise HTTPException(
                    status_code=403,
                    detail=check
                )
        
        # Check exact tier if required
        if tier_id and tier['tier_id'] != tier_id:
            required_level = TIER_HIERARCHY.get(tier_id, 0)
            current_level = TIER_HIERARCHY.get(tier['tier_id'], 0)
            
            if current_level < required_level:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": f"This requires {tier_id} tier or higher",
                        "current_tier": tier['name'],
                        "required_tier": tier_id,
                        "upgrade_url": f"/upgrade/{tier_id}"
                    }
                )
        
        # Return tier info
        return {
            'user_id': user_id,
            'tier_id': tier['tier_id'],
            'tier_name': tier['name'],
            'is_active': tier['is_active'],
            'trial_expiry': tier['trial_expiry'],
            'daily_call_limit': tier['daily_call_limit']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tier validation failed: {str(e)}")


def create_tier_endpoint_decorator(tier_id: Optional[str] = None, feature: Optional[str] = None, action: Optional[str] = None):
    """
    Decorator factory for protecting endpoints with tier requirements
    
    Usage:
        @app.get("/api/code/execute")
        async def execute_code(tier_info = Depends(create_tier_endpoint_decorator(feature='code_execution'))):
            pass
    """
    async def tier_check(tier_info = Depends(require_tier_access)):
        return tier_info
    
    # Bind the parameters
    return tier_check


# Export for easy use
def require_feature(feature: str):
    """Shorthand for requiring a specific feature"""
    return Depends(lambda tier_info = Depends(require_tier_access): tier_info)
