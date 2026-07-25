import pytest
from redis.asyncio import Redis
from src.shared.infrastructure.adapters.cache import RedisCacheAdapter


@pytest.fixture
async def redis_client(infra_containers):
    redis_url = infra_containers["redis_base"] + "/0"
    client = Redis.from_url(redis_url, decode_responses=True)
    yield client
    await client.flushdb()
    await client.aclose()


@pytest.mark.asyncio
async def test_redis_cache_set_dict_nx(redis_client: Redis):
    cache = RedisCacheAdapter(redis_client)
    key = "test_nx_key"

    # First time should succeed
    res1 = await cache.set_dict_nx(key, {"a": 1}, 60)
    assert res1 is True

    # Second time should fail
    res2 = await cache.set_dict_nx(key, {"b": 2}, 60)
    assert res2 is False

    # Value should be the first one
    val = await cache.get_dict(key)
    assert val == {"a": 1}


@pytest.mark.asyncio
async def test_redis_cache_string_methods(redis_client: Redis):
    cache = RedisCacheAdapter(redis_client)

    await cache.set_string("str_key", "hello", 60)
    val = await cache.get_string("str_key")
    assert val == "hello"

    val2 = await cache.get_string("missing_str")
    assert val2 is None


@pytest.mark.asyncio
async def test_redis_cache_mget_strings(redis_client: Redis):
    cache = RedisCacheAdapter(redis_client)

    res = await cache.mget_strings([])
    assert res == []

    await cache.set_string("k1", "v1", 60)
    await cache.set_string("k2", "v2", 60)

    res2 = await cache.mget_strings(["k1", "k2", "k3"])
    assert res2 == ["v1", "v2", None]
