import pytest
from httpx import AsyncClient

from src.modules.auth.authentication.api.dependencies.security import (
    get_current_user,
    get_jwt_payload,
    verify_csrf,
)
from src.modules.auth.authentication.domain.entities import UserIdentity


@pytest.fixture
def override_auth_deps(client: AsyncClient):
    from src import app

    import uuid

    current_user = UserIdentity(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        email="test@example.com",
        is_verified=True,
    )

    app.dependency_overrides[get_current_user] = lambda: current_user
    app.dependency_overrides[get_jwt_payload] = lambda: {
        "jti": "test_jti",
        "exp": 9999999999,
    }
    app.dependency_overrides[verify_csrf] = lambda: None

    yield

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient, override_auth_deps, mocker):
    mock_execute = mocker.patch(
        "src.modules.users.application.use_cases.UpdateProfileUseCase.execute"
    )
    from src.modules.users.domain.entities import UserProfile

    import uuid

    mock_execute.return_value = UserProfile(
        id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
        email="test@example.com",
        name="New Name",
        picture="https://example.com/pic.jpg",
        receive_updates=False,
    )

    # Update the profile
    response = await client.patch(
        "/v1.0/users/me",
        json={"name": "New Name", "picture": "https://example.com/pic.jpg"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["picture"] == "https://example.com/pic.jpg"


@pytest.mark.asyncio
async def test_delete_account(client: AsyncClient, override_auth_deps, mocker):
    mock_execute = mocker.patch(
        "src.modules.users.application.use_cases.DeleteAccountUseCase.execute"
    )

    # Delete the account
    response = await client.delete("/v1.0/users/me")

    assert response.status_code == 204
    mock_execute.assert_called_once()
