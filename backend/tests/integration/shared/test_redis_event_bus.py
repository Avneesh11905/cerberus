import asyncio
import pytest
from redis.asyncio import Redis
from src.shared.infrastructure.adapters.redis_event_bus import (
    RedisEventPublisherAdapter,
    RedisEventSubscriberAdapter,
)


@pytest.fixture
async def redis_client(infra_containers):
    redis_url = infra_containers["redis_base"] + "/0"
    client = Redis.from_url(redis_url, decode_responses=True)
    yield client
    await client.aclose()


@pytest.mark.asyncio
async def test_redis_event_bus(redis_client: Redis):
    publisher = RedisEventPublisherAdapter(redis_client)
    subscriber = RedisEventSubscriberAdapter(redis_client)
    channel = "test_channel"

    # Subscribe and listen in background
    received_messages = []

    async def listen():
        async for msg in subscriber.subscribe(channel):
            received_messages.append(msg)
            if len(received_messages) >= 2:
                break

    task = asyncio.create_task(listen())

    # Need to wait a tiny bit to ensure subscription is active
    await asyncio.sleep(0.1)

    await publisher.publish(channel, {"hello": "world"})
    await publisher.publish(channel, {"test": 123})

    await asyncio.wait_for(task, timeout=2.0)

    assert len(received_messages) == 2
    assert received_messages[0] == {"hello": "world"}
    assert received_messages[1] == {"test": 123}
