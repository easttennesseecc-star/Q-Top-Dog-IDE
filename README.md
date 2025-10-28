# Q-IDE (Quellum TopDog IDE)

**Vision:**
Q-IDE is designed to surpass every existing IDE—including VS Code—by combining all essential features with next-level innovations:

- Multi-agent AI orchestration: Interactive assistant coordinates specialized LLM agents for code generation, review, build health, and hallucination prevention. Each LLM or AI assistant must be aware of its specific role and responsibilities within the multi-agent system.
- Real-time build health dashboard: Always-visible, actionable status of build, tests, dependencies, and code quality.

- AI Assistant (LLM-1) orchestrates all tasks and must specify the exact size and format required for each piece of content requested from Runway (Media Synthesis Module), according to the needs of each task. This ensures all generated assets are fit-for-purpose and seamlessly integrated into the workflow.
- Hallucination and error prevention: AI actively blocks unreliable code and endless fix loops before they enter your build.
- Seamless, visual workflow builder: Drag-and-drop UI for project setup, live previews, and guided onboarding.
- Extensible extension and plugin system: Add, remove, and manage a multitude of extensions and plugins—supporting new languages, tools, and workflows with ease. Q-IDE will match and surpass VS Code in extension support and ecosystem.

- Secure API key management: Easily add, remove, and manage API keys and secrets with robust encryption and access controls, ensuring sensitive credentials are always protected.
- Cross-platform build and deploy: Package for Windows, macOS, Linux, mobile, and web from a single project.

- Integrated AI Code Review & Suggestions: Real-time, context-aware code review and refactoring suggestions from AI agents.
- Live Collaboration & Pair Programming: Multi-user editing, chat, and voice/video integration for remote teamwork.
- Advanced Debugging Tools: Visual step-through debugger, variable inspector, and AI-powered bug explanations.
- Automated Dependency Management: Auto-update, vulnerability scanning, and license compliance checks for all dependencies.
- Project Templates & Guided Onboarding: One-click project scaffolding, onboarding tours, and workflow wizards.
- Customizable Themes & Layouts: User-uploaded backgrounds, animated themes, and layout presets.
- Integrated Documentation & Knowledge Base: AI-generated docs, code search, and context-aware help.
- Cloud Sync & Remote Workspace: Save projects to the cloud, resume work anywhere, and run builds/tests remotely.
- Plugin Marketplace & Community Hub: Discover, rate, and share plugins/extensions; community Q&A and showcase.
- Security & Compliance Dashboard: Real-time security audit, compliance status, and AI-driven risk analysis.

**Mission:**
Make Q-IDE the top dog of IDE platforms—faster, more robust, and better in every way than anything else. Every developer should feel empowered, safe, and productive from start to finish. The app will open automatically and is ready for use.

## Overview
Q-IDE is a modular, multi-agent development environment with a unified dashboard, advanced UI controls, and seamless backend integration. This desktop app is built with Tauri (Rust + React/TypeScript) and Python backend orchestration.

## System Architecture Outline

### I. User Input & Specification Layer
- **LLM-1 (User Interface & Specification Agent)**
  - Handles all user input.
  - Generates two detailed specifications per request:
    - Code specification for LLM-2.
    - Media specification for MSM.

### II. Execution Layer
- **LLM-2 (Code Generation Engine)**
  - Builds core program logic (HTML, React, Python, etc.) from LLM-1’s code spec.
  - Focuses strictly on code.

- **Media Synthesis Module (MSM)**
  - External service (e.g., Runway) for visuals/audio.
  - Generates assets from LLM-1’s media spec.
  - Provides direct asset links for integration.

### III. Validation & Assembly Pipeline
- **LLM-3 (Integration, Testing & Orchestration Engine)**
  - Combines code (LLM-2) and assets (MSM) into a runnable app.
  - Runs integration/unit tests.
  - Produces an Internal Test Log.

- **LLM-4 (The OverWatch / Quality Agent)**
  - Audits the final product for hallucinations and logical errors.
  - Compares the integrated app and test log against:
    - The original specification (LLM-1).
    - The source code (LLM-2).
  - Ensures 100% test pass rate and build health.
  - Operates objectively, does not generate code or run tests.
  - Issues a binary QA Clearance Flag to LLM-5.

- **LLM-5 (Security & Final Assembly Agent)**
  - Final security audit.
  - Assigns Adaptive Resilience Score (ARS).
  - Formats and delivers the complete, verified application.

---

### LLM-4: The OverWatch Integrity Check

1. **Hallucination Defense**
   - Compares final product and test artifacts to original specs and source code.
   - Prevents logical/functional drift.

