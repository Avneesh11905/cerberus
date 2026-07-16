from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.modules.auth.api.dependencies import require_role
from src.modules.auth.domain import UserIdentity
from src.modules.projects.api.dependencies import ProjectManagementUseCaseDep
from src.modules.projects.api.schemas import (
    ProjectCreateReq,
    ProjectCreateRes,
    ProjectReadRes,
)
from src.shared.adapters.uow import SQLAlchemyUnitOfWork, get_uow

router = APIRouter()


@router.post("/", response_model=ProjectCreateRes, status_code=status.HTTP_201_CREATED)
async def create_project(
    req: ProjectCreateReq,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: ProjectManagementUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role("TENANT"))],
):
    """Create a new Cerberus project."""
    async with uow:
        project, api_key, public_key = await usecase.create_project(
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
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: ProjectManagementUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role("TENANT"))],
):
    """List all projects owned by the authenticated tenant."""
    async with uow:
        projects = await usecase.list_projects(uow.session, user.id)
    return [ProjectReadRes.model_validate(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectReadRes)
async def get_project(
    project_id: UUID,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: ProjectManagementUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role("TENANT"))],
):
    """Get a specific project by ID."""
    async with uow:
        project = await usecase.get_project(uow.session, project_id, user.id)
    return ProjectReadRes.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: ProjectManagementUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role("TENANT"))],
):
    """Delete a project and all its associated data."""
    async with uow:
        await usecase.delete_project(uow.session, project_id, user.id)
