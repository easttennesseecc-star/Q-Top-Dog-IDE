# Q Assistant Orchestration - Complete Implementation Guide

**Status**: Framework Ready for Workflow Automation  
**Current**: 50% Complete (Q Assistant interactive working, full orchestration partial)  
**Missing**: Automated workflow state machine between roles  
**Timeline**: ~6-8 hours to complete  
**Complexity**: Medium-High

---

## ✅ What's Already Working

### Q Assistant Interactive Chat
✅ Voice + text input in frontend  
✅ Real-time streaming responses  
✅ Integrated with 5-role orchestration system  
✅ Scope-enforced (no code generation)  
✅ System prompt prevents role confusion  

### Q Assistant Can Request
✅ Code Writer to implement  
✅ Test Auditor to validate  
✅ Verification Overseer to check  
✅ Release Manager to deploy  

### Q Assistant Status
✅ Can receive requirements from user  
✅ Can extract specifications  
✅ Can coordinate team  
❌ Does NOT automatically orchestrate workflow  
❌ Does NOT track handoff between roles  
❌ Does NOT enforce sequential execution  

---

## 🔧 What Needs to Be Built

### 1. Workflow State Machine
```python
# backend/orchestration/workflow_state_machine.py

States:
├─ DISCOVERY (Q Assistant gathers requirements)
├─ PLANNING (Q Assistant creates implementation plan)
├─ HANDOFF_TO_CODER (Q Assistant hands off to Code Writer)
├─ IMPLEMENTATION (Code Writer writes code)
├─ HANDOFF_TO_TESTER (Code Writer hands off to Test Auditor)
├─ TESTING (Test Auditor validates)
├─ HANDOFF_TO_VERIFIER (Test Auditor hands off to Verification Overseer)
├─ VERIFICATION (Verification Overseer checks for issues)
├─ HANDOFF_TO_RELEASER (Verification Overseer hands off to Release Manager)
├─ DEPLOYMENT (Release Manager deploys to production)
└─ COMPLETE (Build finished)

Transitions:
├─ DISCOVERY → PLANNING (Q Assistant: ready to plan)
├─ PLANNING → HANDOFF_TO_CODER (Q Assistant: plan complete, handing off)
├─ HANDOFF_TO_CODER → IMPLEMENTATION (Code Writer: acknowledged, starting)
├─ IMPLEMENTATION → HANDOFF_TO_TESTER (Code Writer: code written, handing off)
├─ HANDOFF_TO_TESTER → TESTING (Test Auditor: acknowledged, starting)
├─ TESTING → VERIFICATION or IMPLEMENTATION (Test Auditor: pass or fail)
├─ HANDOFF_TO_VERIFIER → VERIFICATION (Verification Overseer: acknowledged)
├─ VERIFICATION → DEPLOYMENT or IMPLEMENTATION (Verification Overseer: pass or fail)
├─ HANDOFF_TO_RELEASER → DEPLOYMENT (Release Manager: acknowledged)
└─ DEPLOYMENT → COMPLETE (Release Manager: deployed)
```

### 2. Workflow Tracker Database
```python
# Add to models/subscription.py

class BuildWorkflow:
    __tablename__ = "build_workflows"
    
    id: UUID
    build_id: UUID
    project_id: UUID
    current_state: WorkflowState
    created_at: DateTime
    updated_at: DateTime
    completed_at: Optional[DateTime]
    
    # Track each phase
    discovery_phase: Optional[Dict]  # Q Assistant requirements
    planning_phase: Optional[Dict]   # Q Assistant plan
    implementation_phase: Optional[Dict]  # Code Writer output
    testing_phase: Optional[Dict]    # Test Auditor results
    verification_phase: Optional[Dict]   # Verification Overseer checks
    deployment_phase: Optional[Dict]    # Release Manager deployment
    
    # Handoff records
    handoffs: List[WorkflowHandoff]
    
class WorkflowHandoff:
    __tablename__ = "workflow_handoffs"
    
    id: UUID
    workflow_id: UUID
    from_role: LLMRole
    to_role: LLMRole
    timestamp: DateTime
    data_passed: Dict  # What was passed between roles
    notes: String
```

### 3. Orchestration Service
```python
# backend/services/orchestration_service.py

class OrchestrationService:
    """Manages workflow automation between roles"""
    
    async def start_workflow(self, build_id: str, requirements: Dict) -> str:
        """Start discovery phase with Q Assistant"""
        # Create workflow
        # Set state to DISCOVERY
        # Return workflow ID
    
    async def advance_workflow(self, workflow_id: str, role: LLMRole, result: Dict) -> str:
        """Advance workflow when role completes work"""
        # Get current state
        # Validate state transition
        # Update phase data
        # Determine next role
        # Create handoff record
        # Return next workflow state
    
    async def get_workflow_status(self, workflow_id: str) -> Dict:
        """Get current workflow status and progress"""
        # Return all phases completed so far
        # Return current state
        # Return next expected role
    
    async def rollback_workflow(self, workflow_id: str, phase: str) -> Dict:
        """Rollback to previous phase if errors detected"""
        # Revert state
        # Update phase data
        # Create audit log
```

