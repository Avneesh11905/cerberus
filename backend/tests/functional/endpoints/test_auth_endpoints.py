import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_tenant_registration_validation_error(client: AsyncClient):
    # Missing email
    response = await client.post(
        "/v1.0/auth/tenant/register",
        json={"password": "strongpassword123!", "name": "Test Tenant"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_tenant_login_validation_error(client: AsyncClient):
    # Missing password
    response = await client.post(
        "/v1.0/auth/tenant/login", json={"email": "test@example.com"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_protected_route_unauthenticated(client: AsyncClient):
    # No auth header
    response = await client.get("/v1.0/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_invalid_token(client: AsyncClient):
    # Invalid auth header
    response = await client.get(
        "/v1.0/users/me", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_session_refresh_no_cookie(client: AsyncClient):
    # Missing refresh cookie
    response = await client.post("/v1.0/auth/refresh")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_tenant_registration_success(client: AsyncClient, mocker):
    mock_execute = mocker.patch(
        "src.modules.auth.authentication.application.use_cases.LocalRegisterUseCase.execute",
        return_value=300,
    )

    response = await client.post(
        "/v1.0/auth/tenant/register",
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
