from uuid import UUID

from fastapi import APIRouter

from src.modules.auth.authorization.api.dependencies.roles import RequireTenantRoleDep
from src.modules.projects.api.dependencies import (
    UpdateOauthUseCaseDep,
    UpdateOriginsUseCaseDep,
    UpdateEnvironmentUseCaseDep,
    UpdateFrontendUrlUseCaseDep,
    UpdateNameUseCaseDep,
    GetProjectClaimsUseCaseDep,
    UpdateProjectClaimsUseCaseDep,
)
from src.modules.projects.api.schemas import (
    ProjectEnvUpdateReq,
    ProjectFrontendUrlUpdateReq,
    ProjectNameUpdateReq,
    ProjectOauthUpdateReq,
    ProjectOriginsUpdateReq,
    ProjectReadRes,
    ProjectRes,
    ProjectDefaultClaimsReq,
    ProjectDefaultClaimsRes,
)
from src.shared.api.dependencies import UnitOfWorkDeps

router = APIRouter()


@router.put("/{project_id}/oauth", response_model=ProjectReadRes)
async def update_project_oauth(
    project_id: UUID,
    req: ProjectOauthUpdateReq,
    uow: UnitOfWorkDeps,
    usecase: UpdateOauthUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Update OAuth configuration (client_id, client_secret) for a project."""
    async with uow:
        incoming_config = req.model_dump()["oauth_config"]
        project = await usecase.execute(
            uow.session, project_id, user.id, incoming_config
        )
    return ProjectReadRes.model_validate(project)


@router.put("/{project_id}/origins", response_model=ProjectReadRes)
async def update_project_origins(
    project_id: UUID,
    req: ProjectOriginsUpdateReq,
    uow: UnitOfWorkDeps,
    usecase: UpdateOriginsUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Update CORS allowed origins for a project."""
    async with uow:
        project = await usecase.execute(
            uow.session, project_id, user.id, req.allowed_origins
        )
    return ProjectReadRes.model_validate(project)


@router.put("/{project_id}/environment", response_model=ProjectRes)
async def update_project_environment(
    project_id: UUID,
    req: ProjectEnvUpdateReq,
    uow: UnitOfWorkDeps,
    usecase: UpdateEnvironmentUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Update environment mode for a project."""
    async with uow:
        project = await usecase.execute(
            uow.session, project_id, user.id, req.environment
        )
    return ProjectRes.model_validate(project)


@router.put("/{project_id}/frontend-url", response_model=ProjectRes)
async def update_project_frontend_url(
    project_id: UUID,
    req: ProjectFrontendUrlUpdateReq,
    uow: UnitOfWorkDeps,
    usecase: UpdateFrontendUrlUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Update frontend URL for a project."""
    async with uow:
        project = await usecase.execute(
            uow.session, project_id, user.id, req.frontend_url
        )
    return ProjectRes.model_validate(project)


@router.put("/{project_id}/name", response_model=ProjectRes)
async def update_project_name(
    project_id: UUID,
    req: ProjectNameUpdateReq,
    uow: UnitOfWorkDeps,
    usecase: UpdateNameUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Update name for a project."""
    async with uow:
        project = await usecase.execute(uow.session, project_id, user.id, req.name)
    return ProjectRes.model_validate(project)


@router.get("/{project_id}/claims", response_model=ProjectDefaultClaimsRes)
async def get_project_claims(
    project_id: UUID,
    uow: UnitOfWorkDeps,
    usecase: GetProjectClaimsUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Get default custom claims schema for a project."""
    async with uow:
        claims = await usecase.execute(uow.session, project_id, user.id)
    return ProjectDefaultClaimsRes(project_id=project_id, default_claims=claims)


@router.put("/{project_id}/claims", response_model=ProjectDefaultClaimsRes)
async def update_project_claims(
    project_id: UUID,
    req: ProjectDefaultClaimsReq,
    uow: UnitOfWorkDeps,
    usecase: UpdateProjectClaimsUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Update default custom claims schema for a project."""
    async with uow:
        project = await usecase.execute(uow.session, project_id, user.id, req.claims)
    return ProjectDefaultClaimsRes(
        project_id=project_id, default_claims=project.default_claims
    )
