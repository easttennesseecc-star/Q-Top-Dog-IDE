# LLM Learning Integration - Quick Start Guide

## What You Get

A complete backend system for your coding LLM to:
- **Learn from builds**: Access build history, logs, errors, and warnings
- **Understand your code**: Inspect project structure, dependencies, and source files  
- **Submit intelligence**: Report analysis findings, recommendations, and confidence scores
- **Improve continuously**: Analyze patterns across builds and optimize over time

## Architecture Overview

```
Your Coding LLM
       ↓
   LLMClient (Python)
       ↓
Backend API Endpoints:
  • /llm/learning/builds         → Recent builds with logs
  • /llm/learning/build/{id}     → Detailed build + error analysis
  • /llm/learning/codebase       → Project structure & source files
  • /llm/learning/report         → Submit analysis reports
       ↓
   FastAPI + BUILD_STORE
```

## Quick Start

### 1. Import and Initialize

```python
from backend.llm_client import LLMClient

# Initialize (uses http://127.0.0.1:8000 by default)
client = LLMClient()

# With custom backend URL and OAuth session
client = LLMClient(
    backend_url="http://your-backend:8000",
    session_id="oauth-session-id-123"
)
```

### 2. Fetch Builds and Analyze Failures

```python
# Get recent builds
builds = client.get_builds(limit=20)
print(f"Total builds: {builds.total}")

# Find failed builds
failed = [b for b in builds.builds if b.status == "failed"]

# Get detailed error info
for build in failed[:5]:
    data = client.get_build(build.id)
    errors = data["log_summary"]["errors"]
    print(f"\nBuild {build.id}: {len(errors)} errors")
    for error in errors[:3]:
        print(f"  - {error}")
```

### 3. Get Project Context

```python
# Understand the codebase
codebase = client.get_codebase()

# Check project structure
structure = codebase["structure_summary"]
print(f"Backend: {structure['has_backend']}")
print(f"Frontend: {structure['has_frontend']}")

# Read configuration files
configs = codebase["key_config_files"]
package_json = configs.get("package.json")
tsconfig = configs.get("tsconfig.json")

# Inspect backend source files
backend_files = codebase["backend_files"]
for f in backend_files:
    print(f"{f['name']}: {f['lines']} lines")
    print(f"  Preview: {f['preview'][:100]}...")
```

### 4. Submit Analysis Reports

```python
# Analyze a specific build
build_data = client.get_build("build-123")
errors = build_data["log_summary"]["errors"]

# LLM performs analysis (this is where your LLM logic goes)
analysis = f"Found {len(errors)} errors in build"
recommendations = ["Fix missing imports", "Update dependencies"]
confidence = 0.85

# Submit your findings
result = client.submit_report(
    build_id="build-123",
    report_type="failure_analysis",
    analysis=analysis,
    recommendations=recommendations,
    confidence=confidence
)

print(f"Report submitted with ID: {result['report_id']}")
```

### 5. Full Learning Loop

```python
from backend.llm_client import LLMClient
import time

client = LLMClient()

# Continuous learning process
while True:
    print("Checking for new builds...")
    
    # Fetch recent builds
    builds = client.get_builds(limit=50)
    
    # Analyze builds not yet reported on
    for build in builds.builds:
        build_data = client.get_build(build.id)
        reports = build_data.get("llm_reports", [])
        
        if not reports and build.status in ["failed", "error"]:
            # This build hasn't been analyzed yet
            print(f"Analyzing {build.id}...")
            
            errors = build_data["log_summary"]["errors"]
            log = build_data["log"]
            
            # Your LLM analysis here
            analysis = perform_llm_analysis(errors, log)
            
            # Submit report
            client.submit_report(
                build_id=build.id,
                type="failure_analysis",
                analysis=analysis["text"],
                recommendations=analysis["recommendations"],
                confidence=analysis["confidence"]
            )
    
    # Check periodically
    print("Waiting 5 minutes before next check...")
    time.sleep(300)
```

## API Reference

### GET /llm/learning/builds
Fetch paginated list of builds.

**Query Parameters:**
- `limit` (int, default=20): Max results per request
- `skip` (int, default=0): Pagination offset
- `session_id` (str, optional): OAuth session for auth

**Response:**
```json
{
  "status": "ok",
  "builds": [
    {
      "id": "uuid-123",
      "status": "success",
      "log": "... full build output ..."
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 20
}
```

### GET /llm/learning/build/{build_id}
Get detailed build data with error analysis.

**Response:**
```json
{
  "status": "ok",
  "build": {
    "id": "uuid-123",
    "status": "failed",
    "log": "... full output ...",
    "log_summary": {
      "total_lines": 245,
      "error_count": 3,
      "warning_count": 7,
      "errors": ["Error: ...", "Error: ..."],
      "warnings": ["Warning: ..."]
    }
  }
}
```

### GET /llm/learning/codebase
Get project structure and source files.

**Response:**
```json
{
  "status": "ok",
  "codebase": {
    "workspace_root": "/path/to/project",
    "file_tree": { ... },
    "key_config_files": {
      "package.json": "{ ... }",
      "pyproject.toml": "..."
    },
    "backend_files": [
      {
        "name": "main.py",
        "path": "backend/main.py",
        "lines": 415,
        "preview": "... first 500 chars ..."
      }
    ],
    "structure_summary": {
      "has_backend": true,
      "has_frontend": true,
      "has_tests": true
    }
  }
}
```

### POST /llm/learning/report
Submit LLM analysis report.

**Request Body:**
```json
{
  "build_id": "uuid-123",
  "type": "failure_analysis",
  "analysis": "Detailed findings",
  "recommendations": ["Fix X", "Update Y"],
  "confidence": 0.85
}
```

