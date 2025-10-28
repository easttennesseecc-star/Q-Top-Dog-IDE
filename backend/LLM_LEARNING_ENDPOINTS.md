# 📚 LLM Learning Endpoint Guide

Your custom Coding LLM can now connect to Q-IDE's learning endpoints to analyze builds, extract patterns, and continuously improve. This enables a continuous feedback loop where every build contributes to smarter LLM performance.

## Overview

The learning endpoints provide your Coding LLM with:
- Recent build data and specifications
- Codebase structure and dependencies
- Historical analysis and recommendations
- Performance metrics and accuracy tracking

## API Endpoints

### 1. Get Recent Builds (Analysis Candidates)

```
GET /api/llm/learning/builds?limit=20&skip=0
```

Fetch recent builds for your LLM to analyze.

**Query Parameters:**
- `limit` (int, default=20): Max builds to return
- `skip` (int, default=0): Pagination offset

**Response:**
```json
{
  "status": "ok",
  "count": 5,
  "builds": [
    {
      "id": "build-1234",
      "timestamp": "2024-01-15T10:30:00",
      "spec": { /* user requirements */ },
      "code": { /* generated code */ },
      "test_results": { /* test output */ },
      "errors": [ /* if any */ ]
    }
  ],
  "metadata": {
    "total_analyzed": 324,
    "learning_reports": 87,
    "model_accuracy": 94.2
  }
}
```

### 2. Get Build Details

```
GET /api/llm/learning/build/{build_id}
```

Get detailed information about a specific build.

**Path Parameters:**
- `build_id` (string): The build ID from `get_recent_builds`

**Response:**
```json
{
  "status": "ok",
  "build": {
    "id": "build-1234",
    "timestamp": "2024-01-15T10:30:00",
    "specification": { /* full requirements */ },
    "generated_code": { /* all code files */ },
    "test_results": { /* test output */ },
    "error_logs": [ /* compilation/runtime errors */ ],
    "llm_reports": [ /* previous analyses */ ]
  },
  "analysis_ready": true
}
```

### 3. Get Codebase Structure

```
GET /api/llm/learning/codebase
```

Get the current codebase structure for architectural context.

**Response:**
```json
{
  "status": "ok",
  "structure": {
    "root": "c:\\Quellum-topdog-ide",
    "main_dirs": {
      "frontend": "React 19 + TypeScript + Vite + Tailwind CSS",
      "backend": "FastAPI (Python 3.11) with OAuth 2.0",
      "plugins": "Extension system for LLM agents"
    }
  },
  "entry_points": {
    "frontend_main": "frontend/src/main.tsx",
    "backend_main": "backend/main.py"
  },
  "key_files": [ /* important files */ ],
  "dependencies": { /* frontend/backend deps */ },
  "models": {
    "available": ["GPT-4 Turbo", "Claude 3 Opus", "Ollama (Local)"],
    "active": "GPT-4 Turbo"
  }
}
```

### 4. Submit Learning Report

```
POST /api/llm/learning/report
```

Submit analysis insights from your Coding LLM. This is how your LLM contributes to continuous improvement.

**Request Body:**
```json
{
  "build_id": "build-1234",
  "analysis_type": "code_quality",
  "findings": {
    "pattern_recognition": "description of pattern found",
    "errors_detected": "potential issues",
    "optimizations": "performance improvements identified"
  },
  "recommendations": [
    "Specific action to improve",
    "Another improvement"
  ],
  "confidence": 0.94,
  "model_version": "gpt-4"
}
```

**Analysis Types:**
- `code_quality` - Code patterns, best practices
- `performance` - Performance optimizations
- `architecture` - Architectural improvements
- `security` - Security issues and fixes
- `testing` - Test coverage and quality

**Response:**
```json
{
  "status": "ok",
  "message": "report received and stored",
  "report_id": 87,
  "insights_updated": true
}
```

### 5. Get Learning Metrics

```
GET /api/llm/learning/metrics
```

Get overall learning system metrics.

