import pytest
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.projects.adapters.project_command_repository import (
    SQLProjectCommandRepositoryAdapter,
)
from src.modules.projects.adapters.project_query_repository import (
    SQLProjectQueryRepositoryAdapter,
)
from src.modules.projects.adapters.project_user_repository import (
    SQLProjectUserRepositoryAdapter,
)
from src.modules.projects.domain.entities import ProjectEntity
from src.modules.superadmin.infrastructure.models import Tenant
from src.modules.users.infrastructure.models import User
from src.shared.adapters.encryption import FernetEncryptionAdapter


@pytest.fixture
def encryption_adapter():
    from cryptography.fernet import Fernet

    return FernetEncryptionAdapter(key=Fernet.generate_key().decode())


@pytest.fixture
def project_command_repo(encryption_adapter):
    return SQLProjectCommandRepositoryAdapter(encryption_adapter)


@pytest.fixture
def project_query_repo(encryption_adapter):
    return SQLProjectQueryRepositoryAdapter(encryption_adapter)


@pytest.fixture
def project_user_repo():
    return SQLProjectUserRepositoryAdapter()


@pytest.mark.asyncio
async def test_project_save_and_query(
    db_session: AsyncSession, project_command_repo, project_query_repo
):
    tenant = Tenant(email=f"tenant_{uuid4()}@test.com", name="Tenant")
    db_session.add(tenant)
    await db_session.flush()

    project_name = f"Test Project {uuid4()}"
    new_project = ProjectEntity(
        id=uuid4(),
        tenant_id=tenant.id,
        name=project_name,
        admin_email="admin@project.com",
        private_key="sensitive_private_key",
        public_key="public_key",
        api_key_hash="hash",
        created_at=datetime.now(timezone.utc),
    )

    saved_project = await project_command_repo.save(db_session, new_project)
    await db_session.flush()
    assert saved_project.id == new_project.id

    # Query by ID
    queried = await project_query_repo.get_by_id(db_session, saved_project.id)
    assert queried is not None
    assert queried.name == project_name
    assert queried.private_key == "sensitive_private_key"

    # Query by name
    queried_by_name = await project_query_repo.get_by_name(db_session, project_name)
    assert queried_by_name is not None
    assert queried_by_name.id == saved_project.id

    # Query all for tenant
    projects = await project_query_repo.get_all_for_tenant(db_session, tenant.id)
    assert len(projects) >= 1
    assert any(p.id == saved_project.id for p in projects)


@pytest.mark.asyncio
async def test_project_delete(
    db_session: AsyncSession, project_command_repo, project_query_repo
):
    tenant = Tenant(email=f"tenant_{uuid4()}@test.com", name="Tenant")
    db_session.add(tenant)
    await db_session.flush()

    new_project = ProjectEntity(
        id=uuid4(),
        tenant_id=tenant.id,
        name=f"To Delete {uuid4()}",
        admin_email="admin@project.com",
        private_key="sensitive_private_key",
        public_key="public_key",
        api_key_hash="hash",
        created_at=datetime.now(timezone.utc),
    )
    saved = await project_command_repo.save(db_session, new_project)
    await db_session.flush()

    await project_command_repo.delete(db_session, saved.id)
    await db_session.flush()

    queried = await project_query_repo.get_by_id(db_session, saved.id)
    assert queried is None


@pytest.mark.asyncio
async def test_project_users_operations(
    db_session: AsyncSession, project_command_repo, project_user_repo
):
    tenant = Tenant(email=f"tenant_{uuid4()}@test.com", name="Tenant")
    db_session.add(tenant)
    await db_session.flush()

    new_project = ProjectEntity(
        id=uuid4(),
        tenant_id=tenant.id,
        name=f"User Project {uuid4()}",
        admin_email="admin@project.com",
        private_key="sensitive_private_key",
        public_key="public_key",
        api_key_hash="hash",
        created_at=datetime.now(timezone.utc),
    )
    saved = await project_command_repo.save(db_session, new_project)

    user1 = User(project_id=saved.id, email="u1@test.com", name="User 1")
    user2 = User(project_id=saved.id, email="u2@test.com", name="User 2")
    db_session.add(user1)
    db_session.add(user2)
    await db_session.flush()

    # List users
    users = await project_user_repo.list_project_users(db_session, saved.id)
    assert len(users) == 2

    # Count users
    count = await project_user_repo.count_project_users(db_session, saved.id)
    assert count == 2

    # Update status
    updated = await project_user_repo.update_user_status(
        db_session, saved.id, user1.id, is_active=False
    )
    assert updated is not None
    assert updated.is_active is False

    # Update claims
    updated = await project_user_repo.update_user_claims(
        db_session, saved.id, user1.id, {"admin": True}
    )
    assert updated is not None
    assert updated.custom_claims == {"admin": True}
