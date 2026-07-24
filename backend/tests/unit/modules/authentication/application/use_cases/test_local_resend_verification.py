from unittest.mock import AsyncMock
import pytest
from uuid import uuid4

from src.modules.authentication.application.commands import (
    LocalResendVerificationCommand,
)
from src.modules.authentication.application.use_cases.local_resend_verification import (
    LocalResendVerificationUseCase,
)
from src.core.exceptions import TurnstileVerificationFailed, RateLimitExceededException
from src.modules.authentication.domain.entities import UserIdentity
from src.shared.domain.value_objects import EmailAddress


@pytest.fixture
def mocks():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    return {
        "uow": uow,
        "logger": AsyncMock(),
        "email_sender": AsyncMock(),
        "cache": AsyncMock(),
        "rate_limiter": AsyncMock(),
        "turnstile": AsyncMock(),
    }


@pytest.fixture
def use_case(mocks):
    return LocalResendVerificationUseCase(
        uow=mocks["uow"],
        logger=mocks["logger"],
        email_sender=mocks["email_sender"],
        cache=mocks["cache"],
        rate_limiter=mocks["rate_limiter"],
        turnstile=mocks["turnstile"],
    )


@pytest.mark.asyncio
async def test_resend_verification_success(use_case, mocks):
    # Setup
    command = LocalResendVerificationCommand(
        email="test@example.com",
        project_id=None,
        client_meta=None,
        is_challenged=False,
        turnstile_token=None,
    )

    mocks["cache"].get_dict.side_effect = [
        None,  # cooldown_key
        {"pending_password_hash": "hash", "pending_name": "Test"},  # existing_payload
    ]
    mocks["cache"].incr.return_value = 1

    # User exists but is NOT verified
    user = UserIdentity(
        id=uuid4(),
        email=EmailAddress("test@example.com"),
        is_verified=False,
        role=None,
        project_id=None,
        name="Test",
        picture=None,
    )
    mocks["uow"].user_query_repo.find_by_email.return_value = user

    expires_in, cooldown = await use_case.execute(command)

    assert expires_in > 0
    assert cooldown > 0
    mocks["email_sender"].send_verification_email.assert_called_once()
    assert (
        mocks["email_sender"].send_verification_email.call_args[0][0]
        == "test@example.com"
    )


@pytest.mark.asyncio
async def test_resend_verification_already_verified(use_case, mocks):
    command = LocalResendVerificationCommand(
        email="test@example.com",
        project_id=None,
        client_meta=None,
        is_challenged=False,
        turnstile_token=None,
    )

    mocks["cache"].get_dict.return_value = None

    # User exists and IS verified
    user = UserIdentity(
        id=uuid4(),
        email=EmailAddress("test@example.com"),
        is_verified=True,
        role=None,
        project_id=None,
        name="Test",
        picture=None,
    )
    mocks["uow"].user_query_repo.find_by_email.return_value = user

    await use_case.execute(command)

    # Email should NOT be sent
    mocks["email_sender"].send_verification_email.assert_not_called()


@pytest.mark.asyncio
async def test_resend_verification_cooldown(use_case, mocks):
    command = LocalResendVerificationCommand(
        email="test@example.com",
        project_id=None,
        client_meta=None,
        is_challenged=False,
        turnstile_token=None,
    )

    # Simulate cooldown active
    mocks["cache"].get_dict.return_value = {"cooling_down": True}

    with pytest.raises(RateLimitExceededException):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_resend_verification_turnstile_fail(use_case, mocks):
    command = LocalResendVerificationCommand(
        email="test@example.com",
        project_id=None,
        client_meta=None,
        is_challenged=True,
        turnstile_token="invalid",
    )

    mocks["turnstile"].verify_token.return_value = False

    with pytest.raises(TurnstileVerificationFailed):
        await use_case.execute(command)
