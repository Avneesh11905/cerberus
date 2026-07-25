import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from src.modules.projects.application.use_cases.create_project import (
    CreateProjectUseCase,
)
from src.modules.projects.application.commands.project_commands import (
    CreateProjectCommand,
)


@pytest.fixture
def uow_mock():
    mock = AsyncMock()
    mock.__aenter__.return_value = mock
    mock.__aexit__.return_value = None
    mock.project_command_repo.save = AsyncMock(side_effect=lambda p: p)
    return mock


@pytest.fixture
def api_key_adapter_mock():
    mock = MagicMock()
    mock.generate.return_value = "raw_api_key"
    mock.hash.return_value = "hashed_api_key"
    return mock


@pytest.fixture
def rsa_key_adapter_mock():
    mock = AsyncMock()
    mock.generate_keypair.return_value = ("private", "public")
    return mock


@pytest.fixture
def analytics_mock():
    return MagicMock()


@pytest.mark.asyncio
async def test_create_project(
    uow_mock, api_key_adapter_mock, rsa_key_adapter_mock, analytics_mock
):
    use_case = CreateProjectUseCase(
        uow=uow_mock,
        api_key_adapter=api_key_adapter_mock,
        rsa_key_adapter=rsa_key_adapter_mock,
        analytics=analytics_mock,
    )

    tenant_id = uuid4()
    command = CreateProjectCommand(user_id=tenant_id, name="Test Project")

    result = await use_case.execute(command)

    assert result.project.name == "Test Project"
    assert result.project.tenant_id == tenant_id
    assert result.project.environment == "development"
    assert result.api_key_plaintext == "raw_api_key"
    assert result.public_pem == "public"

    uow_mock.project_command_repo.save.assert_called_once()
    analytics_mock.record_event.assert_called_once()
