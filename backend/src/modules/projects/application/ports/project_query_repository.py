from uuid import UUID
from typing import Protocol, Sequence

from src.modules.projects.domain.entities import ProjectEntity


class ProjectQueryRepositoryPort[SessionType](Protocol):
    async def get_by_id(
        self, session: SessionType, project_id: UUID
    ) -> ProjectEntity | None: ...
    async def get_by_api_key_hash(
        self, session: SessionType, api_key_hash: str
    ) -> ProjectEntity | None: ...
    async def get_by_name(
        self, session: SessionType, name: str
    ) -> ProjectEntity | None: ...
    async def get_all_for_tenant(
        self, session: SessionType, tenant_id: UUID
    ) -> Sequence[ProjectEntity]: ...
    async def get_private_key(
        self, session: SessionType, project_id: UUID
    ) -> str | None: ...
