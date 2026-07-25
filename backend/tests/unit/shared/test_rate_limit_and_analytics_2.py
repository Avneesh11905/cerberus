import pytest
from src.shared.presentation.api.middlewares.rate_limit_and_analytics import parse_rate
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.shared.presentation.api.middlewares.rate_limit_and_analytics import (
    RateLimitAndAnalyticsMiddleware,
)


def test_parse_rate():
    assert parse_rate("10/s") == (10, 1)
    assert parse_rate("10/h") == (10, 3600)
    assert parse_rate("10/d") == (10, 86400)
    assert parse_rate("invalid") == (60, 60)


class DummyCoreSettings:
    ENV = "test"


class DummyRateLimitSettings:
    ENABLED = True


@pytest.fixture
def rate_limiter_mock():
    mock = AsyncMock()
    mock.check_rate_limit.return_value = (True, 59, 1234567890)
    return mock


@pytest.fixture
def test_app(rate_limiter_mock):
    app = FastAPI()
    app.add_middleware(
        RateLimitAndAnalyticsMiddleware,
        core_settings=DummyCoreSettings(),  # type: ignore
        rate_limit_settings=DummyRateLimitSettings(),  # type: ignore
        rate_limiter=rate_limiter_mock,
        analytics=MagicMock(),
        cache=AsyncMock(),
    )

    @app.get("/test")
    def test_route():
        return {"msg": "ok"}

    return app


def test_jwt_exception(test_app):
    client = TestClient(test_app)
    # Invalid JWT will trigger the exception block in line 81
    response = client.get("/test", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 200


def test_api_key_exception(test_app):
    client = TestClient(test_app)
    # To trigger the cache exception in line 92, we mock cache.get_string to raise Exception
    test_app.user_middleware[0].kwargs["cache"].get_string.side_effect = Exception(
        "Cache error"
    )
    response = client.get("/test", headers={"x-cerberus-api-key": "my-key"})
    assert response.status_code == 200
