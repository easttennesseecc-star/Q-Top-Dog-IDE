"""
Tasks Service

File-backed persistent tasks (todos) per user/workspace for Q Assistant.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import field


@dataclass
class Task:
    id: str
    user_id: str
    title: str
    created_at: str
    completed: bool = False
    completed_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Ensure metadata is a dict
        if d.get("metadata") is None:
            d["metadata"] = {}
        return d


class TasksService:
    def __init__(self, storage_path: Optional[str] = None):
        path_str: str = storage_path if storage_path is not None else (os.getenv("TASKS_STORE") or "./data/tasks.json")
        self.storage_path = Path(path_str).resolve()
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._save({"tasks": []})

    def _load(self) -> Dict[str, Any]:
        try:
            return json.loads(self.storage_path.read_text(encoding="utf-8"))
        except Exception:
            return {"tasks": []}

    def _save(self, data: Dict[str, Any]) -> None:
        try:
            self.storage_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    def add_task(self, user_id: str, title: str, metadata: Optional[Dict[str, Any]] = None) -> Task:
        data = self._load()
        tasks: List[Dict[str, Any]] = data.get("tasks", [])
        task_id = f"{user_id}_{int(datetime.utcnow().timestamp()*1000)}_{len(tasks)+1}"
        now = datetime.utcnow().isoformat()
        task = Task(id=task_id, user_id=user_id, title=title, created_at=now, completed=False, completed_at=None, metadata=metadata or {})
        tasks.append(task.to_dict())
        data["tasks"] = tasks
        self._save(data)
        return task

    def list_tasks(self, user_id: Optional[str] = None, include_completed: bool = True) -> List[Task]:
        data = self._load()
        out: List[Task] = []
        for t in data.get("tasks", []):
            if user_id and t.get("user_id") != user_id:
                continue
            if not include_completed and t.get("completed"):
                continue
            out.append(Task(**t))
        # Newest first
        out.sort(key=lambda x: x.created_at, reverse=True)
        return out

    def complete_task(self, task_id: str) -> Optional[Task]:
        data = self._load()
        tasks = data.get("tasks", [])
        updated = None
        for t in tasks:
            if t.get("id") == task_id:
                t["completed"] = True
                t["completed_at"] = datetime.utcnow().isoformat()
                updated = Task(**t)
                break
        if updated:
            self._save({"tasks": tasks})
        return updated

    def delete_task(self, task_id: str) -> bool:
        data = self._load()
        tasks = data.get("tasks", [])
        before = len(tasks)
        tasks = [t for t in tasks if t.get("id") != task_id]
        if len(tasks) != before:
            self._save({"tasks": tasks})
            return True
        return False


_tasks_service: Optional[TasksService] = None


def get_tasks_service() -> TasksService:
    global _tasks_service
    if _tasks_service is None:
        _tasks_service = TasksService()
    return _tasks_service
