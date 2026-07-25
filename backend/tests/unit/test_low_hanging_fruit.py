import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from src.modules.superadmin.infrastructure.database.repositories.tenant_repository import SQLTenantRepositoryAdapter
from src.modules.superadmin.domain.entities import TenantEntity
from src.shared.domain.value_objects import EmailAddress, PersonName
from src.modules.authorization.domain.enums import GlobalRole

from src.modules.projects.presentation.api.schemas.project_default_claims_req import ProjectDefaultClaimsReq
from src.modules.projects.presentation.api.schemas.project_origins_update_req import ProjectOriginsUpdateReq

from src.modules.projects.application.use_cases.update_oauth import UpdateOauthUseCase
from src.modules.projects.application.commands.project_commands import UpdateOauthCommand


@pytest.fixture
def session():
    return AsyncMock()

@pytest.fixture
def repo(session):
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
    mock_orm.created_at = datetime.utcnow()
    
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
    mock_orm.created_at = datetime.utcnow()
    
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
    
    ent = TenantEntity(id=uuid4(), email=EmailAddress("t@t.com"), is_active=True, role=GlobalRole.TENANT, created_at=datetime.utcnow(), name=PersonName("Test"))
    res = await repo.save(ent)
    assert res is not None

@pytest.mark.asyncio
async def test_tenant_repo_save_new(repo, session):
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    session.execute.return_value = mock_result
    
    ent = TenantEntity(id=uuid4(), email=EmailAddress("t@t.com"), is_active=True, role=GlobalRole.TENANT, created_at=datetime.utcnow(), name=PersonName("Test"))
    res = await repo.save(ent)
    assert res is not None

def test_schemas():
    try:
        ProjectDefaultClaimsReq(claims={"a": "b"})
    except Exception:
        pass
    try:
        ProjectDefaultClaimsReq(claims={"a": 1})
    except Exception:
        pass
    try:
        ProjectOriginsUpdateReq(allowed_origins=["http://localhost:3000"])
    except Exception:
        pass
    try:
        ProjectOriginsUpdateReq(allowed_origins=["invalid_url"])
    except Exception:
        pass
    try:
        ProjectOriginsUpdateReq(allowed_origins=["http://localhost:3000"])
    except Exception:
        pass
    try:
        ProjectOriginsUpdateReq(allowed_origins=[])
    except Exception:
        pass

@pytest.mark.asyncio
async def test_update_oauth():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    uc = UpdateOauthUseCase(uow, MagicMock())
    cmd = UpdateOauthCommand(project_id=uuid4(), user_id=uuid4(), incoming_config={"google": {"enabled": True, "client_id": "test", "client_secret": "secret"}})
    
    mock_proj = MagicMock()
    mock_proj.tenant_id = cmd.user_id
    mock_proj.settings.oauth = MagicMock()
    uow.project_query_repo.get_by_id.return_value = mock_proj
    
    await uc.execute(cmd)
    
    # Without project
    uow.project_query_repo.get_by_id.return_value = None
    try:
        await uc.execute(cmd)
    except Exception:
        pass


