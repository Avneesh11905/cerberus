from typing import Protocol
from uuid import UUID

from src.modules.projects.domain.entities import ProjectEntity


class ProjectCommandRepositoryPort(Protocol):
    async def save(self, project: ProjectEntity) -> ProjectEntity: ...
    async def delete(self, project_id: UUID) -> None: ...