**Response:**
```json
{
  "status": "ok",
  "message": "report stored",
  "report_id": 0
}
```

## Report Types

- `failure_analysis`: Deep-dive into what caused a build failure
- `code_improvement`: Suggestions for code optimizations or refactoring
- `test_coverage`: Analysis of test coverage and missing test scenarios
- `dependency_audit`: Review of dependencies and security vulnerabilities
- `performance_analysis`: Build time, memory usage, and optimization opportunities

## Running the Test Script

```bash
cd backend
python test_llm_learning.py
```

This will:
1. Connect to the backend
2. Fetch recent builds
3. Display build statistics
4. Get project structure
5. Submit a sample report
6. Show usage examples

## Integration Examples

### Example 1: Automatic Failure Classification
```python
def classify_failure(client, build_id):
    build = client.get_build(build_id)
    errors = build["log_summary"]["errors"]
    
    if any("import" in e.lower() for e in errors):
        failure_type = "Missing Dependency"
    elif any("test" in e.lower() for e in errors):
        failure_type = "Test Failure"
    elif any("timeout" in e.lower() for e in errors):
        failure_type = "Timeout"
    else:
        failure_type = "Unknown"
    
    client.submit_report(
        build_id=build_id,
        type="failure_analysis",
        analysis=f"Classified as: {failure_type}",
        recommendations=[f"Research {failure_type} patterns"],
        confidence=0.75
    )
```

### Example 2: Project Health Scorecard
```python
def generate_health_score(client):
    builds = client.get_builds(limit=100)
    
    success_count = len([b for b in builds.builds if b.status == "success"])
    total_count = len(builds.builds)
    success_rate = success_count / total_count if total_count > 0 else 0
    
    codebase = client.get_codebase()
    has_tests = codebase["structure_summary"]["has_tests"]
    
    score = success_rate * 0.8
    score += 0.2 if has_tests else 0
    
    return {
        "health_score": score * 100,
        "success_rate": success_rate * 100,
        "total_builds": total_count,
        "has_tests": has_tests
    }
```

### Example 3: Continuous Learning
```python
class CodingLLMAgent:
    def __init__(self, model_name="gpt-4"):
        self.client = LLMClient()
        self.model = model_name
        self.learned_patterns = {}
    
    def learn_from_recent_builds(self, limit=20):
        builds = self.client.get_builds(limit=limit)
        
        for build in builds.builds:
            if build.status == "failed":
                data = self.client.get_build(build.id)
                pattern = self._extract_pattern(data)
                
                if pattern:
                    self.learned_patterns[pattern["type"]] = pattern
                    
                    # Report findings
                    self.client.submit_report(
                        build_id=build.id,
                        type="failure_analysis",
                        analysis=pattern["description"],
                        recommendations=pattern["fixes"],
                        confidence=pattern["confidence"]
                    )
    
    def _extract_pattern(self, build_data):
        errors = build_data["log_summary"]["errors"]
        # Your LLM analysis to extract patterns
        return {
            "type": "import_error",
            "description": "Missing module dependencies",
            "fixes": ["pip install -r requirements.txt"],
            "confidence": 0.9
        }
```

## Best Practices

1. **Batch Requests**: Fetch multiple builds at once rather than one-by-one
2. **Cache Results**: Store codebase structure info locally; it changes infrequently
3. **Gradual Analysis**: Process builds incrementally rather than all at once
4. **Confidence Scores**: Only report high-confidence findings (>0.7) as recommendations
5. **Error Aggregation**: Group similar errors across builds to identify patterns
6. **Timeout Handling**: Set reasonable timeouts for API calls (10-30 seconds)

## Advanced: Custom LLM Integration

To integrate with your own LLM (OpenAI, Anthropic, etc.):

```python
import anthropic

def analyze_with_llm(client: LLMClient, build_id: str):
    # Get build data
    build = client.get_build(build_id)
    errors = build["log_summary"]["errors"]
    log = build["log"]
    
    # Get context
    codebase = client.get_codebase()
    
    # Prepare prompt
    prompt = f"""
    Analyze this build failure:
    
    Errors: {errors}
    Log: {log[:1000]}
    
    Project: {codebase['structure_summary']}
    
    Provide:
    1. Root cause analysis
    2. Recommended fixes
    3. Confidence (0-1)
    """
    
    # Call your LLM
    client_llm = anthropic.Anthropic()
    response = client_llm.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    
    analysis_text = response.content[0].text
    
    # Submit report
    client.submit_report(
        build_id=build_id,
        type="failure_analysis",
        analysis=analysis_text,
        recommendations=["See analysis above"],
        confidence=0.85
    )
```

## Troubleshooting

**"Connection refused" error**
- Ensure backend is running: `python -m uvicorn backend.main:app`
- Check backend URL: default is `http://127.0.0.1:8000`

**"Session not found" error**
- Backend is checking `session_id` validity
- For local dev, pass no `session_id` or use a valid OAuth session ID

**Empty builds list**
- Start a build first via `/build/run` endpoint
- Or trigger build via frontend UI

**Timeout errors**
- Backend may be processing large logs
- Increase timeout in LLMClient or use pagination with smaller limits

## Next Steps

1. ✅ Set up LLMClient and test basic connectivity
2. ✅ Analyze recent builds and extract patterns
3. ✅ Integrate with your preferred LLM (GPT-4, Claude, etc.)
4. ✅ Build specialized analysis agents (security, performance, etc.)
5. ✅ Deploy LLM agent as background service for continuous learning
