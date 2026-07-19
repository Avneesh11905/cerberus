from uuid import UUID

from fastapi import APIRouter, status

from src.modules.auth.authorization.api.dependencies.roles import RequireTenantRoleDep
from src.modules.projects.api.dependencies import (
    CreateProjectUseCaseDep,
    ListProjectsUseCaseDep,
    GetProjectUseCaseDep,
    DeleteProjectUseCaseDep,
)
from src.modules.projects.api.schemas import (
    ProjectCreateReq,
    ProjectCreateRes,
    ProjectReadRes,
)
from src.shared.api.dependencies import UnitOfWorkDeps

router = APIRouter()


@router.post("/", response_model=ProjectCreateRes, status_code=status.HTTP_201_CREATED)
async def create_project(
    req: ProjectCreateReq,
    uow: UnitOfWorkDeps,
    usecase: CreateProjectUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Create a new Cerberus project."""
    async with uow:
        project, api_key, public_key = await usecase.execute(
            uow.session, user.id, req.name
        )
    return ProjectCreateRes(
        id=project.id,
        name=project.name,
        api_key=api_key,
        public_key=public_key,
        created_at=project.created_at,
    )


@router.get("/", response_model=list[ProjectReadRes])
async def list_projects(
    uow: UnitOfWorkDeps,
    usecase: ListProjectsUseCaseDep,
    user: RequireTenantRoleDep,
):
    """List all projects owned by the authenticated tenant."""
    async with uow:
        projects = await usecase.execute(uow.session, user.id)
    return [ProjectReadRes.model_validate(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectReadRes)
async def get_project(
    project_id: UUID,
    uow: UnitOfWorkDeps,
    usecase: GetProjectUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Get a specific project by ID."""
    async with uow:
        project = await usecase.execute(uow.session, project_id, user.id)
    return ProjectReadRes.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    uow: UnitOfWorkDeps,
    usecase: DeleteProjectUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Delete a project and all its associated data."""
    async with uow:
        await usecase.execute(uow.session, project_id, user.id)
