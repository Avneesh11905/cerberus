"""
Provides global FastAPI dependencies.
Includes components like the Redis-based rate limiter (SlowAPI), which protects all endpoints from abuse,
and common pagination or sorting extractors used across multiple domains.
"""

from fastapi import Request, Depends
from typing import Annotated

from src.shared.application.ports import CachePort, UoWPort
from src.shared.adapters import SQLAlchemyUoWAdapter


def get_is_challenged(request: Request) -> bool:
    return getattr(request.state, "is_challenged", False)


def get_cache_adapter() -> CachePort:
    from src.core.container import app_container

    return app_container.cache_adapter


async def get_uow():
    """FastAPI dependency to inject the Unit of Work."""
    yield SQLAlchemyUoWAdapter()


CacheAdapterDep = Annotated[CachePort, Depends(get_cache_adapter)]

UnitOfWorkDeps = Annotated[UoWPort, Depends(get_uow)]

IsChallengedDep = Annotated[bool, Depends(get_is_challenged)]
