import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def uow_mock():
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.project_query_repo = MagicMock()
    uow.project_command_repo = MagicMock()
    return uow


@pytest.mark.asyncio
async def test_password_reset_request():
    from src.modules.authentication.application.use_cases.password_reset_request import (
        PasswordResetRequestUseCase,
    )
    from src.modules.authentication.application.commands import (
        PasswordResetRequestCommand,
    )

    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.user_query_repo = MagicMock()
    uow.project_query_repo = MagicMock()

    cache = MagicMock()
    cache.set_string = AsyncMock()
    email_sender = MagicMock()
    email_sender.send_password_reset_email = AsyncMock()

    rate_limiter = MagicMock()
    rate_limiter.record_failure = AsyncMock()
    rate_limiter.record_success = AsyncMock()

    turnstile = MagicMock()
    turnstile.verify_token = AsyncMock(return_value=True)

    uc = PasswordResetRequestUseCase(
        uow=uow,
        cache=cache,
        email_sender=email_sender,
        frontend_url="http://frontend",
        rate_limiter=rate_limiter,
        turnstile=turnstile,
    )

    # 1. User doesn't exist (silently returns)
    uow.user_query_repo.find_by_email = AsyncMock(return_value=None)
    await uc.execute(
        PasswordResetRequestCommand(
            email="test@test.com",
            is_challenged=True,
            turnstile_token="token",
            client_meta=MagicMock(ip_address="1.1.1.1"),
        )
    )
    rate_limiter.record_success.assert_called_once()

    import uuid

    proj_id = uuid.uuid4()

    # 2. User exists
    user = MagicMock()
    user.id = uuid.uuid4()
    user.is_verified = True
    user.project_id = proj_id
    uow.user_query_repo.find_by_email = AsyncMock(return_value=user)
    project = MagicMock()
    project.frontend_url.value = "http://project"
    uow.project_query_repo.get_by_id = AsyncMock(return_value=project)

    await uc.execute(
        PasswordResetRequestCommand(
            email="test@test.com", is_challenged=False, project_id=proj_id
        )
    )
    cache.set_string.assert_called_once()
    email_sender.send_password_reset_email.assert_called_once()
