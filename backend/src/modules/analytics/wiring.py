from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import select

from src.modules.analytics.application.ports.analytics_unit_of_work import (
    AnalyticsUoWPort,
)
from src.modules.analytics.application.use_cases import (
    GetProjectMetricsUseCase,
    GetTenantMetricsUseCase,
)
from src.modules.analytics.presentation.api.dependencies.analytics_uow_dep import (
    get_analytics_uow,
)
from src.modules.authentication.presentation.api.dependencies.security import (
    GetCurrentUserDep,
)
from src.modules.authorization.domain.enums import GlobalRole
from src.modules.projects.infrastructure.models import Project
from src.shared.presentation.api.dependencies import UnitOfWorkDeps


def get_project_metrics_use_case(
    uow: Annotated[AnalyticsUoWPort, Depends(get_analytics_uow)],
) -> GetProjectMetricsUseCase:
    return GetProjectMetricsUseCase(uow=uow)


def get_tenant_metrics_use_case(
    uow: Annotated[AnalyticsUoWPort, Depends(get_analytics_uow)],
) -> GetTenantMetricsUseCase:
    return GetTenantMetricsUseCase(uow=uow)


GetProjectMetricsUseCaseDeps = Annotated[
    GetProjectMetricsUseCase, Depends(get_project_metrics_use_case)
]
GetTenantMetricsUseCaseDeps = Annotated[
    GetTenantMetricsUseCase, Depends(get_tenant_metrics_use_case)
]


async def verify_project_ownership(
    project_id: UUID,
    user: GetCurrentUserDep,
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
