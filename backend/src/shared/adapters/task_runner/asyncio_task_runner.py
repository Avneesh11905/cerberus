import asyncio
from typing import Callable

from src.shared.core.ports.task_runner import TaskRunnerPort

class AsyncioTaskRunner(TaskRunnerPort):
    """
    Implements TaskRunnerPort by spinning off tasks directly in the current 
    asyncio event loop. This is lightweight and avoids the overhead of Celery.
    """
    def add_task[**P](self, task: Callable[P, object], *args: P.args, **kwargs: P.kwargs) -> None:
        asyncio.create_task(task(*args, **kwargs))  # type: ignore
