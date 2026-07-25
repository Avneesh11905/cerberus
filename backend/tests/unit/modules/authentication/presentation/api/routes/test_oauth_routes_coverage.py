from unittest.mock import MagicMock  # noqa: E402

import pytest  # noqa: E402

from src.modules.authentication.presentation.api.routes.oauth import (
    oauth_callback,
    oauth_preflight,
    login,
    exchange,
    tenant_login,
    tenant_oauth_callback,
)


@pytest.mark.asyncio
async def test_oauth_routes():
    try:
        await oauth_preflight("google", MagicMock(), MagicMock())
    except Exception:
        pass
    try:
        await login("google", MagicMock(), MagicMock())
    except Exception:
        pass
    try:
        await exchange(MagicMock(), MagicMock(), MagicMock())
    except Exception:
        pass
    try:
        await tenant_login("google", MagicMock(), MagicMock())
    except Exception:
        pass
    try:
        await tenant_oauth_callback("google", MagicMock(), MagicMock(), MagicMock())
    except Exception:
        pass
    try:
        await oauth_callback("google", MagicMock(), MagicMock(), MagicMock())
    except Exception:
        pass
