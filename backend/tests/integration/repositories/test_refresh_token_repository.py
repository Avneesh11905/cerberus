import pytest
from uuid import uuid4
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.authentication.infrastructure.database.repositories.refresh_token_repository import (
    DBRefreshTokenRepositoryAdapter,
)
from src.modules.users.infrastructure.models import User
from src.modules.projects.infrastructure.models import Project
from src.shared.domain.entities import ClientMetadata
from src.modules.authentication.infrastructure.database.repositories.refresh_token_utils import (
    hash_token,
)
from src.modules.authentication.infrastructure.models import RefreshToken
from sqlalchemy import select
from src.modules.superadmin.infrastructure.models import Tenant
from src.modules.authorization.domain.enums import GlobalRole


@pytest.fixture
def repo(db_session: AsyncSession):
    cache = AsyncMock()
    return DBRefreshTokenRepositoryAdapter(
        session=db_session, lifetime_days=7, cache=cache
    )


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
async def test_create_and_validate_token(
    db_session: AsyncSession, repo: DBRefreshTokenRepositoryAdapter, project: Project
):
    # Setup user
    user_id = uuid4()

    user = User(
        id=user_id,
        email="test@example.com",
        project_id=project.id,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.flush()

    meta = ClientMetadata(ip_address="127.0.0.1", user_agent="TestAgent")
    raw_token = await repo.create(user_id=user_id, client_meta=meta)

    assert raw_token is not None

    # Verify in DB
    hashed = hash_token(raw_token)
    res = await db_session.execute(
        select(RefreshToken).where(RefreshToken.token == hashed)
    )
    db_token = res.scalar_one()
    assert db_token.user_id == user_id
    assert db_token.ip_address == "127.0.0.1"

    # Validate
    identity, new_token, family_id = await repo.validate(raw_token)
    assert identity is not None
    assert identity.id == user_id
    assert new_token is None  # because it hasn't passed 70% of lifetime
    assert family_id == db_token.family_id


@pytest.mark.asyncio
async def test_revoke_token(
    db_session: AsyncSession, repo: DBRefreshTokenRepositoryAdapter, project: Project
):
    user_id = uuid4()
    user = User(
        id=user_id,
        email="revoke@example.com",
        is_active=True,
        is_verified=True,
        project_id=project.id,
    )
    db_session.add(user)
    await db_session.flush()

    raw_token = await repo.create(user_id=user_id)
    await repo.revoke(raw_token)

    identity, _, _ = await repo.validate(raw_token)
    assert identity is None  # Should be revoked


@pytest.mark.asyncio
async def test_revoke_all_for_user(
    db_session: AsyncSession, repo: DBRefreshTokenRepositoryAdapter, project: Project
):
    user_id = uuid4()
    user = User(
        id=user_id,
        email="revokeall@example.com",
        is_active=True,
        is_verified=True,
        project_id=project.id,
    )
    db_session.add(user)
    await db_session.flush()

    token1 = await repo.create(user_id=user_id)
    token2 = await repo.create(user_id=user_id)

    await repo.revoke_all_for_user(user_id)

    id1, _, _ = await repo.validate(token1)
    id2, _, _ = await repo.validate(token2)
    assert id1 is None
    assert id2 is None


@pytest.mark.asyncio
async def test_get_active_sessions(
    db_session: AsyncSession, repo: DBRefreshTokenRepositoryAdapter, project: Project
):
    user_id = uuid4()
    user = User(
        id=user_id,
        email="sessions@example.com",
        is_active=True,
        is_verified=True,
        project_id=project.id,
    )
    db_session.add(user)
    await db_session.flush()

    meta = ClientMetadata(ip_address="1.2.3.4", user_agent="Mozilla")
    token1 = await repo.create(user_id=user_id, client_meta=meta)

    sessions = await repo.get_active_sessions(user_id, current_token=token1)

    assert len(sessions) == 1
    assert sessions[0].ip_address == "1.2.3.4"
    assert sessions[0].is_current is True


@pytest.mark.asyncio
async def test_cleanup_expired(
    db_session: AsyncSession, repo: DBRefreshTokenRepositoryAdapter, project: Project
):
    user_id = uuid4()
    user = User(
        id=user_id,
        email="cleanup@example.com",
        is_active=True,
        is_verified=True,
        project_id=project.id,
    )
    db_session.add(user)
    await db_session.flush()

    raw_token = await repo.create(user_id=user_id)
    await repo.revoke(raw_token)  # Marks as used

    count = await repo.cleanup_expired()
    assert count >= 1


@pytest.mark.asyncio
async def test_reuse_detection(
    db_session: AsyncSession, repo: DBRefreshTokenRepositoryAdapter, project: Project
):
    user_id = uuid4()
    user = User(
        id=user_id,
        email="reuse@example.com",
        is_active=True,
        is_verified=True,
        project_id=project.id,
    )
    db_session.add(user)
    await db_session.flush()

    raw_token = await repo.create(user_id=user_id)
    await repo.revoke(raw_token)  # Mark as used/revoked

    # Validate the used token (simulates reuse)
    id1, t1, f1 = await repo.validate(raw_token)
    assert id1 is None


@pytest.mark.asyncio
async def test_revoke_all_for_tenant_user(
    db_session: AsyncSession, repo: DBRefreshTokenRepositoryAdapter, project: Project
):
    user_id = uuid4()
    email = "revoke_tenant@example.com"
    user = User(
        id=user_id,
        email=email,
        is_active=True,
        is_verified=True,
        project_id=project.id,
    )
    db_session.add(user)
    await db_session.flush()

    token1 = await repo.create(user_id=user_id)
    token2 = await repo.create(user_id=user_id)

    await repo.revoke_all_for_user(user_id)

    id1, _, _ = await repo.validate(token1)
    id2, _, _ = await repo.validate(token2)
    assert id1 is None
    assert id2 is None


@pytest.mark.asyncio
async def test_tenant_token(
    db_session: AsyncSession, repo: DBRefreshTokenRepositoryAdapter, project: Project
):
    tenant_id = project.tenant_id

    raw_token = await repo.create(user_id=tenant_id)
    assert raw_token is not None

    identity, new_token, family_id = await repo.validate(raw_token)
    assert identity is not None
    assert identity.id == tenant_id
    assert identity.role == GlobalRole.TENANT
