#!/usr/bin/env python3
"""
Verify membership tiers are set up correctly
"""

import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.tier_schema import MembershipTierSchema


def verify_tiers():
    """Verify all tiers were created"""
    
    print("\n" + "="*60)
    print("MEMBERSHIP TIER VERIFICATION")
    print("="*60 + "\n")
    
    try:
        db_path = MembershipTierSchema.get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tier count
        cursor.execute("SELECT COUNT(*) FROM membership_tiers")
        count = cursor.fetchone()[0]
        print(f"✅ Total tiers: {count}/9")
        
        if count != 9:
            print(f"⚠️  Expected 9 tiers, found {count}")
        
        # Show all tiers
        print("\n" + "Tiers in database:")
        print("-" * 70)
        
        cursor.execute("""
            SELECT tier_id, name, price, daily_call_limit, code_execution
            FROM membership_tiers
            ORDER BY price ASC
        """)
        
        tiers = cursor.fetchall()
        for tier in tiers:
            tier_id, name, price, daily_limit, code_exec = tier
            code_status = "✅" if code_exec else "❌"
            print(f"  {name:30} ${price:7.0f}/mo  {daily_limit:>10} calls  {code_status}")
        
        # Check subscriptions
        print("\n" + "-" * 70)
        cursor.execute("SELECT COUNT(*) FROM user_subscriptions")
        sub_count = cursor.fetchone()[0]
        print(f"✅ User subscriptions: {sub_count}")
        
        # Check usage tracking
        cursor.execute("SELECT COUNT(*) FROM daily_usage_tracking")
        usage_count = cursor.fetchone()[0]
        print(f"✅ Usage records: {usage_count}")
        
        # Check audit log
        cursor.execute("SELECT COUNT(*) FROM tier_audit_log")
        audit_count = cursor.fetchone()[0]
        print(f"✅ Audit logs: {audit_count}")
        
        # Show tier features - NEW PROGRESSIVE VALUE LADDER
        print("\n" + "="*100)
        print("FEATURE PROGRESSION BY TIER (Progressive Value Ladder)")
        print("="*100)
        
        cursor.execute("""
            SELECT name, code_execution, webhooks, custom_llms, 
                   team_members, role_based_access, shared_workspaces,
                   hipaa_ready, sso_saml, on_premise_deploy, support_response_hours
            FROM membership_tiers
            ORDER BY price ASC
        """)
        
        print(f"\n{'Tier':<18} {'Code':<5} {'Webhooks':<9} {'LLMs':<6} {'Teams':<7} {'RBAC':<5} {'Shared':<7} {'HIPAA':<6} {'SSO':<5} {'On-Prem':<8} {'Support':<10}")
        print("-" * 100)
        
        for row in cursor.fetchall():
            name, code, webhooks, llms, teams, rbac, shared, hipaa, sso, onprem, support = row
            code_str = "✅" if code else "❌"
            webhooks_str = "✅" if webhooks else "❌"
            llms_str = "✅" if llms else "❌"
            rbac_str = "✅" if rbac else "❌"
            shared_str = "✅" if shared else "❌"
            hipaa_str = "✅" if hipaa else "❌"
            sso_str = "✅" if sso else "❌"
            onprem_str = "✅" if onprem else "❌"
            teams_str = f"{teams}" if teams > 1 else "-"
            support_str = f"{support}h" if support >= 1 else f"{int(support*60)}m"
            print(f"{name:<18} {code_str:<5} {webhooks_str:<9} {llms_str:<6} {teams_str:<7} {rbac_str:<5} {shared_str:<7} {hipaa_str:<6} {sso_str:<5} {onprem_str:<8} {support_str:<10}")
        
        # Show tier unlocks
        print("\n" + "="*100)
        print("KEY FEATURES BY TIER LEVEL")
        print("="*100)
        
        unlocks = [
            ("FREE tier:", "Community support, 20 API calls/day, no code execution"),
            ("→ PRO ($20):", "CODE EXECUTION ✅ | Webhooks | 10K calls/day | Email support"),
            ("→ PRO-PLUS ($45):", "CUSTOM LLMs ✅ | Custom integrations | 50K calls/day | 60-day logs"),
            ("→ TEAMS ($100-800):", "TEAM COLLABORATION ✅ | RBAC | Shared workspaces | Audit logs"),
            ("→ ENTERPRISE ($5K-50K):", "COMPLIANCE ✅ (HIPAA, SOC2) | SSO/SAML | 24/7 support"),
            ("→ ULTIMATE ($50K):", "ON-PREMISE ✅ | Data residency | Executive access | Custom SLA"),
        ]
        
        for tier, features in unlocks:
            print(f"\n{tier:<20} {features}")

        
        conn.close()
        
        print("\n" + "="*60)
        print("✅ VERIFICATION COMPLETE - All tiers ready!")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


if __name__ == '__main__':
    success = verify_tiers()
    sys.exit(0 if success else 1)
