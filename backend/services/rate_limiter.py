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
                SELECT us.tier_id, us.trial_expiry, us.is_active,
                       mt.daily_call_limit, mt.name,
                       mt.org_pooled_api_calls_per_seat
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
            
            tier_id, trial_expiry, is_active, daily_limit, tier_name, org_pooled_per_seat = result
            
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
            
            # Check if limit exceeded; attempt org pooled fallback for team tiers
            if current_usage >= daily_limit:
                # Only Team/Enterprise tiers have org pooled buckets
                if tier_id in ('teams', 'enterprise') and org_pooled_per_seat and int(org_pooled_per_seat) > 0:
                    today = date.today().isoformat()
                    # Find user's organization (first active membership)
                    cursor.execute(
                        "SELECT org_id FROM organization_members WHERE user_id = ? AND is_active = 1 LIMIT 1",
                        (user_id,)
                    )
                    org_row = cursor.fetchone()
                    if org_row:
                        org_id = org_row[0]
                        # Seat count = active members in org
                        cursor.execute(
                            "SELECT COUNT(1) FROM organization_members WHERE org_id = ? AND is_active = 1",
                            (org_id,)
                        )
                        seat_count = int(cursor.fetchone()[0] or 0)
                        total_pool = int(org_pooled_per_seat) * max(seat_count, 0)
                        # Create usage row if missing
                        cursor.execute(
                            "SELECT api_calls_used FROM org_daily_usage WHERE org_id = ? AND usage_date = ?",
                            (org_id, today)
                        )
                        row = cursor.fetchone()
                        if not row:
                            cursor.execute(
                                "INSERT INTO org_daily_usage (org_id, usage_date, api_calls_used) VALUES (?, ?, 0)",
                                (org_id, today)
                            )
                            conn.commit()
                            org_used = 0
                        else:
                            org_used = int(row[0] or 0)
                        if org_used < total_pool:
                            # Consume from org pool
                            cursor.execute(
                                "UPDATE org_daily_usage SET api_calls_used = api_calls_used + 1, updated_at = CURRENT_TIMESTAMP WHERE org_id = ? AND usage_date = ?",
                                (org_id, today)
                            )
                            conn.commit()
                            remaining_org = max(0, total_pool - (org_used + 1))
                            conn.close()
                            return {
                                'allowed': True,
                                'remaining': remaining_org,
                                'limit': total_pool,
                                'used': org_used + 1,
                                'tier': tier_name,
                                'source': 'org_pool',
                                'error': None
                            }
                # No org fallback or exhausted
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
                'source': 'personal',
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

    def get_byok_pool_status(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Return BYOK pool capacity and usage for the user's org when applicable.
        For Teams/Enterprise: capacity = org_byok_base + org_byok_per_seat * active_seats.
        For solo tiers: capacity = byok_slots_per_seat; used = count of stored credentials for that user.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(
                """
                SELECT us.tier_id, mt.byok_slots_per_seat, mt.org_byok_base, mt.org_byok_per_seat
                FROM user_subscriptions us
                JOIN membership_tiers mt ON us.tier_id = mt.tier_id
                WHERE us.user_id = ?
                """,
                (user_id,)
            )
            row = cur.fetchone()
            if not row:
                conn.close()
                return None
            tier_id = row["tier_id"]
            if tier_id in ("teams", "enterprise"):
                # Find org and seat count
                cur.execute(
                    "SELECT org_id FROM organization_members WHERE user_id = ? AND is_active = 1 LIMIT 1",
                    (user_id,)
                )
                org_row = cur.fetchone()
                if not org_row:
                    conn.close()
                    return {"capacity": 0, "used": 0, "scope": "org"}
                org_id = org_row[0]
                cur.execute(
                    "SELECT COUNT(1) FROM organization_members WHERE org_id = ? AND is_active = 1",
                    (org_id,)
                )
                seats = int(cur.fetchone()[0] or 0)
                base = int(row["org_byok_base"] or 0)
                per_seat = int(row["org_byok_per_seat"] or 0)
                capacity = base + per_seat * seats
                # Count active credentials
                cur.execute(
                    "SELECT COUNT(1) FROM organization_byok_credentials WHERE org_id = ? AND active = 1",
                    (org_id,)
                )
                used = int(cur.fetchone()[0] or 0)
                conn.close()
                return {"capacity": capacity, "used": used, "scope": "org", "org_id": org_id}
            else:
                capacity = int(row["byok_slots_per_seat"] or 0)
                # Personal usage: count credentials in llm_credentials.json for this user
                used = 0
                try:
                    from backend.llm_auth import load_credentials  # local import to avoid circular at module level
                    creds = load_credentials()
                    providers = creds.get("providers", {})
                    for p_data in providers.values():
                        try:
                            if p_data.get("user") == user_id:
                                used += 1
                        except Exception:
                            pass
                except Exception:
                    used = 0
                conn.close()
                return {"capacity": capacity, "used": used, "scope": "user"}
        except Exception as e:
            print(f"Error getting BYOK pool status: {e}")
            return None
