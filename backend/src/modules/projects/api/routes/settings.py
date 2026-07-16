from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.modules.auth.api.dependencies import require_role
from src.modules.auth.domain import UserIdentity
from src.modules.projects.api.dependencies import ProjectManagementUseCaseDep
from src.modules.projects.api.schemas import (
    ProjectEnvUpdateReq,
    ProjectFrontendUrlUpdateReq,
    ProjectNameUpdateReq,
    ProjectOauthUpdateReq,
    ProjectOriginsUpdateReq,
    ProjectReadRes,
    ProjectRes,
)
from src.shared.adapters.uow import SQLAlchemyUnitOfWork, get_uow

router = APIRouter()


@router.put("/{project_id}/oauth", response_model=ProjectReadRes)
async def update_project_oauth(
    project_id: UUID,
    req: ProjectOauthUpdateReq,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: ProjectManagementUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role("TENANT"))],
):
    """Update OAuth configuration (client_id, client_secret) for a project."""
    async with uow:
        incoming_config = req.model_dump()["oauth_config"]
        project = await usecase.update_oauth(
            uow.session, project_id, user.id, incoming_config
        )
    return ProjectReadRes.model_validate(project)


@router.put("/{project_id}/origins", response_model=ProjectReadRes)
async def update_project_origins(
    project_id: UUID,
    req: ProjectOriginsUpdateReq,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: ProjectManagementUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role("TENANT"))],
):
    """Update CORS allowed origins for a project."""
    async with uow:
        project = await usecase.update_origins(
            uow.session, project_id, user.id, req.allowed_origins
        )
    return ProjectReadRes.model_validate(project)


@router.put("/{project_id}/environment", response_model=ProjectRes)
async def update_project_environment(
    project_id: UUID,
    req: ProjectEnvUpdateReq,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: ProjectManagementUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role("TENANT"))],
):
    """Update environment mode for a project."""
    async with uow:
        project = await usecase.update_environment(
            uow.session, project_id, user.id, req.environment
        )
    return ProjectRes.model_validate(project)


@router.put("/{project_id}/frontend-url", response_model=ProjectRes)
async def update_project_frontend_url(
    project_id: UUID,
    req: ProjectFrontendUrlUpdateReq,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: ProjectManagementUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role("TENANT"))],
):
    """Update frontend URL for a project."""
    async with uow:
        project = await usecase.update_frontend_url(
            uow.session, project_id, user.id, req.frontend_url
        )
    return ProjectRes.model_validate(project)


@router.put("/{project_id}/name", response_model=ProjectRes)
async def update_project_name(
    project_id: UUID,
    req: ProjectNameUpdateReq,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: ProjectManagementUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role("TENANT"))],
):
    """Update name for a project."""
    async with uow:
        project = await usecase.update_name(uow.session, project_id, user.id, req.name)
    return ProjectRes.model_validate(project)
