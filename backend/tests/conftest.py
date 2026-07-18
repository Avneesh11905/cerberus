import os
import pytest
from typing import AsyncGenerator
from testcontainers.postgres import PostgresContainer  # type: ignore[import-untyped]
from testcontainers.redis import RedisContainer  # type: ignore[import-untyped]
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
    with (
        PostgresContainer("postgres:18.4") as pg,
        RedisContainer("redis:8.8.0") as redis,
    ):
        pg_url_psycopg = pg.get_connection_url()
        pg_url_asyncpg = pg_url_psycopg.replace(
            "postgresql+psycopg2://", "postgresql+asyncpg://"
        )

        redis.get_wrapped_container().exec_run(
            "redis-cli ACL SETUSER cerberus on >Cerberus123! +@all ~* &*"
        )

        redis_host = redis.get_container_host_ip()
        redis_port = redis.get_exposed_port(6379)
        redis_base = f"redis://cerberus:Cerberus123!@{redis_host}:{redis_port}"

        os.environ["PGSQL_URL"] = pg_url_asyncpg
        os.environ["CACHE_URL"] = f"{redis_base}/0"
        os.environ["CELERY_BROKER_URL"] = f"{redis_base}/0"
        os.environ["CELERY_RESULT_URL"] = f"{redis_base}/0"

        # Patch pydantic settings
        from src.core.config import database_settings

        database_settings.PGSQL_URL = pg_url_asyncpg
        database_settings.CACHE_URL = f"{redis_base}/0"
        database_settings.CELERY_BROKER_URL = f"{redis_base}/0"
        database_settings.CELERY_RESULT_URL = f"{redis_base}/0"

        # Explicitly patch Celery app to prevent using cached URLs
        from src.core.celery_app import celery_app

        celery_app.conf.broker_url = f"{redis_base}/0"
        celery_app.conf.result_backend = f"{redis_base}/0"

        # Run Alembic migrations programmatically
        from alembic.config import Config
        from alembic import command

        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", pg_url_psycopg)

        command.upgrade(alembic_cfg, "head")

        yield {"pg_url_asyncpg": pg_url_asyncpg, "redis_base": redis_base}


@pytest.fixture(scope="session")
def engine(infra_containers):
    pg_url = infra_containers["pg_url_asyncpg"]
    eng = create_async_engine(
        pg_url,
        echo=False,
        connect_args={"prepared_statement_cache_size": 0, "statement_cache_size": 0},
    )
    yield eng
    eng.sync_engine.dispose()


@pytest.fixture(scope="function")
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    async with engine.connect() as conn:
        await conn.begin()
        async_session = async_sessionmaker(
            bind=conn, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session() as session:
            yield session
        await conn.rollback()


@pytest.fixture(scope="function")
async def client(db_session) -> AsyncGenerator:
    from httpx import AsyncClient, ASGITransport
    from src import app
    from src.core.database import get_db
    from src.shared.api.dependencies import get_uow
    from src.shared.adapters.uow import SQLAlchemyUoWAdapter

    app.dependency_overrides[get_db] = lambda: db_session

    async def override_get_uow():
        class TestUnitOfWork(SQLAlchemyUoWAdapter):
            def __init__(self):
                self._session = db_session

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                # Don't close session, db_session fixture handles it.
                assert self._session is not None
                if exc_type:
                    await self._session.rollback()
                else:
                    await self._session.commit()

        yield TestUnitOfWork()

    app.dependency_overrides[get_uow] = override_get_uow

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
