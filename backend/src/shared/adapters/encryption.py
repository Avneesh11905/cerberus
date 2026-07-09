from cryptography.fernet import Fernet

from src.shared.core.ports.encryption import EncryptionPort


class FernetEncryptionAdapter(EncryptionPort):
    def __init__(self, key: str):
        self._fernet = Fernet(key.encode("utf-8"))

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string and return the base64-encoded ciphertext."""
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a base64-encoded ciphertext and return the plaintext string."""
        return self._fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
