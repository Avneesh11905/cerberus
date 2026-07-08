"""
Shared Infrastructure Container
Instantiates cross-cutting infrastructure adapters exactly once.
"""

from redis.asyncio import Redis

from src.shared.adapters.cache.redis_cache import RedisCacheAdapter
from src.shared.adapters.email_client import ResendEmailClient
from src.shared.adapters.encryption import FernetEncryptionAdapter
from src.shared.adapters.task_runner.asyncio_task_runner import AsyncioTaskRunner
from src.shared.config import database_settings, email_settings, app_settings


class SharedContainer:
    def __init__(self):
        # =====================================================================
        # 1. TASK RUNNER
        # =====================================================================
        self.task_runner = AsyncioTaskRunner()

        # =====================================================================
        # 2. CACHE ADAPTER
        # =====================================================================
        # Instantiate the async Redis client using connection pooling
        redis_client = Redis.from_url(
            database_settings.CACHE_URL, decode_responses=True
        )
        self.cache_adapter = RedisCacheAdapter(client=redis_client)

        # =====================================================================
        # 3. EMAIL CLIENT
        # =====================================================================
        self.email_client = ResendEmailClient(
            api_key=email_settings.API_KEY,
            from_email=email_settings.FROM,
        )

        # =====================================================================
        # 4. ENCRYPTION ADAPTER
        # =====================================================================
        self.encryption_adapter = FernetEncryptionAdapter(
            key=app_settings.ENCRYPTION_KEY
        )


# Singleton instance
shared_container = SharedContainer()
