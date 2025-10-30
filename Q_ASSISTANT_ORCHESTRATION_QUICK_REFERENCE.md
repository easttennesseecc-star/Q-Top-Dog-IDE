# Q Assistant Orchestration - Quick Reference Guide

**For Immediate Implementation**

---

## 📍 File Locations & What They Do

### State Machine (Validator)
📁 `backend/orchestration/workflow_state_machine.py`
- Defines 11 workflow states
- Validates 28 state transitions
- Maps roles to states
- No database needed - pure logic

### Orchestration Service (Coordinator)
📁 `backend/services/orchestration_service.py`
- `start_workflow()` - Creates new build workflow
- `advance_workflow()` - Moves to next phase
- `get_workflow_status()` - Returns current state
- `request_retry()` - Sends back to previous role
- `rollback_workflow()` - Error recovery

### Database Models
📁 `backend/models/workflow.py`
- `BuildWorkflow` - Main workflow record
- `WorkflowHandoff` - Role-to-role handoff
- `WorkflowEvent` - Audit trail
- Includes SQL migration scripts

### API Endpoints
📁 `backend/routes/orchestration_workflow.py`
- 7 REST endpoints (all documented)
- Full error handling
- JSON request/response

### AI System Prompts
📁 `backend/orchestration/orchestration_prompts.py`
- Q Assistant prompt (discovery + planning)
- Code Writer prompt (implementation)
- Test Auditor prompt (testing)
- Verification Overseer prompt (verification)
- Release Manager prompt (deployment)

### Tests
📁 `backend/tests/test_workflow_orchestration.py`
- 27 unit/integration tests
- All major scenarios covered
- Ready to run

---

## 🔌 Integration Points

### 1. Backend Router Registration ✅ DONE
```python
# backend/main.py (Already added)
from routes.orchestration_workflow import router as orchestration_workflow_router
app.include_router(orchestration_workflow_router)
```

### 2. Database Integration (PHASE 3)
```python
# Need to update OrchestrationService
from sqlalchemy.orm import Session
from models.workflow import BuildWorkflow, WorkflowHandoff

class OrchestrationService:
    def __init__(self, db: Session):
        self.db = db
    
    async def start_workflow(self, ...):
        workflow = BuildWorkflow(...)
        self.db.add(workflow)
        self.db.commit()
        return workflow.id
```

### 3. AI System Prompt Integration (PHASE 3)
```python
# Inject into Q Assistant context
from orchestration_prompts import get_orchestration_prompt

q_assistant_system_prompt = get_orchestration_prompt("q_assistant")
# Pass to LLM when starting workflow
```

### 4. Workflow Initialization (PHASE 3)
```python
# Endpoint to start workflow from chat
@router.post("/chat/start-build-workflow")
async def start_build_from_chat(
    user_id: str,
    project_id: str,
    requirements: Dict,
):
    workflow_id, state = await orchestration.start_workflow(
        project_id=project_id,
        build_id=str(uuid4()),
        user_id=user_id,
        initial_requirements=requirements,
    )
    return {"workflow_id": workflow_id, "state": state.value}
```

---

## 🌊 Workflow State Diagram

```
START
  ↓
DISCOVERY ----→ PLANNING ----→ HANDOFF_TO_CODER ----→ IMPLEMENTATION
  ↑                                                           ↓
  └─────────────────── (if retry) ← ← ← ← ← ← ← ← ← HANDOFF_TO_TESTER
                                                            ↓
                                                       TESTING
                                                      /      \
                                               (pass)        (fail)
                                                /                \
                                               ↓                  ↓
                                   HANDOFF_TO_VERIFIER    (request retry)
                                               ↓                  |
                                           VERIFICATION          |
                                              /       \           |
                                       (approved)  (issues)       |
                                          /            \          |
                                         ↓              └──────────┘
                                HANDOFF_TO_RELEASER
                                         ↓
                                    DEPLOYMENT
                                         ↓
                                    COMPLETE ✅
```

