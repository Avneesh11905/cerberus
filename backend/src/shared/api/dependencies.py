"""
Provides global FastAPI dependencies.
Includes components like the Redis-based rate limiter (SlowAPI), which protects all endpoints from abuse,
and common pagination or sorting extractors used across multiple domains.
"""

from fastapi import Request

from src.shared.application.ports.cache import CachePort


def get_is_challenged(request: Request) -> bool:
    return getattr(request.state, "is_challenged", False)


def get_cache_adapter() -> CachePort:
    from src.core.container import app_container

    return app_container.cache_adapter
