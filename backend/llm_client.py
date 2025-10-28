"""
LLM Learning Client - Interface for coding LLMs to access build and codebase data.

This module provides a simple Python interface for your coding LLM to:
1. Fetch recent builds and their logs
2. Get codebase structure and source files
3. Submit analysis reports and recommendations
4. Learn from build patterns and failures

Usage:
    from llm_client import LLMClient
    
    client = LLMClient(backend_url="http://127.0.0.1:8000")
    
    # Fetch recent builds
    builds = client.get_builds(limit=10)
    
    # Get detailed build data
    build = client.get_build("build-id-123")
    
    # Get codebase structure
    codebase = client.get_codebase()
    
    # Submit analysis
    client.submit_report(
        build_id="build-id-123",
        type="failure_analysis",
        analysis="Test failed because X",
        recommendations=["Fix Y", "Add Z"],
        confidence=0.85
    )
"""

import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class Build:
    id: str
    status: str
    log: str


@dataclass
class BuildSummary:
    total: int
    builds: List[Build]
    skip: int
    limit: int


class LLMClient:
    """Client for accessing Q TopDog LLM learning endpoints."""
    
    def __init__(self, backend_url: str = "http://127.0.0.1:8000", session_id: Optional[str] = None):
        """Initialize LLM client.
        
        Args:
            backend_url: Backend API base URL
            session_id: Optional OAuth session ID for authenticated requests
        """
        self.backend_url = backend_url.rstrip('/')
        self.session_id = session_id
    
    def _get_params(self) -> Dict[str, str]:
        """Get query parameters including session_id if authenticated."""
        params = {}
        if self.session_id:
            params['session_id'] = self.session_id
        return params
    
    def get_builds(self, limit: int = 20, skip: int = 0) -> BuildSummary:
        """Fetch recent builds for learning.
        
        Args:
            limit: Maximum number of builds to return
            skip: Number of builds to skip (for pagination)
        
        Returns:
            BuildSummary with list of builds
        
        Raises:
            requests.RequestException: If API call fails
        """
        params = self._get_params()
        params['limit'] = str(limit)
        params['skip'] = str(skip)
        
        response = requests.get(
            f"{self.backend_url}/llm/learning/builds",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "ok":
            raise Exception(f"API error: {data.get('message', 'unknown')}")
        
        builds = [
            Build(
                id=b.get("id"),
                status=b.get("status"),
                log=b.get("log", "")
            )
            for b in data.get("builds", [])
        ]
        
        return BuildSummary(
            total=data.get("total", 0),
            builds=builds,
            skip=data.get("skip", skip),
            limit=data.get("limit", limit)
        )
    
    def get_build(self, build_id: str) -> Dict[str, Any]:
        """Fetch detailed build data including log analysis.
        
        Args:
            build_id: ID of the build to fetch
        
        Returns:
            Build data with log summary and error analysis
        
        Raises:
            requests.RequestException: If API call fails
        """
        params = self._get_params()
        
        response = requests.get(
            f"{self.backend_url}/llm/learning/build/{build_id}",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "ok":
            raise Exception(f"API error: {data.get('message', 'unknown')}")
        
        return data.get("build", {})
    
    def get_codebase(self) -> Dict[str, Any]:
        """Fetch codebase structure and source files.
        
        Returns:
            Codebase metadata including:
            - file_tree: Recursive directory structure
            - key_config_files: Content of package.json, tsconfig.json, etc.
            - backend_files: Python backend files with previews
            - structure_summary: Quick overview of project layout
        
        Raises:
            requests.RequestException: If API call fails
        """
        params = self._get_params()
        
        response = requests.get(
            f"{self.backend_url}/llm/learning/codebase",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "ok":
            raise Exception(f"API error: {data.get('message', 'unknown')}")
        
        return data.get("codebase", {})
    
    def submit_report(
        self,
        build_id: str,
        report_type: str,
        analysis: str,
        recommendations: Optional[List[str]] = None,
        confidence: float = 0.5
    ) -> Dict[str, Any]:
        """Submit LLM analysis report about a build.
        
        Args:
            build_id: ID of the build being analyzed
            report_type: Type of report (e.g., "failure_analysis", "code_improvement", "test_coverage")
            analysis: Detailed analysis text
            recommendations: List of recommended actions
            confidence: Confidence score (0.0 - 1.0)
        
        Returns:
            API response with report_id
        
        Raises:
            requests.RequestException: If API call fails
        """
        params = self._get_params()
        
        payload = {
            "build_id": build_id,
            "type": report_type,
            "analysis": analysis,
            "recommendations": recommendations or [],
            "confidence": confidence
        }
        
        response = requests.post(
            f"{self.backend_url}/llm/learning/report",
            json=payload,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "ok":
            raise Exception(f"API error: {data.get('message', 'unknown')}")
        
        return data


def analyze_build_failure(client: LLMClient, build_id: str) -> Dict[str, Any]:
    """Example: Analyze a build failure and submit a report.
    
    Args:
        client: LLMClient instance
        build_id: Build to analyze
    
    Returns:
        Analysis result
    """
    build = client.get_build(build_id)
    
    errors = build.get("log_summary", {}).get("errors", [])
    log = build.get("log", "")
    
    # Simple heuristic analysis (replace with LLM call)
    analysis = f"Build failed with {len(errors)} errors.\n"
    analysis += "\n".join(errors[:5])
    
    recommendations = []
    if "import" in log.lower() and "error" in log.lower():
        recommendations.append("Check for missing dependencies or import errors")
    if "test" in log.lower() and "failed" in log.lower():
        recommendations.append("Review failing tests and fix assertion logic")
    if "timeout" in log.lower():
        recommendations.append("Increase timeout or optimize slow operations")
    
    result = client.submit_report(
        build_id=build_id,
        report_type="failure_analysis",
        analysis=analysis,
        recommendations=recommendations,
        confidence=0.7
    )
    
    return result


if __name__ == "__main__":
    # Example usage
    client = LLMClient()
    
    print("Fetching recent builds...")
    builds = client.get_builds(limit=5)
    print(f"Found {builds.total} builds, showing {len(builds.builds)}:")
    for build in builds.builds:
        print(f"  {build.id}: {build.status}")
    
    if builds.builds:
        print(f"\nGetting details for {builds.builds[0].id}...")
        build_data = client.get_build(builds.builds[0].id)
        print(f"Status: {build_data.get('status')}")
        print(f"Errors: {build_data.get('log_summary', {}).get('error_count', 0)}")
    
    print("\nFetching codebase structure...")
    codebase = client.get_codebase()
    print(f"Workspace: {codebase.get('workspace_root')}")
    print(f"Has backend: {codebase.get('structure_summary', {}).get('has_backend', False)}")
    print(f"Has frontend: {codebase.get('structure_summary', {}).get('has_frontend', False)}")
