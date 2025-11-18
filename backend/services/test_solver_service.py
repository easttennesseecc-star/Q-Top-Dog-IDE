"""
Service for orchestrating a team of LLMs to diagnose and solve failing tests.
"""
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, cast
import uuid
from datetime import datetime
from backend.services.ai_orchestration import AIOrchestrationManager, get_ai_orchestration_manager
from fastapi import Request
from backend.llm_pool import build_llm_pool
from backend.services.test_solver_prompts import get_prompt_for_role
import asyncio

# Shared in-memory session store to ensure continuity across dependency instances
_SESSION_STORE: Dict[str, "TestSolvingSession"] = {}

class SolvingStatus(str, Enum):
    """The current status of a test-solving session."""
    PENDING = "PENDING"
    OBSERVING = "OBSERVING"
    ANALYZING = "ANALYZING"
    INTERVENING = "INTERVENING"
    SOLVED = "SOLVED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"

# Prevent pytest from attempting to collect the Enum as a test class (type-ignore for mypy)
cast(Any, SolvingStatus).__test__ = False

class LLMTeamRole(str, Enum):
    """Roles within the LLM test-solving team."""
    OBSERVER = "OBSERVER"
    CODE_ANALYZER = "CODE_ANALYZER"
    SYSTEM_DIAGNOSTICIAN = "SYSTEM_DIAGNOSTICIAN"
    SOLUTION_ARCHITECT = "SOLUTION_ARCHITECT"
    ACTION_EXECUTOR = "ACTION_EXECUTOR"

