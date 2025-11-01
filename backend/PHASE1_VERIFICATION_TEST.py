#!/usr/bin/env python3
"""
PHASE 1 Testing - Simplified Tier Protection Test
Tests that tier validation is properly configured without requiring FastAPI
"""

import sqlite3
from pathlib import Path

print("\n" + "="*70)
print("  PHASE 1 TIER PROTECTION - VERIFICATION TEST")
print("="*70 + "\n")

# Test 1: Database exists and has data
print("✓ TEST 1: Checking database...")
db_path = Path(__file__).parent / "q_ide.db"
if not db_path.exists():
    print("  ❌ FAILED: Database not found")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Check membership_tiers
cursor.execute("SELECT COUNT(*) FROM membership_tiers")
tier_count = cursor.fetchone()[0]
if tier_count != 10:
    print(f"  ❌ FAILED: Expected 10 tiers, got {tier_count}")
    exit(1)
print(f"  ✅ PASSED: Found {tier_count} membership tiers")

# Test 2: Check tier features
print("\n✓ TEST 2: Checking tier features...")
cursor.execute("SELECT name, code_execution, webhooks FROM membership_tiers")
features = cursor.fetchall()
free_tier = next((t for t in features if t[0] == 'FREE'), None)
pro_tier = next((t for t in features if t[0] == 'PRO'), None)

if not free_tier:
    print("  ❌ FAILED: FREE tier not found")
    exit(1)
if not pro_tier:
    print("  ❌ FAILED: PRO tier not found")
    exit(1)

# FREE tier should NOT have code_execution
if free_tier[1]:  # code_execution
    print("  ❌ FAILED: FREE tier should not have code_execution")
    exit(1)
print("  ✅ PASSED: FREE tier doesn't have code_execution")

# PRO tier SHOULD have code_execution
if not pro_tier[1]:  # code_execution
    print("  ❌ FAILED: PRO tier should have code_execution")
    exit(1)
print("  ✅ PASSED: PRO tier has code_execution")

# Test 3: Verify test users
print("\n✓ TEST 3: Creating test users...")
cursor.execute("DELETE FROM user_subscriptions WHERE user_id IN ('test-free', 'test-pro')")

cursor.execute("""
    INSERT INTO user_subscriptions (user_id, tier_id, is_active, subscription_date)
    VALUES ('test-free', 'free', 1, datetime('now'))
""")

cursor.execute("""
    INSERT INTO user_subscriptions (user_id, tier_id, is_active, subscription_date)
    VALUES ('test-pro', 'pro', 1, datetime('now'))
""")

conn.commit()
print("  ✅ PASSED: Test users created")

# Test 4: Check middleware files exist
print("\n✓ TEST 4: Checking middleware...")
middleware_files = [
    "middleware/tier_validator.py",
    "services/rate_limiter.py",
    "services/trial_expiry_job.py"
]

for mf in middleware_files:
    path = Path(__file__).parent / mf
    if not path.exists():
        print(f"  ❌ FAILED: {mf} not found")
        exit(1)
    print(f"  ✅ Found: {mf}")

# Test 5: Check protected endpoints were modified
print("\n✓ TEST 5: Checking protected endpoints...")
protected_files = [
    "llm_chat_routes.py",
    "build_orchestration_routes.py", 
    "routes/orchestration_workflow.py"
]

for pf in protected_files:
    path = Path(__file__).parent / pf
    if not path.exists():
        print(f"  ❌ FAILED: {pf} not found")
        exit(1)
    
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        if 'require_tier_access' not in content:
            print(f"  ❌ FAILED: {pf} doesn't have tier protection")
            exit(1)
        if 'X-User-ID' not in content and 'X-User-Id' not in content:
            print(f"  ⚠️  WARNING: {pf} might not extract user ID properly")
    
    print(f"  ✅ Protected: {pf}")

# Test 6: Check database integration
print("\n✓ TEST 6: Checking database integration...")
cursor.execute("SELECT user_id, tier_id, is_active FROM user_subscriptions WHERE user_id IN ('test-free', 'test-pro') ORDER BY user_id")
users = cursor.fetchall()

if len(users) != 2:
    print(f"  ❌ FAILED: Expected 2 test users, got {len(users)}")
    exit(1)

free_user = next((u for u in users if u[0] == 'test-free'), None)
pro_user = next((u for u in users if u[0] == 'test-pro'), None)

if not free_user or free_user[1] != 'free' or not free_user[2]:
    print("  ❌ FAILED: FREE test user not properly configured")
    exit(1)

if not pro_user or pro_user[1] != 'pro' or not pro_user[2]:
    print("  ❌ FAILED: PRO test user not properly configured")
    exit(1)

print("  ✅ PASSED: Test users properly configured")

conn.close()

print("\n" + "="*70)
print("  ✅ ALL VERIFICATION TESTS PASSED!")
print("="*70)

print("""
NEXT STEPS:

1. Start the backend server in a NEW TERMINAL:
   cd C:\\Quellum-topdog-ide\\backend
   python -m uvicorn main:app --reload
   
   (Ignore any import errors - they're from optional modules)
   
   Once you see "Application startup complete", the server is ready.

2. In another terminal, test the endpoints:
   # Test FREE user (should get 403)
   curl -X POST http://localhost:8000/api/chat/ ^
     -H "X-User-ID: test-free" ^
     -H "Content-Type: application/json" ^
     -d '{"message":"test"}'
   
   # Test PRO user (should get 200 or 422 if validation fails - that's OK)
   curl -X POST http://localhost:8000/api/chat/ ^
     -H "X-User-ID: test-pro" ^
     -H "Content-Type: application/json" ^
     -d '{"message":"test"}'

3. Run the full test suite:
   .\\PHASE1_TEST_SCRIPT.ps1
   
EXPECTED RESULTS:
✅ FREE user: 403 Forbidden (tier not available)
✅ PRO user: 200 OK or 422 (endpoint validation - tier check passed!)
✅ Rate limiting enforced (20 calls/day for FREE)
✅ Webhooks feature blocked for FREE users

""")
