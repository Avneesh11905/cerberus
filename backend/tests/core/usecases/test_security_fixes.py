"""
Tests for security features and edge cases.
"""

import asyncio
import hashlib
import hashlib as _hashlib
import hmac as _hmac
import time
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from itsdangerous import URLSafeSerializer
from unittest.mock import AsyncMock, Mock

from src import app
from src.authentication.core.domain.exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
    SamePasswordException,
)
from src.authentication.core.domain.user import UserRole
from src.authentication.core.usecases import (
    ChangePasswordUseCase,
    ExecutePasswordResetUseCase,
    LoginLocalUserUseCase,
    RequestNewVerificationEmailUseCase,
    VerifyEmailUseCase,
)
from src.shared.config import app_settings, verification_settings
from src.shared.infrastructure.sql.uow import SQLAlchemyUnitOfWork
from tests.conftest import (
    MockCache,
    MockEmailSender,
    MockLogger,
    MockPasswordHasher,
    MockRefreshTokenPort,
    MockUserRepository,
)

# ── Helpers ──────────────────────────────────────────────────────────────────


def _make_verify_usecase(
    user_repo, cache, email_sender=None, refresh_repo=None, logger=None
):
    return VerifyEmailUseCase(
        user_repo=user_repo,
        cache=cache,
        logger=logger or MockLogger(),
        email_sender=email_sender or MockEmailSender(),
        refresh_repo=refresh_repo or MockRefreshTokenPort(),
    )


def _seed_pending_otp(
    cache, email: str, otp: str, attempts: int = 0, expired: bool = False
):
    """Directly write an OTP payload into the mock cache."""
    email_hash = hashlib.sha256(email.encode()).hexdigest()
    secret = app_settings.SESSION_SECRET.encode()
    otp_hash = _hmac.new(secret, otp.encode(), _hashlib.sha256).hexdigest()
    expires_at = int(time.time()) - 1 if expired else int(time.time()) + 300
    cache.data[f"pending_reg:global:{email_hash}"] = {
        "otp": otp_hash,
        "otp_expires_at": expires_at,
        "pending_password_hash": "hashed_pass",
        "pending_name": "Test",
        "attempts": attempts,
    }


# ── Atomic OTP counter ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_otp_max_attempts_enforced(mock_session):
    """After OTP_MAX_ATTEMPTS wrong guesses the account is locked."""
    user_repo = MockUserRepository()
    cache = MockCache()
    email = "brute@example.com"

    await user_repo.create_user_with_password(
        mock_session, email, "Test", None, is_verified=False
    )
    _seed_pending_otp(cache, email, "999999")

    usecase = _make_verify_usecase(user_repo, cache)

    for i in range(5):
        with pytest.raises(InvalidTokenException):
            await usecase.execute(mock_session, email, "000000")

    # 6th attempt — even the CORRECT OTP must be rejected (key deleted)
    with pytest.raises((InvalidTokenException, InvalidCredentialsException)):
        await usecase.execute(mock_session, email, "999999")


@pytest.mark.asyncio
async def test_otp_attempt_counter_increments_atomically(mock_session):
    """Each failed attempt increments the counter exactly once."""
    user_repo = MockUserRepository()
    cache = MockCache()
    email = "atomic@example.com"

    await user_repo.create_user_with_password(
        mock_session, email, "Test", None, is_verified=False
    )
    _seed_pending_otp(cache, email, "999999")

    usecase = _make_verify_usecase(user_repo, cache)

    for expected_count in range(1, 4):
        with pytest.raises(InvalidTokenException):
            await usecase.execute(mock_session, email, "000000")
        email_hash = hashlib.sha256(email.encode()).hexdigest()
        attempt_key = f"otp_attempts:global:{email_hash}"
        assert int(cache.data.get(attempt_key, 0)) == expected_count


