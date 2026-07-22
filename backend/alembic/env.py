import asyncio
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Load the env variables BEFORE importing any Pydantic settings globally
load_dotenv(".env.local")

# Import settings and metadata
import src.core.models  # noqa: F401, E402
import src.modules.analytics.infrastructure.models  # noqa: F401, E402
import src.modules.authentication.infrastructure.models  # noqa: F401, E402
import src.modules.projects.infrastructure.models  # noqa: F401, E402
import src.modules.superadmin.infrastructure.models  # noqa: F401, E402

# Import all models to ensure Alembic registers them for migrations
import src.modules.users.infrastructure.models  # noqa: F401, E402
from src.core.config import get_settings  # noqa: E402
from src.core.database import Base  # noqa: E402

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# Override the sqlalchemy.url with the one from our config.
# We use the ASYNC URL because we are going to use async_engine_from_config

# Escape the '%' symbol specifically for Alembic's configparser
alembic_url = get_settings().database.PGSQL_URL.replace("%", "%%")
config.set_main_option("sqlalchemy.url", alembic_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