2. **Build & Operational Health**
   - Audits test logs for 100% pass rate.
   - Halts pipeline on any failure, sends exception to LLM-1.

## Automation Scripts

Automation scripts are provided in the `build-health/` directory to ensure continuous robustness and stability:

- `check_build_health.py`: Checks backend and frontend build/test status.
- `run_tests.py`: Runs backend and frontend tests for coverage.
- `health_check.sh`: Bash script to run health checks (for Unix environments).

These scripts help maintain build health, automate testing, and support the OverWatch agent's validation pipeline.

---

## LLM Learning & Coding Agent Integration

Q-IDE provides a comprehensive learning system for coding LLMs to:
1. **Observe builds** in real-time and learn from success/failure patterns
2. **Analyze codebase** structure, dependencies, and project layout
3. **Submit reports** with insights, recommendations, and confidence scores
4. **Improve over time** by analyzing build logs, errors, and test coverage

### Architecture

Your coding LLM can use the **LLMClient** to fetch and analyze project data:

```python
from backend.llm_client import LLMClient

# Initialize client
client = LLMClient(backend_url="http://127.0.0.1:8000", session_id=optional_oauth_session_id)

# Get recent builds
builds = client.get_builds(limit=10)

# Analyze a specific build
build_data = client.get_build("build-uuid-123")
errors = build_data["log_summary"]["errors"]
recommendations = build_data["log_summary"]["warnings"]

# Get codebase structure and source files
codebase = client.get_codebase()
backend_files = codebase["backend_files"]
config_files = codebase["key_config_files"]

# Submit analysis report
client.submit_report(
    build_id="build-uuid-123",
    type="failure_analysis",
    analysis="Test failed due to missing dependency 'requests'",
    recommendations=["Install requests: pip install requests", "Re-run tests"],
    confidence=0.95
)
```

### Backend Endpoints

#### 1. Get Recent Builds
**GET** `/llm/learning/builds?limit=20&skip=0`

Returns paginated list of recent builds with metadata and logs.

```json
{
  "status": "ok",
  "builds": [
    {
      "id": "uuid-123",
      "status": "success|failed|running|error",
      "log": "... full build output ...",
      "llm_reports": [...]
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 20
}
```

#### 2. Get Build Details with Analysis
**GET** `/llm/learning/build/{build_id}`

Returns detailed build information including error/warning analysis.

```json
{
  "status": "ok",
  "build": {
    "id": "uuid-123",
    "status": "failed",
    "log": "... full output ...",
    "log_summary": {
      "total_lines": 250,
      "error_count": 3,
      "warning_count": 5,
      "errors": ["Error: ModuleNotFoundError: No module named 'foo'", ...],
      "warnings": ["Warning: unused import", ...]
    }
  }
}
```

#### 3. Get Codebase Structure
**GET** `/llm/learning/codebase`

Returns project structure, source files, and configuration.

```json
{
  "status": "ok",
  "codebase": {
    "workspace_root": "/path/to/project",
    "file_tree": {
      "type": "directory",
      "name": "root",
      "children": [...]
    },
    "key_config_files": {
      "package.json": "{ ... }",
      "tsconfig.json": "{ ... }",
      "pyproject.toml": "[ ... ]"
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

#### 4. Submit LLM Report
**POST** `/llm/learning/report`

Your LLM submits analysis reports about builds or code.

Request body:
```json
{
  "build_id": "uuid-123",
  "type": "failure_analysis|code_improvement|test_coverage",
  "analysis": "Detailed findings and context",
  "recommendations": ["Action 1", "Action 2"],
  "confidence": 0.85
}
```

Response:
```json
{
  "status": "ok",
  "message": "report stored",
  "report_id": 0
}
```

### Usage Example: Automated Failure Analysis

```python
from backend.llm_client import LLMClient, analyze_build_failure

client = LLMClient()

# Get all recent failed builds
builds = client.get_builds(limit=50)
failed_builds = [b for b in builds.builds if b.status == "failed"]

# Analyze each failure and submit report
for build in failed_builds[:5]:
    try:
        result = analyze_build_failure(client, build.id)
        print(f"Submitted analysis for {build.id}: {result}")
    except Exception as e:
        print(f"Error analyzing {build.id}: {e}")
