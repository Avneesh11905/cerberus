from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import secrets
import os


def generate_rsa_keypair() -> tuple[str, str]:
    """Generates a secure 2048-bit RSA key pair for JWT signing."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    public_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode("utf-8")
    )
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

    # Save PEM files to backend/keys/
    keys_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "keys")
    os.makedirs(keys_dir, exist_ok=True)
    
    private_key_path = os.path.join(keys_dir, "jwt_private.pem")
    public_key_path = os.path.join(keys_dir, "jwt_public.pem")
    
    with open(private_key_path, "w", encoding="utf-8") as f:
        f.write(private_pem)
        
    with open(public_key_path, "w", encoding="utf-8") as f:
        f.write(public_pem)

    output_lines = [
        f'SESSION_SECRET="{session_secret}"',
        "",
        "# --- At-rest encryption key (/4) ---",
        "# Used to encrypt OAuth client_secret and RSA private keys in the database.",
        "# Rotate this key only with a full DB re-encryption migration.",
        f'ENCRYPTION_KEY="{encryption_key}"',
    ]

    final_string = "\n".join(output_lines)

    root_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
    backend_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    env_path = backend_env_path if os.path.exists(backend_env_path) else root_env_path
    
    print("\n" + "=" * 50)
    print("Keys generated successfully!")
    print(f"  - RSA Private Key saved to: {private_key_path}")
    print(f"  - RSA Public Key saved to: {public_key_path}")
    
    if os.path.exists(env_path):
        import re
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read()

        content = re.sub(
            r'^SESSION_SECRET=.*$',
            f'SESSION_SECRET="{session_secret}"',
            content,
            flags=re.MULTILINE
        )
        content = re.sub(
            r'^ENCRYPTION_KEY=.*$',
            f'ENCRYPTION_KEY="{encryption_key}"',
            content,
            flags=re.MULTILINE
        )

        with open(env_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"  - Automatically updated SESSION_SECRET and ENCRYPTION_KEY in {env_path}")
    else:
        print(f"\nWARNING: {env_path} not found. Could not automatically update keys.")
        print("Please copy the text below manually into your .env file:\n")
        print(final_string)

    print("=" * 50 + "\n")
    print("SECURITY NOTES:")
    print(f"  - Never share or commit {private_key_path} or ENCRYPTION_KEY.")
    print(f"  - {public_key_path} can be distributed to services that verify your JWTs.")
    print("  - ENCRYPTION_KEY rotation requires a full DB re-encryption migration.")


if __name__ == "__main__":
    main()
