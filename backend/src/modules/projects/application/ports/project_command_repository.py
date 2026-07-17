from typing import Protocol
from uuid import UUID

from src.modules.projects.domain.entities import ProjectEntity


class ProjectCommandRepositoryPort[SessionType](Protocol):
    async def save(
        self, session: SessionType, project: ProjectEntity
    ) -> ProjectEntity: ...
    async def delete(self, session: SessionType, project_id: UUID) -> None: ...
