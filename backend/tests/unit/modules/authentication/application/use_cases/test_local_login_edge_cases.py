import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta

from src.modules.authentication.application.use_cases.local_login import (
    LocalLoginUseCase,
    LocalLoginCommand,
)
from src.modules.authentication.application.commands import ClientMetadata


@pytest.fixture
def base_mocks():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    return {
        "uow": uow,
        "hasher": AsyncMock(),
        "logger": AsyncMock(),
        "email_sender": AsyncMock(),
        "access_token": MagicMock(),
        "claims_provider": AsyncMock(),
        "rate_limiter": AsyncMock(),
        "turnstile": AsyncMock(),
        "analytics": MagicMock(),
        "core_settings": MagicMock(),
    }


@pytest.mark.asyncio
async def test_local_login_soft_deleted_user(base_mocks):
    user_identity = MagicMock()
    user_identity.deleted_at = datetime.now(timezone.utc)
    user_identity.is_verified = True
    user_identity.updated_at = None

    base_mocks["uow"].user_query_repo.find_by_email.return_value = user_identity
    base_mocks["hasher"].verify_password.return_value = True
    base_mocks["claims_provider"].get_custom_claims.return_value = {}

    usecase = LocalLoginUseCase(**base_mocks)
    cmd = LocalLoginCommand(
        email="test@example.com",
        password="pwd",
        client_meta=ClientMetadata(ip_address="1.1.1.1", user_agent="abc"),
    )

    await usecase.execute(cmd)

    base_mocks["uow"].user_command_repo.undelete_user.assert_called_once_with(
        user_identity.id
    )
    base_mocks["email_sender"].send_account_restored_email.assert_called_once()


@pytest.mark.asyncio
async def test_local_login_new_device(base_mocks):
    user_identity = MagicMock()
    user_identity.deleted_at = None
    user_identity.is_verified = True
    user_identity.updated_at = datetime.now(timezone.utc) - timedelta(
        days=1
    )  # old update, so not first login

    base_mocks["uow"].user_query_repo.find_by_email.return_value = user_identity
    base_mocks["hasher"].verify_password.return_value = True
    base_mocks["claims_provider"].get_custom_claims.return_value = {}

    # Mock active sessions
    sess = MagicMock()
    sess.ip_address = "2.2.2.2"
    sess.user_agent = "old"
    base_mocks["uow"].refresh_token_repo.get_active_sessions.return_value = [sess]

    usecase = LocalLoginUseCase(**base_mocks)
    cmd = LocalLoginCommand(
        email="test@example.com",
        password="pwd",
        client_meta=ClientMetadata(ip_address="1.1.1.1", user_agent="abc"),
    )

    await usecase.execute(cmd)

    base_mocks["email_sender"].send_login_detected_email.assert_called_once()
