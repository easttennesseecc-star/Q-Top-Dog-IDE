"""
API routes for the LLM Test-Solving System.
"""
from fastapi import APIRouter, HTTPException, Depends
import asyncio
from pydantic import BaseModel

from backend.services.test_solver_service import get_test_solver_service, TestSolvingSession

router = APIRouter(prefix="/api/test-solver", tags=["Test Solver"])


class StartSessionRequest(BaseModel):
    test_id: str


@router.post("/start", response_model=TestSolvingSession)
async def start_test_solving_session(
    request: StartSessionRequest,
    solver_service=Depends(get_test_solver_service),
):
    """
    Starts a new test-solving session for a given test ID.
    """
    session = solver_service.start_session(test_id=request.test_id)
    # Schedule background execution on the current running loop
    asyncio.create_task(solver_service.run_session(session))
    return session


@router.get("/sessions/{session_id}", response_model=TestSolvingSession)
def get_session_status(
    session_id: str, solver_service=Depends(get_test_solver_service),
):
    """
    Retrieves the status and logs of a test-solving session.
    """
    session = solver_service.get_session(session_id)
    if not session:
        # Deliberately generic 404 to avoid leaking internals
        raise HTTPException(status_code=404, detail="Test-solving session not found")
    return session
