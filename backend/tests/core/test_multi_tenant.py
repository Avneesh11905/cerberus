import pytest
from uuid import uuid4
import hashlib

from src.authentication.core.domain import UserRole
from src.authentication.core.usecases import RegisterLocalUserUseCase
from src.authentication.adapters.security.password_hasher import Argon2PasswordHasher

# Import mocks
from tests.conftest import MockUserRepository, MockEmailSender, MockCache, MockLogger

@pytest.mark.asyncio
async def test_scoped_constraints():
    """Test Scoped Constraints: Register user A under Project X. Register user B under Project Y. Assert both succeed."""
    user_repo = MockUserRepository()
    cache = MockCache()
    email_sender = MockEmailSender()
    logger = MockLogger()
    hasher = Argon2PasswordHasher()
    
    usecase: RegisterLocalUserUseCase = RegisterLocalUserUseCase(
        user_repo=user_repo,
        hasher=hasher,
        logger=logger,
        email_sender=email_sender,
        cache=cache
    )
    
    email = "test@example.com"
    project_x = uuid4()
    project_y = uuid4()
    
    # 1. Register under Project X
    class DummyUoW:
        session = None
    uow = DummyUoW()
    
    await usecase.execute(uow, email, "StrongPass1!", "User A", project_id=project_x)
    
    # 2. Register under Project Y with the SAME EMAIL
    await usecase.execute(uow, email, "StrongPass2!", "User B", project_id=project_y)
    
    # Both should be pending in cache now.
    hash_x = f"pending_reg:{str(project_x)}:{hashlib.sha256(email.encode()).hexdigest()}"
    hash_y = f"pending_reg:{str(project_y)}:{hashlib.sha256(email.encode()).hexdigest()}"
    
    assert hash_x in cache.data
    assert hash_y in cache.data

@pytest.mark.asyncio
async def test_global_registration_does_not_escalate_admin_email():
    """Global use-case registration must not infer admin from email."""
    user_repo = MockUserRepository()
    cache = MockCache()
    email_sender = MockEmailSender()
    logger = MockLogger()
    hasher = Argon2PasswordHasher()

    usecase: RegisterLocalUserUseCase = RegisterLocalUserUseCase(
        user_repo=user_repo,
        hasher=hasher,
        logger=logger,
        email_sender=email_sender,
        cache=cache,
    )

    class DummyUoW:
        session = None

    email = "admin@example.com"
    await usecase.execute(DummyUoW(), email, "AdminPass1!", "Admin")

    hash_global = f"pending_reg:global:{hashlib.sha256(email.encode()).hexdigest()}"
    pending = cache.data[hash_global]
    assert pending["role"] == UserRole.USER


@pytest.mark.asyncio
async def test_explicit_tenant_registration_sets_tenant_role():
    """Tenant role must be selected explicitly by the tenant registration route/use case caller."""
    user_repo = MockUserRepository()
    cache = MockCache()
    email_sender = MockEmailSender()
    logger = MockLogger()
    hasher = Argon2PasswordHasher()

    usecase: RegisterLocalUserUseCase = RegisterLocalUserUseCase(
        user_repo=user_repo,
        hasher=hasher,
        logger=logger,
        email_sender=email_sender,
        cache=cache,
    )

    class DummyUoW:
        session = None

    email = "tenant@example.com"
    await usecase.execute(DummyUoW(), email, "TenantPass1!", "Tenant", role=UserRole.TENANT)

    hash_global = f"pending_reg:global:{hashlib.sha256(email.encode()).hexdigest()}"
    pending = cache.data[hash_global]
    assert pending["role"] == UserRole.TENANT
