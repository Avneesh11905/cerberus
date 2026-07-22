from typing import Protocol
from uuid import UUID


class ProjectKeyRepositoryPort(Protocol):
    async def get_private_key(self, project_id: UUID) -> str | None:
        """Retrieves and decrypts the tenant's private key."""
        ...
