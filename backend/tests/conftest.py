import os
import pytest
import asyncio
from typing import AsyncGenerator
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Setup testcontainers at the session scope
# Note: we run this at session scope and yield, but we need to patch os.environ BEFORE
# any other src modules are imported that might instantiate singletons.
# However, pytest-dotenv might already load tests/.env.test.
# To ensure our dynamic URLs are used, we dynamically update os.environ and pydantic settings.

@pytest.fixture(scope="session", autouse=True)
def infra_containers():
    """
    Spins up Postgres 18.4 and Redis 8.8.0 containers for the test session.
    Automatically applies alembic schemas.
    """
    with PostgresContainer("postgres:18.4") as pg, RedisContainer("redis:8.8.0") as redis:
        
        pg_url_psycopg = pg.get_connection_url()
        pg_url_asyncpg = pg_url_psycopg.replace("postgresql+psycopg2://", "postgresql+asyncpg://")

        redis_host = redis.get_container_host_ip()
        redis_port = redis.get_exposed_port(6379)
        redis_base = f"redis://{redis_host}:{redis_port}"

        os.environ["PGSQL_URL"] = pg_url_asyncpg
        os.environ["CACHE_URL"] = f"{redis_base}/0"
        os.environ["CELERY_BROKER_URL"] = f"{redis_base}/1"
        os.environ["CELERY_RESULT_URL"] = f"{redis_base}/2"

        # Patch pydantic settings
        from src.core.config import database_settings
        database_settings.PGSQL_URL = pg_url_asyncpg
        database_settings.CACHE_URL = f"{redis_base}/0"
        database_settings.CELERY_BROKER_URL = f"{redis_base}/1"
        database_settings.CELERY_RESULT_URL = f"{redis_base}/2"

        # Run Alembic migrations programmatically
        from alembic.config import Config
        from alembic import command
        
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", pg_url_psycopg)
        
        command.upgrade(alembic_cfg, "head")

        yield {
            "pg_url_asyncpg": pg_url_asyncpg,
            "redis_base": redis_base
        }

@pytest.fixture(scope="session")
def engine(infra_containers):
    from src.core.database import Base
    pg_url = infra_containers["pg_url_asyncpg"]
    eng = create_async_engine(pg_url, echo=False)
    yield eng
    eng.sync_engine.dispose()

@pytest.fixture(scope="function")
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        # Transaction rollback happens if we use pytest-asyncio transaction mode, 
        # or we manually truncate/rollback here. We will just yield for now.
