"""
Adapter: ApiKeyAdapter
Concrete implementation of ApiKeyPort using SHA-256 hashing and URL-safe tokens.
"""

import hashlib
import secrets
from uuid import UUID

from src.shared.application.ports import ApiKeyPort


class ApiKeyAdapter(ApiKeyPort):
    def generate(self, project_id: UUID) -> str:
        """Generates a secure API key embedded with the project_id for fast lookup."""
        return f"cerb_{project_id.hex}_{secrets.token_urlsafe(32)}"

    def hash(self, api_key: str) -> str:
        """Uses SHA-256 for fast, deterministic API key hashing to allow quick DB lookups."""
        return hashlib.sha256(api_key.encode()).hexdigest()

    def verify(self, api_key: str, hashed_key: str) -> bool:
        """Verifies a plaintext API key against its hash."""
        return self.hash(api_key) == hashed_key
