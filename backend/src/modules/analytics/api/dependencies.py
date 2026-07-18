from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import select
from src.core.container import app_container
from src.modules.analytics.application.use_cases import (
    GetProjectMetricsUseCase,
    GetTenantMetricsUseCase,
)
from src.modules.auth.authentication.api.dependencies.security import get_current_user
from src.modules.auth.authentication.domain.entities import UserIdentity
from src.modules.projects.infrastructure.models import Project
from src.shared.api.dependencies import UnitOfWorkDeps
from src.modules.auth.authorization.domain.enums import GlobalRole


def get_project_metrics_use_case() -> GetProjectMetricsUseCase:
    return GetProjectMetricsUseCase(repository=app_container.analytics_repo)


def get_tenant_metrics_use_case() -> GetTenantMetricsUseCase:
    return GetTenantMetricsUseCase(repository=app_container.analytics_repo)


GetProjectMetricsUseCaseDeps = Annotated[
    GetProjectMetricsUseCase, Depends(get_project_metrics_use_case)
]
GetTenantMetricsUseCaseDeps = Annotated[
    GetTenantMetricsUseCase, Depends(get_tenant_metrics_use_case)
]


async def verify_project_ownership(
    project_id: UUID,
    user: Annotated[UserIdentity, Depends(get_current_user)],
    uow: UnitOfWorkDeps,
) -> None:
    """Verifies that the current user's tenant owns the requested project, or the user is a superadmin."""
    if user.role != GlobalRole.SUPERADMIN:
        return

    async with uow:
        result = await uow.session.execute(
            select(Project.tenant_id).where(Project.id == project_id)
        )
        tenant_id = result.scalar_one_or_none()

        if not tenant_id:
            raise HTTPException(status_code=404, detail="Project not found")

        if tenant_id != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
