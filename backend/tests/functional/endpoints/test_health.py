import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.sanity
async def test_health_check_success(client: AsyncClient):
    response = await client.get("/v1.0/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["components"]["database"] == "ok"
    assert data["components"]["cache"] == "ok"
