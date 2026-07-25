import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.sanity
async def test_health_check_success(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["components"]["database"] == "ok"
    assert data["components"]["cache"] == "ok"


@pytest.mark.asyncio
async def test_health_check_db_failure(client: AsyncClient, mocker):
    # It's easier to mock the db session dependency or text
    # Let's mock SQLAlchemy text
    mocker.patch(
        "src.shared.presentation.api.routes.health.text",
        side_effect=Exception("DB Error"),
    )
    response = await client.get("/health")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "degraded"
    assert data["components"]["database"] == "error"


@pytest.mark.asyncio
async def test_health_check_cache_failure(client: AsyncClient, mocker):
    class MockRedis:
        async def ping(self):
            raise Exception("Cache Error")

        async def aclose(self):
            pass

    mocker.patch(
        "src.shared.presentation.api.routes.health.redis.from_url",
        return_value=MockRedis(),
    )
    response = await client.get("/health")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "degraded"
    assert data["components"]["cache"] == "error"
