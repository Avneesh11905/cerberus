from unittest.mock import AsyncMock, MagicMock  # noqa: E402
from uuid import uuid4  # noqa: E402

import pytest  # noqa: E402

from src.core.exceptions import TurnstileVerificationFailed  # noqa: E402
from src.modules.authentication.application.commands import ClientMetadata  # noqa: E402
from src.modules.authentication.application.use_cases.local_login import (  # noqa: E402
    LocalLoginCommand,
    LocalLoginUseCase,
)
from src.modules.authentication.application.use_cases.local_resend_verification import (  # noqa: E402
    LocalResendVerificationCommand,
    LocalResendVerificationUseCase,
)
from src.modules.authentication.domain.exceptions import (  # noqa: E402
    InvalidCredentialsException,
    UnverifiedEmailException,
)


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
        "cache": AsyncMock(),
    }


@pytest.mark.asyncio
async def test_local_login_turnstile_fail(base_mocks):
    base_mocks.pop("cache")
    base_mocks["turnstile"].verify_token.return_value = False
    usecase = LocalLoginUseCase(**base_mocks)
    cmd = LocalLoginCommand(
        email="test@example.com",
        password="pwd",
        client_meta=ClientMetadata(ip_address="1.1.1.1", user_agent="abc"),
        is_challenged=True,
        turnstile_token="abc",
    )
    with pytest.raises(TurnstileVerificationFailed):
        await usecase.execute(cmd)


@pytest.mark.asyncio
async def test_local_login_unverified(base_mocks):
    base_mocks.pop("cache")
    base_mocks["turnstile"].verify.return_value = True
    user_identity = MagicMock()
    user_identity.updated_at = None
    user_identity.is_verified = False
    base_mocks["uow"].user_query_repo.find_by_email.return_value = user_identity
    base_mocks["hasher"].verify_password.return_value = True

    usecase = LocalLoginUseCase(**base_mocks)
    cmd = LocalLoginCommand(
        email="test@example.com",
        password="pwd",
        client_meta=ClientMetadata(ip_address="1.1.1.1", user_agent="abc"),
    )
    with pytest.raises(UnverifiedEmailException):
        await usecase.execute(cmd)


@pytest.mark.asyncio
async def test_local_login_invalid_password(base_mocks):
    base_mocks.pop("cache")
    base_mocks["turnstile"].verify.return_value = True
    user_identity = MagicMock()
    user_identity.updated_at = None
    user_identity.is_verified = True
    base_mocks["uow"].user_query_repo.find_by_email.return_value = user_identity
    base_mocks["hasher"].verify_password.return_value = False

    usecase = LocalLoginUseCase(**base_mocks)
    cmd = LocalLoginCommand(
        email="test@example.com",
        password="pwd",
        client_meta=ClientMetadata(ip_address="1.1.1.1", user_agent="abc"),
    )
    with pytest.raises(InvalidCredentialsException):
        await usecase.execute(cmd)


@pytest.mark.asyncio
async def test_local_resend_verification_turnstile_fail(base_mocks):
    base_mocks["turnstile"].verify_token.return_value = False
    usecase = LocalResendVerificationUseCase(
        uow=base_mocks["uow"],
        email_sender=base_mocks["email_sender"],
        logger=base_mocks["logger"],
        turnstile=base_mocks["turnstile"],
        cache=AsyncMock(),
        rate_limiter=base_mocks["rate_limiter"],
    )
    cmd = LocalResendVerificationCommand(
        email="test@example.com", is_challenged=True, turnstile_token="abc"
    )
    with pytest.raises(TurnstileVerificationFailed):
        await usecase.execute(cmd)


from src.modules.authentication.infrastructure.database.repositories.refresh_token_repository import (  # noqa: E402
    DBRefreshTokenRepositoryAdapter,
)


@pytest.mark.asyncio
async def test_refresh_token_repo_revoke_by_family():
    session = AsyncMock()
    session.add = MagicMock()
    result_mock = MagicMock()
    result_mock.scalars.return_value = []
    session.execute.return_value = result_mock
    repo = DBRefreshTokenRepositoryAdapter(session, lifetime_days=30)
    await repo.revoke_by_family(uuid4())
    session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_refresh_token_repo_revoke_all_for_user():
    session = AsyncMock()
    session.add = MagicMock()
    result_mock = MagicMock()
    mock_token = MagicMock()
    result_mock.scalars.return_value = [mock_token]
    session.execute.return_value = result_mock
    repo = DBRefreshTokenRepositoryAdapter(session, lifetime_days=30)
    await repo.revoke_all_for_user(uuid4())
    assert session.execute.call_count == 2  # 1 for select, 1 for revoke family
