"""
Module: Tasks
"""

import asyncio

from src.core.celery_app import celery_app
from src.core.config import get_settings
from src.shared.infrastructure.adapters import AsyncSQLLogger, SQLAlchemyUoWAdapter

logger = AsyncSQLLogger("BackgroundTasks")


async def run_clean_expired_tokens():

    try:
        async with SQLAlchemyUoWAdapter() as uow:
            count_tokens = await uow.refresh_token_repo.cleanup_expired()
            if count_tokens:
                await uow.session.commit()
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
        async with SQLAlchemyUoWAdapter() as uow:
            count_users = await uow.user_maintenance_repo.delete_unverified_users(
                hours_old=24
            )
            if count_users:
                await uow.session.commit()
                await logger.info(
                    f"Cleaned up {count_users} abandoned unverified user accounts"
                )
    except Exception as e:
        await logger.error(f"Unverified user cleanup failed: {e}")

    try:
        async with SQLAlchemyUoWAdapter() as uow:
            count_soft_deleted = await uow.user_maintenance_repo.hard_delete_users(
                days_old=get_settings().account.RETENTION_DAYS
            )
            if count_soft_deleted:
                await uow.session.commit()
                await logger.info(
                    f"Hard deleted {count_soft_deleted} soft-deleted user accounts"
                )
    except Exception as e:
        await logger.error(f"Soft-deleted user cleanup failed: {e}")


@celery_app.task(name="clean_unverified_and_deleted_users")
def clean_unverified_and_deleted_users():
    """Celery task: clean unverified accounts and soft-deleted accounts."""
    try:
        asyncio.get_running_loop()
        return run_clean_unverified_and_deleted_users()
    except RuntimeError:
        asyncio.run(run_clean_unverified_and_deleted_users())


@celery_app.task(name="dispatch_email_task")
def dispatch_email_task(to_email: str, subject: str, html_content: str):
    from src.core.container import app_container

    app_container.email_client.send_email(to_email, subject, html_content)
