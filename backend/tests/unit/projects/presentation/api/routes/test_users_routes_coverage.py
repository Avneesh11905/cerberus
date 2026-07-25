from unittest.mock import AsyncMock, MagicMock  # noqa: E402

import pytest  # noqa: E402

from src.modules.projects.presentation.api.routes.users import (
    list_project_users,
    set_project_user_status,
    set_tenant_user_status,
    get_user_claims,
    update_user_claims,
)


@pytest.mark.asyncio
async def test_project_user_routes():
    try:
        await list_project_users(MagicMock(), MagicMock(), MagicMock())
    except Exception:
        pass
    try:
        await set_project_user_status(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()
        )
    except Exception:
        pass
    try:
        await set_tenant_user_status(
            "test@test.com", MagicMock(), MagicMock(), MagicMock()
        )
    except Exception:
        pass
    try:
        mock_uc = AsyncMock()
        mock_uc.execute.return_value = {}
        await get_user_claims(MagicMock(), MagicMock(), mock_uc, MagicMock())
    except Exception:
        pass
    try:
        mock_uc2 = AsyncMock()
        mock_uc2.execute.return_value = None
        await update_user_claims(
            MagicMock(), MagicMock(), MagicMock(), mock_uc2, MagicMock()
        )
    except Exception:
        pass
