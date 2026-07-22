from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
import time_machine
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from src.modules.authentication.domain.entities import UserIdentity
from src.modules.authentication.infrastructure.security.access_token import (
    JWTAccessTokenAdapter,
)
from src.shared.domain.value_objects import EmailAddress


def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    return private_pem, public_pem


@pytest.fixture(scope="session")
def keys():
    return generate_keys()


@pytest.fixture
def jwt_adapter(keys):
    priv, pub = keys
    return JWTAccessTokenAdapter(private_key=priv, public_key=pub, lifetime_minutes=15)


def test_jwt_creation_and_verification(jwt_adapter):
    user = UserIdentity(
        id=uuid4(),
        email=EmailAddress("test@example.com"),
        is_verified=True,
        role="TENANT",
    )

    token = jwt_adapter.create(user, extra_claims={"custom": "value"})
    assert isinstance(token, str)

    verified_user, payload = jwt_adapter.verify(token)
    assert verified_user is not None
    assert payload is not None
    assert verified_user.id == user.id
    assert verified_user.email == user.email
    assert payload.get("custom") == "value"


def test_jwt_expiry(jwt_adapter):
    user = UserIdentity(
        id=uuid4(),
        email=EmailAddress("test@example.com"),
        is_verified=True,
    )

    with time_machine.travel(datetime.now(timezone.utc), tick=False) as traveller:
        token = jwt_adapter.create(user)

        # Verify works initially
        verified_user, _ = jwt_adapter.verify(token)
        assert verified_user is not None

        # Fast-forward 16 minutes
        traveller.shift(timedelta(minutes=16))

        # Should now be expired
        expired_user, expired_payload = jwt_adapter.verify(token)
        assert expired_user is None
        assert expired_payload is None


def test_jwt_invalid_signature(jwt_adapter, keys):
    user = UserIdentity(
        id=uuid4(),
        email=EmailAddress("test@example.com"),
        is_verified=True,
    )
    token = jwt_adapter.create(user)

    # Try verifying with a DIFFERENT public key
    _, wrong_pub = generate_keys()

    invalid_user, invalid_payload = jwt_adapter.verify(
        token, public_key_override=wrong_pub
    )
    assert invalid_user is None
    assert invalid_payload is None
