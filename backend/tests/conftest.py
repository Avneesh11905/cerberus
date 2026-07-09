from typing import cast, Any
from uuid import UUID, uuid4

import pytest
from pydantic import AnyHttpUrl

from src.authentication.core.domain import UserIdentity, UserRole


class MockUserRepository:
    def __init__(self):
        self.users = {}  # id -> UserIdentity
        self.oauth_links = []  # tuple (user_id, provider, oauth_sub)
        self.passwords = {}  # user_id -> hash
        self.role_updates = []  # list of (user_id, role) — for assertions in tests

    async def find_by_oauth(
        self, session, provider: str, oauth_sub: str, project_id: UUID | None = None
    ) -> UserIdentity | None:
        for link in self.oauth_links:
            if link[1] == provider and link[2] == oauth_sub:
                user = self.users[link[0]]
                if user.project_id == project_id:
                    return user
        return None

    async def find_by_email(
        self, session, email: str, project_id: UUID | None = None
    ) -> UserIdentity | None:
        for user in self.users.values():
            if user.email == email and user.project_id == project_id:
                return user
        return None

    async def create_user_with_oauth(
        self,
        session,
        email: str,
        name: str | None,
        picture: str | None,
        provider: str,
        oauth_sub: str,
        project_id: UUID | None = None,
        role: UserRole = UserRole.USER,
    ) -> UserIdentity:
        user_id = uuid4()
        user = UserIdentity(
            id=user_id,
            email=email,
            name=name,
            picture=cast(AnyHttpUrl, picture) if picture else None,
            is_verified=True,
            project_id=project_id,
            role=role,
        )
        self.users[user_id] = user
        self.oauth_links.append((user_id, provider, oauth_sub))
        return user

    async def link_oauth_account(
        self,
        session: Any,
        user_id: UUID,
        provider: str,
        oauth_sub: str,
        project_id: UUID | None = None,
    ) -> None:
        self.oauth_links.append((user_id, provider, oauth_sub))

    async def create_user_with_password(
        self,
        session,
        email: str,
        name: str | None,
        password_hash: str | None,
        is_verified: bool = False,
        project_id: UUID | None = None,
        role: UserRole = UserRole.USER,
    ) -> UserIdentity:
        user_id = uuid4()
        user = UserIdentity(
            id=user_id,
            email=email,
            name=name,
            is_verified=is_verified,
            project_id=project_id,
            role=role,
        )
        self.users[user_id] = user
        if password_hash is not None:
            self.passwords[user_id] = password_hash
        return user

    async def find_password_hash(self, session, user_id: UUID) -> str | None:
        return self.passwords.get(user_id)

    async def disable_local_login(self, session, user_id: UUID) -> None:
        if user_id in self.passwords:
            del self.passwords[user_id]

    async def verify_user_email(
        self, session, user_id: UUID, name: str | None = None
    ) -> None:
        user = self.users[user_id]
        updated_user = UserIdentity(
            id=user.id,
            email=user.email,
            is_verified=True,
            name=name if name is not None else user.name,
            picture=user.picture,
            project_id=user.project_id,
            role=user.role,
        )
        self.users[user_id] = updated_user

    async def update_password(
        self, session, user_id: UUID, new_password_hash: str
    ) -> None:
        self.passwords[user_id] = new_password_hash

    async def undelete_user(self, session, user_id: UUID) -> None:
        user = self.users.get(user_id)
        if user:
            user.deleted_at = None

    async def cleanup_unverified_users(self, session) -> int:
        return 0

    async def cleanup_soft_deleted_users(self, session, days_old: int = 30) -> int:
        return 0

    async def update_role(self, session, user_id: UUID, role) -> None:
        """Persist a role change. Tracked in self.role_updates for test assertions."""
        user = self.users.get(user_id)
        if user:
            # Replace the user identity with updated role (UserIdentity is immutable-ish)
            updated = UserIdentity(
                id=user.id,
                email=user.email,
                name=user.name,
                picture=user.picture,
                is_verified=user.is_verified,
                project_id=user.project_id,
                role=role,
            )
            self.users[user_id] = updated
        self.role_updates.append((user_id, role))


