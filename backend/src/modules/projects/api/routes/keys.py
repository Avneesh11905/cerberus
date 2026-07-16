from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.modules.auth.api.dependencies import get_cache_adapter, require_role
from src.modules.auth.domain import UserIdentity
from src.modules.projects.api.dependencies import ProjectManagementUseCaseDep
from src.modules.projects.api.schemas import (
    ProjectRotateApiKeyRes,
    ProjectRotateRsaKeysRes,
    ProjectSecretsRes,
)
from src.shared.adapters.uow import SQLAlchemyUnitOfWork, get_uow
from src.shared.application.ports.cache import CachePort

router = APIRouter()


@router.get("/{project_id}/secrets", response_model=ProjectSecretsRes)
async def get_project_secrets(
    project_id: UUID,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: ProjectManagementUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role("TENANT"))],
):
    """
    Returns the RSA public key for the project.
    Note: The plaintext API key cannot be retrieved again, and the hash is no longer exposed.
    """
    async with uow:
        api_key_hash, public_key = await usecase.get_secrets(
            uow.session, project_id, user.id
        )

    return ProjectSecretsRes(
        public_key=public_key,
    )


@router.post("/{project_id}/keys/rotate-api-key", response_model=ProjectRotateApiKeyRes)
async def rotate_project_api_key(
    project_id: UUID,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: ProjectManagementUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role("TENANT"))],
):
    """Rotates the API key, invalidating the old one immediately."""
    async with uow:
        api_key = await usecase.rotate_api_key(uow.session, project_id, user.id)
    return ProjectRotateApiKeyRes(api_key=api_key)


@router.post(
    "/{project_id}/keys/rotate-jwt-secret", response_model=ProjectRotateRsaKeysRes
)
async def rotate_project_jwt_secret(
    project_id: UUID,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: ProjectManagementUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role("TENANT"))],
    cache: Annotated[CachePort, Depends(get_cache_adapter)],
):
    """
    Rotates the RSA keys, invalidating the old ones immediately.
    Note: Rotation immediately invalidates all active access tokens for the project.
    """
    async with uow:
        public_key = await usecase.rotate_jwt_secret(uow.session, project_id, user.id)
    await cache.delete_key(f"project_public_key:{project_id}")
    return ProjectRotateRsaKeysRes(public_key=public_key)
