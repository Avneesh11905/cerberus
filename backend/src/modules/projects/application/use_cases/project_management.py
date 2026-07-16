"""
Module: Project Management Use Cases
"""

from datetime import datetime, timezone
from typing import Any, Sequence
from uuid import UUID

from uuid6 import uuid7

from src.modules.projects.application.ports.project_command_repository import (
    ProjectCommandRepositoryPort,
)
from src.modules.projects.application.ports.project_query_repository import (
    ProjectQueryRepositoryPort,
)
from src.modules.projects.domain.exceptions import (
    ProjectForbiddenError,
    ProjectNotFoundError,
)
from src.modules.projects.domain.project import ProjectEntity
from src.shared.application.ports.api_key import ApiKeyPort
from src.shared.application.ports.encryption import EncryptionPort
from src.shared.application.ports.rsa_key import RsaKeyPort


class ProjectManagementUseCase:
    """Coordinates business logic for projects."""

    def __init__(
        self,
        query_repository: ProjectQueryRepositoryPort,
        command_repository: ProjectCommandRepositoryPort,
        encryption_adapter: EncryptionPort,
        api_key_adapter: ApiKeyPort,
        rsa_key_adapter: RsaKeyPort,
    ):
        self.query_repository = query_repository
        self.command_repository = command_repository
        self.encryption_adapter = encryption_adapter
        self.api_key_adapter = api_key_adapter
        self.rsa_key_adapter = rsa_key_adapter

    async def _get_project_or_404(
        self, session: Any, project_id: UUID, user_id: UUID
    ) -> ProjectEntity:
        project = await self.query_repository.get_by_id(session, project_id)
        if not project:
            raise ProjectNotFoundError("Project not found")

        if project.tenant_id != user_id:
            raise ProjectForbiddenError("Forbidden")

        return project

    async def create_project(
        self, session: Any, user_id: UUID, name: str
    ) -> tuple[ProjectEntity, str, str]:
        project_id = uuid7()
        api_key_plaintext = self.api_key_adapter.generate(project_id)
        api_key_hash = self.api_key_adapter.hash(api_key_plaintext)

        private_pem, public_pem = await self.rsa_key_adapter.generate_keypair()

        project = ProjectEntity(
            id=project_id,
            tenant_id=user_id,
            name=name,
            private_key=private_pem,
            public_key=public_pem,
            api_key_hash=api_key_hash,
            created_at=datetime.now(timezone.utc),
            environment="development",
        )
        saved_project = await self.command_repository.save(session, project)
        return saved_project, api_key_plaintext, public_pem

    async def list_projects(
        self, session: Any, user_id: UUID
    ) -> Sequence[ProjectEntity]:
        return await self.query_repository.get_all_for_tenant(session, user_id)

    async def get_project(
        self, session: Any, project_id: UUID, user_id: UUID
    ) -> ProjectEntity:
        return await self._get_project_or_404(session, project_id, user_id)

    async def delete_project(
        self, session: Any, project_id: UUID, user_id: UUID
    ) -> None:
        project = await self._get_project_or_404(session, project_id, user_id)
        await self.command_repository.delete(session, project.id)

    async def update_oauth(
        self, session: Any, project_id: UUID, user_id: UUID, incoming_config: dict
    ) -> ProjectEntity:
        project = await self._get_project_or_404(session, project_id, user_id)

        # Merge or replace config, applying encryption to sensitive fields like client_secret
        for provider, config in incoming_config.items():
            if "client_secret" in config and config["client_secret"]:
                config["client_secret"] = self.encryption_adapter.encrypt(
                    config["client_secret"]
                )

        project.oauth_config = incoming_config
        project.updated_at = datetime.now(timezone.utc)
        return await self.command_repository.save(session, project)

    async def update_origins(
        self, session: Any, project_id: UUID, user_id: UUID, allowed_origins: list[str]
    ) -> ProjectEntity:
        project = await self._get_project_or_404(session, project_id, user_id)
        project.allowed_origins = allowed_origins
        project.updated_at = datetime.now(timezone.utc)
        return await self.command_repository.save(session, project)

    async def update_environment(
        self, session: Any, project_id: UUID, user_id: UUID, environment: str
    ) -> ProjectEntity:
        project = await self._get_project_or_404(session, project_id, user_id)
        project.environment = environment
        project.updated_at = datetime.now(timezone.utc)
        return await self.command_repository.save(session, project)

    async def update_frontend_url(
        self, session: Any, project_id: UUID, user_id: UUID, frontend_url: str | None
    ) -> ProjectEntity:
        project = await self._get_project_or_404(session, project_id, user_id)
        project.frontend_url = frontend_url
        project.updated_at = datetime.now(timezone.utc)
        return await self.command_repository.save(session, project)

    async def update_name(
        self, session: Any, project_id: UUID, user_id: UUID, name: str
    ) -> ProjectEntity:
        project = await self._get_project_or_404(session, project_id, user_id)
        project.name = name
        project.updated_at = datetime.now(timezone.utc)
        return await self.command_repository.save(session, project)

    async def get_secrets(
        self, session: Any, project_id: UUID, user_id: UUID
    ) -> tuple[str, str]:
        project = await self._get_project_or_404(session, project_id, user_id)
        return project.api_key_hash, project.public_key

    async def rotate_api_key(
        self, session: Any, project_id: UUID, user_id: UUID
    ) -> str:
        project = await self._get_project_or_404(session, project_id, user_id)
        api_key_plaintext = self.api_key_adapter.generate(project.id)
        project.api_key_hash = self.api_key_adapter.hash(api_key_plaintext)
        project.updated_at = datetime.now(timezone.utc)
        await self.command_repository.save(session, project)
        return api_key_plaintext

    async def rotate_jwt_secret(
        self, session: Any, project_id: UUID, user_id: UUID
    ) -> str:
        project = await self._get_project_or_404(session, project_id, user_id)
        private_pem, public_pem = await self.rsa_key_adapter.generate_keypair()
        project.private_key = private_pem
        project.public_key = public_pem
        project.updated_at = datetime.now(timezone.utc)
        await self.command_repository.save(session, project)
        return public_pem
