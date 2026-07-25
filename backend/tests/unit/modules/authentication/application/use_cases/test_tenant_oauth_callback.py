import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.modules.authentication.application.commands import TenantOAuthCallbackCommand
from src.modules.authentication.application.use_cases.tenant_oauth_callback import TenantOAuthCallbackUseCase
from src.modules.authorization.domain.enums import GlobalRole
from src.modules.authentication.domain.entities import UserIdentity
from src.shared.domain.value_objects import EmailAddress

@pytest.fixture
def mocks():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    claims_provider = AsyncMock()
    claims_provider.get_custom_claims.return_value = {}
    return {
        "uow": uow,
        "email_sender": AsyncMock(),
        "access_token": MagicMock(),
        "claims_provider": claims_provider,
        "oauth_service": AsyncMock(),
    }

@pytest.fixture
def use_case(mocks):
    return TenantOAuthCallbackUseCase(
        uow=mocks["uow"],
        email_sender=mocks["email_sender"],
        access_token=mocks["access_token"],
        claims_provider=mocks["claims_provider"],
        oauth_service=mocks["oauth_service"]
    )

@pytest.mark.asyncio
async def test_tenant_oauth_callback_exact_match(use_case, mocks):
    command = TenantOAuthCallbackCommand(
        provider="google",
        request=MagicMock(),
        client_meta=None
    )
    
    user_info = MagicMock()
    user_info.sub = "sub123"
    user_info.email.value = "tenant@example.com"
    user_info.name = "Tenant User"
    user_info.picture = "pic.jpg"
    mocks["oauth_service"].exchange_code_for_user_info.return_value = user_info
    
    user = UserIdentity(
        id=uuid4(),
        email=EmailAddress("tenant@example.com"),
        is_verified=True,
        role=GlobalRole.TENANT,
        project_id=None,
        name="Tenant User",
        picture=None
    )
    user.deleted_at = None
    mocks["uow"].user_query_repo.find_by_oauth.return_value = user
    
    mocks["uow"].refresh_token_repo.create.return_value = "refresh_token"
    mocks["access_token"].create.return_value = "access_token"
    
    res_user, rt, at, is_new = await use_case.execute(command)
    assert res_user.id == user.id
    assert rt == "refresh_token"
    assert at == "access_token"
    assert is_new is False
    mocks["uow"].user_command_repo.update_oauth_profile.assert_called_once()

@pytest.mark.asyncio
async def test_tenant_oauth_callback_email_match(use_case, mocks):
    command = TenantOAuthCallbackCommand(
        provider="google",
        request=MagicMock(),
        client_meta=None
    )
    
    user_info = MagicMock()
    user_info.sub = "sub123"
    user_info.email.value = "tenant2@example.com"
    user_info.name = "Tenant User"
    user_info.picture = "pic.jpg"
    mocks["oauth_service"].exchange_code_for_user_info.return_value = user_info
    
    mocks["uow"].user_query_repo.find_by_oauth.return_value = None
    
    user = UserIdentity(
        id=uuid4(),
        email=EmailAddress("tenant2@example.com"),
        is_verified=True,
        role=GlobalRole.TENANT,
        project_id=None,
        name="Tenant User",
        picture=None
    )
    user.deleted_at = None
    mocks["uow"].user_query_repo.find_by_email.return_value = user
    
    mocks["uow"].refresh_token_repo.create.return_value = "refresh_token"
    mocks["access_token"].create.return_value = "access_token"
    
    res_user, rt, at, is_new = await use_case.execute(command)
    assert res_user.id == user.id
    assert is_new is False
    mocks["uow"].user_command_repo.link_oauth_account.assert_called_once()

@pytest.mark.asyncio
async def test_tenant_oauth_callback_new_user(use_case, mocks):
    command = TenantOAuthCallbackCommand(
        provider="google",
        request=MagicMock(),
        client_meta=None
    )
    
    user_info = MagicMock()
    user_info.sub = "sub123"
    user_info.email.value = "new@example.com"
    user_info.name = "New Tenant"
    user_info.picture = "pic.jpg"
    mocks["oauth_service"].exchange_code_for_user_info.return_value = user_info
    
    mocks["uow"].user_query_repo.find_by_oauth.return_value = None
    mocks["uow"].user_query_repo.find_by_email.return_value = None
    
    new_user = UserIdentity(
        id=uuid4(),
        email=EmailAddress("new@example.com"),
        is_verified=True,
        role=GlobalRole.TENANT,
        project_id=None,
        name="New Tenant",
        picture=None
    )
    mocks["uow"].user_command_repo.create_user_with_oauth.return_value = new_user
    mocks["uow"].refresh_token_repo.create.return_value = "refresh_token"
    mocks["access_token"].create.return_value = "access_token"
    
    res_user, rt, at, is_new = await use_case.execute(command)
    assert res_user.id == new_user.id
    assert is_new is True
    mocks["email_sender"].send_welcome_email.assert_called_once()
