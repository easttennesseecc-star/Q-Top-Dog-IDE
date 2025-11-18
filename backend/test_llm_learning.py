"""
Test script for LLM learning endpoints.

This script:
1. Starts a test build
2. Waits for it to complete
3. Fetches build data and codebase info
4. Submits an analysis report
5. Shows the LLMClient usage examples
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the client
from llm_client import LLMClient


def test_llm_endpoints():
    """Test all LLM learning endpoints."""
    
    client = LLMClient(backend_url="http://127.0.0.1:8000")
    
    print("=" * 60)
    print("Q-IDE LLM Learning Endpoints Test")
    print("=" * 60)
    
    # Test 1: Fetch builds
    print("\n[1] Fetching recent builds...")
    try:
        builds = client.get_builds(limit=5)
        print(f"✓ Found {builds.total} total builds")
        if builds.builds:
            print(f"  Showing {len(builds.builds)} most recent:")
            for build in builds.builds[:3]:
                print(f"    - {build.id[:8]}... ({build.status})")
    except Exception as e:
        print(f"✗ Error fetching builds: {e}")
        return False
    
    # Test 2: Get detailed build data (if any builds exist)
    if builds.builds:
        print(f"\n[2] Fetching detailed data for {builds.builds[0].id[:8]}...")
        try:
            build_data = client.get_build(builds.builds[0].id)
            summary = build_data.get("log_summary", {})
            print("✓ Build details:")
            print(f"  - Status: {build_data.get('status')}")
            print(f"  - Log lines: {summary.get('total_lines', 0)}")
            print(f"  - Errors: {summary.get('error_count', 0)}")
            print(f"  - Warnings: {summary.get('warning_count', 0)}")
            
            if summary.get("errors"):
                print(f"  - First error: {summary['errors'][0][:60]}...")
        except Exception as e:
            print(f"✗ Error fetching build details: {e}")
    
    # Test 3: Get codebase structure
    print("\n[3] Fetching codebase structure...")
    try:
        codebase = client.get_codebase()
        summary = codebase.get("structure_summary", {})
        config = codebase.get("key_config_files", {})
        backend_files = codebase.get("backend_files", [])
        
        print("✓ Codebase info:")
        print(f"  - Backend: {summary.get('has_backend', False)}")
        print(f"  - Frontend: {summary.get('has_frontend', False)}")
        print(f"  - Tests: {summary.get('has_tests', False)}")
        print(f"  - Config files found: {len(config)}")
        print(f"  - Backend Python files: {len(backend_files)}")
        
        if backend_files:
            print(f"  - Backend files: {', '.join([f['name'] for f in backend_files[:3]])}")
    except Exception as e:
        print(f"✗ Error fetching codebase: {e}")
        return False
    
    # Test 4: Submit a sample report (if builds exist)
    if builds.builds:
        print("\n[4] Submitting analysis report...")
        try:
            result = client.submit_report(
                build_id=builds.builds[0].id,
                report_type="failure_analysis",
                analysis="Sample analysis: Build processing completed successfully with comprehensive logging.",
                recommendations=[
                    "Continue monitoring build metrics",
                    "Consider caching for faster builds",
                    "Review and optimize test coverage"
                ],
                confidence=0.92
            )
            print("✓ Report submitted:")
            print(f"  - Report ID: {result.get('report_id', 'N/A')}")
            print(f"  - Message: {result.get('message', 'OK')}")
        except Exception as e:
            print(f"✗ Error submitting report: {e}")
    
    print("\n" + "=" * 60)
    print("LLM Learning Endpoints Test Complete!")
    print("=" * 60)
    
    # Show usage example
    print("\n[Usage Example]")
    print("-" * 60)
    print("""
from backend.llm_client import LLMClient

# Initialize client
client = LLMClient(backend_url="http://127.0.0.1:8000")

# Get recent builds
builds = client.get_builds(limit=10)
for build in builds.builds:
    if build.status == "failed":
        data = client.get_build(build.id)
        errors = data["log_summary"]["errors"]
        # ... your LLM analysis here ...

# Get project structure for context
codebase = client.get_codebase()
config_files = codebase["key_config_files"]

# Submit findings
client.submit_report(
    build_id=build.id,
    type="failure_analysis",
    analysis="...",
    recommendations=[...],
    confidence=0.85
)
    """)
    print("-" * 60)
    
    return True


if __name__ == "__main__":
    try:
        success = test_llm_endpoints()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
