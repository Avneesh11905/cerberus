from datetime import date, timedelta
from uuid import UUID
from fastapi import APIRouter, Path, Query

from src.modules.analytics.api.dependencies import GetTenantMetricsUseCaseDeps
from src.modules.analytics.api.schemas import MetricResponse, QueryAnalyticsResponse

from src.modules.auth.authorization.api.dependencies.roles import RequireTenantRoleDep

router = APIRouter()


@router.get(
    "/tenants/{tenant_id}",
    response_model=QueryAnalyticsResponse,
    summary="Get analytics for a specific tenant (Superadmin)",
)
async def get_tenant_analytics(
    user: RequireTenantRoleDep,
    use_case: GetTenantMetricsUseCaseDeps,
    tenant_id: UUID = Path(...),
    start_date: date = Query(default_factory=lambda: date.today() - timedelta(days=30)),
    end_date: date = Query(default_factory=lambda: date.today()),
):
    metrics = await use_case.execute(tenant_id, start_date, end_date)
    return QueryAnalyticsResponse(
        metrics=[MetricResponse.model_validate(m) for m in metrics]
    )