```

### Security & Authentication

- **Public access (dev)**: Endpoints accessible without `session_id` for local development
- **Authenticated access**: Pass `session_id` (from OAuth sign-in) to `?session_id=` parameter for production deployments
- **Data storage**: Build data and reports stored in-memory (BUILD_STORE); persists within session
- **Production**: Replace with database storage and secure token management

### Integration with Your Coding LLM

1. **Call `/llm/learning/builds`** on startup to load build history
2. **Listen to new builds** via polling `/llm/learning/build/{id}` at regular intervals
3. **Analyze logs** using the `log_summary` field for errors and warnings
4. **Cross-reference** against `/llm/learning/codebase` to understand project context
5. **Submit reports** to `/llm/learning/report` with findings and recommendations
6. **Improve model** by learning from patterns across multiple builds

This allows your LLM to become increasingly effective at predicting and preventing failures, suggesting improvements, and optimizing builds.

---

## 🤖 The "Super Coder" Coding LLM

Q-IDE's learning system enables you to build a specialized "Super Coder" LLM that continuously improves by learning from your codebase, builds, and test results.

### Super Coder Capabilities

Your coding LLM can learn to:
- **Predict and prevent build failures** before they happen
- **Suggest optimizations** based on patterns in your codebase
- **Generate better code** by understanding project structure and conventions
- **Improve test coverage** by analyzing gaps and edge cases
- **Optimize build times** by identifying slow operations
- **Enforce best practices** specific to your project

### Requirements to Connect Your Coding LLM

#### 1. Backend Connection

Your LLM must be able to connect to the Q-IDE backend:

```python
# Basic setup
from backend.llm_client import LLMClient

client = LLMClient(
    backend_url="http://127.0.0.1:8000",  # Or your backend URL
    session_id=optional_oauth_session_id    # Optional: OAuth session
)
```

**Network Requirements:**
- Backend running on `http://127.0.0.1:8000` (configurable)
- Or deployed to production endpoint
- HTTP/HTTPS connectivity (firewall rules may apply)
- 10-30 second timeout for API calls recommended

#### 2. LLM Model Requirements

For optimal "Super Coder" performance, you need:

**Minimum Specifications:**
- **Model**: GPT-4, Claude 3 Opus, or equivalent
- **Context Window**: 32K+ tokens (for full codebase context)
- **API Access**: Direct API key or managed service
- **Rate Limiting**: 100+ requests/hour for analysis
- **Response Time**: <30 seconds per analysis request

**Recommended Specifications:**
- **Model**: GPT-4 Turbo or Claude 3.5 Sonnet
- **Context Window**: 100K+ tokens (for deep project analysis)
- **Fine-tuning**: Optional (custom code patterns)
- **Function Calling**: For structured analysis and recommendations
- **Streaming**: For real-time analysis feedback

#### 3. Data Access & Learning

Your LLM needs access to:

**Build Data:**
```python
builds = client.get_builds(limit=100)  # Recent build history
build_data = client.get_build(build_id)  # Detailed build info
```
Returns: Build logs, error messages, warnings, test results, execution times

**Codebase Analysis:**
```python
codebase = client.get_codebase()  # Project structure
```
Returns: File tree, source code previews, configuration files, dependency lists

**Learning Persistence:**
```python
client.submit_report(
    build_id="uuid",
    type="failure_analysis|code_improvement|test_coverage",
    analysis="Your findings",
    recommendations=["Action 1", "Action 2"],
    confidence=0.85
)
```

#### 4. Integration Patterns

**Pattern 1: Continuous Learning Service**
```python
from backend.llm_agent_example import QIDECodingAgent

agent = QIDECodingAgent(
    backend_url="http://127.0.0.1:8000",
    poll_interval=30  # Check for new builds every 30s
)
agent.continuous_learning_loop()  # Runs indefinitely
```

**Pattern 2: On-Demand Analysis**
```python
# Triggered when user requests code generation
builds = client.get_builds(limit=50)
codebase = client.get_codebase()
recent_failures = [b for b in builds.builds if b.status == "failed"]

# Inject into prompt for better code generation
context = {
    "recent_failures": recent_failures,
    "project_structure": codebase["structure_summary"],
    "backend_files": codebase["backend_files"]
}
```

**Pattern 3: Real-Time Build Monitoring**
```python
# As builds happen, analyze and provide recommendations
import asyncio

async def monitor_builds():
    seen = set()
    while True:
        builds = client.get_builds(limit=20)
        new_builds = [b for b in builds.builds if b.id not in seen]
        
        for build in new_builds:
            if build.status == "failed":
                analysis = await analyze_with_llm(client, build.id)
                client.submit_report(
                    build_id=build.id,
                    type="failure_analysis",
                    **analysis
                )
            seen.add(build.id)
        
        await asyncio.sleep(10)
```

