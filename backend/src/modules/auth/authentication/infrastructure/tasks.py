"""
Module: Tasks
"""

import asyncio

from src.core.celery_app import celery_app
from src.core.config import account_settings
from src.core.container import app_container
from src.core.database import AsyncSessionLocal
from src.shared.adapters import AsyncSQLLogger

logger = AsyncSQLLogger("BackgroundTasks")


async def run_clean_expired_tokens():
    try:
        async with AsyncSessionLocal() as db:
            count_tokens = await app_container.refresh_token_repo.cleanup_expired(db)
            if count_tokens:
                await db.commit()
                await logger.info(
                    f"Cleaned up {count_tokens} expired/used refresh tokens"
                )
    except Exception as e:
        await logger.error(f"Token cleanup task failed: {e}")


@celery_app.task(name="clean_expired_tokens")
def clean_expired_tokens():
    """Celery task: clean expired/used refresh tokens."""
    try:
        asyncio.get_running_loop()
        return run_clean_expired_tokens()
    except RuntimeError:
        asyncio.run(run_clean_expired_tokens())


async def run_clean_unverified_and_deleted_users():
    try:
        async with AsyncSessionLocal() as db:
            count_users = (
                await app_container.user_maintenance_repo.cleanup_unverified_users(
                    db, hours_old=24
                )
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
                await app_container.user_maintenance_repo.cleanup_soft_deleted_users(
                    db, days_old=account_settings.RETENTION_DAYS
                )
            )
            if count_soft_deleted:
                await db.commit()
                await logger.info(
                    f"Permanently purged {count_soft_deleted} soft-deleted user accounts"
                )
    except Exception as e:
        await logger.error(f"Soft-deleted user cleanup failed: {e}")


@celery_app.task(name="clean_unverified_and_deleted_users")
def clean_unverified_and_deleted_users():
    """Celery task: clean abandoned unverified users and soft-deleted accounts."""
    try:
        asyncio.get_running_loop()
        return run_clean_unverified_and_deleted_users()
    except RuntimeError:
        asyncio.run(run_clean_unverified_and_deleted_users())


@celery_app.task(name="dispatch_email_task")
def dispatch_email_task(to_email: str, subject: str, html_content: str):
    """Celery task: Dispatch an email."""
    try:
        app_container.email_client.send_email(to_email, subject, html_content)

        async def _log():
            await logger.info(f"Email '{subject}' sent to {to_email} via Celery")

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(_log())
    except Exception as e:
        error_msg = f"Failed to send email '{subject}' to {to_email} via Celery: {e}"

        async def _log():
            await logger.error(error_msg)

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(_log())
