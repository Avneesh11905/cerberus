import json
import asyncio
from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse, ServerSentEvent

from src.shared.application.ports.event_bus import EventSubscriberPort
from src.modules.analytics.presentation.api.dependencies.event_bus_dep import get_event_subscriber
from src.modules.authorization.presentation.api.dependencies.roles import RequireTenantRoleDep

# Removed {tenant_id} from the path to prevent IDOR (Insecure Direct Object Reference)
router = APIRouter(prefix="/tenants/me/events", tags=["Analytics Events"])


@router.get(
    "/stream",
)
async def tenant_analytics_stream(
    request: Request,
    user: RequireTenantRoleDep,
    subscriber: EventSubscriberPort = Depends(get_event_subscriber),
):
    async def event_generator():
        # The channel is strictly tied to the authenticated user's ID
        channel = f"analytics:tenant:{user.id}"
        try:
            async for data in subscriber.subscribe(channel):
                yield ServerSentEvent(event="tenant_metrics_update", data=json.dumps(data))
        except asyncio.CancelledError:
            pass

    return EventSourceResponse(event_generator())
