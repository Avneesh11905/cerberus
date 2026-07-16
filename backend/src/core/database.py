"""
Manages the global SQLAlchemy asynchronous engine and session maker.
Provides the `get_db` dependency used to inject database sessions into the API routes.
"""

import sys

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from src.core.config import database_settings


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 declarative base for all ORM models."""


is_celery = "celery" in sys.argv[0] or "celery" in sys.modules

if is_celery:
    engine = create_async_engine(
        database_settings.PGSQL_URL,
        echo=False,
        future=True,
        poolclass=NullPool,
    )
else:
    engine = create_async_engine(
        database_settings.PGSQL_URL,
        echo=False,
        future=True,
        pool_size=20,
        max_overflow=10,
        pool_pre_ping=True,
    )

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
