#!/usr/bin/env python3
"""
Setup script for membership tier database
Creates all necessary tables
Run this FIRST before populate_tiers.py
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.tier_schema import MembershipTierSchema


def setup_database():
    """Create all membership tier tables"""
    
    print("\n" + "="*60)
    print("SETTING UP MEMBERSHIP TIER DATABASE (SQLite)")
    print("="*60 + "\n")
    
    try:
        # Create all tables (SQLite)
        MembershipTierSchema.setup_all_tables()
        
        # Verify tables were created
        print("\n" + "-"*60)
        print("VERIFICATION")
        print("-"*60 + "\n")
        
        import sqlite3
        db_path = MembershipTierSchema.get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        tables = ['membership_tiers', 'user_subscriptions', 'daily_usage_tracking', 'tier_audit_log']
        for table in tables:
            query = f"SELECT COUNT(*) FROM {table}"
            cursor.execute(query)
            count = cursor.fetchone()[0]
            print(f"✅ {table}: {count} rows")
        
        conn.close()
        
        print("\n" + "="*60)
        print("✅ DATABASE SETUP COMPLETE")
        print("="*60)
        print("\nNEXT STEPS:")
        print("1. Run: python seeds/populate_tiers.py")
        print("2. Verify tiers with: python scripts/verify_tiers.py")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}\n")
        sys.exit(1)


if __name__ == '__main__':
    setup_database()
