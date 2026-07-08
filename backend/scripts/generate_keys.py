from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import secrets
import subprocess


def generate_rsa_keypair() -> tuple[str, str]:
    """Generates a secure 2048-bit RSA key pair for JWT signing."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode("utf-8")
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")
    return private_pem, public_pem


def generate_fernet_key() -> str:
    """Generates a URL-safe base64-encoded 32-byte Fernet key for at-rest encryption.

    This key is used to encrypt OAuth client_secret values and RSA private keys
    stored in the database. Store it in ENCRYPTION_KEY in .env.
    Never commit it — treat it like a database password.
    """
    return Fernet.generate_key().decode("utf-8")


def main():
    print("Generating RSA-2048 Keypair, Session Secret & Encryption Key...")

    session_secret = secrets.token_hex(32)
    private_pem, public_pem = generate_rsa_keypair()
    encryption_key = generate_fernet_key()

    output_lines = [
        f'SESSION_SECRET="{session_secret}"',
        "",
        f'JWT_PRIVATE_KEY="{private_pem}"',
        "",
        f'JWT_PUBLIC_KEY="{public_pem}"',
        "",
        "# --- At-rest encryption key (/4) ---",
        "# Used to encrypt OAuth client_secret and RSA private keys in the database.",
        "# Rotate this key only with a full DB re-encryption migration.",
        f'ENCRYPTION_KEY="{encryption_key}"',
    ]

    final_string = "\n".join(output_lines)

    print("\n" + "=" * 50)
    print("Keys generated successfully!")
    print("=" * 50 + "\n")
    print(final_string)

    try:
        subprocess.run(["clip"], input=final_string, text=True, check=True)
        print("\n" + "=" * 50)
        print("SUCCESS: Keys copied to clipboard! Paste into your .env file.")
    except Exception as e:
        print(f"\nCould not copy to clipboard automatically: {e}")
        print("Please copy the text above manually.")

    print("=" * 50 + "\n")
    print("SECURITY NOTES:")
    print("  - Never share or commit JWT_PRIVATE_KEY or ENCRYPTION_KEY.")
    print("  - JWT_PUBLIC_KEY can be distributed to services that verify your JWTs.")
    print("  - ENCRYPTION_KEY rotation requires a full DB re-encryption migration.")


if __name__ == "__main__":
    main()
