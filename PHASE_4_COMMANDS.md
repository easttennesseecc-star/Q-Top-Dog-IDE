# 🚀 Phase 4 - Quick Command Reference

**Status**: READY TO EXECUTE  
**Time Remaining**: 1 hour  
**Commands Below**: Copy/paste ready

---

## ⚡ Ultra-Quick Start (2 minutes)

```bash
# Open 2 terminals

# Terminal 1: Start backend (if not running)
cd backend
python main.py

# Wait for output: "✅ Workflow orchestration database initialized and ready"

# Terminal 2: Run all tests
pytest tests/test_workflow_orchestration.py -v

# Expected: 27 passed ✅
```

---

## 🧪 Part 1: Unit Tests (20 minutes)

### Command 1: Run All Tests
```bash
cd backend
pytest tests/test_workflow_orchestration.py -v
```

**Expected Output**:
```
test_workflow_orchestration.py::TestWorkflowStateMachine::test_valid_transition_discovery_to_planning PASSED
test_workflow_orchestration.py::TestWorkflowStateMachine::test_valid_transition_planning_to_handoff PASSED
[... 25 more tests ...]
27 passed in 0.45s ✅
```

### Command 2: Run with Coverage
```bash
pytest tests/test_workflow_orchestration.py -v --cov=backend.orchestration --cov=backend.services
```

**Expected**: Coverage 95%+ on critical paths

### Command 3: Run Specific Test Class
```bash
pytest tests/test_workflow_orchestration.py::TestWorkflowStateMachine -v
```

### Command 4: Run Specific Test
```bash
pytest tests/test_workflow_orchestration.py::TestWorkflowStateMachine::test_valid_transition_discovery_to_planning -v
```

---

## 🌐 Part 2: Manual Workflow Test (20 minutes)

### Setup: Start Backend (Terminal 1)
```bash
cd backend
python main.py

# Wait for:
# 🚀 Running startup tasks...
# 📦 Initializing workflow database...
# ✅ Workflow orchestration database initialized and ready
# ✓ All 3 workflow tables verified
```

### Test Sequence (Terminal 2)

#### Test 2.1: Start Workflow
```bash
# Save this response for next steps
curl -X POST http://localhost:8000/api/workflows/test-project/start \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "build-phase4-test",
    "user_id": "test-user",
    "requirements": {
      "feature": "Test feature for Phase 4",
      "priority": "high"
    }
  }' | jq .

# Copy workflow_id from response
# Example: "workflow_id": "550e8400-e29b-41d4-a716-446655440000"
```

#### Test 2.2: Save Workflow ID
```bash
export WORKFLOW_ID="550e8400-e29b-41d4-a716-446655440000"
echo "Workflow ID: $WORKFLOW_ID"
```

#### Test 2.3: Check Workflow Status
```bash
curl http://localhost:8000/api/workflows/$WORKFLOW_ID/status | jq .

# Expected:
# - current_state: "discovery"
# - progress: 16.7
# - status: "in_progress"
```

#### Test 2.4: Advance to Planning
```bash
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/advance \
  -H "Content-Type: application/json" \
  -d '{
    "role": "Q_ASSISTANT",
    "completed_state": "DISCOVERY",
    "phase_result": {
      "requirements_analyzed": true,
      "features": ["Feature 1", "Feature 2"],
      "tech_stack": ["Python", "PostgreSQL"]
    }
  }' | jq .

# Expected:
# - new_state: "handoff_to_coder"
# - next_role: "code_writer"
```

#### Test 2.5: Check Status After Advance
```bash
curl http://localhost:8000/api/workflows/$WORKFLOW_ID/status | jq .

# Expected:
# - current_state: "handoff_to_coder"
# - progress: 33.3 (2 of 6 phases)
# - completed_phases: ["discovery", "planning"]
# - handoff_history: [1 entry showing role handoff]
```

#### Test 2.6: Continue to Implementation
```bash
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/advance \
  -H "Content-Type: application/json" \
  -d '{
    "role": "CODE_WRITER",
    "completed_state": "IMPLEMENTATION",
    "phase_result": {
      "files_created": 20,
      "lines_of_code": 3000,
      "test_stubs": 50
    }
  }' | jq .

# Expected: new_state: "handoff_to_tester"
```

---

## 🔄 Part 3: Retry Scenario Test (15 minutes)

### Command 1: Continue to Testing Phase
```bash
curl -X POST http://localhost:8000/api/workflows/$WORKFLOW_ID/advance \
  -H "Content-Type: application/json" \
  -d '{
    "role": "TEST_AUDITOR",
    "completed_state": "TESTING",
    "phase_result": {
      "tests_run": 50,
      "tests_passed": 40,
      "tests_failed": 10,
      "coverage": 0.70
    }
  }' | jq .
```

### Command 2: Check Final Status
```bash
curl http://localhost:8000/api/workflows/$WORKFLOW_ID/status | jq .

# Verify:
# - Complete handoff history shows all transitions
# - Progress shows all completed phases
# - Audit trail in database is comprehensive
```

