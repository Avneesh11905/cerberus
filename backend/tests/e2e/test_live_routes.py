import os

# Override environment variables before any app modules are imported
os.environ["CERBERUS_E2E_DB_URL"] = "sqlite+aiosqlite:///./test_live_e2e.db"
os.environ["DB_ASYNC_URL"] = "sqlite+aiosqlite:///./test_live_e2e.db"

import uuid
import asyncio
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from fastapi.testclient import TestClient
import httpx

from src.authentication.adapters.security.password_hasher import Argon2PasswordHasher
from src.shared.infrastructure.sql.connection import Base, get_db
from src.shared.infrastructure.sql.uow import get_uow, SQLAlchemyUnitOfWork
from src.shared.container import shared_container
from tests.conftest import MockCache
from src import app

# --- Configuration ---
TEST_DB_URL = "sqlite+aiosqlite:///./test_live_e2e.db"

test_engine = create_async_engine(TEST_DB_URL)
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

# Test Data
TEST_EMAIL = f"live_e2e_test_{uuid.uuid4().hex[:8]}@example.com"
TEST_PASSWORD = "StrongPassword123!"
TEST_NEW_NAME = "Live Test User Updated"


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


async def override_get_uow():
    async with TestSessionLocal() as session:
        yield SQLAlchemyUnitOfWork(lambda: session)


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_uow] = override_get_uow


@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    loop = asyncio.new_event_loop()

    async def init_db():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    loop.run_until_complete(init_db())

    from src.authentication.container import reset_container, get_container
    from src.users.container import user_profile_repository

    reset_container()
    old_cache = shared_container.cache_adapter
    shared_container.cache_adapter = MockCache()  # type: ignore
    user_profile_repository._refresh_repo = get_container().refresh_token_repo
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_uow] = override_get_uow

    yield
    reset_container()
    shared_container.cache_adapter = old_cache
    user_profile_repository._refresh_repo = get_container().refresh_token_repo

    async def drop_db():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    loop.run_until_complete(drop_db())
    loop.close()

    app.dependency_overrides.clear()
    shared_container.cache_adapter = old_cache  # type: ignore


@pytest.fixture(scope="module")
def client():
    """Provides a shared HTTP client that persists cookies across requests."""
    with TestClient(app, base_url="http://testserver") as c:
        yield c


@pytest.fixture(scope="module")
def state():
    """Simple dictionary to pass state between sequential tests."""
    return {}


@pytest.mark.asyncio
async def db_verify_user(email: str):
    from sqlalchemy import select
    from src.shared.infrastructure.sql.tables import User, UserPassword

    hasher = Argon2PasswordHasher()
    hashed_pw = await hasher.hash_password(TEST_PASSWORD)

    async with TestSessionLocal() as session:
        user = (
            await session.execute(select(User).where(User.email == email))
        ).scalar_one_or_none()
        if user:
            user.is_verified = True
            existing_pw = (
                await session.execute(
                    select(UserPassword).where(UserPassword.user_id == user.id)
                )
            ).scalar_one_or_none()
            if not existing_pw:
                pw = UserPassword(user_id=user.id, password_hash=hashed_pw)
                session.add(pw)
            await session.commit()


@pytest.mark.asyncio
async def db_delete_user(email: str):
    """Fallback cleanup just in case."""
    from sqlalchemy import select
    from src.shared.infrastructure.sql.tables import User

    async with TestSessionLocal() as session:
        user = (
            await session.execute(select(User).where(User.email == email))
        ).scalar_one_or_none()
        if user:
            await session.delete(user)
            await session.commit()


