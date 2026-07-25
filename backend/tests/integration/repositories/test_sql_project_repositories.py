from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.projects.domain.entities import ProjectEntity
from src.modules.projects.infrastructure.database.repositories.project_command_repository import (
    SQLProjectCommandRepositoryAdapter,
)
from src.modules.projects.infrastructure.database.repositories.project_query_repository import (
    SQLProjectQueryRepositoryAdapter,
)
from src.modules.projects.infrastructure.database.repositories.project_user_repository import (
    SQLProjectUserRepositoryAdapter,
)
from src.modules.superadmin.infrastructure.models import Tenant
from src.modules.users.infrastructure.models import User
from src.shared.infrastructure.adapters.encryption import FernetEncryptionAdapter


@pytest.fixture
def encryption_adapter():
    from cryptography.fernet import Fernet

    return FernetEncryptionAdapter(key=Fernet.generate_key().decode())


@pytest.fixture
def project_command_repo(db_session, encryption_adapter):
    return SQLProjectCommandRepositoryAdapter(db_session, encryption_adapter)


@pytest.fixture
def project_query_repo(db_session, encryption_adapter):
    return SQLProjectQueryRepositoryAdapter(db_session, encryption_adapter)


@pytest.fixture
def project_user_repo(db_session):
    return SQLProjectUserRepositoryAdapter(db_session)


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
        private_key="sensitive_private_key",
        public_key="public_key",
        api_key_hash="hash",
        created_at=datetime.now(timezone.utc),
    )

    saved_project = await project_command_repo.save(new_project)
    await db_session.flush()
    assert saved_project.id == new_project.id

    # Query by ID
    queried = await project_query_repo.get_by_id(saved_project.id)
    assert queried is not None
    assert queried.name == project_name
    assert queried.private_key == "sensitive_private_key"

    # Query by name
    queried_by_name = await project_query_repo.get_by_name(project_name)
    assert queried_by_name is not None
    assert queried_by_name.id == saved_project.id

    # Query all for tenant
    projects = await project_query_repo.get_all_for_tenant(tenant.id)
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
        private_key="sensitive_private_key",
        public_key="public_key",
        api_key_hash="hash",
        created_at=datetime.now(timezone.utc),
    )
    saved = await project_command_repo.save(new_project)
    await db_session.flush()

    await project_command_repo.delete(saved.id)
    await db_session.flush()

    queried = await project_query_repo.get_by_id(saved.id)
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
        private_key="sensitive_private_key",
        public_key="public_key",
        api_key_hash="hash",
        created_at=datetime.now(timezone.utc),
    )
    saved = await project_command_repo.save(new_project)

    user1 = User(project_id=saved.id, email="u1@test.com", name="User 1")
    user2 = User(project_id=saved.id, email="u2@test.com", name="User 2")
    db_session.add(user1)
    db_session.add(user2)
    await db_session.flush()

    # List users
    users, count = await project_user_repo.list_project_users(saved.id)
    assert len(users) == 2

    # Count users
    assert count == 2

    # Update status
    updated = await project_user_repo.update_user_status(
        saved.id, user1.id, is_active=False
    )
    assert updated is not None
    assert updated.is_active is False

    # Update claims
    updated = await project_user_repo.update_user_claims(
        saved.id, user1.id, {"admin": True}
    )
    assert updated is not None
    assert updated.custom_claims == {"admin": True}

    # Test search filters
    users, count = await project_user_repo.list_project_users(saved.id, search="u1")
    assert len(users) == 1
    assert users[0].email.value == "u1@test.com"

    _, count = await project_user_repo.list_project_users(saved.id, search="u2")
    assert count == 1

    # Test not found
    not_found_status = await project_user_repo.update_user_status(
        saved.id, uuid4(), True
    )
    assert not_found_status is None

    not_found_claims = await project_user_repo.update_user_claims(saved.id, uuid4(), {})
    assert not_found_claims is None

    # Test tenant user status
    tenant_updated = await project_user_repo.update_tenant_user_status(
        tenant.id, "u2@test.com", False
    )
    assert len(tenant_updated) == 1
    assert tenant_updated[0].is_active is False

    tenant_updated_empty = await project_user_repo.update_tenant_user_status(
        tenant.id, "nonexistent@test.com", False
    )
    assert len(tenant_updated_empty) == 0
