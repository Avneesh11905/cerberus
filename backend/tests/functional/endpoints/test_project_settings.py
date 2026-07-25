import uuid
import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock


@pytest.fixture
def override_tenant_dep():
    from src import app
    from src.modules.authentication.presentation.api.dependencies.security import (
        get_jwt_payload,
    )
    from src.modules.authorization.domain.enums import GlobalRole

    class MockUser:
        id = uuid.uuid4()
        role = GlobalRole.TENANT

    async def mock_get_jwt_payload():
        return {"_user_obj": MockUser()}

    app.dependency_overrides[get_jwt_payload] = mock_get_jwt_payload
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_project_oauth(client: AsyncClient, mocker, override_tenant_dep):
    project_id = uuid.uuid4()
    mock_execute = mocker.patch(
        "src.modules.projects.application.use_cases.update_oauth.UpdateOauthUseCase.execute"
    )

    from src.modules.projects.domain.entities import ProjectEntity
    from datetime import datetime, timezone
    from src.shared.domain.value_objects import HttpsUrl

    mock_project = ProjectEntity(
        id=project_id,
        tenant_id=uuid.uuid4(),
        name="Test",
        environment="development",
        frontend_url=HttpsUrl("http://localhost"),
        oauth_config={},
        allowed_origins=[],
        api_key_hash="hash",
        public_key="pub",
        private_key="priv",
        default_claims={},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_execute.return_value = MagicMock(project=mock_project)

    response = await client.put(
        f"/v1/projects/{project_id}/oauth",
        json={"oauth_config": {"github": {"client_id": "a", "client_secret": "b"}}},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_project_origins(client: AsyncClient, mocker, override_tenant_dep):
    project_id = uuid.uuid4()
    mock_execute = mocker.patch(
        "src.modules.projects.application.use_cases.update_origins.UpdateOriginsUseCase.execute"
    )
    from src.modules.projects.domain.entities import ProjectEntity
    from datetime import datetime, timezone
    from src.shared.domain.value_objects import HttpsUrl

    mock_project = ProjectEntity(
        id=project_id,
        tenant_id=uuid.uuid4(),
        name="Test",
        environment="development",
        frontend_url=HttpsUrl("http://localhost"),
        oauth_config={},
        allowed_origins=[],
        api_key_hash="hash",
        public_key="pub",
        private_key="priv",
        default_claims={},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_execute.return_value = MagicMock(project=mock_project)

    response = await client.put(
        f"/v1/projects/{project_id}/origins",
        json={"allowed_origins": ["http://localhost"]},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_project_environment(
    client: AsyncClient, mocker, override_tenant_dep
):
    project_id = uuid.uuid4()
    mock_execute = mocker.patch(
        "src.modules.projects.application.use_cases.update_environment.UpdateEnvironmentUseCase.execute"
    )
    from src.modules.projects.domain.entities import ProjectEntity
    from datetime import datetime, timezone
    from src.shared.domain.value_objects import HttpsUrl

    mock_project = ProjectEntity(
        id=project_id,
        tenant_id=uuid.uuid4(),
        name="Test",
        environment="development",
        frontend_url=HttpsUrl("http://localhost"),
        oauth_config={},
        allowed_origins=[],
        api_key_hash="hash",
        public_key="pub",
        private_key="priv",
        default_claims={},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_execute.return_value = MagicMock(project=mock_project)

    response = await client.put(
        f"/v1/projects/{project_id}/environment", json={"environment": "production"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_project_frontend_url(
    client: AsyncClient, mocker, override_tenant_dep
):
    project_id = uuid.uuid4()
    mock_execute = mocker.patch(
        "src.modules.projects.application.use_cases.update_frontend_url.UpdateFrontendUrlUseCase.execute"
    )
    from src.modules.projects.domain.entities import ProjectEntity
    from datetime import datetime, timezone
    from src.shared.domain.value_objects import HttpsUrl

    mock_project = ProjectEntity(
        id=project_id,
        tenant_id=uuid.uuid4(),
        name="Test",
        environment="development",
        frontend_url=HttpsUrl("http://localhost"),
        oauth_config={},
        allowed_origins=[],
        api_key_hash="hash",
        public_key="pub",
        private_key="priv",
        default_claims={},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_execute.return_value = MagicMock(project=mock_project)

    response = await client.put(
        f"/v1/projects/{project_id}/frontend-url",
        json={"frontend_url": "https://example.com"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_project_name(client: AsyncClient, mocker, override_tenant_dep):
    project_id = uuid.uuid4()
    mock_execute = mocker.patch(
        "src.modules.projects.application.use_cases.update_name.UpdateNameUseCase.execute"
    )
    from src.modules.projects.domain.entities import ProjectEntity
    from datetime import datetime, timezone
    from src.shared.domain.value_objects import HttpsUrl

    mock_project = ProjectEntity(
        id=project_id,
        tenant_id=uuid.uuid4(),
        name="Test",
        environment="development",
        frontend_url=HttpsUrl("http://localhost"),
        oauth_config={},
        allowed_origins=[],
        api_key_hash="hash",
        public_key="pub",
        private_key="priv",
        default_claims={},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_execute.return_value = MagicMock(project=mock_project)

    response = await client.put(
        f"/v1/projects/{project_id}/name", json={"name": "New Name"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_project_claims(client: AsyncClient, mocker, override_tenant_dep):
    project_id = uuid.uuid4()

    # Get claims
    mock_get = mocker.patch(
        "src.modules.projects.application.use_cases.get_project_claims.GetProjectClaimsUseCase.execute"
    )
    mock_get.return_value = MagicMock(claims={"role": "user"})

    response = await client.get(f"/v1/projects/{project_id}/claims")
    assert response.status_code == 200

    # Update claims
    mock_update = mocker.patch(
        "src.modules.projects.application.use_cases.update_project_claims.UpdateProjectClaimsUseCase.execute"
    )
    from src.modules.projects.domain.entities import ProjectEntity
    from datetime import datetime, timezone
    from src.shared.domain.value_objects import HttpsUrl

    mock_project = ProjectEntity(
        id=project_id,
        tenant_id=uuid.uuid4(),
        name="Test",
        environment="development",
        frontend_url=HttpsUrl("http://localhost"),
        oauth_config={},
        allowed_origins=[],
        api_key_hash="hash",
        public_key="pub",
        private_key="priv",
        default_claims={"custom_field": "admin"},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_update.return_value = MagicMock(project=mock_project)

    response = await client.put(
        f"/v1/projects/{project_id}/claims", json={"claims": {"custom_field": "admin"}}
    )
    assert response.status_code == 200
