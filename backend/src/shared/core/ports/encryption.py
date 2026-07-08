from typing import Protocol

class EncryptionPort(Protocol):
    def encrypt(self, plaintext: str) -> str:
        """Encrypts a plaintext string and returns the ciphertext."""
        ...

    def decrypt(self, ciphertext: str) -> str:
        """Decrypts a ciphertext string and returns the plaintext."""
        ...
