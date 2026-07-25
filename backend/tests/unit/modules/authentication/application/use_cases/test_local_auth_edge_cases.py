import pytest
from unittest.mock import AsyncMock, MagicMock

from src.modules.authentication.application.use_cases.local_resend_verification import (
    LocalResendVerificationUseCase,
    LocalResendVerificationCommand,
)
from src.modules.authentication.application.use_cases.local_verify_email import (
    LocalVerifyEmailUseCase,
    LocalVerifyEmailCommand,
)
from src.modules.authentication.application.commands import ClientMetadata
from src.core.exceptions import TurnstileVerificationFailed, RateLimitExceededException
from src.modules.authentication.domain.exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
)
import time


@pytest.fixture
def resend_mocks():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    return {
        "uow": uow,
        "logger": AsyncMock(),
        "email_sender": AsyncMock(),
        "rate_limiter": AsyncMock(),
        "turnstile": AsyncMock(),
        "cache": AsyncMock(),
    }


@pytest.fixture
def verify_mocks(resend_mocks):
    mocks = resend_mocks.copy()
    mocks["analytics"] = MagicMock()
    return mocks


@pytest.mark.asyncio
async def test_resend_turnstile_missing(resend_mocks):
    usecase = LocalResendVerificationUseCase(**resend_mocks)
    cmd = LocalResendVerificationCommand(
        email="test@example.com",
        client_meta=ClientMetadata(ip_address="1.1.1.1", user_agent="abc"),
        is_challenged=True,
        turnstile_token="",
    )
    with pytest.raises(TurnstileVerificationFailed):
        await usecase.execute(cmd)


@pytest.mark.asyncio
async def test_resend_turnstile_invalid(resend_mocks):
    resend_mocks["turnstile"].verify_token.return_value = False
    usecase = LocalResendVerificationUseCase(**resend_mocks)
    cmd = LocalResendVerificationCommand(
        email="test@example.com",
        client_meta=ClientMetadata(ip_address="1.1.1.1", user_agent="abc"),
        is_challenged=True,
        turnstile_token="invalid",
    )
    with pytest.raises(TurnstileVerificationFailed):
        await usecase.execute(cmd)


@pytest.mark.asyncio
async def test_resend_cooldown_challenged(resend_mocks):
    resend_mocks["turnstile"].verify_token.return_value = True
    resend_mocks["cache"].get_dict.return_value = True  # is_cooling_down
    usecase = LocalResendVerificationUseCase(**resend_mocks)
    cmd = LocalResendVerificationCommand(
        email="test@example.com",
        client_meta=ClientMetadata(ip_address="1.1.1.1", user_agent="abc"),
        is_challenged=True,
        turnstile_token="valid",
    )
    with pytest.raises(RateLimitExceededException):
        await usecase.execute(cmd)


@pytest.mark.asyncio
async def test_resend_user_not_found_challenged(resend_mocks):
    resend_mocks["turnstile"].verify_token.return_value = True
    resend_mocks["cache"].get_dict.return_value = False  # Not cooling down
    resend_mocks["uow"].user_query_repo.find_by_email.return_value = None
    usecase = LocalResendVerificationUseCase(**resend_mocks)
    cmd = LocalResendVerificationCommand(
        email="test@example.com",
        client_meta=ClientMetadata(ip_address="1.1.1.1", user_agent="abc"),
        is_challenged=True,
        turnstile_token="valid",
    )

    res = await usecase.execute(cmd)
    assert res[0] > 0
    resend_mocks["rate_limiter"].record_success.assert_called_once()


@pytest.mark.asyncio
async def test_resend_user_verified_challenged(resend_mocks):
    resend_mocks["turnstile"].verify_token.return_value = True
    resend_mocks["cache"].get_dict.return_value = False  # Not cooling down

    user = MagicMock()
    user.is_verified = True
    resend_mocks["uow"].user_query_repo.find_by_email.return_value = user

    usecase = LocalResendVerificationUseCase(**resend_mocks)
    cmd = LocalResendVerificationCommand(
        email="test@example.com",
        client_meta=ClientMetadata(ip_address="1.1.1.1", user_agent="abc"),
        is_challenged=True,
        turnstile_token="valid",
    )

    res = await usecase.execute(cmd)
    assert res[0] > 0
    resend_mocks["rate_limiter"].record_success.assert_called_once()


