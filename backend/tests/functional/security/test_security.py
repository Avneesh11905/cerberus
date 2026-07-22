import time

import pytest
from httpx import AsyncClient


class FakeRateLimiter:
    def __init__(self):
        self.counts = {}

    async def check_rate_limit(
        self, key: str, limit: int, window: int
    ) -> tuple[bool, int, int]:
        current = self.counts.get(key, 0)
        if current >= limit:
            return False, 0, int(time.time()) + window
        self.counts[key] = current + 1
        return True, limit - (current + 1), int(time.time()) + window


@pytest.fixture
def mock_rate_limiter(mocker):
    from src.core.config import get_settings
    from src.core.container import app_container

    mocker.patch.object(get_settings().rate_limit, "ENABLED", True)

    fake = FakeRateLimiter()
    mock_check = mocker.patch.object(
        app_container.rate_limiter,
        "check_rate_limit",
        side_effect=fake.check_rate_limit,
    )
    mocker.patch.object(app_container.rate_limiter, "record_failure")
    mocker.patch.object(app_container.rate_limiter, "record_captcha_success")
    yield mock_check


@pytest.mark.asyncio
@pytest.mark.sanity
async def test_rate_limit_regular_route(client: AsyncClient, mock_rate_limiter):
    """
    Issue requests to a non-auth route until the limit is exceeded.
    We'll hit /health 61 times (default limit is 60/minute).
    """
    for i in range(60):
        resp = await client.get("/health")
        assert resp.status_code == 200, f"Request {i} failed prematurely"

    # The 61st request should be blocked
    resp = await client.get("/health")
    assert resp.status_code == 429
    assert "X-RateLimit-Limit" in resp.headers
    assert "Retry-After" in resp.headers


@pytest.mark.asyncio
async def test_rate_limit_auth_escalation(client: AsyncClient, mock_rate_limiter):
    """
    Issue requests to an auth route exceeding the auth_rate (10/minute).
    Auth routes should not return 429; they should escalate to a CAPTCHA challenge.
    Without a CAPTCHA token, they will return a 400 from the Turnstile exception.
    """
    for i in range(10):
        resp = await client.post("/v1/auth/login", json={})
        assert resp.status_code == 422, f"Request {i} didn't hit validation error"

    # The 11th request exceeds the rate limit.
    resp = await client.post(
        "/v1/auth/login", json={"email": "a@example.com", "password": "b"}
    )

    # Fastapi Exception handler translates TurnstileVerificationFailed to 403 Forbidden.
    assert resp.status_code == 403
    assert "Turnstile verification failed" in resp.text


@pytest.mark.asyncio
async def test_ip_extraction_and_spoofing(client: AsyncClient, mock_rate_limiter):
    """
    Send spoofed X-Forwarded-For headers and assert the middleware extracts the correct client IP.
    """
    # X-Forwarded-For should take the FIRST IP in the comma-separated list
    headers = {"X-Forwarded-For": "203.0.113.195, 198.51.100.1, 10.0.0.1"}

    resp = await client.get("/health", headers=headers)
    assert resp.status_code == 200

    # Assert RateLimiterPort was called with the correct IP bucket
    mock_rate_limiter.assert_called_once()
    args, kwargs = mock_rate_limiter.call_args
    bucket_key = args[0]
    assert "203.0.113.195" in bucket_key
    assert "10.0.0.1" not in bucket_key

    # Test CF-Connecting-IP (which overrides X-Forwarded-For in the middleware logic)
    headers = {
        "CF-Connecting-IP": "1.1.1.1",
        "X-Forwarded-For": "203.0.113.195, 10.0.0.1",
    }

    mock_rate_limiter.reset_mock()
    resp = await client.get("/health", headers=headers)

    mock_rate_limiter.assert_called_once()
    args, kwargs = mock_rate_limiter.call_args
    bucket_key = args[0]
    assert "1.1.1.1" in bucket_key
