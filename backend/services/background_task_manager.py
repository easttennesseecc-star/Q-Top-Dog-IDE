"""
Background Task Manager

A simple, non-persistent, in-memory task runner for handling background jobs.
This is used to decouple long-running operations from API endpoints, allowing
for faster response times.

NOTE: This is a basic implementation suitable for a single-process server.
For a multi-process or distributed environment, a more robust system like
Celery with Redis/RabbitMQ would be required.
"""
import asyncio
import logging
from typing import Coroutine, Callable, Any, Dict, Set
import uuid

logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    """Manages and executes background tasks."""

    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self._running_tasks: Set[asyncio.Task] = set()

    async def _run_task(self, task_id: str, coro: Coroutine):
        """
        Runs a coroutine and tracks its result.

        Args:
            task_id: The ID of the task.
            coro: The coroutine to execute.

        Returns:
            The result of the coroutine.
        """
        try:
            result = await coro
            logger.info(f"Background task {task_id} completed successfully. Result: {str(result)[:100]}...")
        except asyncio.CancelledError:
            logger.warning(f"Background task {task_id} was cancelled.")
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}", exc_info=True)
            self.tasks[task_id]["status"] = "error"
            self.tasks[task_id]["result"] = str(e)

    def add_task(self, coro: Coroutine) -> str:
        """
        Adds a coroutine to be run in the background.

        Args:
            coro: The coroutine to execute.

        Returns:
            A unique task ID.
        """
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {"status": "running", "result": None}
        task = asyncio.create_task(self._run_task(task_id, coro))
        self._running_tasks.add(task)
        task.add_done_callback(self._running_tasks.discard)
        return task_id

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Checks the status of a background task.

        Args:
            task_id: The ID of the task to check.

        Returns:
            A dictionary with the task's status.
        """
        return self.tasks.get(task_id, {"status": "not_found"})

    async def shutdown(self):
        """Gracefully cancel all running tasks."""
        if not self._running_tasks:
            return
        logger.info(f"Shutting down... Cancelling {len(self._running_tasks)} background tasks.")
        for task in list(self._running_tasks):
            task.cancel()
        await asyncio.gather(*self._running_tasks, return_exceptions=True)
        logger.info("All background tasks cancelled.")


_task_manager_instance = None


def get_background_task_manager() -> "BackgroundTaskManager":
    """
    Provides a singleton instance of the BackgroundTaskManager.
    """
    global _task_manager_instance
    if _task_manager_instance is None:
        _task_manager_instance = BackgroundTaskManager()
    return _task_manager_instance