---

## 🎮 API Endpoint Quick Reference

### Start Workflow
```
POST /api/workflows/{project_id}/start

{
  "build_id": "build-123",
  "user_id": "user-456", 
  "requirements": {
    "feature": "Dark mode",
    "priority": "high"
  }
}

Response:
{
  "workflow_id": "...",
  "initial_state": "discovery",
  "next_role": "q_assistant"
}
```

### Advance Workflow
```
POST /api/workflows/{workflow_id}/advance

{
  "role": "q_assistant",
  "completed_state": "planning",
  "phase_result": {
    "plan": "Detailed implementation plan...",
    "requirements": {...}
  }
}

Response:
{
  "new_state": "handoff_to_coder",
  "next_role": "code_writer",
  "handoff_data": {...}
}
```

### Get Status
```
GET /api/workflows/{workflow_id}/status

Response:
{
  "current_state": "implementation",
  "current_role": "code_writer",
  "progress": {"percentage": 50},
  "completed_phases": ["discovery", "planning"]
}
```

### Request Retry
```
POST /api/workflows/{workflow_id}/request-retry

{
  "reason": "Test coverage too low"
}

Response:
{
  "retry_requested": true,
  "previous_state": "implementation"
}
```

---

## 🧪 Running Tests

```bash
# All tests
pytest backend/tests/test_workflow_orchestration.py -v

# Specific test class
pytest backend/tests/test_workflow_orchestration.py::TestWorkflowStateMachine -v

# With coverage
pytest backend/tests/test_workflow_orchestration.py --cov=backend.orchestration

# Specific test
pytest backend/tests/test_workflow_orchestration.py::TestWorkflowStateMachine::test_valid_transition_discovery_to_planning -v
```

---

## 🔑 Key Classes & Methods

### WorkflowState (Enum)
```python
DISCOVERY, PLANNING, HANDOFF_TO_CODER, IMPLEMENTATION,
HANDOFF_TO_TESTER, TESTING, HANDOFF_TO_VERIFIER,
VERIFICATION, HANDOFF_TO_RELEASER, DEPLOYMENT, COMPLETE
```

### LLMRole (Enum)
```python
Q_ASSISTANT, CODE_WRITER, TEST_AUDITOR,
VERIFICATION_OVERSEER, RELEASE_MANAGER
```

### WorkflowStateTransition
```python
.is_valid_transition(from_state, to_state) → bool
.get_next_role(current_state) → LLMRole
.get_description(state) → str
.STATE_TO_ROLE → Dict[WorkflowState, LLMRole]
.VALID_TRANSITIONS → Set[Tuple[WorkflowState, WorkflowState]]
```

### OrchestrationService (Main class)
```python
async start_workflow(project_id, build_id, user_id, requirements) → (workflow_id, state)
async advance_workflow(workflow_id, current_role, completed_state, phase_result, next_state) → result_dict
async get_workflow_status(workflow_id) → status_dict
async request_retry(workflow_id, current_state, reason) → result_dict
async rollback_workflow(workflow_id, target_state, reason) → result_dict
```

---

## 📊 Database Schema

### build_workflows
```
id (UUID) - Primary key
build_id (VARCHAR) - Unique build identifier
project_id (VARCHAR) - Project this build belongs to
user_id (VARCHAR) - User who created the build
current_state (ENUM) - Current workflow state
created_at (DATETIME) - When workflow started
updated_at (DATETIME) - Last update
completed_at (DATETIME) - When workflow completed
discovery_phase (JSON) - Q Assistant requirements
planning_phase (JSON) - Q Assistant plan
implementation_phase (JSON) - Code Writer code
testing_phase (JSON) - Test Auditor results
verification_phase (JSON) - Verification Overseer report
deployment_phase (JSON) - Release Manager deployment
metadata (JSON) - Additional data
```

