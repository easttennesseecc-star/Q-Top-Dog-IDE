#!/usr/bin/env python3
"""
PHASE 3 VERIFICATION SCRIPT
Comprehensive testing of Phase 3 Pricing Page implementation
Tests backend API, frontend component readiness, and integration
"""

import requests
import json
import sys
from typing import Dict, List, Any

# Configuration
BASE_URL = "http://0.0.0.0:8000"
TEST_USER = "test-pro"
HEADERS = {"X-User-ID": TEST_USER, "Content-Type": "application/json"}

# ANSI Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_section(title: str) -> None:
    """Print a section header"""
    print(f"\n{BLUE}{BOLD}{'='*60}{RESET}")
    print(f"{BLUE}{BOLD}{title:^60}{RESET}")
    print(f"{BLUE}{BOLD}{'='*60}{RESET}\n")

def print_success(msg: str) -> None:
    """Print success message"""
    print(f"{GREEN}✓ {msg}{RESET}")

def print_error(msg: str) -> None:
    """Print error message"""
    print(f"{RED}✗ {msg}{RESET}")

def print_warning(msg: str) -> None:
    """Print warning message"""
    print(f"{YELLOW}⚠ {msg}{RESET}")

def print_info(msg: str) -> None:
    """Print info message"""
    print(f"{BLUE}ℹ {msg}{RESET}")

