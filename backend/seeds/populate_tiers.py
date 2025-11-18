#!/usr/bin/env python3
"""
Populate membership tiers into database
Run this after creating tables
"""

import sys
import os
import sqlite3

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.tier_schema import TIER_CONFIGS, MembershipTierSchema


def populate_tiers():
    """Insert all 9 membership tiers into the database"""
    
    print("\n" + "="*60)
    print("POPULATING MEMBERSHIP TIERS")
    print("="*60 + "\n")
    
    db_path = MembershipTierSchema.get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for tier in TIER_CONFIGS:
        try:
            # Check if tier already exists
            cursor.execute("SELECT tier_id FROM membership_tiers WHERE tier_id = ?", (tier['tier_id'],))
            existing = cursor.fetchone()
            
            if existing:
                print(f"⏭️  {tier['name']} tier already exists (skipping)")
                continue
            
            # Build INSERT query dynamically
            columns = ', '.join(tier.keys())
            placeholders = ', '.join(['?'] * len(tier))
            values = tuple(tier.values())
            
            insert_query = f"INSERT INTO membership_tiers ({columns}) VALUES ({placeholders})"
            
            cursor.execute(insert_query, values)
            conn.commit()
            
            print(f"✅ {tier['name']:30} tier created (${tier['price']:6.0f}/mo)")
            
        except Exception as e:
            print(f"❌ {tier['name']:30} FAILED: {e}")
            conn.rollback()
    
    print("\n" + "="*60)
    print("✅ MEMBERSHIP TIER POPULATION COMPLETE")
    print("="*60 + "\n")
    
    # Verify
    cursor.execute("SELECT COUNT(*) as count FROM membership_tiers")
    count = cursor.fetchone()[0]
    print(f"✅ Total tiers in database: {count}/10\n")
    
    conn.close()


if __name__ == '__main__':
    try:
        populate_tiers()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
