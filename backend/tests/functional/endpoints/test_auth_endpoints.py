import pytest
from httpx import AsyncClient

from src.shared.domain.value_objects import EmailAddress, PersonName


@pytest.mark.asyncio
async def test_tenant_registration_validation_error(client: AsyncClient):
    # Missing email
    response = await client.post(
        "/v1/auth/register",
        json={"password": "strongpassword123!", "name": "Test Tenant"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_tenant_login_validation_error(client: AsyncClient):
    # Missing password
    response = await client.post("/v1/auth/login", json={"email": "test@example.com"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_protected_route_unauthenticated(client: AsyncClient):
    # No auth header
    response = await client.get("/v1/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_invalid_token(client: AsyncClient):
    # Invalid auth header
    response = await client.get(
        "/v1/users/me", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_session_refresh_no_cookie(client: AsyncClient):
    # Missing refresh cookie
    response = await client.post("/v1/auth/refresh")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_tenant_registration_success(client: AsyncClient, mocker):
    mock_execute = mocker.patch(
        "src.modules.authentication.application.use_cases.LocalRegisterUseCase.execute",
        return_value=300,
    )

    response = await client.post(
        "/v1/auth/register",
        json={
            "email": "test_success@example.com",
            "password": "StrongPassword123!",
            "name": "Test Tenant",
        },
    )

    assert response.status_code == 201
    assert (
        response.json()["message"]
        == "Successfully registered! Please check your email for the 6-digit OTP code."
    )
    assert response.json()["expires_in_seconds"] == 300
    mock_execute.assert_called_once()


@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient, mocker):
    import uuid

    from src import app
    from src.modules.authentication.presentation.api.dependencies.project import (
        get_optional_project_id,
    )

    mock_id = uuid.uuid4()
    app.dependency_overrides[get_optional_project_id] = lambda: mock_id

    try:
        mock_execute = mocker.patch(
            "src.modules.authentication.application.use_cases.LocalRegisterUseCase.execute",
            return_value=300,
        )

        response = await client.post(
            "/v1/auth/register",
            json={
                "email": "test_user@example.com",
                "password": "StrongPassword123!",
                "name": "Test User",
            },
            headers={"X-Cerberus-API-Key": "cerb_testkey"},
        )

        print(response.content)
        assert response.status_code == 201
        assert response.json()["expires_in_seconds"] == 300
        mock_execute.assert_called_once()
    finally:
        del app.dependency_overrides[get_optional_project_id]


@pytest.mark.asyncio
async def test_login_user_success(client: AsyncClient, mocker):
    import uuid

    from src import app
    from src.modules.authentication.presentation.api.dependencies.project import (
        get_optional_project_id,
    )
    from src.modules.users.domain.entities import UserProfile

    mock_id = uuid.uuid4()
    app.dependency_overrides[get_optional_project_id] = lambda: mock_id

    try:
        mock_profile = UserProfile(
            id=uuid.uuid4(),
            email=EmailAddress("test_user@example.com"),
            name=PersonName("Test User"),
            receive_updates=True,
        )
        mock_execute = mocker.patch(
            "src.modules.authentication.application.use_cases.LocalLoginUseCase.execute",
            return_value=(mock_profile, "refresh_token", "access_token"),
        )

        response = await client.post(
            "/v1/auth/login",
            json={"email": "test_user@example.com", "password": "StrongPassword123!"},
            headers={"X-Cerberus-API-Key": "cerb_testkey"},
        )

        assert response.status_code == 200
        assert response.json()["access_token"] == "access_token"
        mock_execute.assert_called_once()
    finally:
        del app.dependency_overrides[get_optional_project_id]


@pytest.mark.asyncio
async def test_forgot_password(client: AsyncClient, mocker):
    mock_execute = mocker.patch(
        "src.modules.authentication.application.use_cases.PasswordResetRequestUseCase.execute"
    )

    response = await client.post(
        "/v1/auth/password/forgot",
        json={"email": "test@example.com"},
    )

    assert response.status_code == 200
    assert (
        response.json()["message"]
        == "If an account with that email exists, we sent a password reset link."
    )
    mock_execute.assert_called_once()


@pytest.mark.asyncio
async def test_reset_password_success(client: AsyncClient, mocker):
    mock_execute = mocker.patch(
        "src.modules.authentication.application.use_cases.PasswordResetExecuteUseCase.execute",
        return_value=True,
    )

    response = await client.post(
        "/v1/auth/password/reset",
        json={"token": "valid_token", "new_password": "NewStrongPassword123!"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Password successfully reset"
    mock_execute.assert_called_once()


@pytest.mark.asyncio
async def test_reset_password_failure(client: AsyncClient, mocker):
    mock_execute = mocker.patch(
        "src.modules.authentication.application.use_cases.PasswordResetExecuteUseCase.execute",
        return_value=False,
    )

    response = await client.post(
        "/v1/auth/password/reset",
        json={"token": "invalid_token", "new_password": "NewStrongPassword123!"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid request"
    mock_execute.assert_called_once()


@pytest.mark.asyncio
async def test_change_password_unauthenticated(client: AsyncClient):
    response = await client.patch(
        "/v1/auth/password/",
        json={"current_password": "old_password", "new_password": "new_password"},
    )
    # Should fail due to missing csrf / authentication
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_logout_unauthenticated(client: AsyncClient):
    response = await client.post("/v1/auth/logout")
    # Missing CSRF / Authentication
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_logout_all_unauthenticated(client: AsyncClient):
    response = await client.post("/v1/auth/logout/all")
    # Missing CSRF / Authentication
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_list_sessions_unauthenticated(client: AsyncClient):
    response = await client.get("/v1/auth/sessions")
    # Missing Auth
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_revoke_session_unauthenticated(client: AsyncClient):
    response = await client.delete(
        "/v1/auth/sessions/123e4567-e89b-12d3-a456-426614174000"
    )
    # Missing Auth
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_exchange_invalid_code(client: AsyncClient, mocker):
    # Mock cache to return None
    mocker.patch(
        "src.shared.infrastructure.adapters.cache.RedisCacheAdapter.get_dict",
        return_value=None,
    )
    response = await client.post("/v1/auth/exchange", json={"code": "invalid_code"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid request"


@pytest.mark.asyncio
async def test_verify_email_success(client: AsyncClient, mocker):
    import uuid

    from src.modules.authentication.domain.entities import UserIdentity

    mock_user = UserIdentity(
        id=uuid.uuid4(),
        email=EmailAddress("test@example.com"),
        is_verified=True,
    )
    mock_execute = mocker.patch(
        "src.modules.authentication.application.use_cases.LocalVerifyEmailUseCase.execute",
        return_value=(mock_user, "mock_refresh_token"),
    )

    response = await client.post(
        "/v1/auth/verify-email",
        json={"email": "test@example.com", "otp": "123456"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Email verified successfully"
    mock_execute.assert_called_once()


@pytest.mark.asyncio
async def test_resend_verification_success(client: AsyncClient, mocker):
    mock_execute = mocker.patch(
        "src.modules.authentication.application.use_cases.LocalResendVerificationUseCase.execute",
        return_value=300,
    )

    response = await client.post(
        "/v1/auth/verify-email/resend",
        json={"email": "test@example.com"},
    )
    assert response.status_code == 200
    assert response.json()["expires_in_seconds"] == 300
    mock_execute.assert_called_once()


@pytest.mark.asyncio
async def test_session_refresh_success(client: AsyncClient, mocker):
    mock_execute = mocker.patch(
        "src.modules.authentication.application.use_cases.SessionRefreshUseCase.execute",
        return_value=("new_access_token", "new_refresh_token"),
    )

    client.cookies.set("refresh_token", "valid_refresh_token")
    response = await client.post("/v1/auth/refresh")
    client.cookies.clear()
    assert response.status_code == 200
    assert response.json()["access_token"] == "new_access_token"
    mock_execute.assert_called_once()


@pytest.mark.asyncio
async def test_logout_success(client: AsyncClient, mocker):
    from src import app
    from src.modules.authentication.presentation.api.dependencies.security import (
        get_jwt_payload,
        verify_csrf,
    )

    app.dependency_overrides[verify_csrf] = lambda: True
    app.dependency_overrides[get_jwt_payload] = lambda: {
        "jti": "mock_jti",
        "exp": 1234567890,
    }

    try:
        mock_execute = mocker.patch(
            "src.modules.authentication.application.use_cases.SessionLogoutUseCase.execute",
            return_value=None,
        )

        client.cookies.set("refresh_token", "valid_refresh_token")
        response = await client.post("/v1/auth/logout")
        client.cookies.clear()
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out"
        mock_execute.assert_called_once()
    finally:
        del app.dependency_overrides[verify_csrf]
        del app.dependency_overrides[get_jwt_payload]


@pytest.mark.asyncio
async def test_logout_all_success(client: AsyncClient, mocker):
    import uuid

    from src import app
    from src.modules.authentication.domain.entities import UserIdentity
    from src.modules.authentication.presentation.api.dependencies.security import (
        get_current_user,
        get_jwt_payload,
        verify_csrf,
    )

    app.dependency_overrides[verify_csrf] = lambda: True
    app.dependency_overrides[get_jwt_payload] = lambda: {
        "jti": "mock_jti",
        "exp": 1234567890,
    }
    app.dependency_overrides[get_current_user] = lambda: UserIdentity(
        id=uuid.uuid4(), email=EmailAddress("test@test.com"), is_verified=True
    )

    try:
        mock_execute = mocker.patch(
            "src.modules.authentication.application.use_cases.SessionLogoutAllUseCase.execute",
            return_value=None,
        )

        client.cookies.set("refresh_token", "valid_refresh_token")
        response = await client.post("/v1/auth/logout/all")
        client.cookies.clear()
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out from all devices"
        mock_execute.assert_called_once()
    finally:
        del app.dependency_overrides[verify_csrf]
        del app.dependency_overrides[get_jwt_payload]
        del app.dependency_overrides[get_current_user]


@pytest.mark.asyncio
async def test_exchange_success(client: AsyncClient, mocker):
    mock_data = {
        "refresh_token": "mock_refresh_token",
        "is_new_user": False,
        "access_token": "mock_access_token",
        "user_id": None,
    }
    mock_cache = mocker.patch(
        "src.shared.infrastructure.adapters.cache.RedisCacheAdapter.get_dict",
        return_value=mock_data,
    )
    mock_cache_del = mocker.patch(
        "src.shared.infrastructure.adapters.cache.RedisCacheAdapter.delete_key",
        return_value=None,
    )

    response = await client.post("/v1/auth/exchange", json={"code": "valid_code"})
    assert response.status_code == 200
    assert response.json()["access_token"] == "mock_access_token"
    mock_cache.assert_called_once()
    mock_cache_del.assert_called_once()


@pytest.mark.asyncio
async def test_list_sessions_success(client: AsyncClient, mocker):
    import uuid

    from src import app
    from src.modules.authentication.domain.entities import UserIdentity
    from src.modules.authentication.presentation.api.dependencies.security import (
        get_current_user,
    )

    app.dependency_overrides[get_current_user] = lambda: UserIdentity(
        id=uuid.uuid4(), email=EmailAddress("test@test.com"), is_verified=True
    )

    try:
        mock_execute = mocker.patch(
            "src.modules.authentication.application.use_cases.ListActiveSessionsUseCase.execute",
            return_value=[],
        )

        client.cookies.set("refresh_token", "valid_refresh_token")
        response = await client.get("/v1/auth/sessions")
        client.cookies.clear()
        assert response.status_code == 200
        assert response.json() == []
        mock_execute.assert_called_once()
    finally:
        del app.dependency_overrides[get_current_user]


@pytest.mark.asyncio
async def test_revoke_session_success(client: AsyncClient, mocker):
    import uuid

    from src import app
    from src.modules.authentication.domain.entities import UserIdentity
    from src.modules.authentication.presentation.api.dependencies.security import (
        get_current_user,
    )

    app.dependency_overrides[get_current_user] = lambda: UserIdentity(
        id=uuid.uuid4(), email=EmailAddress("test@test.com"), is_verified=True
    )

    try:
        mock_execute = mocker.patch(
            "src.modules.authentication.application.use_cases.SessionRevokeUseCase.execute",
            return_value=None,
        )
        client.cookies.set("refresh_token", "valid_refresh_token")
        uid = uuid.uuid4()
        response = await client.delete(f"/v1/auth/sessions/{uid}")
        client.cookies.clear()
        assert response.status_code == 204
        mock_execute.assert_called_once()
    finally:
        del app.dependency_overrides[get_current_user]


@pytest.mark.asyncio
async def test_tenant_oauth_login_invalid_provider(client: AsyncClient):
    response = await client.get("/v1/auth/tenant/login/invalid_provider")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid request"


@pytest.mark.asyncio
async def test_oauth_preflight_invalid_api_key(client: AsyncClient):
    response = await client.post("/v1/auth/oauth/preflight/github")
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication failed"


@pytest.mark.asyncio
async def test_login_oauth_no_project(client: AsyncClient):
    response = await client.get("/v1/auth/login/github")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_tenant_oauth_login_success(client: AsyncClient, mocker):
    mocker.patch(
        "src.modules.authentication.application.use_cases.TenantOAuthLoginUrlUseCase.execute",
        return_value=(
            "https://github.com/login",
            {"tenant_oauth_state": {"nonce": "test_nonce"}},
        ),
    )
    response = await client.get("/v1/auth/tenant/login/github")
    assert response.status_code == 302
    assert response.headers["location"] == "https://github.com/login"


@pytest.mark.asyncio
async def test_tenant_oauth_callback_invalid_state(client: AsyncClient):
    response = await client.get("/v1/auth/tenant/callback/github")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid request"
