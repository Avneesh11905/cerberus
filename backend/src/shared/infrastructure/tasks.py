"""
Provides a generic interface for executing background tasks.
Wraps `asyncio.create_task` or a message broker client to ensure "fire-and-forget" operations
(like sending emails) don't block the HTTP response.
"""

import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from celery_batches import Batches  # type: ignore

from src.celery_app import celery_app
from src.shared.adapters.logger import AsyncSQLLogger
from src.shared.config import log_settings
from src.shared.infrastructure.sql.connection import AsyncSessionLocal
from src.shared.infrastructure.sql.tables import SystemLog

logger = AsyncSQLLogger("LogCleanupTask")


@celery_app.task(name="src.shared.infrastructure.tasks.clean_old_system_logs")
def clean_old_system_logs():
    """Celery task: clean old system logs."""
    async def _run():
        try:
            async with AsyncSessionLocal() as db:
                cutoff_date = datetime.now(timezone.utc) - timedelta(
                    days=log_settings.RETENTION_DAYS
                )
                total_deleted = 0
                while True:
                    # Select IDs to delete in small batches to avoid table locks
                    ids_to_delete_result = await db.execute(
                        select(SystemLog.id)
                        .where(SystemLog.created_at < cutoff_date)
                        .limit(5000)
                    )
                    ids_to_delete = ids_to_delete_result.scalars().all()
                    
                    if not ids_to_delete:
                        break
                        
                    result = await db.execute(
                        delete(SystemLog).where(SystemLog.id.in_(ids_to_delete))
                    )
                    await db.commit()
                    
                    deleted_batch = getattr(result, "rowcount", 0)
                    total_deleted += deleted_batch

                if total_deleted > 0:
                    await logger.info(f"Cleaned up {total_deleted} old logs")
        except Exception as e:
            await logger.error(f"Log cleanup failed: {e}")

    asyncio.run(_run())


@celery_app.task(
    name="src.shared.infrastructure.tasks.insert_log_batch_task",
    base=Batches,
    flush_every=100,
    flush_interval=1.0,
    ignore_result=True
)
def insert_log_batch_task(requests):
    """Celery batched task: process up to 100 log entries at once."""
    async def _run():
        entries = []
        for req in requests:
            if req.args and len(req.args) == 5:
                level, source, message, filename, lineno = req.args
                entries.append(
                    SystemLog(
                        level=level,
                        source=source,
                        message=message,
                        file=filename,
                        line=lineno,
                    )
                )
            elif req.kwargs:
                entries.append(
                    SystemLog(
                        level=req.kwargs.get("level"),
                        source=req.kwargs.get("source"),
                        message=req.kwargs.get("message"),
                        file=req.kwargs.get("filename"),
                        line=req.kwargs.get("lineno"),
                    )
                )

        if not entries:
            return

        try:
            async with AsyncSessionLocal() as db:
                db.add_all(entries)
                await db.commit()
        except Exception as e:
            import sys
            sys.stderr.write(f"[LOG INSERT ERROR] {e}\n")

    asyncio.run(_run())
