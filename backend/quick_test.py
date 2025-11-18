#!/usr/bin/env python3
import requests

BASE_URL = "http://127.0.0.1:8000"

print("Testing LLM Config Endpoints")
print("=" * 50)

# Test providers
print("\n[1] GET /llm_config/providers")
try:
    resp = requests.get(f"{BASE_URL}/llm_config/providers")
    print(f"Status: {resp.status_code}")
    if resp.ok:
        data = resp.json()
        print(f"OK - Cloud providers: {len(data.get('cloud', []))}")
        print(f"OK - Local models: {len(data.get('local', []))}")
except Exception as e:
    print(f"ERROR: {e}")

# Test roles
print("\n[2] GET /llm_config/roles")
try:
    resp = requests.get(f"{BASE_URL}/llm_config/roles")
    print(f"Status: {resp.status_code}")
    if resp.ok:
        data = resp.json()
        print(f"OK - Found {len(data.get('roles', []))} roles")
        for role in data.get('roles', [])[:3]:
            print(f"  - {role.get('id')}: {role.get('name')}")
except Exception as e:
    print(f"ERROR: {e}")

# Test status
print("\n[3] GET /llm_config/status")
try:
    resp = requests.get(f"{BASE_URL}/llm_config/status")
    print(f"Status: {resp.status_code}")
    if resp.ok:
        data = resp.json()
        print("OK - Configuration status:")
        print(f"  Cloud providers configured: {data.get('cloud_providers_configured')}/7")
        print(f"  Roles assigned: {data.get('roles_assigned')}/7")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 50)
print("ALL TESTS COMPLETE")
