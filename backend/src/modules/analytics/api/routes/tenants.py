from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query

from src.modules.analytics.api.dependencies import get_query_analytics_use_case
from src.modules.analytics.api.schemas import MetricResponse, QueryAnalyticsResponse
from src.modules.analytics.application.use_cases.query_analytics import (
    QueryAnalyticsUseCase,
)
from src.modules.auth.api.dependencies import require_role
from src.modules.auth.domain import UserIdentity as User
from src.shared.domain.enums import UserRole

router = APIRouter()


@router.get(
    "/tenants/{tenant_id}",
    response_model=QueryAnalyticsResponse,
    summary="Get analytics for a specific tenant (Superadmin)",
)
async def get_tenant_analytics(
    tenant_id: UUID = Path(...),
    start_date: date = Query(default_factory=lambda: date.today() - timedelta(days=30)),
    end_date: date = Query(default_factory=lambda: date.today()),
    use_case: QueryAnalyticsUseCase = Depends(get_query_analytics_use_case),
    user: User = Depends(require_role(UserRole.SUPERADMIN)),
):
    metrics = await use_case.get_tenant_metrics(tenant_id, start_date, end_date)
    return QueryAnalyticsResponse(
        metrics=[MetricResponse.model_validate(m) for m in metrics]
    )