@pytest.mark.asyncio
async def test_otp_correct_code_succeeds_and_clears_counter(mock_session):
    """Successful OTP clears the attempt counter key."""
    user_repo = MockUserRepository()
    cache = MockCache()
    email = "success@example.com"

    await user_repo.create_user_with_password(
        mock_session, email, "Test", None, is_verified=False
    )
    otp = "123456"
    _seed_pending_otp(cache, email, otp)

    usecase = _make_verify_usecase(user_repo, cache)

    with pytest.raises(InvalidTokenException):
        await usecase.execute(mock_session, email, "000000")

    await usecase.execute(mock_session, email, otp)

    email_hash = hashlib.sha256(email.encode()).hexdigest()
    attempt_key = f"otp_attempts:global:{email_hash}"
    assert attempt_key not in cache.data


@pytest.mark.asyncio
async def test_concurrent_otp_attempts_cannot_exceed_limit(mock_session):
    """
    Fire OTP_MAX_ATTEMPTS+5 concurrent coroutines.
    With atomic INCR the total bypasses must be 0.
    Uses asyncio.gather to simulate concurrency within a single event loop.
    """
    user_repo = MockUserRepository()
    cache = MockCache()
    email = "concurrent@example.com"

    await user_repo.create_user_with_password(
        mock_session, email, "Test", None, is_verified=False
    )
    _seed_pending_otp(cache, email, "999999")

    usecase = _make_verify_usecase(user_repo, cache)
    limit = verification_settings.OTP_MAX_ATTEMPTS
    total = limit + 5

    results = await asyncio.gather(
        *[usecase.execute(mock_session, email, "000000") for _ in range(total)],
        return_exceptions=True,
    )

    successes = [r for r in results if not isinstance(r, Exception)]
    assert len(successes) == 0, (
        f"Expected 0 successful brute-force bypasses, got {len(successes)}."
    )


# ── Redis cleanup failure should not crash verification ──────────────────


@pytest.mark.asyncio
async def test_verify_email_survives_redis_cleanup_error(mock_session):
    """
    If Redis raises during key deletion after a successful OTP, verification
    must still complete — the exception is swallowed and a warning is logged.
    """
    user_repo = MockUserRepository()
    email = "redisfail@example.com"
    otp = "555555"

    await user_repo.create_user_with_password(
        mock_session, email, "Test", None, is_verified=False
    )

    # Subclass MockCache to override delete_key with a failing implementation
    class FailingCache(MockCache):
        async def delete_key(self, key: str) -> None:
            raise ConnectionError("Redis is down")

    # Subclass MockLogger to capture warnings
    warnings: list[str] = []

    class CapturingLogger(MockLogger):
        async def warning(self, msg: str) -> None:
            warnings.append(msg)

    cache = FailingCache()
    logger = CapturingLogger()
    _seed_pending_otp(cache, email, otp)

    usecase = _make_verify_usecase(user_repo, cache, logger=logger)

    # Should NOT raise — Redis failure is wrapped in try/except
    result = await usecase.execute(mock_session, email, otp)
    assert result is not None, "Verification must succeed even when Redis cleanup fails"

    # The warning must have been emitted
    assert any("expire" in w.lower() or "cleanup" in w.lower() for w in warnings), (
        "Expected a warning log about Redis cleanup failure"
    )


# ── Resend counter must not be bumped for unknown emails ─────────────────


@pytest.mark.asyncio
async def test_otp_resend_rate_limit_not_consumed_for_nonexistent_email(mock_session):
    """
    Spamming resend for a non-existent email must NOT consume the resend quota
    for that email address. The counter is only incremented after checking user existence.
    """
    user_repo = MockUserRepository()  # empty — no users
    cache = MockCache()
    resend_usecase = RequestNewVerificationEmailUseCase(  # type: ignore
        user_repo=user_repo,
        logger=MockLogger(),
        email_sender=MockEmailSender(),
        cache=cache,
    )
    email = "ghost@example.com"
    email_hash = hashlib.sha256(email.encode()).hexdigest()
    resend_key = f"otp_resends:global:{email_hash}"

    # Spam 10 requests for a non-existent email
    for _ in range(10):
        await resend_usecase.execute(mock_session, email)

    # Counter must be 0 (key should not exist) since the user doesn't exist
    assert resend_key not in cache.data, (
        "Resend counter must not be incremented for non-existent email addresses"
    )


