import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.authentication.infrastructure.database.repositories.sql_user_command_repository import (
    SQLUserCommandRepositoryAdapter,
)
from src.modules.superadmin.infrastructure.models import Tenant
from src.modules.authentication.infrastructure.models import OAuthAccount, Password
from src.modules.authorization.domain.enums import GlobalRole
from sqlalchemy import select


@pytest.mark.asyncio
async def test_create_user_with_oauth_tenant(db_session: AsyncSession):
    repo = SQLUserCommandRepositoryAdapter(db_session)
    identity = await repo.create_user_with_oauth(
        email="tenant@example.com",
        name="Tenant",
        picture=None,
        provider="google",
        oauth_sub="12345",
        project_id=None,
        role=GlobalRole.SUPERADMIN,
    )
    assert identity.email == "tenant@example.com"
    assert identity.is_verified is True

    tenant_res = await db_session.execute(
        select(Tenant).where(Tenant.id == identity.id)
    )
    tenant = tenant_res.scalar_one()
    assert tenant.role == GlobalRole.SUPERADMIN

    oauth_res = await db_session.execute(
        select(OAuthAccount).where(OAuthAccount.tenant_id == identity.id)
    )
    assert oauth_res.scalar_one().provider == "google"


@pytest.mark.asyncio
async def test_link_oauth_account_tenant(db_session: AsyncSession):
    repo = SQLUserCommandRepositoryAdapter(db_session)
    tenant = Tenant(email="t2@example.com", name="T2", is_verified=True)
    db_session.add(tenant)
    await db_session.flush()

    await repo.link_oauth_account(tenant.id, "github", "sub2", project_id=None)
    await db_session.flush()

    oauth_res = await db_session.execute(
        select(OAuthAccount).where(OAuthAccount.tenant_id == tenant.id)
    )
    assert oauth_res.scalar_one().provider == "github"


@pytest.mark.asyncio
async def test_update_password_tenant(db_session: AsyncSession):
    repo = SQLUserCommandRepositoryAdapter(db_session)
    tenant = Tenant(email="t3@example.com", name="T3", is_verified=True)
    db_session.add(tenant)
    await db_session.flush()

    await repo.update_password(tenant.id, "new_hash")
    await db_session.flush()

    pwd_res = await db_session.execute(
        select(Password).where(Password.tenant_id == tenant.id)
    )
    assert pwd_res.scalar_one().password_hash == "new_hash"


@pytest.mark.asyncio
async def test_update_role_tenant(db_session: AsyncSession):
    repo = SQLUserCommandRepositoryAdapter(db_session)
    tenant = Tenant(
        email="t4@example.com", name="T4", is_verified=True, role=GlobalRole.TENANT
    )
    db_session.add(tenant)
    await db_session.flush()

    await repo.update_role(tenant.id, GlobalRole.SUPERADMIN)
    await db_session.flush()

    tenant_res = await db_session.execute(select(Tenant).where(Tenant.id == tenant.id))
    assert tenant_res.scalar_one().role == GlobalRole.SUPERADMIN


@pytest.mark.asyncio
async def test_update_oauth_profile_tenant(db_session: AsyncSession):
    repo = SQLUserCommandRepositoryAdapter(db_session)
    tenant = Tenant(email="t5@example.com", name=None, picture=None, is_verified=False)
    db_session.add(tenant)
    await db_session.flush()

    await repo.update_oauth_profile(tenant.id, name="T5", picture="pic.jpg")
    await db_session.flush()

    tenant_res = await db_session.execute(select(Tenant).where(Tenant.id == tenant.id))
    tenant = tenant_res.scalar_one()
    assert tenant.is_verified is True
    assert tenant.name == "T5"
    assert tenant.picture == "pic.jpg"
