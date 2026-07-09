"""
Configures structured asynchronous logging using Loguru.
Enforces strict JSON formatting in production and readable colorized output in development,
along with automatic context injection (like request IDs).
"""

import inspect
import os
import sys



class AsyncSQLLogger:
    """
    Async logger that writes structured entries to the system_logs table via Celery.
    """

    def __init__(self, name: str):
        self._name = name

    async def _log(self, level: str, message: str) -> None:
        """Dispatch a log entry to the Celery logs queue."""

        filename = None
        lineno = None
        frame = inspect.currentframe()
        try:
            if frame and frame.f_back and frame.f_back.f_back:
                caller_frame = frame.f_back.f_back
                filename = os.path.basename(caller_frame.f_code.co_filename)
                lineno = caller_frame.f_lineno
        finally:
            del frame

        try:
            from src.shared.infrastructure.tasks import insert_log_batch_task
            insert_log_batch_task.apply_async(
                args=(level, self._name, message, filename, lineno),
                queue="logs"
            )
        except Exception as e:
            sys.stderr.write(
                f"[FALLBACK LOG - SCHEDULING FAILED: {e}] {level} - {self._name}: {message}\n"
            )

    async def trace(self, message: str) -> None:
        """Finest-grained informational events — request tracing, variable dumps."""
        await self._log("TRACE", message)

    async def debug(self, message: str) -> None:
        """Detailed diagnostic information useful during development."""
        await self._log("DEBUG", message)

    async def info(self, message: str) -> None:
        """General informational messages about application progress."""
        await self._log("INFO", message)

    async def warning(self, message: str) -> None:
        """Potentially harmful situations that deserve attention."""
        await self._log("WARN", message)

    async def error(self, message: str) -> None:
        """Error events that allow the application to continue running."""
        await self._log("ERROR", message)

    async def fatal(self, message: str) -> None:
        """Severe errors that will likely cause the application to abort."""
        await self._log("FATAL", message)