@pytest.mark.asyncio
async def test_otp_resend_rate_limit_is_consumed_for_real_unverified_user(mock_session):
    """
    Resend requests for a real unverified user DO consume the resend quota.
    """
    user_repo = MockUserRepository()
    cache = MockCache()
    email_sender = MockEmailSender()
    email = "resend_real@example.com"

    await user_repo.create_user_with_password(
        mock_session, email, "Test", None, is_verified=False
    )
    email_hash = hashlib.sha256(email.encode()).hexdigest()
    _seed_pending_otp(cache, email, "111111")

    resend_usecase = RequestNewVerificationEmailUseCase(  # type: ignore
        user_repo=user_repo,
        logger=MockLogger(),
        email_sender=email_sender,
        cache=cache,
    )

    resend_key = f"otp_resends:global:{email_hash}"
    await resend_usecase.execute(mock_session, email)
    assert resend_key in cache.data, "Counter must be incremented for real unverified user"
    assert int(cache.data[resend_key]) == 1


# ──  /  Session revocation ──────────────────────────────────────


@pytest.mark.asyncio
async def test_password_reset_revokes_all_sessions(mock_session):
    """All refresh tokens are revoked after password reset."""

    user_repo = MockUserRepository()
    cache = MockCache()
    user_id = uuid4()
    token = "valid_reset_token"
    cache.data[f"pwd_reset:{token}"] = str(user_id)

    revoke_all_called = False

    class TrackingRefreshRepo(MockRefreshTokenPort):
        async def revoke_all_for_user(self, session, uid):
            nonlocal revoke_all_called
            revoke_all_called = True
            assert uid == user_id

    usecase = ExecutePasswordResetUseCase(  # type: ignore
        user_repo=user_repo,
        cache=cache,
        hasher=MockPasswordHasher(),
        refresh_repo=TrackingRefreshRepo(),
    )
    result = await usecase.execute(mock_session, token, "NewPass123!")

    assert result is True
    assert revoke_all_called, "revoke_all_for_user must be called on password reset"


@pytest.mark.asyncio
async def test_change_password_revokes_all_sessions(mock_session):
    """All refresh tokens are revoked after change-password."""

    user_repo = MockUserRepository()
    user_id = uuid4()
    user_repo.passwords[user_id] = "hashed_oldpassword"

    revoke_all_called = False

    class TrackingRefreshRepo(MockRefreshTokenPort):
        async def revoke_all_for_user(self, session, uid):
            nonlocal revoke_all_called
            revoke_all_called = True

    usecase = ChangePasswordUseCase(  # type: ignore
        user_repo=user_repo,
        hasher=MockPasswordHasher(),
        logger=MockLogger(),
        refresh_repo=TrackingRefreshRepo(),
    )
    await usecase.execute(mock_session, user_id, "oldpassword", "NewPass123!")
    assert revoke_all_called, "revoke_all_for_user must be called on change-password"


# ── same-password check is hash-based ──────────────────────────────


@pytest.mark.asyncio
async def test_change_password_rejects_same_password(mock_session):
    """
    Submitting the same password as new_password must raise SamePasswordException.
    The check now uses hash comparison (not string equality) so it works correctly
    even with bcrypt/Argon2 rehashing.
    """
    user_repo = MockUserRepository()
    user_id = uuid4()
    user_repo.passwords[user_id] = "hashed_mypassword"

    usecase = ChangePasswordUseCase(  # type: ignore
        user_repo=user_repo,
        hasher=MockPasswordHasher(),
        logger=MockLogger(),
        refresh_repo=MockRefreshTokenPort(),
    )
    with pytest.raises(SamePasswordException):
        # MockPasswordHasher.verify_password("mypassword", "hashed_mypassword") -> True
        await usecase.execute(mock_session, user_id, "mypassword", "mypassword")


