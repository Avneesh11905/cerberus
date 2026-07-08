from collections.abc import Mapping
from typing import Annotated
from urllib.parse import urlparse
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from uuid6 import uuid7

from src.authentication.api.dependencies import require_role
from src.authentication.core.domain import UserIdentity
from src.authentication.infrastructure.oauth import PROVIDER_METADATA
from src.projects.schemas import (
    OAuthProviderRes,
    ProjectCreateReq,
    ProjectCreateRes,
    ProjectEnvUpdateReq,
    ProjectFrontendUrlUpdateReq,
    ProjectNameUpdateReq,
    ProjectOauthUpdateReq,
    ProjectOriginsUpdateReq,
    ProjectReadRes,
    ProjectRes,
    ProjectRotateApiKeyRes,
    ProjectRotateRsaKeysRes,
    ProjectSecretsRes,
)
from src.shared.container import shared_container
from src.shared.infrastructure.sql.tables import Project
from src.shared.infrastructure.sql.uow import SQLAlchemyUnitOfWork, get_uow
from src.shared.utils.crypto import generate_api_key, generate_rsa_keypair, hash_api_key

projects_router = APIRouter(prefix="/projects", tags=["Projects"])


def _default_oauth_config() -> dict[str, dict[str, object]]:
    config: dict[str, dict[str, object]] = {"local": {"enabled": True}}
    for provider in PROVIDER_METADATA:
        config[provider] = {"enabled": False}
    return config


def _validate_oauth_provider_keys(oauth_config: Mapping[str, object]) -> None:
    allowed_keys = {"local", *PROVIDER_METADATA.keys()}
    unsupported = sorted(set(oauth_config) - allowed_keys)
    if unsupported:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported OAuth provider(s): {', '.join(unsupported)}",
        )


def _is_localhost(hostname: str | None) -> bool:
    return hostname in {"localhost", "127.0.0.1", "::1"}