### 4. Automated Handoff Endpoints
```python
# backend/routes/orchestration_workflow.py

@router.post("/workflows/{workflow_id}/advance")
async def advance_workflow(
    workflow_id: str,
    role: LLMRole,
    result: Dict = Body(...)
):
    """Q Assistant or any role reports completion and advances workflow"""
    # Validate role matches current state
    # Process result
    # Determine next role
    # Create handoff
    # Return next state and instructions for next role

@router.post("/workflows/{workflow_id}/request-retry")
async def request_workflow_retry(
    workflow_id: str,
    reason: str = Body(...)
):
    """Current role requests previous role to retry"""
    # Move back to previous phase
    # Send context to previous role
    # Log retry reason
    # Return new state

@router.get("/workflows/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """Get full workflow status and history"""
    # Return all completed phases
    # Return current phase
    # Return next phase expectations
    # Return handoff history
```

### 5. Q Assistant Integration
```python
# Modify: backend/q_assistant_scope.py

# Add to Q Assistant system prompt:
"""
When you complete discovery/planning and are ready to handoff:

1. Call: POST /api/builds/{build_id}/workflows/{workflow_id}/advance
   Body: {
     "role": "q_assistant",
     "phase_completed": "planning",
     "implementation_plan": { ...your plan... },
     "requirements": { ...extracted requirements... },
     "next_role_instruction": "Code Writer should now implement according to plan..."
   }

2. System will:
   - Save your output
   - Create handoff record
   - Advance to CODE_WRITER phase
   - Send context to Code Writer

3. You will then:
   - Wait for Code Writer to complete
   - Review their code
   - Provide feedback or approve handoff to Test Auditor
"""
```

---

## 📋 Implementation Roadmap

### Phase 1: State Machine (2 hours)
```
1. Create workflow_state_machine.py
   ├─ Define WorkflowState enum
   ├─ Define valid transitions
   ├─ Create state validation logic
   └─ Add state change logging

2. Update database models
   ├─ Add BuildWorkflow table
   ├─ Add WorkflowHandoff table
   └─ Run migrations
```

### Phase 2: Orchestration Service (3 hours)
```
1. Create orchestration_service.py
   ├─ Implement start_workflow()
   ├─ Implement advance_workflow()
   ├─ Implement get_workflow_status()
   ├─ Implement rollback_workflow()
   └─ Add comprehensive error handling

2. Create workflow routes
   ├─ POST /workflows/{id}/advance
   ├─ GET /workflows/{id}/status
   ├─ POST /workflows/{id}/request-retry
   └─ Register in main.py
```

### Phase 3: Integration (2 hours)
```
1. Update Q Assistant system prompt
   ├─ Add handoff instructions
   ├─ Show workflow endpoint
   └─ Provide examples

2. Update Code Writer system prompt
   ├─ Explain how to receive handoff
   ├─ How to complete and handoff to Test Auditor
   └─ Provide examples

3. Similar updates for Test Auditor, Verification Overseer, Release Manager

4. Create workflow initialization endpoint
   ├─ Start workflow from Q Assistant chat
   ├─ Initialize all required data
   └─ Return workflow ID
```

### Phase 4: Testing (1 hour)
```
1. Unit tests
   ├─ Test state transitions
   ├─ Test handoff creation
   ├─ Test rollback logic

2. Integration tests
   ├─ Test full workflow Discovery → Complete
   ├─ Test error handling
   ├─ Test retry logic

3. Manual testing
   ├─ Start Q Assistant
   ├─ Trigger workflow
   ├─ Watch orchestration happen
```

---

## 🎯 End Result

After implementation:
```
User talks to Q Assistant
     ↓
Q Assistant extracts requirements & creates plan
     ↓
Q Assistant clicks "Ready to Build"
     ↓
POST /api/workflows/{id}/advance (Q Assistant work done)
     ↓
System creates handoff, sets state to CODE_WRITER
     ↓
Code Writer receives plan and requirements
     ↓
Code Writer generates code
     ↓
POST /api/workflows/{id}/advance (Code Writer work done)
     ↓
Test Auditor receives code
     ↓
Test Auditor runs tests
     ↓
If tests pass → Verification Overseer
     ↓
If verification passes → Release Manager
     ↓
Release Manager deploys
     ↓
POST /api/workflows/{id}/advance (Complete!)
     ↓
Workflow marked COMPLETE
     ↓
User gets notification: "Your build is live!"
```

---

## 💡 Quick Implementation (6-8 hours)

**Recommendation**: Implement this AFTER Stripe and Digital Ocean are tested.

**Priority Order**:
1. ✅ Stripe Payments (DONE)
2. ✅ Digital Ocean Deployment (DONE)
3. ⏳ Q Assistant Orchestration (NEXT)
4. Final Integration Testing

---

## 🔗 Files to Create/Modify

**New Files**:
- `backend/orchestration/workflow_state_machine.py`
- `backend/services/orchestration_service.py`
- `backend/routes/orchestration_workflow.py`
- `backend/tests/test_workflow_orchestration.py`

**Modified Files**:
- `backend/models/subscription.py` (add BuildWorkflow, WorkflowHandoff)
- `backend/q_assistant_scope.py` (update system prompt with handoff)
- `backend/main.py` (register new routes)
- Database migrations

---

## ⏭️ Next Steps

1. **Complete Stripe** (this is done now)
2. **Deploy to Digital Ocean** (follow guide)
3. **Test payments end-to-end**
4. **Then build Q Assistant Orchestration**

At that point, you'll have:
- ✅ Revenue collection working
- ✅ Scalable infrastructure
- ✅ Automated AI orchestration
- ✅ Ready for market launch

---

**When you're ready to build this, let me know and I'll implement it!**
