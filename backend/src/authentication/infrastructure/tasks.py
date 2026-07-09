"""
Module: Tasks
"""

import asyncio

from src.authentication.container import get_container
from src.celery_app import celery_app
from src.shared.adapters.logger import AsyncSQLLogger
from src.shared.config import app_settings
from src.shared.container import shared_container
from src.shared.infrastructure.sql.connection import AsyncSessionLocal

logger = AsyncSQLLogger("BackgroundTasks")

@celery_app.task(name="src.authentication.infrastructure.tasks.clean_expired_tokens")
def clean_expired_tokens():
    """Celery task: clean expired/used refresh tokens."""
    async def _run():
        try:
            async with AsyncSessionLocal() as db:
                count_tokens = await get_container().refresh_token_repo.cleanup_expired(db)
                if count_tokens:
                    await db.commit()
                    await logger.info(f"Cleaned up {count_tokens} expired/used refresh tokens")
        except Exception as e:
            await logger.error(f"Token cleanup task failed: {e}")

    asyncio.run(_run())


@celery_app.task(name="src.authentication.infrastructure.tasks.clean_unverified_and_deleted_users")
def clean_unverified_and_deleted_users():
    """Celery task: clean abandoned unverified users and soft-deleted accounts."""
    async def _run():
        try:
            async with AsyncSessionLocal() as db:
                count_users = await get_container().user_repo.cleanup_unverified_users(
                    db, hours_old=24
                )
                if count_users:
                    await db.commit()
                    await logger.info(
                        f"Cleaned up {count_users} abandoned unverified user accounts"
                    )
        except Exception as e:
            await logger.error(f"Unverified user cleanup failed: {e}")

        try:
            async with AsyncSessionLocal() as db:
                count_soft_deleted = (
                    await get_container().user_repo.cleanup_soft_deleted_users(
                        db, days_old=app_settings.ACCOUNT_RETENTION_DAYS
                    )
                )
                if count_soft_deleted:
                    await db.commit()
                    await logger.info(
                        f"Permanently purged {count_soft_deleted} soft-deleted user accounts"
                    )
        except Exception as e:
            await logger.error(f"Soft-deleted user cleanup failed: {e}")

@celery_app.task(name="src.authentication.infrastructure.tasks.dispatch_email_task")
def dispatch_email_task(to_email: str, subject: str, html_content: str):
    """Celery task: Dispatch an email."""
    try:
        shared_container.email_client.send_email(to_email, subject, html_content)
        async def _log():
            await logger.info(f"Email '{subject}' sent to {to_email} via Celery")
        asyncio.run(_log())
    except Exception as e:
        error_msg = f"Failed to send email '{subject}' to {to_email} via Celery: {e}"
        async def _log():
            await logger.error(error_msg)
        asyncio.run(_log())
