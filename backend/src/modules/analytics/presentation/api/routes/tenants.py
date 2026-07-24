from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Path, Query, HTTPException

from src.modules.analytics.application.queries.metrics_queries import (
    GetTenantMetricsQuery,
)
from src.modules.analytics.presentation.api.schemas import (
    MetricResponse,
    QueryAnalyticsResponse,
)
from src.modules.analytics.wiring import (
    GetTenantMetricsUseCaseDeps,
)
from src.modules.authorization.presentation.api.dependencies.roles import (
    RequireTenantRoleDep,
)
from src.modules.authorization.domain.enums import GlobalRole

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
    if user.role != GlobalRole.SUPERADMIN and str(user.id) != str(tenant_id):
        raise HTTPException(status_code=403, detail="You can only access your own metrics.")

    metrics = (
        await use_case.execute(
            GetTenantMetricsQuery(
                tenant_id=tenant_id, start_date=start_date, end_date=end_date
            ),
        )
    ).data
    return QueryAnalyticsResponse(
        metrics=[MetricResponse.model_validate(m) for m in metrics]
    )