class TestLiveRoutesSequential:
    """
    Runs E2E tests sequentially.
    State is shared via the 'client' (for cookies) and 'state' dict (for IDs and tokens).
    """

    def test_01_register_user(self, client: httpx.Client):
        response = client.post(
            "/auth/register/tenant",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "name": "Live Test User",
            },
        )
        assert response.status_code == 201, f"Failed: {response.text}"
        assert "Successfully registered" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_02_verify_user_in_db(self):
        """Bypass the email flow securely."""
        await db_verify_user(TEST_EMAIL)

    def test_03_login_user(self, client: httpx.Client, state: dict):
        response = client.post(
            "/auth/login/local", json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        assert response.json()["message"] == "Authenticated successfully"

        # Now get the access token by refreshing
        csrf_token = client.cookies.get("csrf_token") or ""
        refresh_resp = client.post("/auth/refresh", headers={"X-CSRF": csrf_token})
        assert refresh_resp.status_code == 200, f"Refresh Failed: {refresh_resp.text}"
        data = refresh_resp.json()
        assert "access_token" in data

        # Save token for later
        state["access_token"] = data["access_token"]

    def test_04_get_profile(self, client: httpx.Client, state: dict):
        response = client.get(
            "/users/me", headers={"Authorization": f"Bearer {state['access_token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TEST_EMAIL
        assert data["name"] == "Live Test User"

    def test_05_update_profile(self, client: httpx.Client, state: dict):
        csrf_token = client.cookies.get("csrf_token") or ""
        response = client.patch(
            "/users/me",
            headers={
                "Authorization": f"Bearer {state.get('access_token', '')}",
                "X-CSRF": csrf_token,
            },
            json={"name": TEST_NEW_NAME},
        )
        assert response.status_code == 200
        assert response.json()["name"] == TEST_NEW_NAME

    def test_06_create_project(self, client: httpx.Client, state: dict):
        csrf_token = client.cookies.get("csrf_token") or ""
        response = client.post(
            "/projects/",
            headers={
                "Authorization": f"Bearer {state.get('access_token', '')}",
                "X-CSRF": csrf_token,
            },
            json={"name": "Live E2E Project"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "api_key" in data
        assert "public_key" in data
        state["project_id"] = data["id"]

    def test_07_list_projects(self, client: httpx.Client, state: dict):
        response = client.get(
            "/projects/", headers={"Authorization": f"Bearer {state['access_token']}"}
        )
        assert response.status_code == 200
        projects = response.json()
        assert len(projects) >= 1
        assert any(p["id"] == state["project_id"] for p in projects)

    def test_08_update_project_env(self, client: httpx.Client, state: dict):
        csrf_token = client.cookies.get("csrf_token") or ""
        response = client.put(
            f"/projects/{state['project_id']}/environment",
            headers={
                "Authorization": f"Bearer {state['access_token']}",
                "X-CSRF": csrf_token,
            },
            json={"environment": "development"},
        )
        assert response.status_code == 200
        assert response.json()["environment"] == "development"

    def test_09_project_secrets(self, client: httpx.Client, state: dict):
        response = client.get(
            f"/projects/{state['project_id']}/secrets",
            headers={"Authorization": f"Bearer {state['access_token']}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "api_key_hash" in data
        assert "public_key" in data

    def test_10_rotate_keys(self, client: httpx.Client, state: dict):
        csrf_token = client.cookies.get("csrf_token") or ""
        response_api = client.post(
            f"/projects/{state['project_id']}/keys/rotate-api-key",
            headers={
                "Authorization": f"Bearer {state['access_token']}",
                "X-CSRF": csrf_token,
            },
        )
        assert response_api.status_code == 200
        data_api = response_api.json()
        assert "api_key" in data_api

        response_jwt = client.post(
            f"/projects/{state['project_id']}/keys/rotate-jwt-secret",
            headers={
                "Authorization": f"Bearer {state['access_token']}",
                "X-CSRF": csrf_token,
            },
        )
        assert response_jwt.status_code == 200
        data_jwt = response_jwt.json()
        assert "public_key" in data_jwt

    def test_11_refresh_token(self, client: httpx.Client, state: dict):
        csrf_token = client.cookies.get("csrf_token") or ""
        response = client.post("/auth/refresh", headers={"X-CSRF": csrf_token})
        assert response.status_code == 200, (
            f"Failed: {response.status_code} - {response.text}"
        )
        data = response.json()
        assert "access_token" in data
        # Update access token for subsequent requests
        state["access_token"] = data["access_token"]

    def test_12_delete_project(self, client: httpx.Client, state: dict):
        csrf_token = client.cookies.get("csrf_token") or ""
        response = client.delete(
            f"/projects/{state['project_id']}",
            headers={
                "Authorization": f"Bearer {state['access_token']}",
                "X-CSRF": csrf_token,
            },
        )
        assert response.status_code == 204

    def test_13_logout(self, client: httpx.Client, state: dict):
        csrf_token = client.cookies.get("csrf_token") or ""
        response = client.post(
            "/auth/logout",
            headers={
                "Authorization": f"Bearer {state.get('access_token', '')}",
                "X-CSRF": csrf_token,
            },
        )
        assert response.status_code == 200, (
            f"Failed: {response.status_code} - {response.text}"
        )
        assert response.json()["message"] == "Logged out"

    def test_14_delete_profile(self, client: httpx.Client, state: dict):
        # We logged out, so we need to log in again to delete the profile
        login_resp = client.post(
            "/auth/login/local", json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert login_resp.status_code == 200

        csrf_token = client.cookies.get("csrf_token") or ""
        refresh_resp = client.post("/auth/refresh", headers={"X-CSRF": csrf_token})
        access_token = refresh_resp.json()["access_token"]

        response = client.delete(
            "/users/me",
            headers={"Authorization": f"Bearer {access_token}", "X-CSRF": csrf_token},
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_99_fallback_cleanup(self):
        """Always ensure the test user is removed from DB even if tests failed."""
        await db_delete_user(TEST_EMAIL)
