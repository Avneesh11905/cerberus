import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.shared.presentation.api.middlewares.rate_limit_and_analytics import RateLimitAndAnalyticsMiddleware

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
        cache=cache_mock
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
        cache=cache_mock
    )
    @app.get("/test")
    def test_route():
        return {"msg": "ok"}
        
    client = TestClient(app)
    response = client.get("/test")
    assert response.status_code == 200
    assert "X-RateLimit-Limit" not in response.headers
