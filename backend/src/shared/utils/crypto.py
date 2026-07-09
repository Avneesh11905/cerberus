import hashlib
import secrets
from uuid import UUID

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_api_key(project_id: UUID) -> str:
    """Generates a secure API key embedded with the project_id for fast lookup."""
    return f"cerb_{project_id.hex}_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """Uses SHA-256 for fast, deterministic API key hashing to allow quick DB lookups."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """Verifies a plaintext API key against its hash."""
    return hash_api_key(api_key) == hashed_key


def generate_rsa_keypair() -> tuple[str, str]:
    """
    Generates a 2048-bit RSA keypair.
    Returns (private_key_pem, public_key_pem)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

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
