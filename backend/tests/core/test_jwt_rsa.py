from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from src.authentication.adapters.security.access_token import JWTAccessTokenAdapter
from src.authentication.core.domain import UserIdentity, UserRole
from uuid import uuid4


def _generate_rsa_keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    return private_pem, public_pem


def test_jwt_rsa_signatures():
    global_priv, global_pub = _generate_rsa_keypair()
    tenant_priv, tenant_pub = _generate_rsa_keypair()

    adapter = JWTAccessTokenAdapter(
        private_key=global_priv, public_key=global_pub, lifetime_minutes=15
    )

    user = UserIdentity(
        id=uuid4(), email="test@test.com", role=UserRole.USER, is_verified=True
    )

    # 1. Sign with Global, Verify with Global
    token = adapter.create(user)
    verified_user, payload = adapter.verify(token)
    assert verified_user is not None
    assert verified_user.id == user.id

    # 2. Sign with Tenant, Verify with Global (Should fail)
    token_tenant = adapter.create(user, private_key_override=tenant_priv)
    verified_fail, payload_fail = adapter.verify(
        token_tenant
    )  # Tries global_pub by default
    assert verified_fail is None

    # 3. Sign with Tenant, Verify with Tenant (Should succeed)
    verified_tenant, payload_tenant = adapter.verify(
        token_tenant, public_key_override=tenant_pub
    )
    assert verified_tenant is not None
    assert verified_tenant.id == user.id
