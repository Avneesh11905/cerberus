import uuid

import pytest
from httpx import AsyncClient

from src.modules.authentication.presentation.api.dependencies.project import (
    get_optional_project_id,
)
from src.modules.projects.application.dtos.project_dtos import (
    GetUserClaimsDTO,
    ListProjectUsersDTO,
    SetProjectUserActiveStatusDTO,
    UpdateUserClaimsDTO,
)
from src.modules.projects.domain.entities.project_user import ProjectUser
from src.shared.domain.value_objects import EmailAddress


@pytest.fixture
def override_project_id_dep():
    from src import app

    mock_id = uuid.uuid4()
    # Override get_optional_project_id (the inner dep) so the full chain is
    # short-circuited. Overriding only get_required_project_id is not enough
    # because FastAPI resolves sub-dependencies first; get_optional_project_id
    # would still run, find no API key, and return None -> 401.
    app.dependency_overrides[get_optional_project_id] = lambda: mock_id
    yield mock_id
    # Only remove this specific override, not all overrides (the client fixture
    # also installs UoW overrides that must survive for the test teardown).
    app.dependency_overrides.pop(get_optional_project_id, None)


@pytest.mark.asyncio
async def test_list_project_users_m2m_success(
    client: AsyncClient, mocker, override_project_id_dep
):
    mock_execute = mocker.patch(
        "src.modules.projects.application.use_cases.list_project_users.ListProjectUsersUseCase.execute",
    )

    # Mock return value (users_list, total_count)
    mock_user_id = uuid.uuid4()
    mock_users = [
        ProjectUser(
            id=mock_user_id,
            email=EmailAddress("test@example.com"),
            receive_updates=False,
            project_id=override_project_id_dep,
            is_active=True,
        )
    ]
    mock_execute.return_value = ListProjectUsersDTO(users=mock_users, total=1)

    response = await client.get(
        "/v1/projects/server/users",
        params={"page": 1, "size": 50, "search": "test"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["page"] == 1
    assert data["size"] == 50
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == str(mock_user_id)

    mock_execute.assert_called_once()
    args, kwargs = mock_execute.call_args
    query = args[0]
    assert query.project_id == override_project_id_dep
    assert query.tenant_id is None
    assert query.skip == 0
    assert query.limit == 50
    assert query.search == "test"


@pytest.mark.asyncio
async def test_set_project_user_status_m2m_success(
    client: AsyncClient, mocker, override_project_id_dep
):
    mock_execute = mocker.patch(
        "src.modules.projects.application.use_cases.set_project_user_active_status.SetProjectUserActiveStatusUseCase.execute",
    )

    target_user_id = uuid.uuid4()
    mock_updated_user = ProjectUser(
        id=target_user_id,
        email=EmailAddress("test@example.com"),
        receive_updates=False,
        project_id=override_project_id_dep,
        is_active=False,
    )
    mock_execute.return_value = SetProjectUserActiveStatusDTO(user=mock_updated_user)

    response = await client.put(
        f"/v1/projects/server/users/{target_user_id}/status",
        json={"is_active": False},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Status updated successfully"
    assert data["user_id"] == str(mock_updated_user.id)
    assert data["is_active"] is False

    mock_execute.assert_called_once()
    args, kwargs = mock_execute.call_args
    command = args[0]
    assert command.project_id == override_project_id_dep
    assert command.tenant_id is None
    assert command.user_id == target_user_id
    assert command.is_active is False


@pytest.mark.asyncio
async def test_get_user_claims_m2m_success(
    client: AsyncClient, mocker, override_project_id_dep
):
    mock_execute = mocker.patch(
        "src.modules.projects.application.use_cases.get_user_claims.GetUserClaimsUseCase.execute",
    )

    target_user_id = uuid.uuid4()
    mock_execute.return_value = GetUserClaimsDTO(
        claims={
            "default_claims": {"role": "user"},
            "user_overrides": {"role": "admin"},
            "effective_claims": {"role": "admin"},
        }
    )

    response = await client.get(
        f"/v1/projects/server/users/{target_user_id}/claims",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(target_user_id)
    assert data["default_claims"] == {"role": "user"}
    assert data["user_overrides"] == {"role": "admin"}
    assert data["effective_claims"] == {"role": "admin"}

    mock_execute.assert_called_once()
    args, kwargs = mock_execute.call_args
    query = args[0]
    assert query.project_id == override_project_id_dep
    assert query.tenant_id is None
    assert query.user_id == target_user_id


@pytest.mark.asyncio
async def test_update_user_claims_m2m_success(
    client: AsyncClient, mocker, override_project_id_dep
):
    mock_execute = mocker.patch(
        "src.modules.projects.application.use_cases.update_user_claims.UpdateUserClaimsUseCase.execute",
    )

    target_user_id = uuid.uuid4()
    mock_updated_user = ProjectUser(
        id=target_user_id,
        email=EmailAddress("test@example.com"),
        receive_updates=False,
        project_id=override_project_id_dep,
        is_active=True,
        custom_claims={"plan": "premium"},
    )
    mock_execute.return_value = UpdateUserClaimsDTO(user=mock_updated_user)

    response = await client.patch(
        f"/v1/projects/server/users/{target_user_id}/claims",
        json={"overrides": {"plan": "premium"}},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(target_user_id)
    assert data["user_overrides"] == {"plan": "premium"}
    assert data["effective_claims"] == {"plan": "premium"}

    mock_execute.assert_called_once()
    args, kwargs = mock_execute.call_args
    command = args[0]
    assert command.project_id == override_project_id_dep
    assert command.tenant_id is None
    assert command.user_id == target_user_id
    assert command.overrides == {"plan": "premium"}


@pytest.mark.asyncio
async def test_project_server_endpoints_unauthenticated(client: AsyncClient):
    # Do not override project_id dependency so it fails authentication naturally
    response = await client.get("/v1/projects/server/users")
    assert response.status_code == 401

    uid = uuid.uuid4()
    response2 = await client.put(
        f"/v1/projects/server/users/{uid}/status", json={"is_active": False}
    )
    assert response2.status_code == 401

    response3 = await client.get(f"/v1/projects/server/users/{uid}/claims")
    assert response3.status_code == 401

    response4 = await client.patch(
        f"/v1/projects/server/users/{uid}/claims", json={"overrides": {}}
    )
    assert response4.status_code == 401


@pytest.mark.asyncio
async def test_project_server_endpoints_validation_error(
    client: AsyncClient, override_project_id_dep
):
    # Missing required body
    response = await client.put("/v1/projects/server/users/invalid-uuid/status")
    assert response.status_code == 422

    uid = uuid.uuid4()
    # Invalid overrides field type
    response2 = await client.patch(
        f"/v1/projects/server/users/{uid}/claims", json={"overrides": "not-a-dict"}
    )
    assert response2.status_code == 422
