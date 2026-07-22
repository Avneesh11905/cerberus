import os
from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer  # type: ignore[import-untyped]
from testcontainers.redis import RedisContainer  # type: ignore[import-untyped]

# Setup testcontainers at the session scope
# Note: we run this at session scope and yield, but we need to patch os.environ BEFORE
# any other src modules are imported that might instantiate singletons.
# However, pytest-dotenv might already load tests/.env.test.
# To ensure our dynamic URLs are used, we dynamically update os.environ and pydantic settings.


@pytest.fixture(scope="session")
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
        if "?" in pg_url_asyncpg:
            pg_url_asyncpg += "&ssl=disable"
        else:
            pg_url_asyncpg += "?ssl=disable"

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
        from src.core.config import get_settings

        get_settings().database.PGSQL_URL = pg_url_asyncpg
        get_settings().database.CACHE_URL = f"{redis_base}/0"
        get_settings().database.CELERY_BROKER_URL = f"{redis_base}/0"
        get_settings().database.CELERY_RESULT_URL = f"{redis_base}/0"

        # Explicitly patch Celery app to prevent using cached URLs
        from src.core.celery_app import celery_app

        celery_app.conf.broker_url = f"{redis_base}/0"
        celery_app.conf.result_backend = f"{redis_base}/0"

        # Update the existing cache adapter's redis client in-place so that existing references
        # (e.g. in FastAPI middleware built during test collection) point to the new testcontainer Redis.
        from redis.asyncio import Redis

        from src.core.container import app_container

        new_redis = Redis.from_url(
            get_settings().database.CACHE_URL, decode_responses=True
        )
        app_container.cache_adapter._client = new_redis

        # Run Alembic migrations programmatically
        import subprocess

        env = os.environ.copy()
        env["PGSQL_URL"] = pg_url_asyncpg

        # Run alembic in a subprocess to avoid asyncio.run() clashes with Pytest's event loop
        result = subprocess.run(
            ["uv", "run", "alembic", "upgrade", "head"],
            env=env,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Alembic migration failed:\n{result.stderr}\n{result.stdout}"
            )

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
    from httpx import ASGITransport, AsyncClient

    from src import app
    from src.core.database import get_db
    from src.modules.analytics.presentation.api.dependencies.analytics_uow_dep import (
        get_analytics_uow,
    )
    from src.modules.authentication.presentation.api.dependencies.authentication_uow_dep import (
        get_auth_uow,
    )
    from src.modules.projects.presentation.api.dependencies.projects_uow_dep import (
        get_project_uow,
    )
    from src.modules.superadmin.presentation.api.dependencies.superadmin_uow_dep import (
        get_superadmin_uow,
    )
    from src.modules.users.presentation.api.dependencies.users_uow_dep import (
        get_user_uow,
    )
    from src.shared.infrastructure.adapters.shared_uow import SQLAlchemyUoWAdapter
    from src.shared.presentation.api.dependencies import get_uow

    app.dependency_overrides[get_db] = lambda: db_session

    async def override_get_uow():
        from unittest.mock import MagicMock

        from src.modules.authentication.infrastructure.database.repositories.refresh_token_repository import (
            DBRefreshTokenRepositoryAdapter,
        )
        from src.modules.authentication.infrastructure.database.repositories.sql_user_command_repository import (
            SQLUserCommandRepositoryAdapter,
        )
        from src.modules.authentication.infrastructure.database.repositories.sql_user_maintenance_repository import (
            SQLUserMaintenanceRepositoryAdapter,
        )
        from src.modules.authentication.infrastructure.database.repositories.sql_user_query_repository import (
            SQLUserQueryRepositoryAdapter,
        )
        from src.modules.projects.infrastructure.database.repositories.project_command_repository import (
            SQLProjectCommandRepositoryAdapter,
        )
        from src.modules.projects.infrastructure.database.repositories.project_query_repository import (
            SQLProjectQueryRepositoryAdapter,
        )
        from src.modules.projects.infrastructure.database.repositories.project_user_repository import (
            SQLProjectUserRepositoryAdapter,
        )
        from src.modules.superadmin.infrastructure.database.repositories.system_analytics_repository import (
            SQLSystemAnalyticsRepositoryAdapter,
        )
        from src.modules.superadmin.infrastructure.database.repositories.system_log_repository import (
            SQLSystemLogRepositoryAdapter,
        )
        from src.modules.superadmin.infrastructure.database.repositories.tenant_repository import (
            SQLTenantRepositoryAdapter,
        )
        from src.modules.users.infrastructure.database.repositories.user_profile_repository import (
            SQLUserProfileRepositoryAdapter,
        )
        from src.shared.application.ports.encryption import EncryptionPort

        class TestUnitOfWork(SQLAlchemyUoWAdapter):
            def __init__(self):
                self._session = db_session
                self.cache = MagicMock()
                self.encryption_adapter = MagicMock(spec=EncryptionPort)

            async def __aenter__(self):
                # Init all repos
                self.user_query_repo = SQLUserQueryRepositoryAdapter(self.session)
                self.user_command_repo = SQLUserCommandRepositoryAdapter(self.session)
                self.user_maintenance_repo = SQLUserMaintenanceRepositoryAdapter(
                    self.session
                )
                self.refresh_token_repo = DBRefreshTokenRepositoryAdapter(
                    self.session, 7, self.cache
                )
                self.project_query_repo = SQLProjectQueryRepositoryAdapter(
                    self.session, self.encryption_adapter
                )
                self.project_command_repo = SQLProjectCommandRepositoryAdapter(
                    self.session, self.encryption_adapter
                )
                self.project_user_repo = SQLProjectUserRepositoryAdapter(self.session)
                self.tenant_repo = SQLTenantRepositoryAdapter(self.session)
                self.log_repo = SQLSystemLogRepositoryAdapter(self.session)
                self.system_analytics_repo = SQLSystemAnalyticsRepositoryAdapter(
                    self.session
                )
                self.analytics_repo = self.system_analytics_repo
                self.profile_repo = SQLUserProfileRepositoryAdapter(
                    self.session, self.refresh_token_repo
                )
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                assert self._session is not None
                if exc_type:
                    await self._session.rollback()
                else:
                    await self._session.commit()

        yield TestUnitOfWork()

    app.dependency_overrides[get_auth_uow] = override_get_uow
    app.dependency_overrides[get_project_uow] = override_get_uow
    app.dependency_overrides[get_superadmin_uow] = override_get_uow
    app.dependency_overrides[get_analytics_uow] = override_get_uow
    app.dependency_overrides[get_user_uow] = override_get_uow
    if get_uow in app.dependency_overrides:
        app.dependency_overrides[get_uow] = override_get_uow
    else:
        app.dependency_overrides[get_uow] = override_get_uow

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
