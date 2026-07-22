import httpx
import pytest
import respx
from httpx import Response

from src.core.config.security import TurnstileSettings
from src.shared.infrastructure.adapters.turnstile import CloudflareTurnstileAdapter


@pytest.mark.asyncio
async def test_turnstile_missing_secret_development():
    settings = TurnstileSettings(SECRET_KEY="")
    adapter = CloudflareTurnstileAdapter(settings, is_development=True)
    assert await adapter.verify_token("any-token") is True


@pytest.mark.asyncio
async def test_turnstile_missing_secret_production():
    settings = TurnstileSettings(SECRET_KEY="")
    adapter = CloudflareTurnstileAdapter(settings, is_development=False)
    assert await adapter.verify_token("any-token") is False


@pytest.mark.asyncio
async def test_turnstile_dummy_token_development():
    settings = TurnstileSettings(SECRET_KEY="secret")
    adapter = CloudflareTurnstileAdapter(settings, is_development=True)
    assert await adapter.verify_token("dummy-token") is True


@pytest.mark.asyncio
@respx.mock
async def test_turnstile_verify_success():
    settings = TurnstileSettings(SECRET_KEY="secret")
    adapter = CloudflareTurnstileAdapter(settings, is_development=False)

    respx.post("https://challenges.cloudflare.com/turnstile/v0/siteverify").mock(
        return_value=Response(200, json={"success": True})
    )

    assert await adapter.verify_token("real-token", "1.1.1.1") is True


@pytest.mark.asyncio
@respx.mock
async def test_turnstile_verify_failure_response():
    settings = TurnstileSettings(SECRET_KEY="secret")
    adapter = CloudflareTurnstileAdapter(settings, is_development=False)

    respx.post("https://challenges.cloudflare.com/turnstile/v0/siteverify").mock(
        return_value=Response(
            200, json={"success": False, "error-codes": ["invalid-input-response"]}
        )
    )

    assert await adapter.verify_token("bad-token") is False


@pytest.mark.asyncio
@respx.mock
async def test_turnstile_verify_network_error():
    settings = TurnstileSettings(SECRET_KEY="secret")
    adapter = CloudflareTurnstileAdapter(settings, is_development=False)

    respx.post("https://challenges.cloudflare.com/turnstile/v0/siteverify").mock(
        side_effect=httpx.RequestError("Network unreachable")
    )

    # Fail closed securely
    assert await adapter.verify_token("real-token") is False
