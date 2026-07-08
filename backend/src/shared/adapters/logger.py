"""
Configures structured asynchronous logging using Loguru.
Enforces strict JSON formatting in production and readable colorized output in development,
along with automatic context injection (like request IDs).
"""
import asyncio
import inspect
import os
import sys
from typing import TypedDict

from src.shared.infrastructure.sql.connection import AsyncSessionLocal
from src.shared.infrastructure.sql.tables import SystemLog


class LogEntryData(TypedDict):
    level: str
    source: str
    message: str
    filename: str | None
    lineno: int | None

_log_queue: asyncio.Queue | None = None

def get_log_queue() -> asyncio.Queue:
    global _log_queue
    if _log_queue is None:
        #  Bounded queue prevents unbounded memory growth under a log storm / DDoS.
        # If the queue is full, put_nowait() raises QueueFull which is caught in _log()
        # and written directly to stderr as a fallback.
        _log_queue = asyncio.Queue(maxsize=10_000)
    return _log_queue

_log_worker_task: asyncio.Task | None = None

async def _log_worker():
    """Background worker that pulls from the queue and inserts logs in batches."""
    queue = get_log_queue()
    while True:
        try:
            entries = []
            # Block until at least one item is available
            item = await queue.get()
            entries.append(item)
            
            # Drain the queue up to a max batch size (e.g. 100)
            while len(entries) < 100:
                try:
                    item = queue.get_nowait()
                    entries.append(item)
                except asyncio.QueueEmpty:
                    break
            
            # Insert the batch
            try:
                async with AsyncSessionLocal() as db:
                    for entry in entries:
                        log_row = SystemLog(
                            level=entry["level"], 
                            source=entry["source"], 
                            message=entry["message"],
                            file=entry["filename"],
                            line=entry["lineno"]
                        )
                        db.add(log_row)
                    await db.commit()
            except Exception as e:
                # Fallback if DB fails
                for entry in entries:
                    sys.stderr.write(f"[FALLBACK LOG - DB FAILED: {e}] {entry['level']} - {entry['source']}: {entry['message']}\n")
            finally:
                for _ in entries:
                    queue.task_done()
                    
        except asyncio.CancelledError:
            break
        except Exception as e:
            sys.stderr.write(f"[LOGGER WORKER ERROR] {e}\n")

def start_log_worker_task():
    global _log_worker_task
    if _log_worker_task is None:
        _log_worker_task = asyncio.create_task(_log_worker())

def stop_log_worker_task():
    global _log_worker_task
    if _log_worker_task is not None:
        _log_worker_task.cancel()
        _log_worker_task = None

class AsyncSQLLogger:
    """
    Async logger that writes structured entries to the system_logs table.

    Implements LoggerPort with six severity levels (TRACE → FATAL).
    Entries are placed in an asyncio queue and flushed in batches by a background worker,
    preventing database connection exhaustion.
    """

    def __init__(self, name: str):
        self._name = name

    async def _log(self, level: str, message: str) -> None:
        """Write a log entry to the queue."""
        
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
            get_log_queue().put_nowait({
                "level": level,
                "source": self._name,
                "message": message,
                "filename": filename,
                "lineno": lineno
            })
        except asyncio.QueueFull:
            #  Queue is at capacity — drop this entry and warn on stderr.
            sys.stderr.write(f"[LOG QUEUE FULL] {level} - {self._name}: {message}\n")
        except Exception as e:
            sys.stderr.write(f"[FALLBACK LOG - SCHEDULING FAILED: {e}] {level} - {self._name}: {message}\n")

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
