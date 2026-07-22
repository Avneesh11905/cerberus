from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.projects.application.ports import ProjectCommandRepositoryPort
from src.modules.projects.domain.entities import ProjectEntity
from src.modules.projects.infrastructure.models import Project as ProjectModel
from src.shared.application.ports import EncryptionPort
from src.shared.domain.value_objects import HttpsUrl


class SQLProjectCommandRepositoryAdapter(ProjectCommandRepositoryPort):
    def __init__(self, session: AsyncSession, encryption_adapter: EncryptionPort):
        self._session = session
        self._encryption_adapter = encryption_adapter

    def _to_entity(self, model: ProjectModel) -> ProjectEntity:
        return ProjectEntity(
            id=model.id,
            tenant_id=model.tenant_id,
            name=model.name,
            private_key=self._encryption_adapter.decrypt(model.private_key)
            if model.private_key
            else "",
            public_key=model.public_key,
            api_key_hash=model.api_key_hash,
            oauth_config=model.oauth_config,
            allowed_origins=model.allowed_origins,
            default_claims=model.default_claims,
            environment=model.environment,
            frontend_url=HttpsUrl(model.frontend_url) if model.frontend_url else None,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: ProjectEntity) -> ProjectModel:
        return ProjectModel(
            id=entity.id,
            tenant_id=entity.tenant_id,
            name=entity.name,
            private_key=self._encryption_adapter.encrypt(entity.private_key)
            if entity.private_key
            else "",
            public_key=entity.public_key,
            api_key_hash=entity.api_key_hash,
            oauth_config=entity.oauth_config,
            allowed_origins=entity.allowed_origins,
            default_claims=entity.default_claims,
            environment=entity.environment,
            frontend_url=entity.frontend_url,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def save(self, project: ProjectEntity) -> ProjectEntity:
        model = self._to_model(project)
        merged_model = await self._session.merge(model)
        await self._session.flush()
        return self._to_entity(merged_model)

    async def delete(self, project_id: UUID) -> None:
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.id == project_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
