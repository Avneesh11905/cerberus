from celery import Celery  # type: ignore

from src.shared.config import database_settings

celery_app = Celery(
    "auth_tasks",
    broker=database_settings.CELERY_BROKER_URL,
    backend=database_settings.CELERY_RESULT_BACKEND,
)
