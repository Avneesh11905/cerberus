from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.authentication.core.ports.repository.project import ProjectRepositoryPort
from src.shared.container import shared_container
from src.shared.infrastructure.sql.tables import Project


class SQLProjectRepositoryAdapter(ProjectRepositoryPort[AsyncSession]):
    async def get_private_key(
        self, session: AsyncSession, project_id: UUID
    ) -> str | None:
        result = await session.execute(
            select(Project.private_key).where(Project.id == project_id)
        )
        encrypted_key = result.scalar_one_or_none()
        if encrypted_key:
            return shared_container.encryption_adapter.decrypt(encrypted_key)
        return None
