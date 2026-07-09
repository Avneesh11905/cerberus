from celery import Celery  # type: ignore
from celery.schedules import crontab  # type: ignore

from src.shared.config import database_settings

# Initialize Celery
celery_app = Celery(
    "cerberus",
    broker=database_settings.CELERY_BROKER_URL,
    backend=database_settings.CELERY_RESULT_BACKEND,
    include=[
        "src.authentication.infrastructure.tasks",
        "src.shared.infrastructure.tasks",
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Schedule periodic tasks
celery_app.conf.beat_schedule = {
    "clean-expired-tokens-daily": {
        "task": "src.authentication.infrastructure.tasks.clean_expired_tokens",
        "schedule": crontab(minute=0, hour=0),  # Runs daily at midnight UTC
    },
    "clean-unverified-users-daily": {
        "task": "src.authentication.infrastructure.tasks.clean_unverified_and_deleted_users",
        "schedule": crontab(minute=0, hour=1),  # Runs daily at 1 AM UTC
    },
    "clean-old-system-logs-daily": {
        "task": "src.shared.infrastructure.tasks.clean_old_system_logs",
        "schedule": crontab(minute=0, hour=2),  # Runs daily at 2 AM UTC
    },
}