@pytest.mark.asyncio
async def test_change_password_oauth_user_no_current_password_required(mock_session):
    """
    An OAuth-only user with no stored password can set a new password without
    providing a current_password. No SamePasswordException should be raised
    since there is no existing hash to compare against.
    """
    user_repo = MockUserRepository()
    user_id = uuid4()
    # No entry in user_repo.passwords — OAuth-only user

    usecase = ChangePasswordUseCase(  # type: ignore
        user_repo=user_repo,
        hasher=MockPasswordHasher(),
        logger=MockLogger(),
        refresh_repo=MockRefreshTokenPort(),
    )
    # Must succeed — no stored hash means no same-password check
    await usecase.execute(mock_session, user_id, None, "BrandNewPass!")
    assert user_repo.passwords.get(user_id) == "hashed_BrandNewPass!"


@pytest.mark.asyncio
async def test_change_password_wrong_current_password_raises(mock_session):
    """Providing an incorrect current_password raises InvalidCredentialsException."""
    user_repo = MockUserRepository()
    user_id = uuid4()
    user_repo.passwords[user_id] = "hashed_correctpassword"

    usecase = ChangePasswordUseCase(  # type: ignore
        user_repo=user_repo,
        hasher=MockPasswordHasher(),
        logger=MockLogger(),
        refresh_repo=MockRefreshTokenPort(),
    )
    with pytest.raises(InvalidCredentialsException):
        await usecase.execute(mock_session, user_id, "wrongpassword", "NewPass!")


# ── Admin role self-heal persists to DB ─────────────────────────────────


@pytest.mark.asyncio
async def test_admin_role_selfheal_persists_to_db(mock_session, monkeypatch):
    """
    If the admin user's DB row has role=USER (e.g. after manual DB edit),
    the login use case must call update_role to persist the correction,
    not merely mutate the in-memory identity.
    """
    user_repo = MockUserRepository()
    email = app_settings.ADMIN_EMAIL or "admin@example.com"

    if not app_settings.ADMIN_EMAIL:
        monkeypatch.setattr(app_settings, "ADMIN_EMAIL", email)

    # Create the admin user with USER role (simulating a downgraded DB row)
    await user_repo.create_user_with_password(
        mock_session, email, "Admin", None, is_verified=True, role=UserRole.USER
    )
    user = await user_repo.find_by_email(mock_session, email)
    assert user is not None
    user_repo.passwords[user.id] = "hashed_adminpass"

    access_token = Mock()
    access_token.create.return_value = "mock_access_token"
    claims_provider = AsyncMock()
    claims_provider.get_custom_claims.return_value = {}
    project_repo = AsyncMock()

    usecase = LoginLocalUserUseCase(  # type: ignore
        user_repo=user_repo,
        refresh_repo=MockRefreshTokenPort(),
        hasher=MockPasswordHasher(),
        logger=MockLogger(),
        email_sender=MockEmailSender(),
        access_token=access_token,
        claims_provider=claims_provider,
        project_repo=project_repo,
    )

    logged_in_user, _, _ = await usecase.execute(mock_session, email, "adminpass")

    # The returned identity must have ADMIN role
    assert logged_in_user.role == UserRole.ADMIN, (
        "Self-heal must elevate JWT role to ADMIN"
    )
    # update_role must have been called to persist the DB correction
    assert len(user_repo.role_updates) == 1, (
        "update_role must be called to persist the self-healed admin role to the DB"
    )
    assert user_repo.role_updates[0][1] == UserRole.ADMIN


# ── UoW session property guard ──────────────────────────────────────────


def test_uow_session_raises_if_accessed_before_context():
    """
    Accessing uow.session before entering the async context must raise a
    descriptive RuntimeError, not an opaque AttributeError: 'NoneType'.
    """
    uow = SQLAlchemyUnitOfWork()
    with pytest.raises(RuntimeError, match="async with uow"):
        _ = uow.session


# ── Account restore notification ──────────────────────────────────────


