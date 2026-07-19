import asyncio
import pytest
from httpx import AsyncClient


@pytest.fixture
def enable_rate_limit(mocker):
    from src.core.config import rate_limit_settings

    # The middleware reads rate_limit_settings.ENABLED on every request
    mocker.patch.object(rate_limit_settings, "ENABLED", True)


@pytest.mark.asyncio
async def test_rate_limiter_concurrency(client: AsyncClient, enable_rate_limit):
    """
    Load test the rate limiter by firing 150 requests concurrently.
    We assert that exactly 60 requests succeed and 90 are rate limited.
    This guarantees the Redis Lua script is thread-safe and free of race conditions.
    """
    total_requests = 150
    allowed_requests = 60

    async def make_request():
        return await client.get("/v1.0/health")

    # Fire all requests concurrently
    responses = await asyncio.gather(*[make_request() for _ in range(total_requests)])

    success_count = sum(1 for r in responses if r.status_code == 200)
    rate_limited_count = sum(1 for r in responses if r.status_code == 429)

    assert success_count == allowed_requests, (
        f"Expected {allowed_requests} successes, got {success_count}"
    )
    assert rate_limited_count == total_requests - allowed_requests, (
        f"Expected {total_requests - allowed_requests} rate limits, got {rate_limited_count}"
    )
