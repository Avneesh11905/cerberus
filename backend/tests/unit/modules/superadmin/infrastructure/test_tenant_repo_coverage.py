import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, UTC

from src.modules.superadmin.infrastructure.database.repositories.tenant_repository import (
    SQLTenantRepositoryAdapter,
)
from src.modules.superadmin.domain.entities import TenantEntity
from src.shared.domain.value_objects import EmailAddress, PersonName
from src.modules.authorization.domain.enums import GlobalRole


@pytest.fixture
def session():
    return AsyncMock()


@pytest.fixture
def repo(session):
    session.add = MagicMock()
    return SQLTenantRepositoryAdapter(session)


@pytest.mark.asyncio
async def test_tenant_repo_get_by_id(repo, session):
    mock_result = MagicMock()
    mock_orm = MagicMock()
    mock_orm.id = uuid4()
    mock_orm.email = "test@example.com"
    mock_orm.name = "Test"
    mock_orm.is_active = True
    mock_orm.role = GlobalRole.SUPERADMIN
    mock_orm.created_at = datetime.now(UTC)

    mock_result.scalars.return_value.first.return_value = mock_orm
    session.execute.return_value = mock_result

    res = await repo.get_by_id(uuid4())
    assert res is not None

    # test None
    mock_result.scalars.return_value.first.return_value = None
    res2 = await repo.get_by_id(uuid4())
    assert res2 is None


@pytest.mark.asyncio
async def test_tenant_repo_get_all(repo, session):
    mock_result = MagicMock()

    mock_orm = MagicMock()
    mock_orm.id = uuid4()
    mock_orm.email = "test@example.com"
    mock_orm.name = "Test"
    mock_orm.is_active = True
    mock_orm.role = GlobalRole.SUPERADMIN
    mock_orm.created_at = datetime.now(UTC)

    mock_result.scalars.return_value.all.return_value = [mock_orm]
    session.execute.return_value = mock_result

    res = await repo.get_all(search="test")
    assert len(res) == 1


@pytest.mark.asyncio
async def test_tenant_repo_count_all(repo, session):
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = 5
    session.execute.return_value = mock_result

    res = await repo.count_all(search="test")
    assert res == 5

    res2 = await repo.count_all(search=None)
    assert res2 == 5


@pytest.mark.asyncio
async def test_tenant_repo_save_existing(repo, session):
    mock_result = MagicMock()
    mock_orm = MagicMock()
    mock_orm.id = uuid4()
    mock_orm.email = "test@example.com"
    mock_orm.name = "Test"
    mock_result.scalars.return_value.first.return_value = mock_orm
    session.execute.return_value = mock_result

    ent = TenantEntity(
        id=uuid4(),
        email=EmailAddress("t@t.com"),
        is_active=True,
        role=GlobalRole.TENANT,
        created_at=datetime.now(UTC),
        name=PersonName("Test"),
    )
    res = await repo.save(ent)
    assert res is not None


@pytest.mark.asyncio
async def test_tenant_repo_save_new(repo, session):
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    session.execute.return_value = mock_result

    ent = TenantEntity(
        id=uuid4(),
        email=EmailAddress("t@t.com"),
        is_active=True,
        role=GlobalRole.TENANT,
        created_at=datetime.now(UTC),
        name=PersonName("Test"),
    )
    res = await repo.save(ent)
    assert res is not None
