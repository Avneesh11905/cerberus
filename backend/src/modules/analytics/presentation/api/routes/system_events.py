import json
import asyncio
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse, ServerSentEvent
from src.modules.analytics.presentation.api.dependencies.event_bus_dep import (
    EventSubscriberPortDep,
)
from src.modules.authorization.presentation.api.dependencies.roles import (
    RequireSuperAdminRoleDep,
)

router = APIRouter(prefix="/system/events", tags=["Analytics Events"])


@router.get(
    "/stream",
)
async def system_analytics_stream(
    request: Request,
    user: RequireSuperAdminRoleDep,
    subscriber: EventSubscriberPortDep,
):
    async def event_generator():
        from src.modules.superadmin.infrastructure.database.repositories.superadmin_uow import SQLSuperadminUnitOfWork
        from src.modules.superadmin.application.use_cases.get_system_analytics import GetSystemAnalyticsUseCase
        import dataclasses

        uow = SQLSuperadminUnitOfWork()
        use_case = GetSystemAnalyticsUseCase(uow=uow)
        
        initial_data = await use_case.execute()
        yield ServerSentEvent(
            event="system_metrics_update", data=json.dumps(dataclasses.asdict(initial_data))
        )

        channel = "analytics:system:global"
        try:
            async for data in subscriber.subscribe(channel):
                yield ServerSentEvent(
                    event="system_metrics_update", data=json.dumps(data)
                )
        except asyncio.CancelledError:
            pass

    return EventSourceResponse(event_generator())