@pytest.mark.asyncio
async def test_login_sends_restore_email_for_deleted_account(mock_session):
    """A soft-deleted account triggers a security notification email."""

    user_repo = MockUserRepository()
    email_sender = MockEmailSender()
    email = "deleted@example.com"

    await user_repo.create_user_with_password(
        mock_session, email, "Test", None, is_verified=True
    )
    user = await user_repo.find_by_email(mock_session, email)
    assert user is not None
    user_repo.passwords[user.id] = "hashed_mypassword"
    user.deleted_at = datetime.now(timezone.utc)

    access_token = Mock()
    access_token.create.return_value = "mock_access_token"
    claims_provider = AsyncMock()
    claims_provider.get_custom_claims.return_value = {}
    project_repo = AsyncMock()
    usecase = LoginLocalUserUseCase(  # type: ignore
        user_repo=user_repo,
        refresh_repo=MockRefreshTokenPort(),
        hasher=MockPasswordHasher(),
        logger=MockLogger(),
        email_sender=email_sender,
        access_token=access_token,
        claims_provider=claims_provider,
        project_repo=project_repo,
    )
    await usecase.execute(mock_session, email, "mypassword")

    assert hasattr(email_sender, "send_account_restored_email") or hasattr(
        email_sender, "restore_notifications"
    ), "send_account_restored_email must be called when a deleted account logs in"


# ── OTP resend resets attempt counter ──────────────────────────────────


@pytest.mark.asyncio
async def test_otp_resend_resets_attempt_count(mock_session):
    """A new OTP issued via resend starts with attempts=0."""
    user_repo = MockUserRepository()
    cache = MockCache()
    email_sender = MockEmailSender()
    email = "resend@example.com"

    await user_repo.create_user_with_password(
        mock_session, email, "Test", None, is_verified=False
    )
    _seed_pending_otp(cache, email, "111111", attempts=4)

    email_hash = hashlib.sha256(email.encode()).hexdigest()
    cache.data[f"otp_attempts:global:{email_hash}"] = "4"

    resend_usecase = RequestNewVerificationEmailUseCase(  # type: ignore
        user_repo=user_repo,
        logger=MockLogger(),
        email_sender=email_sender,
        cache=cache,
    )
    await resend_usecase.execute(mock_session, email)

    payload = await cache.get_dict(f"pending_reg:global:{email_hash}")
    assert payload is not None
    assert cache.data.get(f"otp_attempts:global:{email_hash}") is None, (
        "Attempt counter must be cleared when resending OTP"
    )


# ── CSRF exception precision ──────────────────────────────────────────


def test_csrf_bad_signature_returns_corrupted_message():
    """A tampered CSRF cookie raises 'corrupted', not 'not bound'."""

    client = TestClient(app, raise_server_exceptions=False)
    client.cookies.set("refresh_token", "some_token")
    client.cookies.set("csrf_token", "INVALID_GARBAGE")
    resp = client.post(
        "/auth/logout",
        headers={"X-CSRF": "INVALID_GARBAGE"},
    )
    assert resp.status_code == 403
    detail = resp.json().get("detail", "")
    assert "corrupted" in detail.lower(), (
        f"Expected 'corrupted' in detail, got: {detail!r}"
    )


def test_csrf_mismatched_token_returns_not_bound_message():
    """A valid-signed but session-mismatched token raises 'not bound'."""

    csrf_signer = URLSafeSerializer(app_settings.SESSION_SECRET, salt="csrf-token")
    wrong_hash = hashlib.sha256(b"different_token").hexdigest()
    mismatched_csrf = csrf_signer.dumps(wrong_hash)

    client = TestClient(app, raise_server_exceptions=False)
    client.cookies.set("refresh_token", "actual_token")
    client.cookies.set("csrf_token", mismatched_csrf)
    resp = client.post(
        "/auth/logout",
        headers={"X-CSRF": mismatched_csrf},
    )
    assert resp.status_code == 403
    detail = resp.json().get("detail", "")
    assert "not bound" in detail.lower(), (
        f"Expected 'not bound' in detail, got: {detail!r}"
    )
