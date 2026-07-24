"""
Provides secure, one-way cryptographic hashing for passwords using Argon2id.
Argon2id is currently the OWASP recommended algorithm because it resists both GPU cracking and side-channel timing attacks.
"""

import asyncio
import sys
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class Argon2PasswordHasherAdapter:
    def __init__(self):
        is_testing = "pytest" in sys.modules
        self.pwd_context = PasswordHasher(
            time_cost=1 if is_testing else 3,
            memory_cost=1024 if is_testing else 65536,
            parallelism=1 if is_testing else 2,
        )

    async def hash_password(self, password: str) -> str:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.pwd_context.hash, password)

    async def verify_password(self, password: str, hashed_password: str) -> bool:
        loop = asyncio.get_running_loop()
        def verify():
            try:
                return self.pwd_context.verify(hashed_password, password)
            except VerifyMismatchError:
                return False
            except Exception:
                return False
        return await loop.run_in_executor(None, verify)

    async def dummy_verify(self) -> None:
        loop = asyncio.get_running_loop()
        # To simulate verify timing, we can just hash a dummy string
        await loop.run_in_executor(None, self.pwd_context.hash, "dummy")

