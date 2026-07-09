"""
Provides global FastAPI dependencies.
Includes components like the Redis-based rate limiter (SlowAPI), which protects all endpoints from abuse,
and common pagination or sorting extractors used across multiple domains.
"""

import hashlib
from typing import Annotated, Any, Callable, Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request
from slowapi import Limiter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.core.ports.cache import CachePort

from src.shared.config import app_settings, database_settings
from src.shared.infrastructure.sql.connection import get_db
from src.shared.infrastructure.sql.tables import Project


def get_client_ip(request: Request) -> str:
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        return cf_ip.strip()
    return request.client.host if request.client else "127.0.0.1"


class DynamicLimiter(Limiter):
    def _check_request_limit(
        self,
        request: Request,
        endpoint_func: Optional[Callable[..., Any]],
        in_middleware: bool = True,
    ) -> None:
        # Development Bypass: Check if the project is in "development" mode
        project_id = request.path_params.get("project_id")
        if project_id:
            environments = getattr(request.app.state, "project_environments", {})
            if environments.get(project_id) == "development":
                return  # Bypass rate limiting for development projects!

        super()._check_request_limit(request, endpoint_func, in_middleware)


limiter = DynamicLimiter(
    key_func=get_client_ip,
    storage_uri=database_settings.CACHE_URL,
    enabled=(app_settings.ENV != "development"),
)


def hash_api_key(api_key: str) -> str:
    """Uses SHA-256 for fast, deterministic API key hashing to allow quick DB lookups."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def get_cache_adapter() -> CachePort:
    from src.shared.container import shared_container
    return shared_container.cache_adapter


async def get_project_id_from_api_key(
    x_cerberus_api_key: Annotated[
        str | None, Header(alias="X-Cerberus-API-Key")
    ] = None,
    db: AsyncSession = Depends(get_db),
    cache_adapter: CachePort = Depends(get_cache_adapter),
) -> UUID | None:
    """
    Dependency that extracts the API key from headers, hashes it, and returns the project ID.
    Returns None if no key is provided (e.g., for requests to the global dashboard).
    Raises 401 if the key is provided but invalid.
    """
    if not x_cerberus_api_key:
        return None

    api_key_hash = hash_api_key(x_cerberus_api_key)
    cache_key = f"api_key_hash:{api_key_hash}"
    cached_project_id = await cache_adapter.get_string(cache_key)

    if cached_project_id:
        return UUID(cached_project_id)

    result = await db.execute(
        select(Project.id).where(Project.api_key_hash == api_key_hash)
    )
    project_id = result.scalar_one_or_none()

    if not project_id:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    await cache_adapter.set_string(cache_key, str(project_id), ttl=600)
    return project_id
