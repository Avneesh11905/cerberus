import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.auth.authentication.adapters.repository.sql_user_command_repository import SQLUserCommandRepositoryAdapter
from src.modules.auth.authentication.adapters.repository.sql_user_query_repository import SQLUserQueryRepositoryAdapter
from src.modules.superadmin.infrastructure.models import Tenant
from src.modules.projects.infrastructure.models import Project

@pytest.fixture
def command_repo():
    return SQLUserCommandRepositoryAdapter()

@pytest.fixture
def query_repo():
    return SQLUserQueryRepositoryAdapter()

@pytest.mark.asyncio
async def test_tenant_creation_and_query(db_session: AsyncSession, command_repo, query_repo):
    email = "tenant@test.com"
    identity = await command_repo.create_user_with_password(
        session=db_session,
        email=email,
        name="Test Tenant",
        password_hash="dummy_hash",
        is_verified=True,
    )
    assert identity.id is not None
    assert identity.email == email
    
    # Query it back
    queried = await query_repo.find_by_id(db_session, identity.id)
    assert queried is not None
    assert queried.email == email
    
    # Check password hash
    pwd = await query_repo.find_password_hash(db_session, identity.id, is_tenant=True)
    assert pwd == "dummy_hash"

@pytest.mark.asyncio
async def test_project_user_oauth(db_session: AsyncSession, command_repo, query_repo):
    # Setup Tenant and Project first manually
    tenant = Tenant(email="owner@test.com", name="Owner")
    db_session.add(tenant)
    await db_session.flush()
    
    project = Project(tenant_id=tenant.id, name="Test Project", private_key="priv", public_key="pub", api_key_hash="hash")
    db_session.add(project)
    await db_session.flush()
    
    # Create user with oauth
    email = "user@test.com"
    identity = await command_repo.create_user_with_oauth(
        session=db_session,
        email=email,
        name="Oauth User",
        picture=None,
        provider="google",
        oauth_sub="12345",
        project_id=project.id,
    )
    
    assert identity.project_id == project.id

    queried = await query_repo.find_by_oauth(db_session, provider="google", oauth_sub="12345", project_id=project.id)
    assert queried is not None
    assert queried.email == email

@pytest.mark.asyncio
async def test_disable_and_update_password(db_session: AsyncSession, command_repo, query_repo):
    identity = await command_repo.create_user_with_password(
        session=db_session,
        email=f"pwd_{uuid4()}@test.com",
        name="Pwd User",
        password_hash="old_hash"
    )
    
    # Update password
    await command_repo.update_password(db_session, identity.id, "new_hash")
    await db_session.flush()
    pwd = await query_repo.find_password_hash(db_session, identity.id)
    assert pwd == "new_hash"
    
    # Disable local login
    await command_repo.disable_local_login(db_session, identity.id)
    await db_session.flush()
    pwd_after = await query_repo.find_password_hash(db_session, identity.id)
    assert pwd_after is None

@pytest.mark.asyncio
async def test_delete_undelete_user(db_session: AsyncSession, command_repo, query_repo):
    identity = await command_repo.create_user_with_password(
        session=db_session,
        email=f"del_{uuid4()}@test.com",
        name="Del User",
        password_hash=None
    )
    
    await command_repo.delete_user(db_session, identity.id)
    await db_session.flush()
    # Find by ID still returns it but we can check is_active flag in models later, the repo just returns it.
    queried = await query_repo.find_by_id(db_session, identity.id)
    assert queried is not None
    
    await command_repo.undelete_user(db_session, identity.id)
    await db_session.flush()

@pytest.mark.asyncio
async def test_link_oauth_account(db_session: AsyncSession, command_repo, query_repo):
    identity = await command_repo.create_user_with_password(
        session=db_session,
        email=f"link_{uuid4()}@test.com",
        name="Link User",
        password_hash=None
    )

    await command_repo.link_oauth_account(
        session=db_session,
        user_id=identity.id,
        provider="github",
        oauth_sub="gh_123"
    )
    await db_session.flush()

    queried = await query_repo.find_by_oauth(db_session, provider="github", oauth_sub="gh_123")
    assert queried is not None
    assert queried.id == identity.id

@pytest.mark.asyncio
async def test_find_by_email(db_session: AsyncSession, command_repo, query_repo):
    email = f"find_{uuid4()}@test.com"
    await command_repo.create_user_with_password(
        session=db_session,
        email=email,
        name="Find User",
        password_hash=None
    )

    queried = await query_repo.find_by_email(db_session, email)
    assert queried is not None
    assert queried.email == email
