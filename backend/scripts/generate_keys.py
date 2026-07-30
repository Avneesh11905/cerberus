import os
import secrets

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# ANSI escape codes for coloring
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def generate_fernet_key() -> str:
    return Fernet.generate_key().decode("utf-8")


def generate_rsa_keypair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem.decode("utf-8"), public_pem.decode("utf-8")


def main():
    print(
        f"{CYAN}Generating RSA-2048 Keypair, Session Secret & Encryption Key...{RESET}"
    )

    session_secret = secrets.token_hex(32)
    private_pem, public_pem = generate_rsa_keypair()
    encryption_key = generate_fernet_key()

    # Save PEM files to a 'keys' folder in the backend root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(script_dir)
    keys_dir = os.path.join(backend_dir, "keys")
    os.makedirs(keys_dir, exist_ok=True)

    private_key_path = os.path.join(keys_dir, "jwt_private.pem")
    public_key_path = os.path.join(keys_dir, "jwt_public.pem")

    with open(private_key_path, "w", encoding="utf-8") as f:
        f.write(private_pem)

    with open(public_key_path, "w", encoding="utf-8") as f:
        f.write(public_pem)

    print("\n" + "=" * 60)
    print(f"{GREEN}✔ Keys generated successfully!{RESET}")
    print(f"  - RSA Private Key saved to: {private_key_path}")
    print(f"  - RSA Public Key saved to:  {public_key_path}")
    print("=" * 60)

    print(
        f"\n{RED}🚨 CRITICAL WARNING: PLEASE SAVE THESE SECRETS IMMEDIATELY 🚨{RESET}"
    )
    print(
        f"{YELLOW}These secrets are NOT saved anywhere and will NOT be visible again.{RESET}"
    )
    print("Please copy and paste these into your .env file:\n")

    print(f'{CYAN}SESSION_SECRET={RESET}"{session_secret}"')
    print("")
    print(f"{YELLOW}# --- At-rest encryption key (/4) ---{RESET}")
    print(
        f"{YELLOW}# Used to encrypt OAuth client_secret and RSA private keys in the database.{RESET}"
    )
    print(
        f"{YELLOW}# Rotate this key only with a full DB re-encryption migration.{RESET}"
    )
    print(f'{CYAN}ENCRYPTION_KEY={RESET}"{encryption_key}"')
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
