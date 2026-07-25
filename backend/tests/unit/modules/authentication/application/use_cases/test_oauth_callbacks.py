from unittest.mock import AsyncMock, MagicMock
import pytest
from uuid import uuid4

from src.modules.authentication.application.commands import (
    ProjectUserOAuthCallbackCommand,
    TenantOAuthCallbackCommand,
)
from src.modules.authentication.application.use_cases.project_user_oauth_callback import (
    ProjectUserOAuthCallbackUseCase,
)
from src.modules.authentication.application.use_cases.tenant_oauth_callback import (
    TenantOAuthCallbackUseCase,
)
from src.modules.authentication.domain.entities import UserIdentity
from src.shared.domain.value_objects import EmailAddress
from src.shared.domain.entities import ClientMetadata


@pytest.fixture
def mocks():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    return {
        "uow": uow,
        "email_sender": AsyncMock(),
        "access_token": MagicMock(),
        "claims_provider": AsyncMock(),
        "oauth_service": AsyncMock(),
        "role_provisioning": AsyncMock(),
    }


@pytest.fixture
def project_use_case(mocks):
    return ProjectUserOAuthCallbackUseCase(
        uow=mocks["uow"],
        email_sender=mocks["email_sender"],
        access_token=mocks["access_token"],
        claims_provider=mocks["claims_provider"],
        oauth_service=mocks["oauth_service"],
        role_provisioning=mocks["role_provisioning"],
    )


@pytest.fixture
def tenant_use_case(mocks):
    return TenantOAuthCallbackUseCase(
        uow=mocks["uow"],
        email_sender=mocks["email_sender"],
        access_token=mocks["access_token"],
        claims_provider=mocks["claims_provider"],
        oauth_service=mocks["oauth_service"],
    )


class MockUserInfo:
    def __init__(self):
        self.sub = "oauth_sub_123"
        self.email = EmailAddress("test@example.com")
        self.name = "Test User"
        self.picture = "http://picture.com"


@pytest.mark.asyncio
async def test_project_oauth_exact_match(project_use_case, mocks):
    command = ProjectUserOAuthCallbackCommand(
        provider="google",
        project_id=uuid4(),
        request=MagicMock(),
        client_meta=ClientMetadata(ip_address="1.1.1.1", user_agent="test"),
    )

    mocks["oauth_service"].exchange_code_for_user_info.return_value = MockUserInfo()
    mocks["role_provisioning"].determine_default_role.return_value = "member"

    user = UserIdentity(
        id=uuid4(),
        email=EmailAddress("test@example.com"),
        is_verified=True,
        project_id=command.project_id,
        name="Test",
        picture=None,
    )

    # Provider match found
    mocks["uow"].user_query_repo.find_by_oauth.return_value = user
    mocks["uow"].refresh_token_repo.create.return_value = "refresh_token"
    mocks["claims_provider"].get_custom_claims.return_value = {}
    mocks["access_token"].create.return_value = "access_token"
    mocks["uow"].refresh_token_repo.get_active_sessions.return_value = []

    user_ret, rt, at, is_new, fallback = await project_use_case.execute(command)

    assert user_ret.id == user.id
    assert is_new is False
    assert rt == "refresh_token"
    assert at == "access_token"


@pytest.mark.asyncio
async def test_project_oauth_email_match(project_use_case, mocks):
    command = ProjectUserOAuthCallbackCommand(
        provider="google",
        project_id=uuid4(),
        request=MagicMock(),
        client_meta=ClientMetadata(ip_address="1.1.1.1", user_agent="test"),
    )

    mocks["oauth_service"].exchange_code_for_user_info.return_value = MockUserInfo()
    mocks["role_provisioning"].determine_default_role.return_value = "member"

    user = UserIdentity(
        id=uuid4(),
        email=EmailAddress("test@example.com"),
        is_verified=True,
        project_id=command.project_id,
        name="Test",
        picture=None,
    )

    # Provider match NOT found, but email match IS found
    mocks["uow"].user_query_repo.find_by_oauth.return_value = None
    mocks["uow"].user_query_repo.find_by_email.return_value = user
    mocks["uow"].refresh_token_repo.create.return_value = "refresh_token"
    mocks["claims_provider"].get_custom_claims.return_value = {}
    mocks["access_token"].create.return_value = "access_token"
    mocks["uow"].refresh_token_repo.get_active_sessions.return_value = []

    user_ret, rt, at, is_new, fallback = await project_use_case.execute(command)

    assert user_ret.id == user.id
    assert is_new is False
    mocks["uow"].user_command_repo.link_oauth_account.assert_called_once()


@pytest.mark.asyncio
async def test_project_oauth_new_user(project_use_case, mocks):
    command = ProjectUserOAuthCallbackCommand(
        provider="google", project_id=uuid4(), request=MagicMock(), client_meta=None
    )

    mocks["oauth_service"].exchange_code_for_user_info.return_value = MockUserInfo()
    mocks["role_provisioning"].determine_default_role.return_value = "member"

    new_user = UserIdentity(
        id=uuid4(),
        email=EmailAddress("test@example.com"),
        is_verified=True,
        project_id=command.project_id,
        name="Test",
        picture=None,
    )

    # NOT found anywhere
    mocks["uow"].user_query_repo.find_by_oauth.return_value = None
    mocks["uow"].user_query_repo.find_by_email.return_value = None
    mocks["uow"].user_command_repo.create_user_with_oauth.return_value = new_user
    mocks["uow"].refresh_token_repo.create.return_value = "refresh_token"
    mocks["claims_provider"].get_custom_claims.return_value = {}
    mocks["access_token"].create.return_value = "access_token"

    user_ret, rt, at, is_new, fallback = await project_use_case.execute(command)

    assert user_ret.id == new_user.id
    assert is_new is True
    mocks["uow"].user_command_repo.create_user_with_oauth.assert_called_once()


@pytest.mark.asyncio
async def test_tenant_oauth_exact_match(tenant_use_case, mocks):
    command = TenantOAuthCallbackCommand(
        provider="google",
        request=MagicMock(),
        client_meta=ClientMetadata(ip_address="1.1.1.1", user_agent="test"),
    )

    mocks["oauth_service"].exchange_code_for_user_info.return_value = MockUserInfo()

    user = UserIdentity(
        id=uuid4(),
        email=EmailAddress("test@example.com"),
        is_verified=True,
        project_id=None,
        name="Test",
        picture=None,
    )

    # Provider match found
    mocks["uow"].user_query_repo.find_by_oauth.return_value = user
    mocks["uow"].refresh_token_repo.create.return_value = "refresh_token"
    mocks["claims_provider"].get_custom_claims.return_value = {}
    mocks["access_token"].create.return_value = "access_token"
    mocks["uow"].refresh_token_repo.get_active_sessions.return_value = []

    user_ret, rt, at, is_new = await tenant_use_case.execute(command)

    assert user_ret.id == user.id
    assert is_new is False
