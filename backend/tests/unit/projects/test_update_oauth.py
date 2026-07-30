import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime
from src.modules.projects.application.use_cases.update_oauth import UpdateOauthUseCase
from src.modules.projects.application.commands.project_commands import (
    UpdateOauthCommand,
)
from src.modules.projects.domain.exceptions.project_validation_error import (
    ProjectValidationError,
)
from src.modules.projects.domain.entities.project_entity import ProjectEntity


@pytest.fixture
def uow():
    mock_uow = AsyncMock()
    mock_uow.__aenter__.return_value = mock_uow
    mock_uow.project_query_repo = AsyncMock()
    mock_uow.project_command_repo = AsyncMock()
    return mock_uow


@pytest.fixture
def encryption():
    enc = MagicMock()
    enc.encrypt.side_effect = lambda x: f"encrypted_{x}"
    return enc


@pytest.fixture
def use_case(uow, encryption):
    return UpdateOauthUseCase(uow, encryption)


@pytest.mark.asyncio
async def test_update_oauth_success_new_config(use_case, uow):
    project_id = uuid4()
    user_id = uuid4()
    project = ProjectEntity(
        id=project_id,
        name="Test",
        tenant_id=user_id,
        private_key="",
        public_key="",
        api_key_hash="",
        created_at=datetime.now(),
    )
    project.oauth_config = None  # type: ignore
    uow.project_query_repo.get_by_id.return_value = project
    uow.project_command_repo.save.return_value = project

    command = UpdateOauthCommand(
        project_id=project_id,
        user_id=user_id,
        incoming_config={
            "google": {
                "enabled": True,
                "client_id": "google_id",
                "client_secret": "google_secret",
            },
            "github": {"enabled": False},
        },
    )

    res = await use_case.execute(command)

    assert res.project.oauth_config["google"]["enabled"] is True
    assert res.project.oauth_config["google"]["client_id"] == "google_id"
    assert (
        res.project.oauth_config["google"]["client_secret"] == "encrypted_google_secret"
    )

    assert res.project.oauth_config["github"]["enabled"] is False
    assert res.project.oauth_config["github"]["client_id"] is None


@pytest.mark.asyncio
async def test_update_oauth_missing_client_id(use_case, uow):
    project_id = uuid4()
    user_id = uuid4()
    project = ProjectEntity(
        id=project_id,
        name="Test",
        tenant_id=user_id,
        private_key="",
        public_key="",
        api_key_hash="",
        created_at=datetime.now(),
    )
    uow.project_query_repo.get_by_id.return_value = project

    command = UpdateOauthCommand(
        project_id=project_id,
        user_id=user_id,
        incoming_config={"google": {"enabled": True, "client_secret": "google_secret"}},
    )

    with pytest.raises(ProjectValidationError) as exc:
        await use_case.execute(command)

    assert "Client ID is required" in exc.value.errors[0]["msg"]


@pytest.mark.asyncio
async def test_update_oauth_missing_client_secret_and_no_old_secret(use_case, uow):
    project_id = uuid4()
    user_id = uuid4()
    project = ProjectEntity(
        id=project_id,
        name="Test",
        tenant_id=user_id,
        private_key="",
        public_key="",
        api_key_hash="",
        created_at=datetime.now(),
    )
    project.oauth_config = {"google": {"client_id": "old_id"}}  # no secret
    uow.project_query_repo.get_by_id.return_value = project

    command = UpdateOauthCommand(
        project_id=project_id,
        user_id=user_id,
        incoming_config={
            "google": {
                "enabled": True,
                "client_id": "google_id",
            }
        },
    )

    with pytest.raises(ProjectValidationError) as exc:
        await use_case.execute(command)

    assert "Client Secret is required" in exc.value.errors[0]["msg"]


@pytest.mark.asyncio
async def test_update_oauth_retain_old_secret(use_case, uow):
    project_id = uuid4()
    user_id = uuid4()
    project = ProjectEntity(
        id=project_id,
        name="Test",
        tenant_id=user_id,
        private_key="",
        public_key="",
        api_key_hash="",
        created_at=datetime.now(),
    )
    project.oauth_config = {
        "google": {"client_id": "old_id", "client_secret": "old_secret_enc"}
    }
    uow.project_query_repo.get_by_id.return_value = project
    uow.project_command_repo.save.return_value = project

    command = UpdateOauthCommand(
        project_id=project_id,
        user_id=user_id,
        incoming_config={
            "google": {
                "enabled": True,
                "client_id": "new_google_id",
            }
        },
    )

    res = await use_case.execute(command)
    assert res.project.oauth_config["google"]["client_id"] == "new_google_id"
    assert res.project.oauth_config["google"]["client_secret"] == "old_secret_enc"