class MockEmailSender:
    def __init__(self):
        self.sent_otps = {}

    async def send_welcome_email(self, to_email: str, name: str | None):
        pass

    async def send_password_reset_email(self, to_email: str, reset_url: str):
        pass

    async def send_verification_email(self, to_email: str, otp: str):
        self.sent_otps[to_email] = otp

    async def send_account_restored_email(self, to_email: str, name: str | None):
        pass

    async def send_login_detected_email(
        self, to_email: str, ip_address: str, device_info: str
    ):
        pass


class MockCache:
    def __init__(self):
        self.data = {}

    async def set_string(self, key: str, value: str, ttl_seconds: int):
        self.data[key] = value

    async def get_string(self, key: str):
        return self.data.get(key)

    async def mget_strings(self, keys: list[str]) -> list[str | None]:
        return [self.data.get(key) for key in keys]

    async def set_dict(self, key: str, data: dict, ttl: int):
        self.data[key] = data

    async def get_dict(self, key: str) -> dict | None:
        return self.data.get(key)

    async def delete_key(self, key: str):
        if key in self.data:
            del self.data[key]

    async def incr(self, key: str, ttl: int | None = None) -> int:
        if key not in self.data:
            self.data[key] = "1"
            return 1
        else:
            val = int(self.data[key]) + 1
            self.data[key] = str(val)
            return val

    async def set_dict_nx(self, key: str, data: dict, ttl: int) -> bool:
        if key in self.data:
            return False
        self.data[key] = data
        return True

    async def increment_and_check_exceeds(
        self, attempt_key: str, redis_key: str, attempt_ttl: int, max_attempts: int
    ) -> bool:
        current = await self.incr(attempt_key, attempt_ttl)
        if current > max_attempts:
            await self.delete_key(redis_key)
            return True
        return False


class MockRefreshTokenPort:
    async def create(
        self,
        session,
        user_id: UUID,
        family_id: UUID | None = None,
        auth_provider: str = "local",
        client_meta=None,
    ) -> str:
        return f"mock_token_for_{user_id}"

    async def validate(
        self, session, token: str, client_meta=None
    ) -> tuple[UserIdentity | None, str | None, UUID | None]:
        return None, None, None

    async def revoke(self, session, token: str) -> None:
        pass

    async def revoke_by_family(self, session, family_id: UUID) -> None:
        pass

    async def revoke_all_for_user(self, session, user_id: UUID) -> None:
        pass

    async def get_active_sessions(
        self, session, user_id: UUID, current_token: str | None = None
    ) -> list:
        return []

    async def cleanup_expired(self, session) -> int:
        return 0


class MockPasswordHasher:
    async def hash_password(self, password: str) -> str:
        return f"hashed_{password}"

    async def verify_password(self, password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed_{password}"

    async def dummy_verify(self) -> None:
        pass


class MockLogger:
    async def info(self, msg: str):
        pass

    async def warning(self, msg: str):
        pass

    async def error(self, msg: str):
        pass

    async def fatal(self, msg: str):
        pass

    async def debug(self, msg: str):
        pass

    async def trace(self, msg: str):
        pass


@pytest.fixture
def user_repo():
    return MockUserRepository()


@pytest.fixture
def refresh_token_port():
    return MockRefreshTokenPort()


@pytest.fixture
def password_hasher():
    return MockPasswordHasher()


@pytest.fixture
def logger_port():
    return MockLogger()


@pytest.fixture
def mock_session():
    class DummySession:
        session: "DummySession"

        async def flush(self):
            pass

    dummy = DummySession()
    dummy.session = DummySession()
    return dummy