**Response:**
```json
{
  "status": "ok",
  "builds_analyzed": 324,
  "learning_reports_submitted": 87,
  "model_accuracy": 94.2,
  "avg_confidence": 0.918,
  "patterns_learned": 156,
  "recommendations_implemented": 43,
  "model_improvements": [
    "React pattern recognition +3.2%",
    "Error handling detection +1.8%",
    "TypeScript type inference +2.1%"
  ]
}
```

## Integration Example

### Python Example

```python
from backend.llm_learning_integration import CodingLLMLearningClient

# Initialize client
client = CodingLLMLearningClient()

# Step 1: Get recent builds
builds = client.get_recent_builds(limit=10)

# Step 2: Analyze a build
for build in builds:
    build_detail = client.get_build_detail(build["id"])
    
    # Step 3: Your LLM analyzes the build
    # ... (your analysis logic) ...
    
    # Step 4: Submit findings
    report = client.submit_learning_report(
        build_id=build["id"],
        analysis_type="code_quality",
        findings={
            "patterns": "found X, Y, Z patterns",
            "issues": "potential improvements"
        },
        recommendations=["fix 1", "fix 2"],
        confidence=0.92
    )

# Step 5: Check metrics
metrics = client.get_metrics()
print(f"Model accuracy: {metrics['model_accuracy']}%")
```

### JavaScript/TypeScript Example

```typescript
class LLMLearningClient {
  private baseUrl = "http://localhost:8000/api/llm/learning";
  
  async getRecentBuilds(limit = 20) {
    const response = await fetch(`${this.baseUrl}/builds?limit=${limit}`);
    return response.json();
  }
  
  async getBuildDetail(buildId: string) {
    const response = await fetch(`${this.baseUrl}/build/${buildId}`);
    return response.json();
  }
  
  async submitReport(report: {
    build_id: string;
    analysis_type: string;
    findings: object;
    recommendations: string[];
    confidence: number;
    model_version: string;
  }) {
    const response = await fetch(`${this.baseUrl}/report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(report)
    });
    return response.json();
  }
  
  async getMetrics() {
    const response = await fetch(`${this.baseUrl}/metrics`);
    return response.json();
  }
}

// Usage
const client = new LLMLearningClient();
const builds = await client.getRecentBuilds();
```

## Continuous Learning Workflow

Here's the recommended workflow for your Coding LLM:

```
1. FETCH Recent Builds
   └─> Gets new builds to analyze
   
2. ANALYZE Each Build
   └─> Your LLM reviews code quality, patterns, errors
   
3. GENERATE Insights
   └─> Identify improvements and patterns
   
4. SUBMIT Report
   └─> POST analysis to /api/llm/learning/report
   
5. TRACK Metrics
   └─> Monitor model_accuracy and patterns_learned
   
6. ITERATE
   └─> Loop back to step 1
```

## Authentication

For production deployments, add bearer token authentication:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     http://localhost:8000/api/llm/learning/builds
```

Configure in your LLM client:

```python
client.session.headers.update({
    "Authorization": f"Bearer {api_key}"
})
```

## Rate Limits

- `GET /api/llm/learning/builds` - 100 req/min
- `POST /api/llm/learning/report` - 50 req/min
- `GET /api/llm/learning/metrics` - 60 req/min

## Best Practices

1. **Batch Processing**: Fetch multiple builds and process them together
2. **Confidence Scoring**: Only submit reports with confidence > 0.7
3. **Diverse Analysis**: Mix different analysis_types for comprehensive learning
4. **Error Handling**: Gracefully handle API failures and retry with exponential backoff
5. **Caching**: Cache codebase structure (doesn't change frequently)

## Running the Example

```bash
cd backend/
python llm_learning_integration.py
```

This will demonstrate the full learning workflow with example reports.

## Troubleshooting

**Connection refused?**
- Ensure backend is running: `python backend/main.py`
- Check port 8000 is accessible

**No builds available?**
- Run builds in Q-IDE first
- Builds are stored in `.build_history.json`

**Reports not being saved?**
- Check `.llm_reports.json` file exists and is writable

## Future Enhancements

Planned improvements to the learning system:
- [ ] Database backing for scalability
- [ ] Distributed learning across multiple LLMs
- [ ] Real-time metrics dashboard
- [ ] Pattern clustering and categorization
- [ ] Automated model retraining pipeline
