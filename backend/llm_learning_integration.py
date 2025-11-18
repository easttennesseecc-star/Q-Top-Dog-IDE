"""
LLM Learning Integration Example
Shows how to connect your custom Coding LLM to the learning endpoints
for continuous improvement and knowledge extraction.

Usage:
    python backend/llm_learning_integration.py
"""

import requests
from typing import List, Dict

# Configuration
API_BASE_URL = "http://localhost:8000/api/llm/learning"
CODING_LLM_MODEL = "gpt-4"  # Change to your model


class CodingLLMLearningClient:
    """Client for your custom Coding LLM to connect to learning endpoints."""
    
    def __init__(self, base_url: str = API_BASE_URL, model: str = CODING_LLM_MODEL):
        self.base_url = base_url
        self.model = model
        self.session = requests.Session()
    
    def get_recent_builds(self, limit: int = 20) -> List[Dict]:
        """Fetch recent builds for your LLM to analyze."""
        try:
            response = self.session.get(
                f"{self.base_url}/builds",
                params={"limit": limit, "skip": 0}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("builds", [])
        except Exception as e:
            print(f"Error fetching builds: {e}")
            return []
    
    def get_build_detail(self, build_id: str) -> Dict:
        """Get detailed info about a specific build."""
        try:
            response = self.session.get(f"{self.base_url}/build/{build_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching build detail: {e}")
            return {}
    
    def get_codebase_info(self) -> Dict:
        """Get current codebase structure for context."""
        try:
            response = self.session.get(f"{self.base_url}/codebase")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching codebase info: {e}")
            return {}
    
    def submit_learning_report(
        self,
        build_id: str,
        analysis_type: str,
        findings: Dict,
        recommendations: List[str],
        confidence: float
    ) -> Dict:
        """Submit a learning report from your LLM analysis."""
        try:
            report = {
                "build_id": build_id,
                "analysis_type": analysis_type,
                "findings": findings,
                "recommendations": recommendations,
                "confidence": confidence,
                "model_version": self.model
            }
            response = self.session.post(
                f"{self.base_url}/report",
                json=report
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error submitting report: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_metrics(self) -> Dict:
        """Get learning system metrics."""
        try:
            response = self.session.get(f"{self.base_url}/metrics")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching metrics: {e}")
            return {}


def example_learning_workflow():
    """Example: How your Coding LLM learns from builds."""
    
    print("=" * 70)
    print("Coding LLM Learning Integration Example")
    print("=" * 70)
    
    client = CodingLLMLearningClient()
    
    # Step 1: Get codebase context
    print("\n📚 Step 1: Fetching codebase structure...")
    codebase = client.get_codebase_info()
    if codebase.get("status") == "ok":
        print("  ✓ Codebase info loaded")
        print(f"    - Main dirs: {', '.join(codebase['structure']['main_dirs'].keys())}")
        print(f"    - Models available: {', '.join(codebase['models']['available'])}")
    
    # Step 2: Get recent builds to analyze
    print("\n🔍 Step 2: Fetching recent builds...")
    builds = client.get_recent_builds(limit=5)
    print(f"  ✓ Retrieved {len(builds)} builds for analysis")
    
    if builds:
        # Step 3: Analyze a build
        build = builds[0]
        build_id = build.get("id", "unknown")
        print(f"\n🔎 Step 3: Analyzing build {build_id[:12]}...")
        
        build_detail = client.get_build_detail(build_id)
        if build_detail.get("status") == "ok":
            print("  ✓ Build details retrieved")
            
            # Step 4: Generate insights and submit report
            print("\n💡 Step 4: Generating learning insights...")
            
            report = client.submit_learning_report(
                build_id=build_id,
                analysis_type="code_quality",
                findings={
                    "pattern_recognition": "React hooks usage +15% over baseline",
                    "error_handling": "2 potential null reference issues detected",
                    "performance": "Bundle size optimizable by 8%"
                },
                recommendations=[
                    "Add error boundary for React component",
                    "Implement null-coalescing in data access",
                    "Tree-shake unused CSS utilities"
                ],
                confidence=0.94
            )
            
            if report.get("status") == "ok":
                print("  ✓ Report submitted successfully")
                print(f"    - Report ID: {report.get('report_id')}")
                print(f"    - Insights updated: {report.get('insights_updated')}")
    
    # Step 5: Get learning metrics
    print("\n📊 Step 5: Current learning metrics...")
    metrics = client.get_metrics()
    if metrics.get("status") == "ok":
        print(f"  ✓ Builds analyzed: {metrics.get('builds_analyzed')}")
        print(f"  ✓ Reports submitted: {metrics.get('learning_reports_submitted')}")
        print(f"  ✓ Model accuracy: {metrics.get('model_accuracy')}%")
        print("  ✓ Recent improvements:")
        for improvement in metrics.get("model_improvements", [])[:3]:
            print(f"    - {improvement}")
    
    print("\n" + "=" * 70)
    print("Learning workflow complete! Your LLM can now:")
    print("  1. Analyze recent builds from Q-IDE")
    print("  2. Generate insights and recommendations")
    print("  3. Submit learning reports for continuous improvement")
    print("=" * 70)


if __name__ == "__main__":
    example_learning_workflow()
