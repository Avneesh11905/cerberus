import json
import asyncio
from typing import Annotated
from fastapi import APIRouter, Request, Depends
from sse_starlette.sse import EventSourceResponse, ServerSentEvent
from src.modules.superadmin.wiring import get_superadmin_uow, SuperAdminUoWPort
from src.modules.analytics.presentation.api.dependencies.event_bus_dep import (
    EventSubscriberPortDep,
)
from src.modules.authorization.presentation.api.dependencies.roles import (
    RequireSuperAdminRoleDep,
)

router = APIRouter(prefix="/system/events", tags=["Analytics Events"])


@router.get("/stream")
async def system_analytics_stream(
    request: Request,
    user: RequireSuperAdminRoleDep,
    subscriber: EventSubscriberPortDep,
    uow: Annotated[SuperAdminUoWPort, Depends(get_superadmin_uow)],
):
    async def event_generator():
        from src.modules.superadmin.application.use_cases.get_system_analytics import (
            GetSystemAnalyticsUseCase,
        )
        import dataclasses

        # ── Phase 1: Short-lived DB fetch — open, query, close ────────────────
        # The use case manages its own UoW internally
        use_case = GetSystemAnalyticsUseCase(uow=uow)
        initial_data = await use_case.execute()

        # We enter the UoW context explicitly here to fetch the timeseries,
        # ensuring the session is closed before the long-lived SSE stream.
        async with uow:
            timeseries = await uow.analytics_repo.get_global_timeseries(days=30)

        # Session is now closed and returned to the pool.
        payload = dataclasses.asdict(initial_data)
        payload["metrics"] = timeseries

        yield ServerSentEvent(
            data=json.dumps(payload),
        )

        # ── Phase 2: Long-lived Redis pub/sub — no DB connection held ─────────
        channel = "analytics:system:global"
        try:
            async for data in subscriber.subscribe(channel):
                yield ServerSentEvent(data=json.dumps(data))
        except asyncio.CancelledError:
            pass

    return EventSourceResponse(event_generator())
