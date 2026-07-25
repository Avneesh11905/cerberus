import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.authentication.infrastructure.database.repositories.sql_user_query_repository import (
    SQLUserQueryRepositoryAdapter,
)
from src.modules.projects.infrastructure.models import Project
from src.modules.users.infrastructure.models import User
from src.modules.authentication.infrastructure.models import Password, OAuthAccount
from src.modules.superadmin.infrastructure.models import Tenant
from src.modules.authorization.domain.enums import GlobalRole


@pytest.fixture
def repo(db_session: AsyncSession):
    return SQLUserQueryRepositoryAdapter(session=db_session)


@pytest.fixture
async def project(db_session: AsyncSession):
    t = Tenant(
        id=uuid4(),
        email="tenant_query@example.com",
        name="Tenant",
        role=GlobalRole.TENANT,
        is_active=True,
        is_verified=True,
    )
    db_session.add(t)
    await db_session.flush()
    p = Project(
        id=uuid4(),
        name="Test Project",
        tenant_id=t.id,
        private_key="dummy_private",
        public_key="dummy_public",
        api_key_hash="dummy_hash",
    )
    db_session.add(p)
    await db_session.flush()
    return p


@pytest.fixture
async def setup_users(db_session: AsyncSession, project: Project):
    user_id = uuid4()
    user = User(
        id=user_id,
        email="query_user@example.com",
        name="Query User",
        project_id=project.id,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)

    pw = Password(user_id=user_id, password_hash="hash123")
    db_session.add(pw)

    oauth_user_id = uuid4()
    oauth_user = User(
        id=oauth_user_id,
        email="oauth_query@example.com",
        project_id=project.id,
        is_active=True,
        is_verified=True,
    )
    db_session.add(oauth_user)

    oauth_acc = OAuthAccount(
        user_id=oauth_user_id, provider="google", oauth_sub="sub123"
    )
    db_session.add(oauth_acc)

    tenant_id = uuid4()
    tenant = Tenant(
        id=tenant_id,
        email="query_tenant@example.com",
        name="Query Tenant",
        role=GlobalRole.TENANT,
        is_active=True,
        is_verified=True,
    )
    db_session.add(tenant)

    await db_session.flush()

    return {
        "user_id": user_id,
        "oauth_user_id": oauth_user_id,
        "tenant_id": tenant_id,
        "project_id": project.id,
    }


@pytest.mark.asyncio
async def test_find_by_email(
    db_session: AsyncSession, repo: SQLUserQueryRepositoryAdapter, setup_users
):
    user = await repo.find_by_email("query_user@example.com", setup_users["project_id"])
    assert user is not None
    assert user.id == setup_users["user_id"]

    tenant = await repo.find_by_email("query_tenant@example.com")
    assert tenant is not None
    assert tenant.id == setup_users["tenant_id"]

    not_found = await repo.find_by_email("unknown@example.com")
    assert not_found is None


@pytest.mark.asyncio
async def test_find_by_id(
    db_session: AsyncSession, repo: SQLUserQueryRepositoryAdapter, setup_users
):
    user = await repo.find_by_id(setup_users["user_id"])
    assert user is not None
    assert user.id == setup_users["user_id"]

    tenant = await repo.find_by_id(setup_users["tenant_id"])
    assert tenant is not None
    assert tenant.id == setup_users["tenant_id"]

    not_found = await repo.find_by_id(uuid4())
    assert not_found is None


@pytest.mark.asyncio
async def test_find_by_oauth(
    db_session: AsyncSession, repo: SQLUserQueryRepositoryAdapter, setup_users
):
    user = await repo.find_by_oauth("google", "sub123", setup_users["project_id"])
    assert user is not None
    assert user.id == setup_users["oauth_user_id"]

    not_found = await repo.find_by_oauth("google", "unknown", setup_users["project_id"])
    assert not_found is None


@pytest.mark.asyncio
async def test_find_password_hash(
    db_session: AsyncSession, repo: SQLUserQueryRepositoryAdapter, setup_users
):
    pw_hash = await repo.find_password_hash(setup_users["user_id"])
    assert pw_hash == "hash123"

    not_found = await repo.find_password_hash(uuid4())
    assert not_found is None