---

## 🗄️ Part 4: Database Verification (5 minutes)

### Command 1: Check Database File Exists
```bash
# Linux/Mac
ls -lah topdog_ide.db

# Windows PowerShell
Get-Item topdog_ide.db | Select-Object FullName, Length
```

### Command 2: Check Workflow Record
```bash
# Using sqlite3
sqlite3 topdog_ide.db "SELECT id, build_id, current_state FROM build_workflows LIMIT 5;"

# Expected output:
# 550e8400-e29b-41d4-a716-446655440000|build-phase4-test|handoff_to_tester
```

### Command 3: Check Handoff Records
```bash
sqlite3 topdog_ide.db "SELECT workflow_id, from_role, to_role, from_state, to_state FROM workflow_handoffs;"

# Expected: Multiple rows showing role transitions
# q_assistant → code_writer: discovery → handoff_to_coder
# code_writer → test_auditor: implementation → handoff_to_tester
```

### Command 4: Check Event Audit Trail
```bash
sqlite3 topdog_ide.db "SELECT event_type, COUNT(*) FROM workflow_events GROUP BY event_type;"

# Expected:
# workflow_started|1
# state_advanced|3 (or more)
```

### Command 5: Verify Data Integrity
```bash
# Check all handoffs point to valid workflows
sqlite3 topdog_ide.db "
SELECT h.workflow_id, w.id as workflow_exists
FROM workflow_handoffs h
LEFT JOIN build_workflows w ON h.workflow_id = w.id
WHERE w.id IS NULL;
"

# Expected: No results (all foreign keys valid)
```

---

## ✅ Validation Checklist

As you run commands, check off items:

### Unit Tests
- [ ] Command ran without errors
- [ ] 27 tests all passed
- [ ] No failures or skipped tests
- [ ] Execution time < 1 second

### Start Workflow
- [ ] HTTP 200 status
- [ ] workflow_id returned (UUID format)
- [ ] initial_state is "discovery"
- [ ] status is "started"

### Get Status
- [ ] HTTP 200 status
- [ ] Current state matches expected
- [ ] Progress percentage calculated
- [ ] Completed phases list populated

### Advance Workflow
- [ ] HTTP 200 status
- [ ] new_state matches expectation
- [ ] next_role identified correctly
- [ ] handoff_data contains context

### Database Records
- [ ] build_workflows record created
- [ ] workflow_handoffs record created for each advance
- [ ] workflow_events record created for each state change
- [ ] Foreign keys all valid (referential integrity)

### Final Status
- [ ] All completed phases listed
- [ ] Full handoff_history visible
- [ ] Elapsed time calculated
- [ ] Progress updated correctly

---

## 🎯 Success Criteria - All Must Pass

```
✅ Unit Tests:           27/27 PASSED
✅ Workflow Creation:     Returns valid workflow_id
✅ State Progression:     discovery → planning → implementation → ...
✅ Database Persistence: Records created for each operation
✅ Status Queries:       Returns real data from database
✅ Handoff Tracking:     All role handoffs recorded
✅ Audit Trail:          All events logged
✅ Error Handling:       Errors return proper HTTP status
✅ Data Integrity:       All foreign keys valid
✅ Performance:          API responses < 100ms
```

---

## 🚨 If Tests Fail

### Failure: Unit Tests Don't Run
```bash
# Check pytest installed
pip install pytest pytest-asyncio pytest-cov

# Check imports work
python -c "from backend.services.orchestration_service import OrchestrationService; print('✅ OK')"

# Run with verbose error
pytest tests/test_workflow_orchestration.py -vv --tb=long
```

### Failure: Workflow Not Found Error
```bash
# Check database initialized
python -c "from backend.services.workflow_db_manager import WorkflowDatabaseManager; m = WorkflowDatabaseManager('sqlite:///./topdog_ide.db'); print('✅ OK' if m.verify_schema() else '❌ ERROR')"

# Check backend is running with DB initialized
# Look for: "✅ Workflow orchestration database initialized and ready"
```

### Failure: API Returns 500 Error
```bash
# Check backend logs
tail -f backend/logs/q-ide-topdog.log

# Restart backend with verbose logging
cd backend
python -c "import logging; logging.basicConfig(level=logging.DEBUG); from main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8000)"
```

### Failure: Database Lock Error
```bash
# Database file locked - another process using it
# Kill existing Python processes
pkill -f "python main.py"

# Or Windows
taskkill /F /IM python.exe

# Wait 2 seconds, then restart backend
```

---

## 📊 Expected Output Examples