@pytest.mark.asyncio
async def test_resend_rate_limit_exceeded_challenged(resend_mocks):
    resend_mocks["turnstile"].verify_token.return_value = True
    resend_mocks["cache"].get_dict.return_value = False  # Not cooling down

    user = MagicMock()
    user.is_verified = False
    resend_mocks["uow"].user_query_repo.find_by_email.return_value = user

    resend_mocks["cache"].incr.return_value = 4  # resends > 3

    usecase = LocalResendVerificationUseCase(**resend_mocks)
    cmd = LocalResendVerificationCommand(
        email="test@example.com",
        client_meta=ClientMetadata(ip_address="1.1.1.1", user_agent="abc"),
        is_challenged=True,
        turnstile_token="valid",
    )

    res = await usecase.execute(cmd)
    assert res[0] > 0
    resend_mocks["rate_limiter"].record_failure.assert_called_once()


@pytest.mark.asyncio
async def test_resend_pending_reg_expired_challenged(resend_mocks):
    resend_mocks["turnstile"].verify_token.return_value = True

    # First get_dict call is cooldown (False), second is pending reg (None)
    resend_mocks["cache"].get_dict.side_effect = [False, None]

    user = MagicMock()
    user.is_verified = False
    resend_mocks["uow"].user_query_repo.find_by_email.return_value = user

    resend_mocks["cache"].incr.return_value = 1  # resends <= 3

    usecase = LocalResendVerificationUseCase(**resend_mocks)
    cmd = LocalResendVerificationCommand(
        email="test@example.com",
        client_meta=ClientMetadata(ip_address="1.1.1.1", user_agent="abc"),
        is_challenged=True,
        turnstile_token="valid",
    )

    res = await usecase.execute(cmd)
    assert res[0] > 0
    resend_mocks["rate_limiter"].record_failure.assert_called_once()


# Local Verify Email
@pytest.mark.asyncio
async def test_verify_user_not_found_challenged(verify_mocks):
    verify_mocks["uow"].user_query_repo.find_by_email.return_value = None
    usecase = LocalVerifyEmailUseCase(**verify_mocks)
    cmd = LocalVerifyEmailCommand(
        email="test@example.com",
        otp="123456",
        client_meta=ClientMetadata(ip_address="1.1.1.1", user_agent="abc"),
        is_challenged=True,
    )
    with pytest.raises(InvalidCredentialsException):
        await usecase.execute(cmd)
    verify_mocks["rate_limiter"].record_captcha_success.assert_called_once()


@pytest.mark.asyncio
async def test_verify_user_already_verified_challenged(verify_mocks):
    user = MagicMock()
    user.is_verified = True
    verify_mocks["uow"].user_query_repo.find_by_email.return_value = user
    usecase = LocalVerifyEmailUseCase(**verify_mocks)
    cmd = LocalVerifyEmailCommand(
        email="test@example.com",
        otp="123456",
        client_meta=ClientMetadata(ip_address="1.1.1.1", user_agent="abc"),
        is_challenged=True,
    )
    with pytest.raises(InvalidCredentialsException):
        await usecase.execute(cmd)
    verify_mocks["rate_limiter"].record_captcha_success.assert_called_once()


@pytest.mark.asyncio
async def test_verify_pending_reg_expired_challenged(verify_mocks):
    user = MagicMock()
    user.is_verified = False
    verify_mocks["uow"].user_query_repo.find_by_email.return_value = user
    verify_mocks["cache"].get_dict.return_value = None
    verify_mocks["cache"].increment_and_check_exceeds.return_value = False
    usecase = LocalVerifyEmailUseCase(**verify_mocks)
    cmd = LocalVerifyEmailCommand(
        email="test@example.com",
        otp="123456",
        client_meta=ClientMetadata(ip_address="1.1.1.1", user_agent="abc"),
        is_challenged=True,
    )
    with pytest.raises(InvalidTokenException):
        await usecase.execute(cmd)
    verify_mocks["rate_limiter"].record_captcha_success.assert_called_once()


@pytest.mark.asyncio
async def test_verify_otp_mismatch_challenged(verify_mocks):
    user = MagicMock()
    user.is_verified = False
    verify_mocks["uow"].user_query_repo.find_by_email.return_value = user
    verify_mocks["cache"].get_dict.return_value = {
        "otp": "000000",
        "otp_expires_at": time.time() + 300,
    }
    verify_mocks["cache"].increment_and_check_exceeds.return_value = False
    usecase = LocalVerifyEmailUseCase(**verify_mocks)
    cmd = LocalVerifyEmailCommand(
        email="test@example.com",
        otp="123456",
        client_meta=ClientMetadata(ip_address="1.1.1.1", user_agent="abc"),
        is_challenged=True,
    )
    with pytest.raises(InvalidTokenException):
        await usecase.execute(cmd)
    verify_mocks["rate_limiter"].record_captcha_success.assert_called_once()
