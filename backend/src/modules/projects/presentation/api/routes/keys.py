from uuid import UUID

from fastapi import APIRouter

from src.modules.authorization.presentation.api.dependencies.roles import (
    RequireTenantRoleDep,
)
from src.modules.projects.application.commands.project_commands import (
    RotateApiKeyCommand,
    RotateJwtSecretCommand,
)
from src.modules.projects.application.queries.project_queries import (
    GetProjectPublicCredentialsQuery,
)
from src.modules.projects.presentation.api.schemas import (
    ProjectRotateApiKeyRes,
    ProjectRotateRsaKeysRes,
    ProjectSecretsRes,
)
from src.modules.projects.wiring import (
    GetProjectPublicCredentialsUseCaseDep,
    RotateApiKeyUseCaseDep,
    RotateJwtSecretUseCaseDep,
)
from src.shared.presentation.api.dependencies import CacheAdapterDep

router = APIRouter()


@router.get("/{project_id}/secrets", response_model=ProjectSecretsRes)
async def get_project_secrets(
    project_id: UUID,
    usecase: GetProjectPublicCredentialsUseCaseDep,
    user: RequireTenantRoleDep,
):
    """
    Returns the RSA public key for the project.
    Note: The plaintext API key cannot be retrieved again, and the hash is no longer exposed.
    """
    dto = await usecase.execute(
        GetProjectPublicCredentialsQuery(project_id=project_id, user_id=user.id),
    )
    public_key = dto.public_key

    return ProjectSecretsRes(
        public_key=public_key,
    )


@router.post("/{project_id}/keys/rotate-api-key", response_model=ProjectRotateApiKeyRes)
async def rotate_project_api_key(
    project_id: UUID,
    usecase: RotateApiKeyUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Rotates the API key, invalidating the old one immediately."""
    dto = await usecase.execute(
        RotateApiKeyCommand(project_id=project_id, user_id=user.id)
    )
    api_key = dto.api_key_plaintext
    return ProjectRotateApiKeyRes(api_key=api_key)


@router.post(
    "/{project_id}/keys/rotate-jwt-secret", response_model=ProjectRotateRsaKeysRes
)
async def rotate_project_jwt_secret(
    project_id: UUID,
    usecase: RotateJwtSecretUseCaseDep,
    cache: CacheAdapterDep,
    user: RequireTenantRoleDep,
):
    """
    Rotates the RSA keys, invalidating the old ones immediately.
    Note: Rotation immediately invalidates all active access tokens for the project.
    """
    dto = await usecase.execute(
        RotateJwtSecretCommand(project_id=project_id, user_id=user.id)
    )
    public_key = dto.public_pem
    await cache.delete_key(f"project_public_key:{project_id}")
    return ProjectRotateRsaKeysRes(public_key=public_key)
