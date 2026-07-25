import pytest
from httpx import AsyncClient
import uuid

from src.modules.authentication.presentation.api.dependencies.project import (
    get_required_project_id,
)


@pytest.mark.asyncio
async def test_auth_oauth_preflight_success(client: AsyncClient, mocker):
    mocker.patch(
        "src.modules.authentication.application.use_cases.ProjectUserOAuthLoginUrlUseCase.execute",
        return_value=("https://github.com/login", {"oauth_state": {"nonce": "test"}}),
    )
    from src import app

    app.dependency_overrides[get_required_project_id] = lambda: uuid.uuid4()
    response = await client.post(
        "/v1/auth/oauth/preflight/github",
        headers={"X-Cerberus-API-Key": "cerb_testkey"},
    )
    app.dependency_overrides.pop(get_required_project_id, None)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_auth_login_success(client: AsyncClient, mocker):
    mocker.patch(
        "src.modules.authentication.application.use_cases.ProjectUserOAuthLoginUrlUseCase.execute",
        return_value=("https://github.com/login", {"oauth_state": {"nonce": "test"}}),
    )
    mock_session = mocker.patch(
        "starlette.requests.Request.session", new_callable=mocker.PropertyMock
    )
    mock_session.return_value = {
        "oauth_preflight_project_id": "00000000-0000-0000-0000-000000000000"
    }
    response = await client.get("/v1/auth/login/github")
    assert response.status_code in (302, 303, 307)


@pytest.mark.asyncio
async def test_auth_tenant_login_success(client: AsyncClient, mocker):
    mocker.patch(
        "src.modules.authentication.application.use_cases.TenantOAuthLoginUrlUseCase.execute",
        return_value=(
            "https://github.com/login",
            {"tenant_oauth_state": {"nonce": "test"}},
        ),
    )
    response = await client.get("/v1/auth/tenant/login/github")
    assert response.status_code in (302, 303, 307)


@pytest.mark.asyncio
async def test_auth_tenant_callback_success(client: AsyncClient, mocker):
    import uuid
    from src.modules.authentication.domain.entities import UserIdentity
    from src.shared.domain.value_objects.email_address import EmailAddress

    mock_user = UserIdentity(
        id=uuid.uuid4(), email=EmailAddress("test@test.com"), is_verified=True
    )
    mocker.patch(
        "src.modules.authentication.application.use_cases.TenantOAuthCallbackUseCase.execute",
        return_value=(mock_user, "mock_refresh_token", "mock_access_token", False),
    )
    mock_session = mocker.patch(
        "starlette.requests.Request.session", new_callable=mocker.PropertyMock
    )
    mock_session.return_value = {"tenant_oauth_state": {"nonce": "valid_nonce"}}
    response = await client.get("/v1/auth/tenant/callback/github?state=valid_nonce")
    assert response.status_code in (302, 303, 307)


@pytest.mark.asyncio
async def test_auth_callback_success(client: AsyncClient, mocker):
    import uuid
    from src.modules.authentication.domain.entities import UserIdentity
    from src.shared.domain.value_objects.email_address import EmailAddress

    mock_user = UserIdentity(
        id=uuid.uuid4(), email=EmailAddress("test@test.com"), is_verified=True
    )
    mocker.patch(
        "src.modules.authentication.application.use_cases.ProjectUserOAuthCallbackUseCase.execute",
        return_value=(
            mock_user,
            "mock_refresh_token",
            "mock_access_token",
            False,
            "http://fallback.com",
        ),
    )
    mock_session = mocker.patch(
        "starlette.requests.Request.session", new_callable=mocker.PropertyMock
    )
    mock_session.return_value = {
        "oauth_state": {
            "nonce": "valid_nonce",
            "project_id": "00000000-0000-0000-0000-000000000000",
        }
    }
    response = await client.get("/v1/auth/callback/google?state=valid_nonce")
    assert response.status_code in (302, 303, 307)
