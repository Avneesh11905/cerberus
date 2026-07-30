from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select, func

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.projects.application.ports import ProjectQueryRepositoryPort
from src.modules.projects.domain.entities import ProjectEntity
from src.modules.projects.infrastructure.models import Project as ProjectModel
from src.shared.application.ports import EncryptionPort
from src.shared.domain.value_objects import HttpsUrl


class SQLProjectQueryRepositoryAdapter(ProjectQueryRepositoryPort):
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

    async def get_by_id(self, project_id: UUID) -> ProjectEntity | None:
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.id == project_id)
        )
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def get_by_api_key_hash(self, api_key_hash: str) -> ProjectEntity | None:
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.api_key_hash == api_key_hash)
        )
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def get_by_name(self, name: str) -> ProjectEntity | None:
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.name == name)
        )
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def get_all_for_tenant(self, tenant_id: UUID) -> Sequence[ProjectEntity]:
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.tenant_id == tenant_id)
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_paginated_for_tenant(self, tenant_id: UUID, skip: int, limit: int) -> tuple[Sequence[ProjectEntity], int]:
        count_result = await self._session.execute(
            select(func.count()).select_from(ProjectModel).where(ProjectModel.tenant_id == tenant_id)
        )
        total = count_result.scalar() or 0

        result = await self._session.execute(
            select(ProjectModel)
            .where(ProjectModel.tenant_id == tenant_id)
            .order_by(ProjectModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        items = [self._to_entity(model) for model in result.scalars().all()]
        return items, total

    async def get_private_key(self, project_id: UUID) -> str | None:
        result = await self._session.execute(
            select(ProjectModel.private_key).where(ProjectModel.id == project_id)
        )
        key = result.scalar_one_or_none()
        if key:
            return self._encryption_adapter.decrypt(key)
        return None
