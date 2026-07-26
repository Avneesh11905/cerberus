import json
import asyncio
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse, ServerSentEvent
from src.modules.analytics.presentation.api.dependencies.event_bus_dep import (
    EventSubscriberPortDep,
)
from src.modules.analytics.wiring import (
    VerifyProjectOwenershipDeps,
    GetProjectMetricsUseCaseDeps,
)

router = APIRouter(prefix="/projects/{project_id}/events", tags=["Analytics Events"])


def _serialize_metric(m) -> dict:
    """Serialize ORM model or plain dict to a JSON-safe dict."""
    if isinstance(m, dict):
        row = m
    else:
        row = {
            "date": str(m.date) if m.date else None,
            "api_requests": m.api_requests or 0,
            "login_successes": m.login_successes or 0,
            "login_failures": m.login_failures or 0,
            "registrations": m.registrations or 0,
            "active_users": m.active_users or 0,
        }
    if row.get("date") and not isinstance(row["date"], str):
        row["date"] = str(row["date"])
    return row


@router.get(
    "/stream",
    dependencies=[VerifyProjectOwenershipDeps],
)
async def project_analytics_stream(
    project_id: str,
    request: Request,
    subscriber: EventSubscriberPortDep,
    get_metrics_use_case: GetProjectMetricsUseCaseDeps,
):
    async def event_generator():
        from src.modules.analytics.application.queries.metrics_queries import (
            GetProjectMetricsQuery,
        )
        from datetime import date, timedelta
        from uuid import UUID

        # ── Phase 1: Short-lived DB fetch ─────────────────────────────────────
        # The use case opens and closes the UoW internally (async with self.uow).
        # After execute() returns the session is committed and returned to pool.
        result = await get_metrics_use_case.execute(
            GetProjectMetricsQuery(
                project_id=UUID(project_id),
                start_date=date.today() - timedelta(days=30),
                end_date=date.today(),
            )
        )
        metrics = [_serialize_metric(m) for m in result.metrics]

        yield ServerSentEvent(
            data=json.dumps({"metrics": metrics, "totals": result.totals}),
        )

        # ── Phase 2: Long-lived Redis pub/sub — no DB connection held ─────────
        channel = f"analytics:project:{project_id}"
        try:
            async for data in subscriber.subscribe(channel):
                yield ServerSentEvent(data=json.dumps(data))
        except asyncio.CancelledError:
            pass

    return EventSourceResponse(event_generator())
