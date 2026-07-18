import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
from fastapi import Request

from src.modules.auth.authentication.adapters.security.oauth_service import (
    OAuthServiceAdapter,
)
from src.modules.auth.authentication.domain.entities import OAuthUserInfo
from src.modules.auth.authentication.domain.exceptions import OAuthFailedException
from src.modules.projects.domain.entities import ProjectEntity


@pytest.fixture
def mock_project_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_encryption():
    enc = Mock()
    enc.decrypt.return_value = "decrypted-secret"
    return enc


@pytest.fixture
def oauth_adapter(mock_project_repo, mock_encryption):
    return OAuthServiceAdapter(
        project_query_repo=mock_project_repo, encryption_adapter=mock_encryption
    )


@pytest.mark.asyncio
async def test_get_authorization_url_tenant(oauth_adapter):
    request = Mock(spec=Request)

    # We mock _get_client so we don't need to do actual HTTP for well-known endpoints in unit tests
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.headers = {
        "location": "https://accounts.google.com/o/oauth2/v2/auth?..."
    }
    mock_client.authorize_redirect.return_value = mock_response

    oauth_adapter._get_client = AsyncMock(return_value=mock_client)

    url = await oauth_adapter.get_authorization_url(
        provider="google",
        project_id=None,
        request=request,
        redirect_uri="http://localhost/callback",
        state="somestate",
        session=AsyncMock(),
    )

    assert url == "https://accounts.google.com/o/oauth2/v2/auth?..."
    mock_client.authorize_redirect.assert_called_once_with(
        request, "http://localhost/callback", state="somestate"
    )


@pytest.mark.asyncio
async def test_exchange_code_tenant(oauth_adapter, monkeypatch):
    request = Mock(spec=Request)

    mock_client = AsyncMock()
    mock_client.authorize_access_token.return_value = {
        "access_token": "token",
        "userinfo": {"sub": "123", "email": "test@example.com", "email_verified": True},
    }
    oauth_adapter._get_client = AsyncMock(return_value=mock_client)

    # Mock the parser from registry
    from src.modules.auth.authentication.infrastructure.oauth import PARSERS

    mock_parser = AsyncMock(
        return_value=OAuthUserInfo(
            sub="123", email="test@example.com", provider="google"
        )
    )
    monkeypatch.setitem(PARSERS, "google", mock_parser)

    user_info = await oauth_adapter.exchange_code_for_user_info(
        provider="google", project_id=None, request=request, session=AsyncMock()
    )

    assert user_info.email == "test@example.com"
    assert user_info.sub == "123"
    mock_client.authorize_access_token.assert_called_once_with(request)


@pytest.mark.asyncio
async def test_get_client_project_dynamic(
    oauth_adapter, mock_project_repo, mock_encryption
):
    project_id = uuid4()
    from datetime import datetime, timezone

    project = ProjectEntity(
        id=project_id,
        tenant_id=uuid4(),
        name="Test",
        private_key="priv",
        public_key="pub",
        api_key_hash="hash",
        created_at=datetime.now(timezone.utc),
        oauth_config={
            "google": {
                "enabled": True,
                "client_id": "test-client-id",
                "client_secret": "encrypted-secret",
            }
        },
    )
    mock_project_repo.get_by_id.return_value = project

    from src.modules.auth.authentication.infrastructure.oauth.registry import (
        oauth_registry,
        ProviderMetadata,
    )

    oauth_registry.metadata["google"] = ProviderMetadata(
        key="google",
        display_name="Google",
        authlib_config={
            "server_metadata_url": "https://accounts.google.com/.well-known/openid-configuration"
        },
    )

    # Get dynamic client
    client = await oauth_adapter._get_client("google", project_id, AsyncMock())

    mock_encryption.decrypt.assert_called_once_with("encrypted-secret")
    assert client.client_id == "test-client-id"
    assert client.client_secret == "decrypted-secret"
    assert client.name == "google"


@pytest.mark.asyncio
async def test_get_client_project_not_enabled(oauth_adapter, mock_project_repo):
    project_id = uuid4()
    from datetime import datetime, timezone

    project = ProjectEntity(
        id=project_id,
        tenant_id=uuid4(),
        name="Test",
        private_key="priv",
        public_key="pub",
        api_key_hash="hash",
        created_at=datetime.now(timezone.utc),
        oauth_config={
            "google": {
                "enabled": False,
                "client_id": "test-client-id",
                "client_secret": "encrypted-secret",
            }
        },
    )
    mock_project_repo.get_by_id.return_value = project

    with pytest.raises(
        OAuthFailedException, match="OAuth provider not enabled or configured"
    ):
        await oauth_adapter._get_client("google", project_id, AsyncMock())
