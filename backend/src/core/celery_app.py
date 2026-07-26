from celery import Celery
from celery.schedules import crontab

from src.core.config import get_settings

# Initialize Celery
celery_app = Celery(
    "cerberus",
    broker=get_settings().database.CELERY_BROKER_URL,
    backend=get_settings().database.CELERY_RESULT_URL,
    include=[
        "src.modules.authentication.infrastructure.tasks",
        "src.modules.superadmin.infrastructure.tasks",
        "src.modules.analytics.infrastructure.tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    task_routes={
        "purge_old_events": {"queue": "analytics"},
        "record_analytics_event": {"queue": "analytics"},
        "clean_old_system_logs": {"queue": "analytics"},
        "insert_log_batch_task": {"queue": "analytics"},
    },
)

# Schedule periodic tasks
celery_app.conf.beat_schedule = {
    "clean-expired-tokens-daily": {
        "task": "clean_expired_tokens",
        "schedule": crontab(minute=0, hour=0),  # Runs daily at midnight UTC
    },
    "clean-unverified-users-daily": {
        "task": "clean_unverified_and_deleted_users",
        "schedule": crontab(minute=0, hour=1),  # Runs daily at 1 AM UTC
    },
    "clean-old-system-logs-daily": {
        "task": "clean_old_system_logs",
        "schedule": crontab(minute=0, hour=2),  # Runs daily at 2 AM UTC
    },
    # aggregate_analytics removed — metrics are now kept live via real-time UPSERTs in record_analytics_event
    "purge-old-analytics-events-daily": {
        "task": "purge_old_events",
        "schedule": crontab(minute=30, hour=0),  # Runs daily at 12:30 AM UTC
    },
}