#### 5. API Key & Authentication Setup

**For Development (No Auth):**
```python
client = LLMClient()  # Works immediately
```

**For Production (With OAuth):**
```python
# User signs in via frontend
session_id = "oauth-session-from-google-signin"
client = LLMClient(session_id=session_id)
```

**Your LLM Provider Keys** (Keep Secure):
```bash
# Set environment variables (never commit to git)
export OPENAI_API_KEY="sk-..."           # For GPT-4
export ANTHROPIC_API_KEY="sk-ant-..."    # For Claude
```

#### 6. Environment Variables Required

Set these before running your LLM service:

```bash
# Backend Configuration
BACKEND_URL=http://127.0.0.1:8000

# LLM Provider (choose one)
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
OLLAMA_BASE_URL=http://127.0.0.1:11434  # For local Ollama

# LLM Model Selection
LLM_MODEL=gpt-4-turbo  # or claude-3-opus, etc.
LLM_TEMPERATURE=0.7    # 0.0-1.0 (lower = more deterministic)
LLM_MAX_TOKENS=4096

# Optional: OAuth Session
OAUTH_SESSION_ID=optional-session-id

# Optional: Logging & Debug
DEBUG=false
LOG_LEVEL=INFO
```

#### 7. Performance Tuning

**For Fast Analysis (Quick Recommendations):**
```python
# Use faster model, smaller context
client = LLMClient()
builds = client.get_builds(limit=10)  # Less history
codebase = client.get_codebase()      # Cached structure
```

**For Deep Analysis (Thorough Improvements):**
```python
# Use powerful model, large context
builds = client.get_builds(limit=100)  # Full history
build_details = [client.get_build(b.id) for b in builds.builds]  # All logs
```

#### 8. Testing Your LLM Connection

Run the test script to verify everything works:

```bash
cd C:\Quellum-topdog-ide\backend
python test_llm_learning.py
```

Expected output shows:
- ✓ Backend connectivity
- ✓ Build history accessible
- ✓ Codebase analysis working
- ✓ Report submission confirmed

#### 9. Starting Your Super Coder

```bash
# Option 1: Run example agent (minimal setup)
cd C:\Quellum-topdog-ide\backend
python llm_agent_example.py

# Option 2: Deploy your custom LLM
python your_coding_llm_service.py

# Option 3: Integrate into existing service
from backend.llm_client import LLMClient
# Your implementation here
```

#### 10. Monitoring & Validation

Check that your LLM is learning:

```bash
# View saved learnings
cat .llm_learnings.json

# Check build reports
curl http://127.0.0.1:8000/llm/learning/builds

# Verify OAuth is working (if configured)
curl http://127.0.0.1:8000/auth/status?session_id=YOUR_SESSION_ID
```

### Super Coder Best Practices

