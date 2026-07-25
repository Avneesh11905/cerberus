import pytest
from redis.asyncio import Redis
from src.shared.infrastructure.adapters.cache import RedisCacheAdapter
from src.shared.infrastructure.adapters.rate_limiter import RedisRateLimiterAdapter


@pytest.fixture
async def redis_client(infra_containers):
    redis_url = infra_containers["redis_base"] + "/0"
    client = Redis.from_url(redis_url, decode_responses=True)
    yield client
    await client.flushdb()
    await client.aclose()


@pytest.mark.asyncio
async def test_redis_rate_limiter(redis_client: Redis):
    cache = RedisCacheAdapter(redis_client)
    limiter = RedisRateLimiterAdapter(cache)
    key = "test_limit"

    # Test record failure
    await limiter.record_failure(key)
    await limiter.record_failure(key)
    count = await limiter.get_failure_count(key)
    assert count == 2

    # Test success resets failure
    await limiter.record_success(key)
    count_after = await limiter.get_failure_count(key)
    assert count_after == 0

    # Test captcha
    cleared = await limiter.is_captcha_cleared(key)
    assert cleared is False

    await limiter.record_captcha_success(key)
    cleared_after = await limiter.is_captcha_cleared(key)
    assert cleared_after is True
