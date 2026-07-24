from unittest.mock import AsyncMock

import pytest
from fastapi.responses import Response

from src.modules.authentication.presentation.api.utils import (
    build_auth_redirect_async,
    create_exchange_code,
    delete_refresh_token_cookie,
)
from src.shared.presentation.api.utils import origin_from_url


def test_delete_refresh_token_cookie():
    response = Response()
    delete_refresh_token_cookie(response)

    cookies = response.headers.getlist("set-cookie")
    assert any("refresh_token=" in c for c in cookies)
    assert any("csrf_token=" in c for c in cookies)


@pytest.mark.asyncio
async def test_create_exchange_code():
    mock_cache = AsyncMock()
    mock_cache.set_dict = AsyncMock()

    code = await create_exchange_code(
        mock_cache,
        refresh_token="test_rt",
        is_new_user=True,
        access_token="test_at",
        user_id="test_uid",
    )

    # Verify in cache
    mock_cache.set_dict.assert_called_once()
    args, kwargs = mock_cache.set_dict.call_args
    assert args[0] == f"exchange_code:{code}"
    assert args[1]["refresh_token"] == "test_rt"
    assert args[1]["is_new_user"] is True
    assert args[1]["access_token"] == "test_at"
    assert args[1]["user_id"] == "test_uid"
    assert kwargs["ttl"] == 120


@pytest.mark.asyncio
async def test_build_auth_redirect_async():
    mock_cache = AsyncMock()
    mock_cache.set_dict = AsyncMock()

    response = await build_auth_redirect_async(
        refresh_token="test_rt",
        cache=mock_cache,
        is_new_user=True,
        access_token="test_at",
        user_id="test_uid",
        frontend_url="https://frontend.com/",
    )

    assert response.status_code == 307
    location = response.headers.get("location")
    assert location is not None
    assert "https://frontend.com/oauth/callback?code=" in location
    assert "&new_user=true" in location


def test_origin_from_url():
    assert origin_from_url("https://example.com/some/path") == "https://example.com"
    assert origin_from_url("http://localhost:3000") == "http://localhost:3000"
    assert origin_from_url(None) is None
    assert origin_from_url("invalid-url") is None
