import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.shared.presentation.api.middlewares.rate_limit_and_analytics import (
    RateLimitAndAnalyticsMiddleware,
)

app = FastAPI()


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
def analytics_mock():
    return MagicMock()


@pytest.fixture
def cache_mock():
    mock = AsyncMock()
    mock.get_string.return_value = None
    return mock


@pytest.fixture
def test_app(rate_limiter_mock, analytics_mock, cache_mock):
    app = FastAPI()
    app.add_middleware(
        RateLimitAndAnalyticsMiddleware,
        core_settings=DummyCoreSettings(),  # type: ignore
        rate_limit_settings=DummyRateLimitSettings(),  # type: ignore
        rate_limiter=rate_limiter_mock,
        analytics=analytics_mock,
        cache=cache_mock,
    )

    @app.get("/test")
    def test_route():
        return {"msg": "ok"}

    @app.get("/auth/login")
    def auth_route():
        return {"msg": "auth ok"}

    return app


@pytest.fixture
def client(test_app):
    return TestClient(test_app)


def test_rate_limit_allowed(client, rate_limiter_mock, analytics_mock):
    response = client.get("/test")
    assert response.status_code == 200
    assert response.headers["X-RateLimit-Limit"] == "60"
    assert response.headers["X-RateLimit-Remaining"] == "59"
    rate_limiter_mock.check_rate_limit.assert_called_once()
    analytics_mock.record_event.assert_called_once()


def test_rate_limit_blocked(test_app, rate_limiter_mock):
    rate_limiter_mock.check_rate_limit.return_value = (False, 0, 1234567890)
    client = TestClient(test_app)
    response = client.get("/test")
    assert response.status_code == 429
    assert response.headers["X-RateLimit-Remaining"] == "0"


def test_auth_route_challenged(test_app, rate_limiter_mock):
    rate_limiter_mock.check_rate_limit.return_value = (False, 0, 1234567890)
    client = TestClient(test_app)
    response = client.get("/auth/login")
    # Because it escalates instead of blocking immediately in middleware, it passes through to route
    assert response.status_code == 200


def test_rate_limit_disabled(test_app, rate_limiter_mock, analytics_mock, cache_mock):
    app = FastAPI()

    class DisabledSettings:
        ENABLED = False

    app.add_middleware(
        RateLimitAndAnalyticsMiddleware,
        core_settings=DummyCoreSettings(),  # type: ignore
        rate_limit_settings=DisabledSettings(),  # type: ignore
        rate_limiter=rate_limiter_mock,
        analytics=analytics_mock,
        cache=cache_mock,
    )

    @app.get("/test")
    def test_route():
        return {"msg": "ok"}

    client = TestClient(app)
    response = client.get("/test")
    assert response.status_code == 200
    assert "X-RateLimit-Limit" not in response.headers


def test_cf_connecting_ip(client):
    response = client.get("/test", headers={"cf-connecting-ip": "1.1.1.1"})
    assert response.status_code == 200


def test_x_forwarded_for(client):
    response = client.get("/test", headers={"x-forwarded-for": "2.2.2.2, 3.3.3.3"})
    assert response.status_code == 200


def test_development_env_bypass(test_app):
    test_app.state.project_environments = {"test-project": "development"}

    # Needs valid token
    import jwt

    token = jwt.encode(
        {"project_id": "test-project"},
        "a_secret_key_that_is_at_least_32_bytes_long!",
        algorithm="HS256",
    )
    client = TestClient(test_app)

    response = client.get("/test", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_api_key_bypass(test_app, cache_mock):
    test_app.state.project_environments = {"test-project": "development"}
    cache_mock.get_string.return_value = "test-project"

    client = TestClient(test_app)
    response = client.get("/test", headers={"x-cerberus-api-key": "my-key"})
    assert response.status_code == 200


def test_ignore_health_endpoint(client, analytics_mock):
    client.get("/health")
    # Actually wait, there is no /health route in test_app, it will return 404, but middleware runs
    analytics_mock.record_event.assert_not_called()


def test_429_dev_mode(test_app, rate_limiter_mock):
    test_app.user_middleware[0].kwargs["core_settings"].ENV = "development"
    rate_limiter_mock.check_rate_limit.return_value = (False, 0, 1234567890)
    client = TestClient(test_app)
    response = client.get("/test")
    assert response.status_code == 429
    assert "Try again" in response.json()["detail"]
