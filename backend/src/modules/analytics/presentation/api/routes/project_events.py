import json
import asyncio
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse, ServerSentEvent
from src.modules.analytics.presentation.api.dependencies.event_bus_dep import EventSubscriberPortDep
from src.modules.analytics.wiring import VerifyProjectOwenershipDeps

router = APIRouter(prefix="/projects/{project_id}/events", tags=["Analytics Events"])


@router.get(
    "/stream",
    dependencies=[VerifyProjectOwenershipDeps],
)
async def project_analytics_stream(
    project_id: str,
    request: Request,
    subscriber: EventSubscriberPortDep,
):
    async def event_generator():
        channel = f"analytics:project:{project_id}"
        try:
            async for data in subscriber.subscribe(channel):
                yield ServerSentEvent(event="project_metrics_update", data=json.dumps(data))
        except asyncio.CancelledError:
            pass

    return EventSourceResponse(event_generator())
