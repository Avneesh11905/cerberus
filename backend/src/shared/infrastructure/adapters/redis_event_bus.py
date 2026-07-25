import json
import asyncio
from typing import Any, AsyncGenerator
from redis.asyncio import Redis

from src.shared.application.ports.event_bus import (
    EventPublisherPort,
    EventSubscriberPort,
)


class RedisEventPublisherAdapter(EventPublisherPort):
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def publish(self, channel: str, message: dict[str, Any]) -> None:
        await self.redis.publish(channel, json.dumps(message))


class RedisEventSubscriberAdapter(EventSubscriberPort):
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def subscribe(self, channel: str) -> AsyncGenerator[dict[str, Any], None]:
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    yield json.loads(message["data"])
        except asyncio.CancelledError:
            # Client disconnected via sse-starlette throwing CancelledError
            pass
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.aclose()
