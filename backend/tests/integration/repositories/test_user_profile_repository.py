import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.users.infrastructure.database.repositories.user_profile_repository import SQLUserProfileRepositoryAdapter
from src.modules.projects.infrastructure.models import Project
from src.modules.users.infrastructure.models import User
from src.modules.authentication.infrastructure.models import Password, OAuthAccount
from src.modules.superadmin.infrastructure.models import Tenant
from src.modules.authorization.domain.enums import GlobalRole
from src.modules.users.domain.exceptions import UserNotFoundException
from src.shared.domain.value_objects import PersonName, HttpsUrl

@pytest.fixture
def refresh_repo_mock():
    return AsyncMock()

@pytest.fixture
def repo(db_session: AsyncSession, refresh_repo_mock):
    return SQLUserProfileRepositoryAdapter(session=db_session, refresh_repo=refresh_repo_mock)

@pytest.fixture
async def project(db_session: AsyncSession):
    t = Tenant(id=uuid4(), email="tenant_profile@example.com", name="Tenant", role=GlobalRole.TENANT, is_active=True, is_verified=True)
    db_session.add(t)
    await db_session.flush()
    p = Project(
        id=uuid4(), 
        name="Test Project", 
        tenant_id=t.id,
        private_key="dummy_private",
        public_key="dummy_public",
        api_key_hash="dummy_hash"
    )
    db_session.add(p)
    await db_session.flush()
    return p

@pytest.fixture
async def setup_users(db_session: AsyncSession, project: Project):
    user_id = uuid4()
    user = User(
        id=user_id,
        email="profile_user@example.com",
        name="Profile User",
        project_id=project.id,
        is_active=True,
        is_verified=True,
        receive_updates=True
    )
    db_session.add(user)
    
    pw = Password(user_id=user_id, password_hash="hash123")
    db_session.add(pw)
    
    tenant_id = uuid4()
    tenant = Tenant(
        id=tenant_id,
        email="profile_tenant@example.com",
        name="Profile Tenant",
        role=GlobalRole.TENANT,
        is_active=True,
        is_verified=True
    )
    db_session.add(tenant)
    
    oauth_acc = OAuthAccount(
        tenant_id=tenant_id,
        provider="github",
        oauth_sub="sub456"
    )
    db_session.add(oauth_acc)
    
    await db_session.flush()
    
    return {
        "user_id": user_id,
        "tenant_id": tenant_id
    }

@pytest.mark.asyncio
async def test_get_profile(db_session: AsyncSession, repo: SQLUserProfileRepositoryAdapter, setup_users):
    profile = await repo.get_profile(setup_users["user_id"])
    assert profile is not None
    assert profile.id == setup_users["user_id"]
    assert profile.email.value == "profile_user@example.com"
    assert "local" in profile.login_methods
    
    tenant_profile = await repo.get_profile(setup_users["tenant_id"])
    assert tenant_profile is not None
    assert tenant_profile.id == setup_users["tenant_id"]
    assert tenant_profile.email.value == "profile_tenant@example.com"
    assert "github" in tenant_profile.login_methods
    
    not_found = await repo.get_profile(uuid4())
    assert not_found is None

@pytest.mark.asyncio
async def test_save_profile(db_session: AsyncSession, repo: SQLUserProfileRepositoryAdapter, setup_users):
    profile = await repo.get_profile(setup_users["user_id"])
    assert profile is not None
    
    profile.name = PersonName("Updated Name")
    profile.picture = HttpsUrl("https://example.com/updated.jpg")
    profile.receive_updates = False
    
    updated_profile = await repo.save_profile(profile)
    assert updated_profile.name.value == "Updated Name"
    assert updated_profile.picture.value == "https://example.com/updated.jpg"
    assert updated_profile.receive_updates is False
    
    tenant_profile = await repo.get_profile(setup_users["tenant_id"])
    tenant_profile.name = PersonName("Updated Tenant")
    updated_tenant = await repo.save_profile(tenant_profile)
    assert updated_tenant.name.value == "Updated Tenant"
    
    profile.id = uuid4()
    with pytest.raises(UserNotFoundException):
        await repo.save_profile(profile)

@pytest.mark.asyncio
async def test_delete_user(db_session: AsyncSession, repo: SQLUserProfileRepositoryAdapter, setup_users, refresh_repo_mock):
    await repo.delete_user(setup_users["user_id"])
    refresh_repo_mock.revoke_all_for_user.assert_called_with(setup_users["user_id"])
    
    profile = await repo.get_profile(setup_users["user_id"])
    assert profile is None
    
    await repo.delete_user(setup_users["tenant_id"])
    refresh_repo_mock.revoke_all_for_user.assert_called_with(setup_users["tenant_id"])
    
    tenant_profile = await repo.get_profile(setup_users["tenant_id"])
    assert tenant_profile is None
    
    # Non existent
    await repo.delete_user(uuid4())
