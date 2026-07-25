import pytest
from unittest.mock import AsyncMock, MagicMock

from src.modules.projects.application.use_cases.rotate_api_key import (
    RotateApiKeyUseCase,
)
from src.modules.projects.application.use_cases.rotate_jwt_secret import (
    RotateJwtSecretUseCase,
)
from src.modules.projects.application.use_cases.update_project_claims import (
    UpdateProjectClaimsUseCase,
)
from src.modules.projects.application.commands.project_commands import (
    RotateApiKeyCommand,
    RotateJwtSecretCommand,
    UpdateProjectClaimsCommand,
)
from src.modules.projects.domain.entities.project_entity import ProjectEntity


@pytest.fixture
def uow_mock():
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.project_query_repo = MagicMock()
    uow.project_command_repo = MagicMock()
    return uow


@pytest.mark.asyncio
async def test_rotate_api_key(uow_mock):
    import uuid

    api_key_adapter = MagicMock()
    api_key_adapter.generate.return_value = "plain"
    api_key_adapter.hash.return_value = "hash"
    analytics = MagicMock()

    uc = RotateApiKeyUseCase(uow_mock, api_key_adapter, analytics)

    proj_id = uuid.uuid4()
    user_id = uuid.uuid4()

    project = ProjectEntity(
        id=proj_id,
        tenant_id=uuid.uuid4(),
        name="Proj 1",
        private_key="priv",
        public_key="pub",
        api_key_hash="hash",
        created_at=MagicMock(),
        allowed_origins=["*"],
    )
    uc._get_project_or_404 = AsyncMock(return_value=project)  # type: ignore

    uow_mock.project_command_repo.save = AsyncMock()

    dto = await uc.execute(RotateApiKeyCommand(project_id=proj_id, user_id=user_id))

    assert dto.api_key_plaintext == "plain"
    assert project.api_key_hash == "hash"
    analytics.record_event.assert_called_once()
    uow_mock.project_command_repo.save.assert_called_once_with(project)


@pytest.mark.asyncio
async def test_rotate_jwt_secret(uow_mock):
    import uuid

    rsa_key_adapter = MagicMock()
    rsa_key_adapter.generate_keypair = AsyncMock(return_value=("priv", "pub"))
    analytics = MagicMock()

    uc = RotateJwtSecretUseCase(uow_mock, rsa_key_adapter, analytics)

    proj_id = uuid.uuid4()
    user_id = uuid.uuid4()

    project = ProjectEntity(
        id=proj_id,
        tenant_id=uuid.uuid4(),
        name="Proj 1",
        private_key="priv",
        public_key="pub",
        api_key_hash="hash",
        created_at=MagicMock(),
        allowed_origins=["*"],
    )
    uc._get_project_or_404 = AsyncMock(return_value=project)  # type: ignore

    uow_mock.project_command_repo.save = AsyncMock()

    dto = await uc.execute(RotateJwtSecretCommand(project_id=proj_id, user_id=user_id))

    assert dto.public_pem == "pub"
    assert project.private_key == "priv"
    assert project.public_key == "pub"
    analytics.record_event.assert_called_once()
    uow_mock.project_command_repo.save.assert_called_once_with(project)


@pytest.mark.asyncio
async def test_update_project_claims(uow_mock):
    import uuid

    cache = MagicMock()
    cache.delete_key = AsyncMock()

    uc = UpdateProjectClaimsUseCase(uow_mock, cache)

    proj_id = uuid.uuid4()
    user_id = uuid.uuid4()

    project = ProjectEntity(
        id=proj_id,
        tenant_id=uuid.uuid4(),
        name="Proj 1",
        private_key="priv",
        public_key="pub",
        api_key_hash="hash",
        created_at=MagicMock(),
        allowed_origins=["*"],
    )
    uc._get_project_or_404 = AsyncMock(return_value=project)  # type: ignore

    uow_mock.project_command_repo.save = AsyncMock(return_value=project)

    # 1. Success
    dto = await uc.execute(
        UpdateProjectClaimsCommand(
            project_id=proj_id, user_id=user_id, default_claims={"custom": "val"}
        )
    )

    assert dto.project == project
    assert project.default_claims == {"custom": "val"}
    cache.delete_key.assert_called_once()

    # 2. Too many claims
    try:
        await uc.execute(
            UpdateProjectClaimsCommand(
                project_id=proj_id,
                user_id=user_id,
                default_claims={f"k{i}": "v" for i in range(12)},
            )
        )
    except ValueError as e:
        assert "Maximum" in str(e)

    # 3. Reserved key
    try:
        await uc.execute(
            UpdateProjectClaimsCommand(
                project_id=proj_id, user_id=user_id, default_claims={"sub": "v"}
            )
        )
    except ValueError as e:
        assert "Reserved" in str(e)
