"""
Port: ApiKeyPort
Defines the contract for generating, hashing, and verifying project API keys.
"""

from typing import Protocol
from uuid import UUID


class ApiKeyPort(Protocol):
    def generate(self, project_id: UUID) -> str:
        """Generate a new API key embedding the project_id for fast lookup."""
        ...

    def hash(self, api_key: str) -> str:
        """Deterministically hash an API key for secure DB storage and lookup."""
        ...

    def verify(self, api_key: str, hashed_key: str) -> bool:
        """Verify a plaintext API key against its stored hash."""
        ...
