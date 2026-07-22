import hashlib
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request, status

from src.modules.authentication.application.ports import AuthUoWPort
from src.modules.authentication.presentation.api.dependencies.authentication_uow_dep import (
    get_auth_uow,
)
from src.shared.presentation.api.dependencies import CacheAdapterDep


async def get_optional_project_id(
    request: Request,
    cache_adapter: CacheAdapterDep,
    uow: Annotated[AuthUoWPort, Depends(get_auth_uow)],
    api_key: Annotated[str | None, Header(alias="X-Cerberus-API-Key")] = None,
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

        async with uow:
            project = await uow.project_query_repo.get_by_api_key_hash(key_hash)
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


OptionalProjectIdDep = Annotated[UUID | None, Depends(get_optional_project_id)]
RequiredProjectIdDep = Annotated[UUID, Depends(get_required_project_id)]
