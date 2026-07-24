from unittest.mock import AsyncMock, MagicMock
import pytest
from uuid import uuid4
import time

from src.modules.authentication.application.commands import LocalVerifyEmailCommand
from src.modules.authentication.application.use_cases.local_verify_email import (
    LocalVerifyEmailUseCase,
)
from src.modules.authentication.domain.exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
)
from src.modules.authentication.domain.entities import UserIdentity
from src.shared.domain.value_objects import EmailAddress
from src.core.exceptions import RateLimitExceededException
from src.modules.authentication.application.utils import hash_otp


@pytest.fixture
def mocks():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    return {
        "uow": uow,
        "cache": AsyncMock(),
        "logger": AsyncMock(),
        "email_sender": AsyncMock(),
        "rate_limiter": AsyncMock(),
        "turnstile": AsyncMock(),
        "analytics": MagicMock(),
    }


@pytest.fixture
def use_case(mocks):
    return LocalVerifyEmailUseCase(
        uow=mocks["uow"],
        cache=mocks["cache"],
        logger=mocks["logger"],
        email_sender=mocks["email_sender"],
        rate_limiter=mocks["rate_limiter"],
        turnstile=mocks["turnstile"],
        analytics=mocks["analytics"],
    )


@pytest.mark.asyncio
async def test_local_verify_success(use_case, mocks):
    command = LocalVerifyEmailCommand(
        email="test@example.com", otp="123456", project_id=None, client_meta=None
    )

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
    mocks["cache"].increment_and_check_exceeds.return_value = False

    # Correct OTP
    payload = {
        "otp_expires_at": int(time.time()) + 100,
        "otp": hash_otp("123456"),
        "pending_name": "Test",
        "pending_password_hash": "hash",
    }
    mocks["cache"].get_dict.return_value = payload
    mocks["uow"].refresh_token_repo.create.return_value = "token"

    user_ret, token = await use_case.execute(command)

    assert user_ret.id == user.id
    assert token == "token"
    mocks["uow"].user_command_repo.verify_user_email.assert_called_once()
    mocks["email_sender"].send_welcome_email.assert_called_once()


@pytest.mark.asyncio
async def test_local_verify_user_not_found(use_case, mocks):
    command = LocalVerifyEmailCommand(
        email="unknown@example.com", otp="123456", project_id=None, client_meta=None
    )

    mocks["uow"].user_query_repo.find_by_email.return_value = None

    with pytest.raises(InvalidCredentialsException):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_local_verify_already_verified(use_case, mocks):
    command = LocalVerifyEmailCommand(
        email="test@example.com", otp="123456", project_id=None, client_meta=None
    )

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

    with pytest.raises(InvalidCredentialsException):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_local_verify_rate_limited(use_case, mocks):
    command = LocalVerifyEmailCommand(
        email="test@example.com", otp="123456", project_id=None, client_meta=None
    )

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
    mocks["cache"].increment_and_check_exceeds.return_value = True

    with pytest.raises(RateLimitExceededException):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_local_verify_invalid_otp(use_case, mocks):
    command = LocalVerifyEmailCommand(
        email="test@example.com",
        otp="111111",  # Wrong
        project_id=None,
        client_meta=None,
    )

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
    mocks["cache"].increment_and_check_exceeds.return_value = False

    # Correct OTP is 123456
    payload = {
        "otp_expires_at": int(time.time()) + 100,
        "otp": hash_otp("123456"),
        "pending_name": "Test",
    }
    mocks["cache"].get_dict.return_value = payload

    with pytest.raises(InvalidTokenException):
        await use_case.execute(command)
