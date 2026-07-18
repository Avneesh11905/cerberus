from typing import Protocol
from uuid import UUID


class ProjectRepositoryPort[SessionType](Protocol):
    async def get_private_key(
        self, session: SessionType, project_id: UUID
    ) -> str | None:
        """Retrieves and decrypts the tenant's private key."""
        ...
