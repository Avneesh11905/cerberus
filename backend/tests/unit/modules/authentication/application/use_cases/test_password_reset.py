from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from uuid import uuid4

from src.modules.authentication.application.commands import (
    PasswordResetRequestCommand,
    PasswordResetExecuteCommand,
)
from src.modules.authentication.application.use_cases.password_reset_request import (
    PasswordResetRequestUseCase,
)
from src.modules.authentication.application.use_cases.password_reset_execute import (
    PasswordResetExecuteUseCase,
)
from src.modules.authentication.domain.entities import UserIdentity
from src.shared.domain.value_objects import EmailAddress


@pytest.fixture
def mocks():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    return {
        "uow": uow,
        "cache": AsyncMock(),
        "email_sender": AsyncMock(),
        "frontend_url": "https://test.cerberus.com",
        "rate_limiter": AsyncMock(),
        "turnstile": AsyncMock(),
        "hasher": AsyncMock(),
        "analytics": MagicMock(),
    }


@pytest.fixture
def request_use_case(mocks):
    return PasswordResetRequestUseCase(
        uow=mocks["uow"],
        cache=mocks["cache"],
        email_sender=mocks["email_sender"],
        frontend_url=mocks["frontend_url"],
        rate_limiter=mocks["rate_limiter"],
        turnstile=mocks["turnstile"],
    )


@pytest.fixture
def execute_use_case(mocks):
    return PasswordResetExecuteUseCase(
        uow=mocks["uow"],
        cache=mocks["cache"],
        hasher=mocks["hasher"],
        rate_limiter=mocks["rate_limiter"],
        turnstile=mocks["turnstile"],
        analytics=mocks["analytics"],
    )


@pytest.mark.asyncio
async def test_password_reset_request_success(request_use_case, mocks):
    command = PasswordResetRequestCommand(
        email="test@example.com",
        project_id=None,
        client_meta=None,
        is_challenged=False,
        turnstile_token=None,
    )

    user_id = uuid4()
    user = UserIdentity(
        id=user_id,
        email=EmailAddress("test@example.com"),
        is_verified=True,
        role=None,
        project_id=None,
        name="Test",
        picture=None,
    )
    mocks["uow"].user_query_repo.find_by_email.return_value = user

    with patch("secrets.token_urlsafe", return_value="mock_token"):
        await request_use_case.execute(command)

    mocks["cache"].set_string.assert_called_once_with(
        "pwd_reset:mock_token", str(user_id), 900
    )
    mocks["email_sender"].send_password_reset_email.assert_called_once()
    assert (
        "mock_token" in mocks["email_sender"].send_password_reset_email.call_args[0][1]
    )


@pytest.mark.asyncio
async def test_password_reset_request_user_not_found(request_use_case, mocks):
    command = PasswordResetRequestCommand(
        email="unknown@example.com",
        project_id=None,
        client_meta=None,
        is_challenged=False,
        turnstile_token=None,
    )

    mocks["uow"].user_query_repo.find_by_email.return_value = None

    # Should silently succeed
    await request_use_case.execute(command)

    mocks["email_sender"].send_password_reset_email.assert_not_called()


@pytest.mark.asyncio
async def test_password_reset_execute_success(execute_use_case, mocks):
    command = PasswordResetExecuteCommand(
        token="mock_token",
        new_password="NewPassword123!",
        client_meta=None,
        is_challenged=False,
        turnstile_token=None,
    )

    user_id = uuid4()
    mocks["cache"].get_string.return_value = str(user_id)
    mocks["hasher"].hash_password.return_value = "hashed_new_password"

    result = await execute_use_case.execute(command)

    assert result is True
    mocks["uow"].user_command_repo.update_password.assert_called_once_with(
        user_id, "hashed_new_password"
    )
    mocks["uow"].refresh_token_repo.revoke_all_for_user.assert_called_once_with(user_id)
    mocks["cache"].delete_key.assert_called_once_with("pwd_reset:mock_token")


@pytest.mark.asyncio
async def test_password_reset_execute_invalid_token(execute_use_case, mocks):
    command = PasswordResetExecuteCommand(
        token="invalid_token",
        new_password="NewPassword123!",
        client_meta=None,
        is_challenged=False,
        turnstile_token=None,
    )

    mocks["cache"].get_string.return_value = None

    result = await execute_use_case.execute(command)

    assert result is False
    mocks["uow"].user_command_repo.update_password.assert_not_called()