1. **Start Small**: Begin with 10-20 builds, then scale to 100+
2. **Focus on Patterns**: Identify the top 3-5 failure patterns first
3. **High Confidence Only**: Only submit recommendations with >0.8 confidence
4. **Persist Learning**: Save patterns between sessions
5. **Test Recommendations**: Verify suggested fixes actually work
6. **Feedback Loop**: Use build results to refine analysis
7. **Monitor Performance**: Track accuracy of predictions over time
8. **Rate Limiting**: Respect API limits (don't spam requests)

### Integration with Your LLM Provider

**OpenAI GPT-4:**
```python
import openai
from backend.llm_client import LLMClient

openai.api_key = os.getenv("OPENAI_API_KEY")
client = LLMClient()

def analyze_build(build_id):
    build = client.get_build(build_id)
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a code quality expert."},
            {"role": "user", "content": f"Analyze: {build['log_summary']}"}
        ]
    )
    return response.choices[0].message.content
```

**Anthropic Claude:**
```python
import anthropic
from backend.llm_client import LLMClient

client_llm = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
client = LLMClient()

def analyze_build(build_id):
    build = client.get_build(build_id)
    response = client_llm.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": f"Analyze this build failure: {build['log']}"}
        ]
    )
    return response.content[0].text
```

**Local Ollama:**
```python
import requests
from backend.llm_client import LLMClient

client = LLMClient()
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

def analyze_build(build_id):
    build = client.get_build(build_id)
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": "neural-chat",
            "prompt": f"Analyze: {build['log'][:1000]}",
            "stream": False
        }
    )
    return response.json()["response"]
```

---

## OAuth Callback Flow

Q-IDE supports Google and GitHub OAuth with popup-based authentication. The callback flow works as follows:

### OAuth Callback Redirect URIs

When registering OAuth apps, use these redirect URIs:

**Google OAuth:**
- Development: `http://127.0.0.1:8000/auth/google/callback`
- Production: `https://your-domain.com/auth/google/callback`

**GitHub OAuth:**
- Development: `http://127.0.0.1:8000/auth/github/callback`
- Production: `https://your-domain.com/auth/github/callback`

### Callback Handling Architecture

```
User clicks "Sign in with Google"
    ↓
Frontend opens popup to /auth/google/start
    ↓
Backend redirects to Google consent screen
    ↓
User authorizes
    ↓
Google redirects to /auth/google/callback with code
    ↓
Backend exchanges code for token
    ↓
Backend redirects to oauth-callback.html
    ↓
oauth-callback.html posts result to parent window
    ↓
Parent window receives message, closes popup
    ↓
Frontend updates UI with user session
```

### Frontend OAuth Flow

```typescript
// 1. User clicks "Sign in with Google" button
const handleGoogleSignIn = async () => {
  const startResponse = await fetch('/auth/google/start');
  const { auth_url } = await startResponse.json();
  
  // 2. Open OAuth consent popup
  const popup = window.open(auth_url, 'google-signin', 'width=500,height=600');
  
  // 3. Listen for callback from popup
  window.addEventListener('message', (event) => {
    if (event.data.type === 'google-signin-success') {
      // 4. Update session
      saveSession(event.data.session_id);
      popup.close();
    }
  });
};
```

### Backend OAuth Endpoints

**GET /auth/google/start** - Initiates Google OAuth
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?..."
}
```

**GET /auth/google/callback** - Google redirects here after user authorizes
- Query params: `code`, `state`, `error`
- Exchanges code for token
- Fetches user profile
- Creates/updates user in system
- Creates session
- Redirects to callback HTML page

**GET /auth/github/start** - Initiates GitHub OAuth
```json
{
  "auth_url": "https://github.com/login/oauth/authorize?..."
}
```

**GET /auth/github/callback** - GitHub redirects here after user authorizes
- Query params: `code`, `state`, `error`
- Exchanges code for token
- Fetches user profile
- Links account to existing user (via state/session_id)
- Redirects to callback HTML page

### Callback HTML Page

The `frontend/public/oauth-callback.html` handles:
1. Extracting code from URL parameters
2. Validating origin (security)
3. Posting result to parent window
4. Closing popup after success

```html
<!-- Flow: -->
<!-- 1. Backend redirects to oauth-callback.html with code/state -->
<!-- 2. JavaScript extracts code from URL -->
<!-- 3. Posts message to parent window -->
<!-- 4. Parent receives message and processes -->
<!-- 5. Popup closes automatically -->
```

### Setting Up OAuth Providers

**Google Cloud Console:**
1. Go to https://console.cloud.google.com
2. Create new project
3. Enable Google+ API
4. Create OAuth 2.0 credentials (Web application)
5. Add redirect URIs:
   - `http://127.0.0.1:8000/auth/google/callback` (dev)
   - `https://your-domain/auth/google/callback` (prod)
6. Copy Client ID and Client Secret

**GitHub Settings:**
1. Go to https://github.com/settings/developers
2. New OAuth App
3. Authorization callback URL:
   - `http://127.0.0.1:8000/auth/github/callback` (dev)
   - `https://your-domain/auth/github/callback` (prod)
4. Copy Client ID and Client Secret

### Environment Variables for OAuth

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# GitHub OAuth
GITHUB_CLIENT_ID=your-client-id
GITHUB_CLIENT_SECRET=your-client-secret

# Backend URL (used in redirects)
BACKEND_URL=http://127.0.0.1:8000  # dev
# or
BACKEND_URL=https://your-domain.com  # prod
```

### Testing OAuth Flow Locally

```bash
# 1. Set environment variables
export GOOGLE_CLIENT_ID=...
export GOOGLE_CLIENT_SECRET=...

# 2. Start backend
python -m uvicorn backend.main:app --reload

# 3. Open frontend
# (Usually at http://localhost:1431)

# 4. Click "Sign In" button
# Browser opens popup
# Complete OAuth consent
# Check console for success message
```

### Troubleshooting OAuth

| Issue | Solution |
|-------|----------|
| "CORS error" | Backend CORS is configured for localhost:1431 |
| "Invalid redirect URI" | Check redirect URIs in OAuth app settings match exactly |
| "Code expired" | Code is valid for ~10 minutes; try again |
| "Pop-up blocked" | Browser blocked popup; check security settings |
| "Session not found" | Ensure session_id is valid before linking account |

---
val