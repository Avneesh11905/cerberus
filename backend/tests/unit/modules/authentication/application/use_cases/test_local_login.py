from unittest.mock import AsyncMock, MagicMock
import pytest
from uuid import uuid4

from src.modules.authentication.application.commands import LocalLoginCommand
from src.modules.authentication.application.use_cases.local_login import (
    LocalLoginUseCase,
)
from src.modules.authentication.domain.exceptions import (
    InvalidCredentialsException,
    UnverifiedEmailException,
)
from src.modules.authentication.domain.entities import UserIdentity
from src.shared.domain.value_objects import EmailAddress
from src.core.config import get_settings


@pytest.fixture
def mocks():
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
        "core_settings": get_settings().core,
    }


@pytest.fixture
def use_case(mocks):
    return LocalLoginUseCase(
        uow=mocks["uow"],
        hasher=mocks["hasher"],
        logger=mocks["logger"],
        email_sender=mocks["email_sender"],
        access_token=mocks["access_token"],
        claims_provider=mocks["claims_provider"],
        rate_limiter=mocks["rate_limiter"],
        turnstile=mocks["turnstile"],
        analytics=mocks["analytics"],
        core_settings=mocks["core_settings"],
    )


@pytest.mark.asyncio
async def test_local_login_success(use_case, mocks):
    command = LocalLoginCommand(
        email="test@example.com",
        password="Password123!",
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
    mocks["uow"].user_query_repo.find_password_hash.return_value = "hashed_password"
    mocks["hasher"].verify_password.return_value = True
    mocks["uow"].refresh_token_repo.create.return_value = "refresh_token"
    mocks["access_token"].create.return_value = "access_token"
    mocks["claims_provider"].get_custom_claims.return_value = {}
    mocks["uow"].user_query_repo.find_by_id.return_value = user
    mocks["uow"].refresh_token_repo.get_active_sessions.return_value = []

    profile, rt, at = await use_case.execute(command)

    assert profile.id == user_id
    assert rt == "refresh_token"
    assert at == "access_token"
    mocks["analytics"].record_event.assert_called_once()
    assert mocks["analytics"].record_event.call_args[1]["event_type"] == "LOGIN_SUCCESS"


@pytest.mark.asyncio
async def test_local_login_user_not_found(use_case, mocks):
    command = LocalLoginCommand(
        email="unknown@example.com",
        password="Password123!",
        project_id=None,
        client_meta=None,
        is_challenged=True,
        turnstile_token="test_token",
    )

    mocks["uow"].user_query_repo.find_by_email.return_value = None
    mocks["turnstile"].verify_token.return_value = True

    with pytest.raises(InvalidCredentialsException):
        await use_case.execute(command)

    mocks["hasher"].dummy_verify.assert_called_once()


@pytest.mark.asyncio
async def test_local_login_unverified_email(use_case, mocks):
    command = LocalLoginCommand(
        email="unverified@example.com",
        password="Password123!",
        project_id=None,
        client_meta=None,
        is_challenged=True,
        turnstile_token="test_token",
    )

    user = UserIdentity(
        id=uuid4(),
        email=EmailAddress("unverified@example.com"),
        is_verified=False,
        role=None,
        project_id=None,
        name="Test",
        picture=None,
    )
    mocks["uow"].user_query_repo.find_by_email.return_value = user
    mocks["turnstile"].verify_token.return_value = True

    with pytest.raises(UnverifiedEmailException):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_local_login_invalid_password(use_case, mocks):
    command = LocalLoginCommand(
        email="test@example.com",
        password="WrongPassword123!",
        project_id=None,
        client_meta=None,
        is_challenged=True,
        turnstile_token="test_token",
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
    mocks["uow"].user_query_repo.find_password_hash.return_value = "hashed_password"
    mocks["hasher"].verify_password.return_value = False
    mocks["turnstile"].verify_token.return_value = True

    with pytest.raises(InvalidCredentialsException):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_local_login_oauth_only(use_case, mocks):
    command = LocalLoginCommand(
        email="oauth@example.com",
        password="Password123!",
        project_id=None,
        client_meta=None,
        is_challenged=True,
        turnstile_token="test_token",
    )

    user = UserIdentity(
        id=uuid4(),
        email=EmailAddress("oauth@example.com"),
        is_verified=True,
        role=None,
        project_id=None,
        name="Test",
        picture=None,
    )
    mocks["uow"].user_query_repo.find_by_email.return_value = user
    mocks["uow"].user_query_repo.find_password_hash.return_value = None
    mocks["turnstile"].verify_token.return_value = True

    with pytest.raises(InvalidCredentialsException):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_local_login_superadmin_heal(use_case, mocks, monkeypatch):
    monkeypatch.setattr(mocks["core_settings"], "SUPERADMIN_EMAIL", "super@example.com")
    command = LocalLoginCommand(
        email="super@example.com",
        password="Password123!",
        project_id=None,
        client_meta=None,
        is_challenged=False,
        turnstile_token=None,
    )
    user_id = uuid4()
    user = UserIdentity(
        id=user_id,
        email=EmailAddress("super@example.com"),
        is_verified=True,
        role=None,
        project_id=None,
        name="Test",
        picture=None,
    )
    mocks["uow"].user_query_repo.find_by_email.return_value = user
    mocks["uow"].user_query_repo.find_password_hash.return_value = "hashed_password"
    mocks["hasher"].verify_password.return_value = True
    mocks["uow"].refresh_token_repo.create.return_value = "refresh_token"
    mocks["access_token"].create.return_value = "access_token"
    mocks["claims_provider"].get_custom_claims.return_value = {}
    mocks["uow"].user_query_repo.find_by_id.return_value = user
    mocks["uow"].refresh_token_repo.get_active_sessions.return_value = []

    await use_case.execute(command)
    mocks["uow"].user_command_repo.update_role.assert_called_once()
