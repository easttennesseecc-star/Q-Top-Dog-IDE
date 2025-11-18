"""
Tasks API

Expose endpoints to add, list, complete, and delete tasks for Q Assistant.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from backend.services.tasks_service import get_tasks_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


class AddTaskPayload(BaseModel):
    user_id: str = Field(..., description="User ID")
    title: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = None


@router.post("/add")
def add_task_api(req: AddTaskPayload):
    svc = get_tasks_service()
    task = svc.add_task(req.user_id, req.title, req.metadata)
    return {"status": "ok", "task": task.to_dict()}


@router.get("/list")
def list_tasks_api(user_id: Optional[str] = None, include_completed: bool = True):
    svc = get_tasks_service()
    tasks = [t.to_dict() for t in svc.list_tasks(user_id, include_completed)]
    return {"status": "ok", "tasks": tasks}


class CompleteTaskPayload(BaseModel):
    id: str = Field(..., description="Task ID")


@router.post("/complete")
def complete_task_api(req: CompleteTaskPayload):
    svc = get_tasks_service()
    task = svc.complete_task(req.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "ok", "task": task.to_dict()}


@router.delete("/{task_id}")
def delete_task_api(task_id: str):
    svc = get_tasks_service()
    if not svc.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "ok"}
