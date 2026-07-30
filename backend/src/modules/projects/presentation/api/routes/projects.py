from uuid import UUID

from fastapi import APIRouter, status

from src.modules.authorization.presentation.api.dependencies.roles import (
    RequireTenantRoleDep,
)
from src.modules.projects.application.commands.project_commands import (
    CreateProjectCommand,
    DeleteProjectCommand,
)
from src.modules.projects.application.queries.project_queries import (
    GetProjectQuery,
    ListProjectsQuery,
)
from src.modules.projects.presentation.api.schemas import (
    ProjectCreateReq,
    ProjectCreateRes,
    ProjectReadRes,
    PaginatedProjectsRes,
)
from fastapi import Query
from src.modules.projects.wiring import (
    CreateProjectUseCaseDep,
    DeleteProjectUseCaseDep,
    GetProjectUseCaseDep,
    ListProjectsUseCaseDep,
)

router = APIRouter()


@router.post("/", response_model=ProjectCreateRes, status_code=status.HTTP_201_CREATED)
async def create_project(
    req: ProjectCreateReq,
    usecase: CreateProjectUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Create a new Cerberus project."""
    dto = await usecase.execute(CreateProjectCommand(user_id=user.id, name=req.name))
    project, api_key, public_key = (
        dto.project,
        dto.api_key_plaintext,
        dto.public_pem,
    )
    return ProjectCreateRes(
        id=project.id,
        name=project.name,
        api_key=api_key,
        public_key=public_key,
        created_at=project.created_at,
    )


@router.get("/", response_model=PaginatedProjectsRes)
async def list_projects(
    usecase: ListProjectsUseCaseDep,
    user: RequireTenantRoleDep,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    """List all projects owned by the authenticated tenant."""
    skip = (page - 1) * size
    dto = await usecase.execute(
        ListProjectsQuery(user_id=user.id, skip=skip, limit=size)
    )

    return PaginatedProjectsRes(
        items=[ProjectReadRes.model_validate(p) for p in dto.projects],
        total=dto.total,
        page=page,
        size=size,
    )


@router.get("/{project_id}", response_model=ProjectReadRes)
async def get_project(
    project_id: UUID,
    usecase: GetProjectUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Get a specific project by ID."""
    dto = await usecase.execute(GetProjectQuery(project_id=project_id, user_id=user.id))
    project = dto.project
    return ProjectReadRes.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    usecase: DeleteProjectUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Delete a project and all its associated data."""
    await usecase.execute(DeleteProjectCommand(project_id=project_id, user_id=user.id))
