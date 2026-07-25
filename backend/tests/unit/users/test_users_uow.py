import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.modules.users.infrastructure.database.repositories.users_uow import (
    SQLUserUnitOfWork,
)


@pytest.mark.asyncio
async def test_sql_user_uow_aenter():
    mock_session_factory = MagicMock()
    mock_session = AsyncMock()
    mock_session_factory.return_value = mock_session
    uow = SQLUserUnitOfWork(mock_session_factory)

    with (
        patch("src.core.config.get_settings") as mock_get_settings,
        patch("src.core.container.app_container") as mock_app_container,
        patch(
            "src.modules.users.infrastructure.database.repositories.users_uow.DBRefreshTokenRepositoryAdapter"
        ) as mock_db_refresh,
        patch(
            "src.modules.users.infrastructure.database.repositories.users_uow.SQLUserProfileRepositoryAdapter"
        ) as mock_sql_profile,
    ):
        mock_settings = MagicMock()
        mock_settings.token.REFRESH_TOKEN_LIFETIME_DAYS = 30
        mock_get_settings.return_value = mock_settings

        await uow.__aenter__()

        mock_db_refresh.assert_called_once_with(
            uow.session, 30, mock_app_container.cache_adapter
        )
        mock_sql_profile.assert_called_once_with(uow.session, uow.refresh_repo)
        assert uow.refresh_repo == mock_db_refresh.return_value
        assert uow.profile_repo == mock_sql_profile.return_value