def check_server_health() -> bool:
    """Check if backend server is running"""
    print_section("Backend Server Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/api/tiers", headers=HEADERS, timeout=5)
        if response.status_code == 200:
            print_success(f"Backend server is running on {BASE_URL}")
            return True
        else:
            print_error(f"Backend returned {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to backend at {BASE_URL}")
        print_info("Start backend with: cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def verify_tiers_endpoint() -> Dict[str, Any]:
    """Verify /api/tiers endpoint"""
    print_section("Verify /api/tiers Endpoint")
    
    result = {
        "endpoint_works": False,
        "tiers_count": 0,
        "tiers": [],
        "tier_structure_valid": False
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/tiers", headers=HEADERS, timeout=5)
        
        if response.status_code != 200:
            print_error(f"Endpoint returned {response.status_code}")
            return result
        
        data = response.json()
        tiers = data.get("tiers", [])
        
        result["endpoint_works"] = True
        result["tiers_count"] = len(tiers)
        result["tiers"] = tiers
        
        print_success(f"Endpoint responds with {len(tiers)} tiers")
        
        # Verify structure
        required_fields = {"id", "name", "price", "emoji", "description", "monthly_api_calls", "support_level", "features"}
        
        for tier in tiers:
            tier_fields = set(tier.keys())
            if required_fields.issubset(tier_fields):
                result["tier_structure_valid"] = True
                break
        
        if result["tier_structure_valid"]:
            print_success("Tier structure contains required fields")
            
            # Print first tier as sample
            if tiers:
                tier = tiers[0]
                print_info(f"Sample tier: {tier.get('name')} ({tier.get('emoji')}) - ${tier.get('price')}/mo")
        else:
            print_error("Tier structure missing required fields")
            if tiers:
                print_info(f"First tier fields: {list(tiers[0].keys())}")
        
        return result
        
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON response: {e}")
        return result
    except Exception as e:
        print_error(f"Error: {e}")
        return result

def verify_tier_names(tiers: List[Dict]) -> bool:
    """Verify expected tier names exist"""
    print_section("Verify Tier Names")
    
    tier_names = {tier.get("name") for tier in tiers}
    expected_names = {
        "FREE", "STARTER", "PRO", "PROFESSIONAL", "TEAM", "TEAM_PLUS",
        "ENTERPRISE", "ENTERPRISE_PLUS", "ENTERPRISE_ULTIMATE", "PREMIUM"
    }
    
    found = tier_names.intersection(expected_names)
    missing = expected_names - tier_names
    extra = tier_names - expected_names
    
    if len(found) >= 8:
        print_success(f"Found {len(found)} expected tier names")
        for name in sorted(found):
            print_info(f"  • {name}")
        return True
    else:
        print_error(f"Only found {len(found)} of {len(expected_names)} expected tiers")
        if missing:
            print_warning(f"Missing: {missing}")
        if extra:
            print_warning(f"Extra: {extra}")
        return False

def verify_tier_pricing(tiers: List[Dict]) -> bool:
    """Verify tier pricing is reasonable"""
    print_section("Verify Tier Pricing")
    
    tiers_by_name = {t.get("name"): t for t in tiers}
    
    # Expected pricing order (should increase with tier level)
    pricing_checks = [
        ("FREE", 0),
        ("STARTER", (0, 100)),
        ("PROFESSIONAL", (100, 500)),
        ("ENTERPRISE", (500, 10000))
    ]
    
    all_valid = True
    for tier_name, expected_price in pricing_checks:
        tier = tiers_by_name.get(tier_name)
        if not tier:
            print_warning(f"Tier {tier_name} not found")
            continue
        
        price = tier.get("price", 0)
        
        if isinstance(expected_price, tuple):
            min_price, max_price = expected_price
            if min_price <= price <= max_price:
                print_success(f"{tier_name}: ${price}/mo (expected range ${min_price}-${max_price})")
            else:
                print_error(f"{tier_name}: ${price}/mo (expected range ${min_price}-${max_price})")
                all_valid = False
        else:
            if price == expected_price:
                print_success(f"{tier_name}: ${price}/mo")
            else:
                print_error(f"{tier_name}: ${price}/mo (expected ${expected_price})")
                all_valid = False
    
    return all_valid

def verify_tier_features(tiers: List[Dict]) -> bool:
    """Verify tiers have features"""
    print_section("Verify Tier Features")
    
    all_valid = True
    
    for tier in tiers[:3]:  # Check first 3 tiers
        name = tier.get("name")
        features = tier.get("features", [])
        
        if isinstance(features, list) and len(features) > 0:
            print_success(f"{name}: {len(features)} features")
        else:
            print_error(f"{name}: No features found")
            all_valid = False
    
    return all_valid

def verify_api_calls_limit(tiers: List[Dict]) -> bool:
    """Verify monthly API call limits"""
    print_section("Verify API Call Limits")
    
    all_valid = True
    
    for tier in tiers:
        name = tier.get("name")
        calls = tier.get("monthly_api_calls", 0)
        
        if calls >= 0:
            if calls >= 1000000:
                print_success(f"{name}: Unlimited API calls")
            else:
                print_success(f"{name}: {calls:,} API calls/month")
        else:
            print_error(f"{name}: Invalid API call limit: {calls}")
            all_valid = False
    
    return all_valid

def verify_support_levels(tiers: List[Dict]) -> bool:
    """Verify support levels are set"""
    print_section("Verify Support Levels")
    
    support_levels = set()
    all_valid = True
    
    for tier in tiers:
        name = tier.get("name")
        support = tier.get("support_level", "")
        
        if support:
            support_levels.add(support)
            print_info(f"{name}: {support}")
        else:
            print_error(f"{name}: No support level")
            all_valid = False
    
    print_info(f"Support levels found: {sorted(support_levels)}")
    return all_valid

def verify_user_tier_info() -> bool:
    """Verify user tier info endpoint"""
    print_section("Verify User Tier Info")
    
    try:
        response = requests.get(f"{BASE_URL}/api/tier/info", headers=HEADERS, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            tier_name = data.get("tier_name")
            print_success(f"User {TEST_USER} is on tier: {tier_name}")
            return True
        else:
            print_error(f"Endpoint returned {response.status_code}")
            return False
    except Exception as e:
        print_warning(f"Could not verify user tier: {e}")
        return True  # Non-critical

def verify_file_structure() -> bool:
    """Verify file structure for Phase 3"""
    print_section("Verify File Structure")
    
    import os
    
    files_to_check = [
        ("PricingPage.tsx", "C:\\Quellum-topdog-ide\\frontend\\src\\pages\\PricingPage.tsx"),
        ("pricing-page.css", "C:\\Quellum-topdog-ide\\frontend\\src\\styles\\pricing-page.css"),
    ]
    
    all_exist = True
    
    for name, path in files_to_check:
        if os.path.exists(path):
            size = os.path.getsize(path)
            print_success(f"{name}: {size:,} bytes")
        else:
            print_error(f"{name}: File not found at {path}")
            all_exist = False
    
    return all_exist

def main():
    """Run all verifications"""
    print(f"\n{BOLD}{'='*60}")
    print(f"{'PHASE 3 VERIFICATION SCRIPT':^60}")
    print(f"{'='*60}{RESET}\n")
    
    results = {
        "server_running": False,
        "endpoint_works": False,
        "tier_names_valid": False,
        "pricing_valid": False,
        "features_valid": False,
        "api_limits_valid": False,
        "support_levels_valid": False,
        "files_exist": False,
        "total_tiers": 0
    }
    
    # Check server
    if not check_server_health():
        print_section("❌ VERIFICATION FAILED")
        print_error("Backend server is not running. Cannot continue.")
        sys.exit(1)
    results["server_running"] = True
    
    # Check endpoint
    tier_data = verify_tiers_endpoint()
    results["endpoint_works"] = tier_data["endpoint_works"]
    results["total_tiers"] = tier_data["tiers_count"]
    
    if not tier_data["endpoint_works"]:
        print_section("❌ VERIFICATION FAILED")
        print_error("Tiers endpoint is not working. Cannot continue.")
        sys.exit(1)
    
    tiers = tier_data["tiers"]
    
    # Run additional checks
    results["tier_names_valid"] = verify_tier_names(tiers)
    results["pricing_valid"] = verify_tier_pricing(tiers)
    results["features_valid"] = verify_tier_features(tiers)
    results["api_limits_valid"] = verify_api_calls_limit(tiers)
    results["support_levels_valid"] = verify_support_levels(tiers)
    results["files_exist"] = verify_file_structure()
    verify_user_tier_info()
    
    # Summary
    print_section("VERIFICATION SUMMARY")
    
    passed = sum(1 for k, v in results.items() if k != "total_tiers" and v)
    total = len([k for k in results.keys() if k != "total_tiers"])
    
    print_info(f"Tests passed: {passed}/{total}")
    print_info(f"Total tiers in database: {results['total_tiers']}")
    
    print(f"\n{BOLD}Results:{RESET}")
    for key, value in results.items():
        if key == "total_tiers":
            continue
        status = f"{GREEN}PASS{RESET}" if value else f"{RED}FAIL{RESET}"
        key_display = key.replace("_", " ").title()
        print(f"  {key_display}: {status}")
    
    # Final verdict
    print_section("PHASE 3 VERIFICATION RESULT")
    
    if passed == total:
        print_success("ALL CHECKS PASSED ✓")
        print_info("Phase 3 is ready for testing!")
        print_info("Next steps:")
        print_info("  1. Start frontend: cd frontend && npm start")
        print_info("  2. Open http://localhost:3000")
        print_info("  3. Click 'Pricing' tab")
        print_info("  4. Test grid/table views and FAQ")
        return 0
    else:
        print_error(f"Some checks failed ({total - passed} failed)")
        print_warning("Please review the errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
