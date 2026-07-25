import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.modules.authentication.infrastructure.database.repositories.refresh_token_repository import (
    DBRefreshTokenRepositoryAdapter,
)
from src.modules.users.infrastructure.models import User
from src.modules.projects.infrastructure.models import Project
from src.shared.domain.entities import ClientMetadata
from src.modules.authentication.infrastructure.models import RefreshToken
from src.modules.superadmin.infrastructure.models import Tenant
from src.modules.authorization.domain.enums import GlobalRole


@pytest.fixture
def repo(db_session: AsyncSession):
    cache = AsyncMock()
    return DBRefreshTokenRepositoryAdapter(
        session=db_session, lifetime_days=7, cache=cache
    )


@pytest.fixture
async def active_tenant(db_session: AsyncSession):
    t = Tenant(
        id=uuid4(),
        email="tenant_act@example.com",
        name="Tenant Act",
        role=GlobalRole.TENANT,
        is_active=True,
        is_verified=True,
    )
    db_session.add(t)
    await db_session.flush()
    return t


@pytest.fixture
async def project(db_session: AsyncSession, active_tenant):
    p = Project(
        id=uuid4(),
        name="Test Project",
        tenant_id=active_tenant.id,
        private_key="dummy_private",
        public_key="dummy_public",
        api_key_hash="dummy_hash",
    )
    db_session.add(p)
    await db_session.flush()
    return p


@pytest.mark.asyncio
async def test_validate_and_rotate_expired(
    db_session: AsyncSession, repo: DBRefreshTokenRepositoryAdapter, project: Project
):
    user_id = uuid4()
    user = User(
        id=user_id,
        email="test_exp@example.com",
        name="Test User",
        project_id=project.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    token_str = await repo.create(user_id)

    # Make token expired
    res = await db_session.execute(
        select(RefreshToken).where(RefreshToken.user_id == user_id)
    )
    refresh = res.scalar_one()
    refresh.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    db_session.add(refresh)
    await db_session.flush()

    identity, new_token, custom_claims = await repo.validate(token_str)
    assert identity is None
    assert new_token is None


@pytest.mark.asyncio
async def test_validate_and_rotate_inactive_user(
    db_session: AsyncSession, repo: DBRefreshTokenRepositoryAdapter, project: Project
):
    user_id = uuid4()
    user = User(
        id=user_id,
        email="test_inact@example.com",
        name="Test User",
        project_id=project.id,
        is_active=False,
    )
    db_session.add(user)
    await db_session.flush()

    token_str = await repo.create(user_id)

    identity, new_token, custom_claims = await repo.validate(token_str)
    assert identity is None
    assert new_token is None


@pytest.mark.asyncio
async def test_validate_and_rotate_client_meta(
    db_session: AsyncSession, repo: DBRefreshTokenRepositoryAdapter, project: Project
):
    user_id = uuid4()
    user = User(
        id=user_id,
        email="test_meta@example.com",
        name="Test User",
        project_id=project.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    token_str = await repo.create(user_id)

    meta = ClientMetadata(ip_address="1.1.1.1", user_agent="Mozilla")
    identity, new_token, custom_claims = await repo.validate(
        token_str, client_meta=meta
    )

    assert identity is not None
    assert identity.id == user_id

    # Verify DB was updated
    res = await db_session.execute(
        select(RefreshToken).where(RefreshToken.user_id == user_id)
    )
    refresh = res.scalar_one()
    assert refresh.ip_address == "1.1.1.1"


@pytest.mark.asyncio
async def test_validate_and_rotate_rotation_branch(
    db_session: AsyncSession, repo: DBRefreshTokenRepositoryAdapter, project: Project
):
    user_id = uuid4()
    user = User(
        id=user_id,
        email="test_rot@example.com",
        name="Test User",
        project_id=project.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    token_str = await repo.create(user_id)

    # Make token almost expired (under 30% lifetime)
    res = await db_session.execute(
        select(RefreshToken).where(RefreshToken.user_id == user_id)
    )
    refresh = res.scalar_one()
    # 7 days lifetime. 30% is 2.1 days.
    refresh.expires_at = datetime.now(timezone.utc) + timedelta(days=1)
    db_session.add(refresh)
    await db_session.flush()

    identity, new_token, custom_claims = await repo.validate(token_str)
    assert identity is not None
    assert new_token is not None  # rotated!
    assert new_token != token_str


@pytest.mark.asyncio
async def test_validate_and_rotate_inactive_tenant(db_session: AsyncSession):
    cache = AsyncMock()
    repo = DBRefreshTokenRepositoryAdapter(
        session=db_session, lifetime_days=7, cache=cache
    )

    t = Tenant(
        id=uuid4(),
        email="tenant_inact@example.com",
        name="Tenant Inact",
        role=GlobalRole.TENANT,
        is_active=False,
        is_verified=True,
    )
    db_session.add(t)
    await db_session.flush()

    token_str = await repo.create(t.id)

    identity, new_token, custom_claims = await repo.validate(token_str)
    assert identity is None
