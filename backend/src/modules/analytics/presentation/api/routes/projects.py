from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query

from src.modules.analytics.application.queries.metrics_queries import (
    GetProjectMetricsQuery,
)
from src.modules.analytics.presentation.api.schemas import (
    MetricResponse,
    QueryAnalyticsResponse,
)
from src.modules.analytics.wiring import (
    GetProjectMetricsUseCaseDeps,
    verify_project_ownership,
)

router = APIRouter()


@router.get(
    "/projects/{project_id}",
    response_model=QueryAnalyticsResponse,
    summary="Get analytics for a specific project",
    dependencies=[Depends(verify_project_ownership)],
)
async def get_project_analytics(
    use_case: GetProjectMetricsUseCaseDeps,
    project_id: UUID = Path(...),
    start_date: date = Query(default_factory=lambda: date.today() - timedelta(days=30)),
    end_date: date = Query(default_factory=lambda: date.today()),
):
    metrics = (
        await use_case.execute(
            GetProjectMetricsQuery(
                project_id=project_id, start_date=start_date, end_date=end_date
            ),
        )
    ).data
    return QueryAnalyticsResponse(
        metrics=[MetricResponse.model_validate(m) for m in metrics]
    )