def _normalize_origin(origin: str, environment: str) -> str:
    parsed = urlparse(origin.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise HTTPException(
            status_code=400, detail="Allowed origins must be absolute http(s) origins"
        )

    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise HTTPException(
            status_code=400,
            detail="Allowed origins must not include path, query, or fragment",
        )

    if (
        environment == "production"
        and parsed.scheme != "https"
        and not _is_localhost(parsed.hostname)
    ):
        raise HTTPException(status_code=400, detail="Production origins must use HTTPS")

    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


def _validate_frontend_url(frontend_url: str, environment: str) -> str:
    parsed = urlparse(frontend_url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise HTTPException(
            status_code=400, detail="Frontend URL must be an absolute http(s) URL"
        )

    if parsed.query or parsed.fragment:
        raise HTTPException(
            status_code=400, detail="Frontend URL must not include query or fragment"
        )

    if (
        environment == "production"
        and parsed.scheme != "https"
        and not _is_localhost(parsed.hostname)
    ):
        raise HTTPException(
            status_code=400, detail="Production frontend URL must use HTTPS"
        )

    return frontend_url.strip().rstrip("/")


def _origin_from_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


@projects_router.post("/", response_model=ProjectCreateRes)
async def create_project(
    req: ProjectCreateReq,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    user: Annotated[UserIdentity, Depends(require_role("tenant"))],
):
    """Create a new project. Returns the API key and RSA keys plaintext exactly ONCE."""
    project_id = uuid7()
    api_key = generate_api_key(project_id)
    hashed_api_key = hash_api_key(api_key)
    private_pem, public_pem = generate_rsa_keypair()

    project = Project(
        id=project_id,
        tenant_id=user.id,
        name=req.name,
        private_key=shared_container.encryption_adapter.encrypt(private_pem),
        public_key=public_pem,
        api_key_hash=hashed_api_key,
        oauth_config=_default_oauth_config(),
    )

    async with uow:
        uow.session.add(project)
        await uow.session.flush()
        await uow.session.refresh(project)

    return ProjectCreateRes(
        id=project.id,
        name=project.name,
        api_key=api_key,
        public_key=project.public_key,
        created_at=project.created_at,
    )


@projects_router.get("/oauth-providers", response_model=list[OAuthProviderRes])
async def list_oauth_providers(
    user: Annotated[UserIdentity, Depends(require_role("tenant"))],
):
    """Return registered OAuth providers and required config fields."""
    return [
        OAuthProviderRes(
            key=metadata.key,
            display_name=metadata.display_name,
            scopes=metadata.scopes,
            required_fields=metadata.required_fields,
        )
        for metadata in sorted(
            PROVIDER_METADATA.values(), key=lambda item: item.display_name
        )
    ]


@projects_router.get("/", response_model=list[ProjectReadRes])
async def list_projects(
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    user: Annotated[UserIdentity, Depends(require_role("tenant"))],
):
    """List all projects for the current tenant."""
    async with uow:
        result = await uow.session.execute(
            select(Project).where(Project.tenant_id == user.id)
        )
        projects = result.scalars().all()
    return projects


@projects_router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: UUID,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    user: Annotated[UserIdentity, Depends(require_role("tenant"))],
):
    """Delete a project and cascade delete all its end-users."""
    async with uow:
        result = await uow.session.execute(
            select(Project).where(
                Project.id == project_id, Project.tenant_id == user.id
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        await uow.session.delete(project)
    return


@projects_router.put("/{project_id}/oauth", response_model=ProjectReadRes)
async def update_project_oauth(
    project_id: UUID,
    req: ProjectOauthUpdateReq,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    user: Annotated[UserIdentity, Depends(require_role("tenant"))],
):
    """Update OAuth configuration (client_id, client_secret) for a project."""
    async with uow:
        result = await uow.session.execute(
            select(Project).where(
                Project.id == project_id, Project.tenant_id == user.id
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        incoming_config = {
            provider: provider_config.model_dump()
            for provider, provider_config in req.oauth_config.items()
        }
        _validate_oauth_provider_keys(incoming_config)
        existing_config = project.oauth_config or {}

        for provider, provider_config in incoming_config.items():
            if (
                isinstance(provider_config, dict)
                and not provider_config.get("client_secret")
                and isinstance(existing_config.get(provider), dict)
                and existing_config[provider].get("client_secret")
            ):
                provider_config["client_secret"] = existing_config[provider][
                    "client_secret"
                ]
            elif isinstance(provider_config, dict) and provider_config.get(
                "client_secret"
            ):
                provider_config["client_secret"] = (
                    shared_container.encryption_adapter.encrypt(
                        provider_config["client_secret"]
                    )
                )

        project.oauth_config = incoming_config
        await uow.session.flush()
        await uow.session.refresh(project)
    return project


@projects_router.put("/{project_id}/origins", response_model=ProjectReadRes)
async def update_project_origins(
    project_id: UUID,
    req: ProjectOriginsUpdateReq,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    user: Annotated[UserIdentity, Depends(require_role("tenant"))],
):
    """Update CORS allowed origins for a project."""
    async with uow:
        result = await uow.session.execute(
            select(Project).where(
                Project.id == project_id, Project.tenant_id == user.id
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        cleaned_origins = [
            _normalize_origin(origin, project.environment)
            for origin in req.allowed_origins
            if origin.strip()
        ]

        project.allowed_origins = cleaned_origins
        await uow.session.flush()
        await uow.session.refresh(project)
    return project


@projects_router.put("/{project_id}/environment", response_model=ProjectRes)
async def update_project_environment(
    project_id: UUID,
    req: ProjectEnvUpdateReq,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    user: Annotated[UserIdentity, Depends(require_role("tenant"))],
):
    """Update environment mode for a project."""
    async with uow:
        result = await uow.session.execute(
            select(Project).where(
                Project.id == project_id, Project.tenant_id == user.id
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        project.environment = req.environment
        await uow.session.flush()
        await uow.session.refresh(project)
    return project


@projects_router.put("/{project_id}/frontend-url", response_model=ProjectRes)
async def update_project_frontend_url(
    project_id: UUID,
    req: ProjectFrontendUrlUpdateReq,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    user: Annotated[UserIdentity, Depends(require_role("tenant"))],
):
    """Update frontend URL for a project."""
    async with uow:
        result = await uow.session.execute(
            select(Project).where(
                Project.id == project_id, Project.tenant_id == user.id
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        if req.frontend_url:
            frontend_url = _validate_frontend_url(req.frontend_url, project.environment)
            frontend_origin = _origin_from_url(frontend_url)
            allowed_origins = {
                origin.rstrip("/") for origin in (project.allowed_origins or [])
            }
            if allowed_origins and frontend_origin not in allowed_origins:
                raise HTTPException(
                    status_code=400,
                    detail="Frontend URL origin must be in allowed origins",
                )
            project.frontend_url = frontend_url
        else:
            project.frontend_url = None
        await uow.session.flush()
        await uow.session.refresh(project)
    return project


@projects_router.put("/{project_id}/name", response_model=ProjectRes)
async def update_project_name(
    project_id: UUID,
    req: ProjectNameUpdateReq,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    user: Annotated[UserIdentity, Depends(require_role("tenant"))],
):
    """Update name for a project."""
    async with uow:
        result = await uow.session.execute(
            select(Project).where(
                Project.id == project_id, Project.tenant_id == user.id
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        project.name = req.name
        await uow.session.flush()
        await uow.session.refresh(project)
    return project


@projects_router.get("/{project_id}/secrets", response_model=ProjectSecretsRes)
async def get_project_secrets(
    project_id: UUID,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    user: Annotated[UserIdentity, Depends(require_role("tenant"))],
):
    """
    Returns the hashed API key and RSA keys for backup.
    Note: The plaintext API key cannot be retrieved again, only the hash is stored.
    """
    async with uow:
        result = await uow.session.execute(
            select(Project).where(
                Project.id == project_id, Project.tenant_id == user.id
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

    return ProjectSecretsRes(
        api_key_hash=project.api_key_hash,
        public_key=project.public_key,
    )


@projects_router.post(
    "/{project_id}/keys/rotate-api-key", response_model=ProjectRotateApiKeyRes
)
async def rotate_project_api_key(
    project_id: UUID,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    user: Annotated[UserIdentity, Depends(require_role("tenant"))],
):
    """Rotates the API key, invalidating the old one immediately."""
    async with uow:
        result = await uow.session.execute(
            select(Project).where(
                Project.id == project_id, Project.tenant_id == user.id
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        api_key = generate_api_key(project.id)
        hashed_api_key = hash_api_key(api_key)

        project.api_key_hash = hashed_api_key

        await uow.session.flush()

    return ProjectRotateApiKeyRes(api_key=api_key)


@projects_router.post(
    "/{project_id}/keys/rotate-jwt-secret", response_model=ProjectRotateRsaKeysRes
)
async def rotate_project_jwt_secret(
    project_id: UUID,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    user: Annotated[UserIdentity, Depends(require_role("tenant"))],
):
    """
    Rotates the RSA keys, invalidating the old ones immediately.
    Note: Rotation immediately invalidates all active access tokens for the project.
    """
    async with uow:
        result = await uow.session.execute(
            select(Project).where(
                Project.id == project_id, Project.tenant_id == user.id
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        private_pem, public_pem = generate_rsa_keypair()

        project.private_key = shared_container.encryption_adapter.encrypt(private_pem)
        project.public_key = public_pem

        await uow.session.flush()

    return ProjectRotateRsaKeysRes(public_key=public_pem)
