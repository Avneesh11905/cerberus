from uuid import UUID

from fastapi import APIRouter

from src.modules.authorization.presentation.api.dependencies.roles import (
    RequireTenantRoleDep,
)
from src.modules.projects.application.commands.project_commands import (
    UpdateEnvironmentCommand,
    UpdateFrontendUrlCommand,
    UpdateNameCommand,
    UpdateOauthCommand,
    UpdateOriginsCommand,
    UpdateProjectClaimsCommand,
)
from src.modules.projects.application.queries.project_queries import (
    GetProjectClaimsQuery,
)
from src.modules.projects.presentation.api.schemas import (
    ProjectDefaultClaimsReq,
    ProjectDefaultClaimsRes,
    ProjectEnvUpdateReq,
    ProjectFrontendUrlUpdateReq,
    ProjectNameUpdateReq,
    ProjectOauthUpdateReq,
    ProjectOriginsUpdateReq,
    ProjectReadRes,
    ProjectRes,
)
from src.modules.projects.wiring import (
    GetProjectClaimsUseCaseDep,
    UpdateEnvironmentUseCaseDep,
    UpdateFrontendUrlUseCaseDep,
    UpdateNameUseCaseDep,
    UpdateOauthUseCaseDep,
    UpdateOriginsUseCaseDep,
    UpdateProjectClaimsUseCaseDep,
)

router = APIRouter()


@router.put("/{project_id}/oauth", response_model=ProjectReadRes)
async def update_project_oauth(
    project_id: UUID,
    req: ProjectOauthUpdateReq,
    usecase: UpdateOauthUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Update OAuth configuration (client_id, client_secret) for a project."""
    incoming_config = req.model_dump()["oauth_config"]
    dto = await usecase.execute(
        UpdateOauthCommand(
            project_id=project_id, user_id=user.id, incoming_config=incoming_config
        ),
    )
    project = dto.project
    return ProjectReadRes.model_validate(project)


@router.put("/{project_id}/origins", response_model=ProjectReadRes)
async def update_project_origins(
    project_id: UUID,
    req: ProjectOriginsUpdateReq,
    usecase: UpdateOriginsUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Update CORS allowed origins for a project."""
    dto = await usecase.execute(
        UpdateOriginsCommand(
            project_id=project_id,
            user_id=user.id,
            allowed_origins=req.allowed_origins,
        ),
    )
    project = dto.project
    return ProjectReadRes.model_validate(project)


@router.put("/{project_id}/environment", response_model=ProjectRes)
async def update_project_environment(
    project_id: UUID,
    req: ProjectEnvUpdateReq,
    usecase: UpdateEnvironmentUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Update environment mode for a project."""
    dto = await usecase.execute(
        UpdateEnvironmentCommand(
            project_id=project_id, user_id=user.id, environment=req.environment
        ),
    )
    project = dto.project
    return ProjectRes.model_validate(project)


@router.put("/{project_id}/frontend-url", response_model=ProjectRes)
async def update_project_frontend_url(
    project_id: UUID,
    req: ProjectFrontendUrlUpdateReq,
    usecase: UpdateFrontendUrlUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Update frontend URL for a project."""
    dto = await usecase.execute(
        UpdateFrontendUrlCommand(
            project_id=project_id, user_id=user.id, frontend_url=req.frontend_url
        ),
    )
    project = dto.project
    return ProjectRes.model_validate(project)


@router.put("/{project_id}/name", response_model=ProjectRes)
async def update_project_name(
    project_id: UUID,
    req: ProjectNameUpdateReq,
    usecase: UpdateNameUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Update name for a project."""
    dto = await usecase.execute(
        UpdateNameCommand(project_id=project_id, user_id=user.id, name=req.name),
    )
    project = dto.project
    return ProjectRes.model_validate(project)


@router.get("/{project_id}/claims", response_model=ProjectDefaultClaimsRes)
async def get_project_claims(
    project_id: UUID,
    usecase: GetProjectClaimsUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Get default custom claims schema for a project."""
    dto = await usecase.execute(
        GetProjectClaimsQuery(project_id=project_id, user_id=user.id)
    )
    claims = dto.claims
    return ProjectDefaultClaimsRes(project_id=project_id, default_claims=claims)


@router.put("/{project_id}/claims", response_model=ProjectDefaultClaimsRes)
async def update_project_claims(
    project_id: UUID,
    req: ProjectDefaultClaimsReq,
    usecase: UpdateProjectClaimsUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Update default custom claims schema for a project."""
    dto = await usecase.execute(
        UpdateProjectClaimsCommand(
            project_id=project_id, user_id=user.id, default_claims=req.claims
        ),
    )
    project = dto.project
    return ProjectDefaultClaimsRes(
        project_id=project_id, default_claims=project.default_claims or {}
    )
