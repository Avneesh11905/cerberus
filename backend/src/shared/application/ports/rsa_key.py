"""
Port: RsaKeyPort
Defines the contract for generating RSA keypairs used for per-project JWT signing.
"""

from typing import Protocol


class RsaKeyPort(Protocol):
    async def generate_keypair(self) -> tuple[str, str]:
        """
        Generate a 2048-bit RSA keypair asynchronously.
        Returns (private_key_pem, public_key_pem).
        """
        ...
