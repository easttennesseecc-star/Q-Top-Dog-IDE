"""
Rate limiting service for membership tiers
Checks daily API call limits and trial expiry
"""

import sqlite3
import os
from datetime import datetime, date
from typing import Any, Dict, Optional
from backend.database.tier_schema import MembershipTierSchema


class RateLimiter:
    """Manages rate limiting based on membership tier"""
    
    def __init__(self):
        self.db_path = MembershipTierSchema.get_db_path()
    
    def check_limit(self, user_id: str) -> Dict[str, Any]:
        """
        Check if user has exceeded daily limits
        Returns: {
            'allowed': bool,
            'remaining': int or None,
            'error': str or None,
            'tier': str or None
        }
        """
        # Test/dev bypass: allow disabling rate limiter in tests to avoid DB contention
        try:
            if os.getenv("DISABLE_RATE_LIMITER", "false").lower() in ("1", "true", "yes"):
                return {
                    'allowed': True,
                    'remaining': 999999,
                    'limit': 999999,
                    'used': 0,
                    'tier': 'bypass',
                    'error': None
                }
        except Exception:
            # Fall through to normal path on any env parsing error
            pass
        try:
            # Use a short timeout to avoid hanging if the DB is locked under concurrent tests
            conn = sqlite3.connect(self.db_path, timeout=0.2)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get user's subscription
            query = """
                SELECT us.tier_id, us.trial_expiry, us.is_active, mt.daily_call_limit, mt.name
                FROM user_subscriptions us
                JOIN membership_tiers mt ON us.tier_id = mt.tier_id
                WHERE us.user_id = ?
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return {
                    'allowed': False,
                    'error': 'No active subscription found',
                    'remaining': None,
                    'tier': None
                }
            
            tier_id, trial_expiry, is_active, daily_limit, tier_name = result
            
            # Check if subscription is active
            if not is_active:
                conn.close()
                return {
                    'allowed': False,
                    'error': 'Subscription is inactive or trial expired',
                    'remaining': None,
                    'tier': tier_name
                }
            
            # Check trial expiry for FREE tier
            if tier_id == 'free' and trial_expiry:
                if datetime.fromisoformat(trial_expiry) < datetime.utcnow():
                    conn.close()
                    return {
                        'allowed': False,
                        'error': 'FREE tier trial expired',
                        'expired_at': trial_expiry,
                        'remaining': None,
                        'tier': tier_name
                    }
            
            # Check daily usage
            today = date.today().isoformat()
            usage_query = """
                SELECT api_calls_used
                FROM daily_usage_tracking
                WHERE user_id = ? AND usage_date = ?
            """
            cursor.execute(usage_query, (user_id, today))
            usage_result = cursor.fetchone()
            
            if not usage_result:
                # Create usage record for today
                insert_query = """
                    INSERT INTO daily_usage_tracking (user_id, usage_date, api_calls_used)
                    VALUES (?, ?, 0)
                """
                cursor.execute(insert_query, (user_id, today))
                conn.commit()
                current_usage = 0
            else:
                current_usage = usage_result[0]
            
            # Check if limit exceeded
            if current_usage >= daily_limit:
                conn.close()
                return {
                    'allowed': False,
                    'error': 'Daily API call limit exceeded',
                    'limit': daily_limit,
                    'used': current_usage,
                    'remaining': 0,
                    'tier': tier_name
                }
            
            # Increment usage
            update_query = """
                UPDATE daily_usage_tracking
                SET api_calls_used = api_calls_used + 1, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND usage_date = ?
            """
            cursor.execute(update_query, (user_id, today))
            conn.commit()
            
            # Return success
            remaining = daily_limit - current_usage - 1
            conn.close()
            return {
                'allowed': True,
                'remaining': remaining,
                'limit': daily_limit,
                'used': current_usage + 1,
                'tier': tier_name,
                'error': None
            }
            
        except Exception as e:
            return {
                'allowed': False,
                'error': f'Rate limiter check failed: {str(e)}',
                'remaining': None,
                'tier': None
            }
    
    def get_user_tier(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's current tier information"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT mt.*, us.trial_expiry, us.subscription_date
                FROM membership_tiers mt
                JOIN user_subscriptions us ON mt.tier_id = us.tier_id
                WHERE us.user_id = ?
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return None
            
            # Convert Row object to dict
            return dict(result)
            
        except Exception as e:
            print(f"Error getting tier: {e}")
            return None
    
    def get_daily_usage(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's daily usage for today"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = date.today().isoformat()
            query = """
                SELECT api_calls_used, llm_requests_used, code_executions_used, storage_used_gb
                FROM daily_usage_tracking
                WHERE user_id = ? AND usage_date = ?
            """
            cursor.execute(query, (user_id, today))
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return {
                    'api_calls_used': 0,
                    'llm_requests_used': 0,
                    'code_executions_used': 0,
                    'storage_used_gb': 0
                }
            
            return {
                'api_calls_used': result[0],
                'llm_requests_used': result[1],
                'code_executions_used': result[2],
                'storage_used_gb': result[3]
            }
            
        except Exception as e:
            print(f"Error getting daily usage: {e}")
            return None
