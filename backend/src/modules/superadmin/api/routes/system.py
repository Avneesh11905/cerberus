from fastapi import APIRouter

from src.modules.auth.authorization.api.dependencies.roles import (
    RequireSuperAdminRoleDep,
)
from src.modules.superadmin.api.dependencies import (
    GetSystemAnalyticsUseCaseDep,
    ListTenantLogsUseCaseDep,
)
from src.modules.superadmin.api.schemas import (
    PaginatedSystemLogRes,
    SystemAnalyticsRes,
    SystemLogRes,
)
from src.shared.api.dependencies import UnitOfWorkDeps

router = APIRouter()


@router.get("/logs", response_model=PaginatedSystemLogRes)
async def list_system_logs(
    uow: UnitOfWorkDeps,
    use_case: ListTenantLogsUseCaseDep,
    admin: RequireSuperAdminRoleDep,
    page: int = 1,
    limit: int = 100,
    level: str | None = None,
):
    """View recent system activity logs (audits, errors, events)."""
    skip = (page - 1) * limit
    async with uow:
        logs, total = await use_case.execute(
            uow.session, skip=skip, limit=limit, level=level
        )

    return PaginatedSystemLogRes(
        items=[SystemLogRes.model_validate(log) for log in logs],
        total=total,
        page=page,
        size=limit,
    )


@router.get("/analytics", response_model=SystemAnalyticsRes)
async def get_system_analytics(
    uow: UnitOfWorkDeps,
    use_case: GetSystemAnalyticsUseCaseDep,
    admin: RequireSuperAdminRoleDep,
):
    """View system-wide aggregated analytics metrics."""
    async with uow:
        analytics_entity = await use_case.execute(uow.session)

    return SystemAnalyticsRes.model_validate(analytics_entity)
