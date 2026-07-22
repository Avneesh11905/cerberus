"""
Provides global FastAPI dependencies.
Includes components like the Redis-based rate limiter (SlowAPI), which protects all endpoints from abuse,
and common pagination or sorting extractors used across multiple domains.
"""

from typing import Annotated

from fastapi import Depends, Request

from src.core.container import app_container
from src.shared.application.ports.cache import CachePort
from src.shared.application.ports.shared_unit_of_work import UoWPort
from src.shared.infrastructure.adapters.shared_uow import SQLAlchemyUoWAdapter


def get_is_challenged(request: Request) -> bool:
    return getattr(request.state, "is_challenged", False)


IsChallengedDep = Annotated[bool, Depends(get_is_challenged)]


def get_cache_adapter() -> CachePort:
    return app_container.cache_adapter


CacheAdapterDep = Annotated[CachePort, Depends(get_cache_adapter)]


async def get_uow():
    """FastAPI dependency to inject the Unit of Work."""
    yield SQLAlchemyUoWAdapter()


UnitOfWorkDeps = Annotated[UoWPort, Depends(get_uow)]
