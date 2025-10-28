#!/usr/bin/env python3
"""
Test script for LLM configuration endpoints
"""

import requests
import json
from pprint import pprint

BASE_URL = "http://127.0.0.1:8000"

def test_providers():
    """Test GET /llm_config/providers"""
    print("\n=== Testing GET /llm_config/providers ===")
    try:
        resp = requests.get(f"{BASE_URL}/llm_config/providers")
        print(f"Status: {resp.status_code}")
        print(f"Response:")
        pprint(resp.json())
        return resp.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_roles():
    """Test GET /llm_config/roles"""
    print("\n=== Testing GET /llm_config/roles ===")
    try:
        resp = requests.get(f"{BASE_URL}/llm_config/roles")
        print(f"Status: {resp.status_code}")
        print(f"Response:")
        pprint(resp.json())
        return resp.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_setup_instructions():
    """Test GET /llm_config/setup/{provider}"""
    print("\n=== Testing GET /llm_config/setup/openai ===")
    try:
        resp = requests.get(f"{BASE_URL}/llm_config/setup/openai")
        print(f"Status: {resp.status_code}")
        print(f"Response:")
        pprint(resp.json())
        return resp.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_api_key_operations():
    """Test API key save/check/delete"""
    print("\n=== Testing API Key Operations ===")
    
    # Test save
    print("\n1. POST /llm_config/api_key (save)")
    try:
        payload = {
            "provider": "openai",
            "api_key": "sk-test-key-12345"
        }
        resp = requests.post(f"{BASE_URL}/llm_config/api_key", json=payload)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
        if resp.status_code != 200:
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    # Test check
    print("\n2. GET /llm_config/api_key/openai (check)")
    try:
        resp = requests.get(f"{BASE_URL}/llm_config/api_key/openai")
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
        if resp.status_code != 200:
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    # Test delete
    print("\n3. DELETE /llm_config/api_key/openai (delete)")
    try:
        resp = requests.delete(f"{BASE_URL}/llm_config/api_key/openai")
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
        return resp.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_role_assignment():
    """Test role assignment operations"""
    print("\n=== Testing Role Assignment Operations ===")
    
    # Test assignment
    print("\n1. POST /llm_config/role_assignment")
    try:
        payload = {
            "role_id": "analysis",
            "model": "gpt-4"
        }
        resp = requests.post(f"{BASE_URL}/llm_config/role_assignment", json=payload)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
        if resp.status_code != 200:
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    # Test get assignment
    print("\n2. GET /llm_config/role_assignment/analysis")
    try:
        resp = requests.get(f"{BASE_URL}/llm_config/role_assignment/analysis")
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
        return resp.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_status():
    """Test GET /llm_config/status"""
    print("\n=== Testing GET /llm_config/status ===")
    try:
        resp = requests.get(f"{BASE_URL}/llm_config/status")
        print(f"Status: {resp.status_code}")
        print(f"Response:")
        pprint(resp.json())
        return resp.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Starting LLM Config Endpoint Tests...")
    print(f"Base URL: {BASE_URL}")
    
    results = {
        "providers": test_providers(),
        "roles": test_roles(),
        "setup_instructions": test_setup_instructions(),
        "api_key_operations": test_api_key_operations(),
        "role_assignment": test_role_assignment(),
        "status": test_status(),
    }
    
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
