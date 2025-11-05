"""
Trial expiry check service
Runs daily to deactivate expired FREE tier trials
"""

import sqlite3
from datetime import datetime, timedelta
from backend.database.tier_schema import MembershipTierSchema
import threading
import time


class TrialExpiryChecker:
    """Manages trial expiry checks"""
    
    def __init__(self):
        self.db_path = MembershipTierSchema.get_db_path()
        self.running = False
        self.thread = None
    
    def check_expired_trials(self):
        """Deactivate expired FREE tier trials"""
        try:
            print("\n🔄 Checking for expired trials...")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find expired FREE tier trials that are still active
            query = """
                SELECT user_id, trial_expiry
                FROM user_subscriptions
                WHERE tier_id = 'free' 
                  AND trial_expiry < datetime('now')
                  AND is_active = TRUE
            """
            cursor.execute(query)
            expired_trials = cursor.fetchall()
            
            if not expired_trials:
                print("✅ No expired trials found")
                conn.close()
                return
            
            # Deactivate each expired trial
            count = 0
            for user_id, trial_expiry in expired_trials:
                try:
                    # Update user_subscriptions
                    update_query = """
                        UPDATE user_subscriptions
                        SET is_active = FALSE
                        WHERE user_id = ? AND tier_id = 'free'
                    """
                    cursor.execute(update_query, (user_id,))
                    
                    # Log to audit table
                    audit_query = """
                        INSERT INTO tier_audit_log (user_id, old_tier, new_tier, change_reason)
                        VALUES (?, ?, ?, ?)
                    """
                    cursor.execute(audit_query, (user_id, 'free', 'free', 'trial_expired'))
                    
                    conn.commit()
                    count += 1
                    print(f"  ⏰ Trial expired for {user_id}")
                    
                except Exception as e:
                    print(f"  ❌ Error deactivating trial for {user_id}: {e}")
                    conn.rollback()
            
            conn.close()
            print(f"✅ Marked {count} trials as expired\n")
            
        except Exception as e:
            print(f"❌ Error checking expired trials: {e}")
    
    def start_background_job(self, check_interval_hours: int = 24):
        """
        Start background thread for checking expired trials
        
        Args:
            check_interval_hours: How often to check (default: daily)
        """
        if self.running:
            print("⚠️  Trial checker already running")
            return
        
        self.running = True
        
        def run_periodic_check():
            while self.running:
                try:
                    self.check_expired_trials()
                    # Sleep for specified interval
                    sleep_seconds = check_interval_hours * 60 * 60
                    time.sleep(sleep_seconds)
                except Exception as e:
                    print(f"Error in trial checker thread: {e}")
                    time.sleep(60)  # Retry after 1 minute
        
        self.thread = threading.Thread(target=run_periodic_check, daemon=True)
        self.thread.start()
        print(f"✅ Trial expiry checker started (checks every {check_interval_hours} hour(s))")
    
    def stop_background_job(self):
        """Stop the background job"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("⏹️  Trial expiry checker stopped")
    
    def schedule_check_at_midnight(self):
        """
        Schedule trial expiry check to run at midnight UTC every day
        More sophisticated than simple interval
        """
        if self.running:
            print("⚠️  Trial checker already running")
            return
        
        self.running = True
        
        def run_daily_at_midnight():
            while self.running:
                try:
                    now = datetime.utcnow()
                    
                    # Calculate time until next midnight UTC
                    tomorrow = now.date() + timedelta(days=1)
                    midnight = datetime.combine(tomorrow, datetime.min.time())
                    seconds_until_midnight = (midnight - now).total_seconds()
                    
                    print(f"⏰ Next trial check at midnight UTC ({seconds_until_midnight/3600:.1f} hours)")
                    
                    # Sleep until midnight
                    time.sleep(seconds_until_midnight)
                    
                    # Run check
                    self.check_expired_trials()
                    
                except Exception as e:
                    print(f"Error in midnight scheduler: {e}")
                    time.sleep(60)
        
        self.thread = threading.Thread(target=run_daily_at_midnight, daemon=True)
        self.thread.start()
        print("✅ Trial expiry checker started (runs daily at midnight UTC)")
    
    def __del__(self):
        """Cleanup on destruction"""
        self.stop_background_job()


# Singleton instance
_trial_checker = None


def initialize_trial_checker():
    """Initialize the trial expiry checker"""
    global _trial_checker
    if _trial_checker is None:
        _trial_checker = TrialExpiryChecker()
    return _trial_checker


def start_trial_checker(schedule_type: str = 'daily'):
    """
    Start the trial expiry checker
    
    Args:
        schedule_type: 'daily' (at midnight) or 'interval' (every N hours)
    """
    checker = initialize_trial_checker()
    
    if schedule_type == 'daily':
        checker.schedule_check_at_midnight()
    else:
        checker.start_background_job(check_interval_hours=24)
    
    return checker


def stop_trial_checker():
    """Stop the trial expiry checker"""
    global _trial_checker
    if _trial_checker:
        _trial_checker.stop_background_job()