### Test Run Success
```
pytest tests/test_workflow_orchestration.py -v

collected 27 items

test_workflow_orchestration.py::TestWorkflowStateMachine::test_valid_transition_discovery_to_planning PASSED [ 3%]
test_workflow_orchestration.py::TestWorkflowStateMachine::test_valid_transition_planning_to_handoff PASSED [ 7%]
test_workflow_orchestration.py::TestWorkflowStateMachine::test_valid_transition_implementation_to_handoff_tester PASSED [ 11%]
test_workflow_orchestration.py::TestWorkflowStateMachine::test_valid_transition_testing_to_verification PASSED [ 15%]
test_workflow_orchestration.py::TestWorkflowStateMachine::test_invalid_transition_discovery_to_deployment PASSED [ 19%]
test_workflow_orchestration.py::TestWorkflowStateMachine::test_invalid_transition_same_state PASSED [ 22%]
test_workflow_orchestration.py::TestWorkflowStateMachine::test_retry_testing_to_implementation PASSED [ 26%]
test_workflow_orchestration.py::TestWorkflowStateMachine::test_retry_verification_to_implementation PASSED [ 30%]
test_workflow_orchestration.py::TestWorkflowStateMachine::test_get_next_role_from_planning PASSED [ 33%]
test_workflow_orchestration.py::TestWorkflowStateMachine::test_get_next_role_from_implementation PASSED [ 37%]
test_workflow_orchestration.py::TestWorkflowStateMachine::test_get_next_role_from_testing PASSED [ 40%]
test_workflow_orchestration.py::TestWorkflowStateMachine::test_get_next_role_from_deployment PASSED [ 44%]
test_workflow_orchestration.py::TestWorkflowStateMachine::test_state_to_role_mapping PASSED [ 48%]
test_workflow_orchestration.py::TestWorkflowPhaseData::test_set_and_get_discovery_data PASSED [ 51%]
test_workflow_orchestration.py::TestWorkflowPhaseData::test_set_and_get_implementation_data PASSED [ 55%]
test_workflow_orchestration.py::TestWorkflowPhaseData::test_to_dict_converts_all_phases PASSED [ 59%]
test_workflow_orchestration.py::TestOrchestrationService::test_start_workflow_returns_workflow_id PASSED [ 63%]
test_workflow_orchestration.py::TestOrchestrationService::test_start_workflow_initial_state_discovery PASSED [ 66%]
test_workflow_orchestration.py::TestOrchestrationService::test_advance_workflow_planning_to_handoff PASSED [ 70%]
test_workflow_orchestration.py::TestOrchestrationService::test_advance_workflow_deployment_to_complete PASSED [ 74%]
test_workflow_orchestration.py::TestOrchestrationService::test_advance_workflow_invalid_transition_raises_error PASSED [ 77%]
test_workflow_orchestration.py::TestOrchestrationService::test_get_workflow_status_returns_status PASSED [ 81%]
test_workflow_orchestration.py::TestOrchestrationService::test_request_retry_from_testing PASSED [ 85%]
test_workflow_orchestration.py::TestOrchestrationService::test_rollback_workflow PASSED [ 88%]
test_workflow_orchestration.py::TestOrchestrationService::test_get_workflow_stats PASSED [ 92%]
test_workflow_orchestration.py::TestWorkflowIntegration::test_complete_workflow_discovery_to_implementation PASSED [ 96%]
test_workflow_orchestration.py::TestWorkflowIntegration::test_workflow_with_retry_loop PASSED [100%]

==================== 27 passed in 0.45s ✅ ====================
```

### API Response Example
```json
{
  "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
  "build_id": "build-phase4-test",
  "project_id": "test-project",
  "current_state": "handoff_to_tester",
  "current_role": "test_auditor",
  "progress": 50.0,
  "completed_phases": ["discovery", "planning", "implementation"],
  "handoff_history": [
    {
      "from_role": "q_assistant",
      "to_role": "code_writer",
      "from_state": "discovery",
      "to_state": "handoff_to_coder",
      "timestamp": "2025-10-29T10:35:00.000000",
      "notes": "q_assistant completed discovery"
    },
    {
      "from_role": "code_writer",
      "to_role": "test_auditor",
      "from_state": "implementation",
      "to_state": "handoff_to_tester",
      "timestamp": "2025-10-29T10:37:00.000000",
      "notes": "code_writer completed implementation"
    }
  ],
  "elapsed_time": "0h 7m",
  "created_at": "2025-10-29T10:30:00.000000",
  "updated_at": "2025-10-29T10:37:00.000000",
  "status": "in_progress"
}
```

---

## 🎉 Final Checkpoint

**Before starting Phase 4**:
- [ ] Backend running (listen for startup messages)
- [ ] Database file exists (topdog_ide.db or your DATABASE_URL)
- [ ] Pytest installed and working
- [ ] curl or Postman ready for API testing

**After completing Phase 4**:
- [ ] All 27 tests passing
- [ ] Manual workflow test successful
- [ ] Database records verified
- [ ] Documentation updated
- [ ] Ready for Phase 5 ✅

---

**🚀 START PHASE 4:** `pytest backend/tests/test_workflow_orchestration.py -v`

**Expected Result**: ✅ 27 passed in ~0.5s
