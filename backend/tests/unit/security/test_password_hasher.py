import pytest
from src.modules.auth.authentication.adapters.security.password_hasher import (
    Argon2PasswordHasherAdapter,
)


@pytest.fixture
def hasher():
    return Argon2PasswordHasherAdapter()


@pytest.mark.asyncio
async def test_password_hashing_and_verification(hasher):
    password = "supersecretpassword123!"

    # Hash the password
    hashed = await hasher.hash_password(password)
    assert hashed != password
    assert hashed.startswith("$argon2")

    # Verify with correct password
    is_valid = await hasher.verify_password(password, hashed)
    assert is_valid is True

    # Verify with incorrect password
    is_valid = await hasher.verify_password("wrongpassword", hashed)
    assert is_valid is False


@pytest.mark.asyncio
async def test_dummy_verify(hasher):
    # Just ensures it runs without error (used for timing attack mitigation)
    await hasher.dummy_verify()
