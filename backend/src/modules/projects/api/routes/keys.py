from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.modules.auth.authorization.api.dependencies.roles import require_role
from src.modules.auth.authorization.domain.enums import GlobalRole
from src.modules.auth.authentication.api.dependencies.core import get_cache_adapter
from src.modules.auth.authentication.domain.entities import UserIdentity
from src.modules.projects.api.dependencies import (
    GetProjectPublicCredentialsUseCaseDep,
    RotateApiKeyUseCaseDep,
    RotateJwtSecretUseCaseDep,
)
from src.modules.projects.api.schemas import (
    ProjectRotateApiKeyRes,
    ProjectRotateRsaKeysRes,
    ProjectSecretsRes,
)
from src.shared.api.dependencies import UnitOfWorkDeps
from src.shared.application.ports import CachePort

router = APIRouter()


@router.get("/{project_id}/secrets", response_model=ProjectSecretsRes)
async def get_project_secrets(
    project_id: UUID,
    uow: UnitOfWorkDeps,
    usecase: GetProjectPublicCredentialsUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role(GlobalRole.TENANT))],
):
    """
    Returns the RSA public key for the project.
    Note: The plaintext API key cannot be retrieved again, and the hash is no longer exposed.
    """
    async with uow:
        _, public_key = await usecase.execute(uow.session, project_id, user.id)

    return ProjectSecretsRes(
        public_key=public_key,
    )


@router.post("/{project_id}/keys/rotate-api-key", response_model=ProjectRotateApiKeyRes)
async def rotate_project_api_key(
    project_id: UUID,
    uow: UnitOfWorkDeps,
    usecase: RotateApiKeyUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role(GlobalRole.TENANT))],
):
    """Rotates the API key, invalidating the old one immediately."""
    async with uow:
        api_key = await usecase.execute(uow.session, project_id, user.id)
    return ProjectRotateApiKeyRes(api_key=api_key)


@router.post(
    "/{project_id}/keys/rotate-jwt-secret", response_model=ProjectRotateRsaKeysRes
)
async def rotate_project_jwt_secret(
    project_id: UUID,
    uow: UnitOfWorkDeps,
    usecase: RotateJwtSecretUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role(GlobalRole.TENANT))],
    cache: Annotated[CachePort, Depends(get_cache_adapter)],
):
    """
    Rotates the RSA keys, invalidating the old ones immediately.
    Note: Rotation immediately invalidates all active access tokens for the project.
    """
    async with uow:
        public_key = await usecase.execute(uow.session, project_id, user.id)
    await cache.delete_key(f"project_public_key:{project_id}")
    return ProjectRotateRsaKeysRes(public_key=public_key)
