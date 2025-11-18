"""
Example LLM Agent Integration - Demonstrates how to wire your coding LLM with Q-IDE.

This example shows:
1. Continuous build monitoring
2. Error pattern analysis
3. Automated recommendation generation
4. Report submission back to Q-IDE

You can replace the simple heuristics here with actual LLM calls to:
- OpenAI GPT-4
- Anthropic Claude
- Local Ollama instances
- Any other LLM API
"""

import time
import json
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

# Import the LLM client
from llm_client import LLMClient


class QIDECodingAgent:
    """Example coding LLM agent that learns from Q-IDE builds."""
    
    def __init__(
        self,
        backend_url: str = "http://127.0.0.1:8000",
        session_id: Optional[str] = None,
        poll_interval: int = 30,
        learning_file: str = ".llm_learnings.json"
    ):
        """Initialize the coding agent.
        
        Args:
            backend_url: Q-IDE backend URL
            session_id: OAuth session ID (optional)
            poll_interval: Seconds between build checks
            learning_file: File to persist learned patterns
        """
        self.client = LLMClient(backend_url, session_id)
        self.poll_interval = poll_interval
        self.learning_file = Path(learning_file)
        self.learned_patterns: Dict[str, Dict] = {}
        self.analyzed_builds: set = set()
        
        # Load previously learned patterns
        self._load_learnings()
    
    def _load_learnings(self):
        """Load persisted learnings from file."""
        if self.learning_file.exists():
            try:
                with open(self.learning_file, 'r') as f:
                    data = json.load(f)
                    self.learned_patterns = data.get("patterns", {})
                    self.analyzed_builds = set(data.get("analyzed", []))
                    print(f"✓ Loaded {len(self.learned_patterns)} learned patterns")
            except Exception as e:
                print(f"⚠ Could not load learnings: {e}")
    
    def _save_learnings(self):
        """Persist learnings to file."""
        try:
            with open(self.learning_file, 'w') as f:
                json.dump({
                    "patterns": self.learned_patterns,
                    "analyzed": list(self.analyzed_builds),
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"⚠ Could not save learnings: {e}")
    
    def analyze_build_failure(self, build_id: str, build_data: Dict) -> Dict:
        """Analyze a failed build and generate recommendations.
        
        This is where you'd call your actual LLM. Here we use heuristics.
        
        Args:
            build_id: ID of the build
            build_data: Build data from /llm/learning/build endpoint
        
        Returns:
            Analysis result with recommendations
        """
        errors = build_data.get("log_summary", {}).get("errors", [])
        log = build_data.get("log", "")
        
        # Heuristic pattern detection (replace with LLM calls)
        analysis_result = {
            "type": "unknown",
            "description": "Build failure detected",
            "recommendations": [],
            "confidence": 0.5
        }
        
        # Pattern: Missing dependencies
        if any(keyword in " ".join(errors).lower() for keyword in ["modulenotfound", "import", "no module", "cannot find"]):
            analysis_result["type"] = "missing_dependency"
            analysis_result["description"] = "Build failed due to missing module or import error"
            analysis_result["recommendations"] = [
                "Check requirements.txt and ensure all dependencies are listed",
                "Run 'pip install -r requirements.txt' (Python) or 'npm install' (Node)",
                "Verify module names in import statements are correct"
            ]
            analysis_result["confidence"] = 0.9
        
        # Pattern: Test failures
        elif "test" in log.lower() and any("failed" in e.lower() for e in errors):
            analysis_result["type"] = "test_failure"
            analysis_result["description"] = "One or more tests failed during build"
            analysis_result["recommendations"] = [
                "Review failing test output above",
                "Verify test fixtures and mocks are properly configured",
                "Check if code changes broke existing test assumptions"
            ]
            analysis_result["confidence"] = 0.85
        
        # Pattern: Timeout
        elif "timeout" in log.lower():
            analysis_result["type"] = "timeout"
            analysis_result["description"] = "Build timed out, likely due to slow operations or hanging processes"
            analysis_result["recommendations"] = [
                "Profile build steps to identify slow operations",
                "Increase timeout limits if appropriate",
                "Consider parallelizing independent build tasks",
                "Check for network calls or external service dependencies"
            ]
            analysis_result["confidence"] = 0.8
        
        # Pattern: Syntax/lint errors
        elif any(keyword in " ".join(errors).lower() for keyword in ["syntax", "indent", "unexpected"]):
            analysis_result["type"] = "syntax_error"
            analysis_result["description"] = "Build failed due to syntax or formatting errors"
            analysis_result["recommendations"] = [
                "Fix syntax errors shown in output",
                "Run linter/formatter: 'black .' (Python) or 'eslint --fix' (JS)",
                "Review recent code changes for typos"
            ]
            analysis_result["confidence"] = 0.95
        
        # Pattern: Permission/access issues
        elif any(keyword in " ".join(errors).lower() for keyword in ["permission", "access denied", "unauthorized", "not found"]):
            analysis_result["type"] = "access_error"
            analysis_result["description"] = "Build failed due to permission or file access issues"
            analysis_result["recommendations"] = [
                "Check file permissions: 'ls -la' or 'icacls' on Windows",
                "Verify all required files are present in repository",
                "Ensure environment variables are properly configured"
            ]
            analysis_result["confidence"] = 0.75
        
        # Store learned pattern
        if analysis_result["confidence"] > 0.7:
            pattern_key = analysis_result["type"]
            if pattern_key not in self.learned_patterns:
                self.learned_patterns[pattern_key] = {
                    "count": 0,
                    "first_seen": datetime.now().isoformat(),
                    "last_seen": datetime.now().isoformat(),
                    "recommendations": analysis_result["recommendations"]
                }
            self.learned_patterns[pattern_key]["count"] += 1
            self.learned_patterns[pattern_key]["last_seen"] = datetime.now().isoformat()
        
        return analysis_result
    
    def process_single_build(self, build_id: str) -> Optional[Dict]:
        """Analyze a single build and submit report.
        
        Args:
            build_id: Build to analyze
        
        Returns:
            Report submission result or None if error
        """
        if build_id in self.analyzed_builds:
            return None  # Already analyzed
        
        try:
            # Get build data
            build_data = self.client.get_build(build_id)
            status = build_data.get("status", "unknown")
            
            # Only analyze failed builds (modify as needed)
            if status != "failed":
                self.analyzed_builds.add(build_id)
                return None
            
            print(f"\n📊 Analyzing build {build_id[:8]}...")
            
            # Analyze failure
            analysis = self.analyze_build_failure(build_id, build_data)
            
            print(f"  Type: {analysis['type']}")
            print(f"  Confidence: {analysis['confidence']}")
            print("  Recommendations:")
            for rec in analysis["recommendations"]:
                print(f"    • {rec}")
            
            # Submit report to Q-IDE
            result = self.client.submit_report(
                build_id=build_id,
                report_type="failure_analysis",
                analysis=analysis["description"],
                recommendations=analysis["recommendations"],
                confidence=analysis["confidence"]
            )
            
            self.analyzed_builds.add(build_id)
            self._save_learnings()
            
            print(f"  ✓ Report submitted (ID: {result.get('report_id', 'N/A')})")
            
            return result
        
        except Exception as e:
            print(f"  ✗ Error analyzing build: {e}")
            return None
    
    def continuous_learning_loop(self, max_iterations: Optional[int] = None):
        """Run continuous learning loop.
        
        Args:
            max_iterations: Max iterations to run (None = infinite)
        """
        iteration = 0
        
        print("\n" + "=" * 60)
        print("Q-IDE Coding Agent - Continuous Learning Mode")
        print("=" * 60)
        print(f"Backend: {self.client.backend_url}")
        print(f"Poll interval: {self.poll_interval}s")
        print(f"Already analyzed: {len(self.analyzed_builds)} builds")
        print("=" * 60)
        
        try:
            while max_iterations is None or iteration < max_iterations:
                iteration += 1
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Polling for new builds... (iteration {iteration})")
                
                try:
                    # Get recent builds
                    builds = self.client.get_builds(limit=50)
                    print(f"Found {builds.total} total builds")
                    
                    # Analyze unanalyzed failed builds
                    new_analyses = 0
                    for build in builds.builds:
                        if build.id not in self.analyzed_builds and build.status == "failed":
                            result = self.process_single_build(build.id)
                            if result:
                                new_analyses += 1
                    
                    if new_analyses == 0:
                        print("No new builds to analyze")
                    else:
                        print(f"✓ Analyzed {new_analyses} new build(s)")
                    
                    # Show learning summary
                    if self.learned_patterns:
                        print(f"\n📚 Learned patterns ({len(self.learned_patterns)} types):")
                        for ptype, pdata in self.learned_patterns.items():
                            count = pdata.get("count", 0)
                            print(f"  • {ptype}: seen {count} time(s)")
                
                except Exception as e:
                    print(f"⚠ Error in poll cycle: {e}")
                
                # Wait before next poll
                if max_iterations is None or iteration < max_iterations:
                    print(f"Waiting {self.poll_interval}s before next check...")
                    time.sleep(self.poll_interval)
        
        except KeyboardInterrupt:
            print("\n\n⏹ Agent stopped by user")
        
        finally:
            print("\n" + "=" * 60)
            print("Learning Summary:")
            print(f"Total builds analyzed: {len(self.analyzed_builds)}")
            print(f"Total patterns learned: {len(self.learned_patterns)}")
            if self.learned_patterns:
                print("\nPattern distribution:")
                for ptype, pdata in self.learned_patterns.items():
                    print(f"  {ptype}: {pdata.get('count', 0)} occurrences")
            print("=" * 60)
            self._save_learnings()


def main():
    """Example usage of the coding agent."""
    
    # Initialize agent
    agent = QIDECodingAgent(
        backend_url="http://127.0.0.1:8000",
        poll_interval=30
    )
    
    # Run continuous learning (limit to 5 iterations for demo)
    agent.continuous_learning_loop(max_iterations=5)
    
    # Or analyze specific builds:
    # print("\nManual build analysis mode:")
    # builds = agent.client.get_builds(limit=10)
    # for build in builds.builds[:3]:
    #     if build.status == "failed":
    #         agent.process_single_build(build.id)


if __name__ == "__main__":
    main()
