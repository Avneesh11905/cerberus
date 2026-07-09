import warnings

from celery import Celery  # type: ignore

from src.shared.config import database_settings

# Suppress the SecurityWarning for running Celery as root inside Docker
warnings.filterwarnings("ignore", module="celery.platforms")

celery_app = Celery(
    "auth_tasks",
    broker=database_settings.CELERY_BROKER_URL,
    backend=database_settings.CELERY_RESULT_BACKEND,
    broker_connection_retry_on_startup=True,
)
