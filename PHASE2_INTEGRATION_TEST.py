#!/usr/bin/env python
"""
Phase 2 Integration Test
Tests the tier system endpoints with backend server
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_endpoints():
    """Test all tier endpoints"""
    
    test_user_id = "test-pro"
    
    print("\n" + "="*60)
    print("PHASE 2 INTEGRATION TEST - Tier System APIs")
    print("="*60)
    
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": test_user_id
    }
    
    tests = [
        {
            "name": "/api/tier/info - Get current tier info",
            "method": "GET",
            "url": f"{BASE_URL}/api/tier/info",
            "headers": headers,
        },
        {
            "name": "/api/tier/usage - Get API usage",
            "method": "GET",
            "url": f"{BASE_URL}/api/tier/usage",
            "headers": headers,
        },
        {
            "name": "/api/tier/trial - Get trial info",
            "method": "GET",
            "url": f"{BASE_URL}/api/tier/trial",
            "headers": headers,
        },
        {
            "name": "/api/tiers - Get all available tiers",
            "method": "GET",
            "url": f"{BASE_URL}/api/tiers",
            "headers": headers,
        },
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print(f"\nTesting: {test['name']}")
            print(f"   URL: {test['url']}")
            print(f"   User: {test_user_id}")
            
            if test["method"] == "GET":
                response = requests.get(test["url"], headers=test["headers"], timeout=5)
            else:
                response = requests.post(test["url"], headers=test["headers"], timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print("   SUCCESS (200)")
                print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
                passed += 1
            else:
                print(f"   FAILED ({response.status_code})")
                print(f"   Error: {response.text[:200]}")
                failed += 1
                
        except requests.exceptions.ConnectionError:
            print("   CONNECTION ERROR - Is the server running on port 8000?")
            failed += 1
        except Exception as e:
            print(f"   ERROR: {str(e)}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return passed, failed

if __name__ == "__main__":
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    for i in range(30):
        try:
            requests.get(f"{BASE_URL}/api/health", timeout=1)
            print("Server is ready!")
            break
        except:
            print(f"Waiting... ({i+1}/30)")
            time.sleep(1)
    else:
        print("Server did not start in time")
        exit(1)
    
    passed, failed = test_endpoints()
    exit(0 if failed == 0 else 1)
