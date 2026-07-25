import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.authentication.infrastructure.database.repositories.sql_user_command_repository import (
    SQLUserCommandRepositoryAdapter,
)
from src.modules.projects.infrastructure.models import Project
from sqlalchemy import select
from src.modules.users.infrastructure.models import User
from src.modules.authentication.infrastructure.models import Password, OAuthAccount
from src.modules.superadmin.infrastructure.models import Tenant
from src.modules.authorization.domain.enums import GlobalRole


@pytest.fixture
def repo(db_session: AsyncSession):
    return SQLUserCommandRepositoryAdapter(session=db_session)


@pytest.fixture
async def project(db_session: AsyncSession):
    t = Tenant(
        id=uuid4(),
        email="tenant@example.com",
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


@pytest.mark.asyncio
async def test_create_user_with_password(
    db_session: AsyncSession, repo: SQLUserCommandRepositoryAdapter, project
):
    identity = await repo.create_user_with_password(
        email="pass_user@example.com",
        name="Pass User",
        password_hash="hash123",
        is_verified=False,
        project_id=project.id,
    )

    assert identity.email.value == "pass_user@example.com"
    assert identity.name == "Pass User"
    assert identity.is_verified is False

    # Verify in DB
    user = (
        await db_session.execute(select(User).where(User.id == identity.id))
    ).scalar_one()
    assert user.project_id == project.id

    pw = (
        await db_session.execute(
            select(Password).where(Password.user_id == identity.id)
        )
    ).scalar_one()
    assert pw.password_hash == "hash123"


@pytest.mark.asyncio
async def test_create_tenant_with_password(
    db_session: AsyncSession, repo: SQLUserCommandRepositoryAdapter
):
    identity = await repo.create_user_with_password(
        email="tenant@example.com",
        name="Tenant User",
        password_hash="hash123",
        is_verified=False,
        role=GlobalRole.TENANT,
    )

    assert identity.email.value == "tenant@example.com"
    assert identity.role == GlobalRole.TENANT

    tenant = (
        await db_session.execute(select(Tenant).where(Tenant.id == identity.id))
    ).scalar_one()
    assert tenant.role == GlobalRole.TENANT

    pw = (
        await db_session.execute(
            select(Password).where(Password.tenant_id == identity.id)
        )
    ).scalar_one()
    assert pw.password_hash == "hash123"


@pytest.mark.asyncio
async def test_create_user_with_oauth(
    db_session: AsyncSession, repo: SQLUserCommandRepositoryAdapter, project
):
    identity = await repo.create_user_with_oauth(
        email="oauth@example.com",
        name="OAuth User",
        picture="https://example.com/pic.jpg",
        provider="google",
        oauth_sub="sub123",
        project_id=project.id,
    )

    assert identity.is_verified is True

    oauth = (
        await db_session.execute(
            select(OAuthAccount).where(OAuthAccount.user_id == identity.id)
        )
    ).scalar_one()
    assert oauth.provider == "google"
    assert oauth.oauth_sub == "sub123"


@pytest.mark.asyncio
async def test_update_password(
    db_session: AsyncSession, repo: SQLUserCommandRepositoryAdapter, project
):
    identity = await repo.create_user_with_password(
        "update_pw@example.com", "Test", "old_hash", project_id=project.id
    )

    await repo.update_password(identity.id, "new_hash")
    await db_session.flush()

    pw = (
        await db_session.execute(
            select(Password).where(Password.user_id == identity.id)
        )
    ).scalar_one()
    assert pw.password_hash == "new_hash"


@pytest.mark.asyncio
async def test_disable_local_login(
    db_session: AsyncSession, repo: SQLUserCommandRepositoryAdapter, project
):
    identity = await repo.create_user_with_password(
        "disable_login@example.com", "Test", "hash", project_id=project.id
    )

    await repo.disable_local_login(identity.id)
    await db_session.flush()

    pw = (
        await db_session.execute(
            select(Password).where(Password.user_id == identity.id)
        )
    ).scalar_one_or_none()
    assert pw is None


@pytest.mark.asyncio
async def test_verify_user_email(
    db_session: AsyncSession, repo: SQLUserCommandRepositoryAdapter, project
):
    identity = await repo.create_user_with_password(
        "verify@example.com", "Test", "hash", is_verified=False, project_id=project.id
    )

    await repo.verify_user_email(identity.id, name="Verified Name")
    await db_session.flush()

    user = (
        await db_session.execute(select(User).where(User.id == identity.id))
    ).scalar_one()
    assert user.is_verified is True
    assert user.name == "Verified Name"


@pytest.mark.asyncio
async def test_delete_undelete_user(
    db_session: AsyncSession, repo: SQLUserCommandRepositoryAdapter, project
):
    identity = await repo.create_user_with_password(
        "delete@example.com", "Test", "hash", project_id=project.id
    )

    await repo.delete_user(identity.id)
    await db_session.flush()

    user = (
        await db_session.execute(select(User).where(User.id == identity.id))
    ).scalar_one()
    assert user.is_active is False
    assert user.deleted_at is not None

    await repo.undelete_user(identity.id)
    await db_session.flush()

    user = (
        await db_session.execute(select(User).where(User.id == identity.id))
    ).scalar_one()
    assert user.deleted_at is None


@pytest.mark.asyncio
async def test_update_oauth_profile(
    db_session: AsyncSession, repo: SQLUserCommandRepositoryAdapter, project
):
    identity = await repo.create_user_with_password(
        "oauth_prof@example.com", None, "hash", is_verified=False, project_id=project.id
    )

    await repo.update_oauth_profile(
        identity.id, name="Oauth Name", picture="https://example.com/oauth_pic.jpg"
    )
    await db_session.flush()

    user = (
        await db_session.execute(select(User).where(User.id == identity.id))
    ).scalar_one()
    assert user.is_verified is True
    assert user.name == "Oauth Name"
    assert user.picture == "https://example.com/oauth_pic.jpg"
