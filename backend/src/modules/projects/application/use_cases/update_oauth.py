from datetime import datetime, timezone
from uuid import UUID

from src.modules.projects.application.ports import (
    ProjectCommandRepositoryPort,
    ProjectQueryRepositoryPort,
)
from src.modules.projects.domain.entities import ProjectEntity
from src.shared.application.ports import EncryptionPort
from .base_project import BaseProjectUseCase


class UpdateOauthUseCase[SessionType](BaseProjectUseCase[SessionType]):
    def __init__(
        self,
        query_repository: ProjectQueryRepositoryPort,
        command_repository: ProjectCommandRepositoryPort,
        encryption_adapter: EncryptionPort,
    ):
        super().__init__(query_repository)
        self.command_repository = command_repository
        self.encryption_adapter = encryption_adapter

    async def execute(
        self,
        session: SessionType,
        project_id: UUID,
        user_id: UUID,
        incoming_config: dict,
    ) -> ProjectEntity:
        project = await self._get_project_or_404(session, project_id, user_id)

        for provider, config in incoming_config.items():
            if "client_secret" in config and config["client_secret"]:
                config["client_secret"] = self.encryption_adapter.encrypt(
                    config["client_secret"]
                )

        project.oauth_config = incoming_config
        project.updated_at = datetime.now(timezone.utc)
        return await self.command_repository.save(session, project)
