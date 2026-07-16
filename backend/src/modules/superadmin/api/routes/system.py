from typing import Annotated

from fastapi import APIRouter, Depends

from src.modules.auth.api.dependencies import require_role
from src.modules.auth.domain import UserIdentity
from src.modules.superadmin.api.dependencies import TenantManagementUseCaseDep
from src.modules.superadmin.api.schemas import (
    PaginatedSystemLogRes,
    SystemAnalyticsRes,
    SystemLogRes,
)
from src.shared.adapters.uow import SQLAlchemyUnitOfWork, get_uow

router = APIRouter()


@router.get("/logs", response_model=PaginatedSystemLogRes)
async def list_system_logs(
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    use_case: TenantManagementUseCaseDep,
    admin: Annotated[UserIdentity, Depends(require_role("SUPERADMIN"))],
    page: int = 1,
    limit: int = 100,
    level: str | None = None,
):
    """View recent system activity logs (audits, errors, events)."""
    skip = (page - 1) * limit
    async with uow:
        logs, total = await use_case.list_logs(
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
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    use_case: TenantManagementUseCaseDep,
    admin: Annotated[UserIdentity, Depends(require_role("SUPERADMIN"))],
):
    """View system-wide aggregated analytics metrics."""
    async with uow:
        analytics_entity = await use_case.get_system_analytics(uow.session)

    return SystemAnalyticsRes.model_validate(analytics_entity)
