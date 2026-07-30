from fastapi import APIRouter

from src.modules.authorization.presentation.api.dependencies.roles import (
    RequireSuperAdminRoleDep,
)
from src.modules.superadmin.presentation.api.schemas import (
    PaginatedSystemLogRes,
    SystemAnalyticsRes,
    SystemLogRes,
)
from src.modules.superadmin.wiring import (
    GetSystemAnalyticsUseCaseDep,
    ListTenantLogsUseCaseDep,
)

router = APIRouter()


@router.get("/logs", response_model=PaginatedSystemLogRes)
async def list_system_logs(
    use_case: ListTenantLogsUseCaseDep,
    admin: RequireSuperAdminRoleDep,
    page: int = 1,
    limit: int = 100,
    level: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    """View recent system activity logs (audits, errors, events)."""
    skip = (page - 1) * limit
    
    from datetime import datetime
    
    parsed_start = None
    parsed_end = None
    if start_date:
        try:
            parsed_start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        except ValueError:
            pass
    if end_date:
        try:
            parsed_end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        except ValueError:
            pass
            
    logs, total = await use_case.execute(
        skip=skip, 
        limit=limit, 
        level=level,
        start_date=parsed_start,
        end_date=parsed_end
    )

    return PaginatedSystemLogRes(
        items=[SystemLogRes.model_validate(log) for log in logs],
        total=total,
        page=page,
        size=limit,
    )


@router.get("/analytics", response_model=SystemAnalyticsRes)
async def get_system_analytics(
    use_case: GetSystemAnalyticsUseCaseDep,
    admin: RequireSuperAdminRoleDep,
):
    """View system-wide aggregated analytics metrics."""
    analytics_entity = await use_case.execute()

    return SystemAnalyticsRes.model_validate(analytics_entity)
