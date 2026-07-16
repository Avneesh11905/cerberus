from typing import Generic, Protocol, TypeVar
from uuid import UUID

from src.modules.projects.domain.project import ProjectEntity

SessionType = TypeVar("SessionType", contravariant=True)


class ProjectCommandRepositoryPort(Protocol, Generic[SessionType]):
    async def save(
        self, session: SessionType, project: ProjectEntity
    ) -> ProjectEntity: ...
    async def delete(self, session: SessionType, project_id: UUID) -> None: ...
