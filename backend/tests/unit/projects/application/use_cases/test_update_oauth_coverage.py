import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.modules.projects.application.use_cases.update_oauth import UpdateOauthUseCase
from src.modules.projects.application.commands.project_commands import (
    UpdateOauthCommand,
)


@pytest.mark.asyncio
async def test_update_oauth():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    uc = UpdateOauthUseCase(uow, MagicMock())
    cmd = UpdateOauthCommand(
        project_id=uuid4(),
        user_id=uuid4(),
        incoming_config={
            "google": {"enabled": True, "client_id": "test", "client_secret": "secret"}
        },
    )

    mock_proj = MagicMock()
    mock_proj.tenant_id = cmd.user_id
    mock_proj.settings.oauth = MagicMock()
    uow.project_query_repo.get_by_id.return_value = mock_proj

    await uc.execute(cmd)

    # Without project
    uow.project_query_repo.get_by_id.return_value = None
    try:
        await uc.execute(cmd)
    except Exception:
        pass