### workflow_handoffs
```
id (UUID) - Primary key
workflow_id (VARCHAR FK) - Parent workflow
from_role (ENUM) - Role completing work
to_role (ENUM) - Next role
from_state (ENUM) - Previous state
to_state (ENUM) - New state
data_transferred (JSON) - What was passed
notes (VARCHAR) - Human notes
timestamp (DATETIME) - When handoff occurred
```

### workflow_events
```
id (UUID) - Primary key
workflow_id (VARCHAR FK) - Parent workflow
event_type (VARCHAR) - Type of event
triggered_by (ENUM) - Which role triggered
event_data (JSON) - Event details
timestamp (DATETIME) - When event occurred
```

---

## ⚙️ Configuration

### System Prompts Location
```python
from backend.orchestration.orchestration_prompts import (
    get_orchestration_prompt,
    get_workflow_context,
    SYSTEM_PROMPTS,
)

# Get Q Assistant prompt
q_prompt = get_orchestration_prompt("q_assistant")

# Get Code Writer prompt
cw_prompt = get_orchestration_prompt("code_writer")

# Get context for current workflow
context = get_workflow_context(workflow_id="...", current_state="implementation")
```

### Environment Variables (Already in .env.example)
```
DATABASE_URL=postgresql://user:pass@localhost/topdog_orchestration
WORKFLOW_TIMEOUT=3600  # 1 hour
WORKFLOW_MAX_RETRIES=3
LOG_LEVEL=INFO
```

---

## 🔍 Troubleshooting

### Workflow stuck in a state?
```python
# Use rollback endpoint
POST /api/workflows/{workflow_id}/rollback

{
  "target_state": "implementation",
  "reason": "Stuck, rolling back for retry"
}
```

### Can't find workflow?
```python
# Check status endpoint
GET /api/workflows/{workflow_id}/status

# Check history to see what happened
GET /api/workflows/{workflow_id}/history
```

### Tests failing?
```bash
# Run with verbose output
pytest backend/tests/test_workflow_orchestration.py -vv

# Run single test with pdb
pytest backend/tests/test_workflow_orchestration.py::TestClass::test_name -vv -s --pdb
```

---

## 📚 Documentation Files

| Document | Purpose |
|----------|---------|
| `Q_ASSISTANT_ORCHESTRATION_IMPLEMENTATION_COMPLETE.md` | Full technical details |
| `Q_ASSISTANT_ORCHESTRATION_PHASE_1_2_SUMMARY.md` | What was just built |
| `Q_ASSISTANT_ORCHESTRATION_ROADMAP.md` | Original plan (reference) |
| This file | Quick reference |

---

## ✅ Checklist for Phase 3 Integration

- [ ] Run database migrations (create 3 tables)
- [ ] Update OrchestrationService to use real DB session
- [ ] Implement BuildWorkflow save/load in service
- [ ] Implement WorkflowHandoff logging
- [ ] Add query methods for status/history
- [ ] Inject orchestration prompts into Q Assistant
- [ ] Update Code Writer prompt with handoff instructions
- [ ] Update Test Auditor prompt
- [ ] Update Verification Overseer prompt
- [ ] Update Release Manager prompt
- [ ] Create workflow initialization endpoint
- [ ] Test database integration (start → advance → status)
- [ ] Test retry loop (status check during testing)
- [ ] Test rollback scenario
- [ ] Run all 27 unit tests with `pytest`
- [ ] Manual end-to-end workflow test

---

## 🚀 Go-Live Readiness

### Completed ✅
- [x] State machine fully designed
- [x] Service layer fully implemented
- [x] API endpoints fully specified
- [x] Database models created
- [x] System prompts for all roles
- [x] 27 unit/integration tests

### Remaining (Phase 3-4)
- [ ] Database integration
- [ ] AI system prompt injection
- [ ] Test execution
- [ ] End-to-end validation

### Time to Complete
- Phase 3: 2 hours
- Phase 4: 1 hour
- **Total: 3 hours to production ready**

---

**Ready to start Phase 3? Let's integrate with the database and AI systems!** 🎯
