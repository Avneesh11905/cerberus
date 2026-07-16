"""
Adapter: RsaKeyAdapter
Concrete implementation of RsaKeyPort using the cryptography library.
RSA keypair generation is CPU-bound, so it runs in a threadpool executor.
"""

import asyncio

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from src.shared.application.ports.rsa_key import RsaKeyPort


class RsaKeyAdapter(RsaKeyPort):
    def _generate_sync(self) -> tuple[str, str]:
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

    async def generate_keypair(self) -> tuple[str, str]:
        """Generates a 2048-bit RSA keypair asynchronously using a threadpool executor."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._generate_sync)
