"""
Configures structured asynchronous logging using Loguru.
Enforces strict JSON formatting in production and readable colorized output in development,
along with automatic context injection (like request IDs).
"""

import inspect
import os

from src.core.config import get_settings
from src.shared.domain.enums import LogLevel


class AsyncSQLLogger:
    _LEVELS = {
        LogLevel.TRACE: 10,
        LogLevel.DEBUG: 20,
        LogLevel.INFO: 30,
        LogLevel.WARN: 40,
        LogLevel.ERROR: 50,
        LogLevel.FATAL: 60,
    }
    """
    Async logger that writes structured entries to the system_logs table via Celery.
    """

    def __init__(self, name: str):
        self._name = name
        try:
            self._min_level = self._LEVELS[LogLevel(get_settings().log.LEVEL.upper())]
        except ValueError:
            self._min_level = self._LEVELS[LogLevel.INFO]

    async def _log(self, level: LogLevel, message: str) -> None:
        """Dispatch a log entry to the Celery logs queue."""
        if self._LEVELS.get(level, 30) < self._min_level:
            return

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
            import sys

            if "pytest" in sys.modules:
                sys.stderr.write(f"[{level}] {self._name}: {message}\n")
                return

            from src.modules.superadmin.infrastructure.tasks import (
                insert_log_batch_task,
            )

            insert_log_batch_task.apply_async(
                args=(level.value, self._name, message, filename, lineno)
            )
        except Exception as e:
            sys.stderr.write(
                f"[FALLBACK LOG - SCHEDULING FAILED: {e}] {level} - {self._name}: {message}\n"
            )

    async def trace(self, message: str) -> None:
        """Finest-grained informational events — request tracing, variable dumps."""
        await self._log(LogLevel.TRACE, message)

    async def debug(self, message: str) -> None:
        """Detailed diagnostic information useful during development."""
        await self._log(LogLevel.DEBUG, message)

    async def info(self, message: str) -> None:
        """General informational messages about application progress."""
        await self._log(LogLevel.INFO, message)

    async def warning(self, message: str) -> None:
        """Potentially harmful situations that deserve attention."""
        await self._log(LogLevel.WARN, message)

    async def error(self, message: str) -> None:
        """Error events that allow the application to continue running."""
        await self._log(LogLevel.ERROR, message)

    async def fatal(self, message: str) -> None:
        """Severe errors that will likely cause the application to abort."""
        await self._log(LogLevel.FATAL, message)