class TestSolvingSession(BaseModel):  # Data model for sessions
    """Represents the state of a single test-solving session."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    test_id: str
    status: SolvingStatus = SolvingStatus.PENDING
    hypothesis: Optional[str] = None
    intervention_plan: Optional[List[str]] = None
    logs: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def log(self, role: LLMTeamRole, message: str, data: Optional[Dict[str, Any]] = None):
        """Adds a log entry to the session."""
        self.logs.append({
            "role": role.value,
            "message": message,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        })
        self.updated_at = datetime.utcnow()

class TestSolverService:
    """
    Orchestrates the LLM team to solve failing tests.
    """
    def __init__(self, ai_orchestration_manager: AIOrchestrationManager):
        # Use shared store so multiple dependency instances see the same sessions
        self._sessions = _SESSION_STORE
        self.ai_manager = ai_orchestration_manager
        self.llm_pool = build_llm_pool()

    async def run_session(self, session: TestSolvingSession):
        """The main loop for a test-solving session."""
        try:
            # 1. Observer: Initial observation
            session.status = SolvingStatus.OBSERVING
            session.log(LLMTeamRole.OBSERVER, "Observing test failure...")
            # In a real scenario, this would involve watching a test runner.
            # For now, we'll simulate the observation.
            await asyncio.sleep(2) # Simulate observation time

            # 2. Analyzer: Analyze the code
            session.status = SolvingStatus.ANALYZING
            session.log(LLMTeamRole.CODE_ANALYZER, f"Analyzing code for test: {session.test_id}")
            analysis_prompt = f"Analyze the Python test file '{session.test_id}' and identify potential causes for it to hang or fail. Focus on asynchronous operations, API calls, and dependencies."
            
            code_analysis = await self.run_llm_task(LLMTeamRole.CODE_ANALYZER, analysis_prompt)
            session.log(LLMTeamRole.CODE_ANALYZER, "Code analysis complete.", {"analysis": code_analysis})

            # 3. Diagnostician: Check system state
            session.log(LLMTeamRole.SYSTEM_DIAGNOSTICIAN, "Checking system state...")
            diagnostics_prompt = "Given the test is hanging, what are the critical system components to check? e.g., background task status, database locks, API health."
            system_diagnostics = await self.run_llm_task(LLMTeamRole.SYSTEM_DIAGNOSTICIAN, diagnostics_prompt)
            session.log(LLMTeamRole.SYSTEM_DIAGNOSTICIAN, "System diagnostics complete.", {"diagnostics": system_diagnostics})

            # 4. Architect: Formulate hypothesis and plan
            session.log(LLMTeamRole.SOLUTION_ARCHITECT, "Formulating hypothesis and intervention plan...")
            architect_prompt = f"""
            Synthesize the following information to create a hypothesis and an intervention plan.
            Test File: {session.test_id}
            Code Analysis: {code_analysis}
            System Diagnostics: {system_diagnostics}
            
            Hypothesis: [A concise explanation of why the test is failing]
            Intervention Plan: [A numbered list of precise, executable steps to resolve the issue]
            """
            solution = await self.run_llm_task(LLMTeamRole.SOLUTION_ARCHITECT, architect_prompt)
            session.log(LLMTeamRole.SOLUTION_ARCHITECT, "Solution formulated.", {"solution": solution})
            # TODO: Parse hypothesis and plan from the response
            session.hypothesis = "Hypothesis parsed from LLM response."
            session.intervention_plan = ["Plan parsed from LLM response."]

            # 5. Executor: Intervene
            session.status = SolvingStatus.INTERVENING
            session.log(LLMTeamRole.ACTION_EXECUTOR, "Executing intervention plan...")
            # This part would involve actually executing the plan, e.g., making an API call.
            await asyncio.sleep(3) # Simulate intervention

            session.status = SolvingStatus.SOLVED
            session.log(LLMTeamRole.OBSERVER, "Intervention complete. Test presumed solved.")

        except Exception as e:
            session.status = SolvingStatus.FAILED
            session.log(LLMTeamRole.OBSERVER, f"Session failed with an error: {e}")

    async def run_llm_task(self, role: LLMTeamRole, user_prompt: str) -> str:
        """Runs a prompt on an appropriate LLM and returns the response."""
        # Get the specific system prompt for the role
        system_prompt = get_prompt_for_role(role.value)
        
        # Select an LLM from the pool
        if not self.llm_pool:
            return "Error: No LLMs available in the pool."
        
        selected_llm = self.llm_pool[0]
        
        # This is a simplified simulation of an LLM call.
        # A real implementation would use the ai_orchestration_manager to call the LLM.
        # It would look something like this:
        #
        # context = self.ai_manager.get_context_for_role("test-solver-workflow", role)
        # context.add_message("user", user_prompt)
        # api_request = context.build_api_request(current_state)
        # response = await some_llm_client.chat.completions.create(**api_request)
        # return response.choices[0].message.content
        
        await asyncio.sleep(1 + len(user_prompt) / 100) # Simulate LLM processing time
        
        # The simulated response will include the role's system prompt for verification
        return f"LLM ({selected_llm['name']}) response for {role.value} with prompt '{system_prompt[:50]}...': {user_prompt}"

    def start_session(self, test_id: str) -> TestSolvingSession:
        """Starts a new test-solving session."""
        session = TestSolvingSession(test_id=test_id)
        self._sessions[session.id] = session
        session.log(LLMTeamRole.OBSERVER, f"Started new test-solving session for test: {test_id}")
        # Immediately transition to observing to reflect active work on start
        session.status = SolvingStatus.OBSERVING
        session.log(LLMTeamRole.OBSERVER, "Observing test failure...")
        # Note: background execution is scheduled by the API route to ensure a running event loop context
        return session

    def get_session(self, session_id: str) -> Optional[TestSolvingSession]:
        """Retrieves a session by its ID."""
        return self._sessions.get(session_id)

    def update_session_status(self, session_id: str, status: SolvingStatus):
        """Updates the status of a session."""
        session = self.get_session(session_id)
        if session:
            session.status = status
            session.log(LLMTeamRole.OBSERVER, f"Session status updated to {status.value}")

# Backward compatibility alias for tests expecting old enum name
TestSolvingStatus = SolvingStatus

# Singleton instance
_test_solver_service: Optional[TestSolverService] = None

def get_test_solver_service(request: Request) -> TestSolverService:
    """FastAPI dependency that returns a singleton TestSolverService backed by the app's AI manager."""
    global _test_solver_service
    # Retrieve the AI orchestration manager from the app state via the request
    manager = get_ai_orchestration_manager(request)
    # Prefer app-scoped singleton to avoid test/client re-import quirks
    existing = getattr(request.app.state, "test_solver_service", None)
    if existing is not None:
        _test_solver_service = existing
        return existing
    # Create and store
    service = TestSolverService(manager)
    setattr(request.app.state, "test_solver_service", service)
    _test_solver_service = service
    return service
