import hashlib
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.auth.api.dependencies.core import (
    get_cache_adapter,
    get_project_repository,
)
from src.modules.projects.application.ports import ProjectQueryRepositoryPort
from src.shared.application.ports import CachePort


async def get_optional_project_id(
    request: Request,
    api_key: Annotated[str | None, Header(alias="X-Cerberus-API-Key")] = None,
    db: AsyncSession = Depends(get_db),
    cache_adapter: CachePort = Depends(get_cache_adapter),
    project_repo: ProjectQueryRepositoryPort = Depends(get_project_repository),
) -> UUID | None:
    if api_key:
        if not api_key.startswith("cerb_"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API Key format",
            )

        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        cache_key = f"api_key_hash:{key_hash}"
        cached_project_id = await cache_adapter.get_string(cache_key)

        if cached_project_id:
            return UUID(cached_project_id)

        project = await project_repo.get_by_api_key_hash(db, key_hash)
        project_id = project.id if project else None

        if not project_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key"
            )

        await cache_adapter.set_string(cache_key, str(project_id), ttl=600)
        return project_id

    return None


async def get_required_project_id(
    project_id: Annotated[UUID | None, Depends(get_optional_project_id)],
) -> UUID:
    """Enforces that a Project API key was provided."""
    if not project_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Project API Key (X-Cerberus-API-Key header) is required.",
        )
    return project_id
