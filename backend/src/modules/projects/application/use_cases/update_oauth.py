from datetime import datetime, UTC
from typing import cast

from src.modules.projects.domain.exceptions.project_error import ProjectError

from src.modules.projects.application.commands.project_commands import (
    UpdateOauthCommand,
)
from src.modules.projects.application.dtos.project_dtos import UpdateOauthDTO
from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort

from src.shared.application.ports import EncryptionPort

from .base_project import BaseProjectUseCase


class UpdateOauthUseCase(BaseProjectUseCase):
    def __init__(self, uow: ProjectUoWPort, encryption_adapter: EncryptionPort):
        self.uow = uow
        self.encryption_adapter = encryption_adapter
        super().__init__()

    async def execute(self, command: UpdateOauthCommand) -> UpdateOauthDTO:
        async with self.uow:
            project = await self._get_project_or_404(
                self.uow, command.project_id, command.user_id
            )

            existing_config = project.oauth_config or {}
            final_config = {}

            for provider, _ in command.incoming_config.items():
                old_provider_config = existing_config.get(provider, {})
                provider_config = cast(
                    dict[str, str], command.incoming_config.get(provider, {})
                )

                is_enabled = provider_config.get("enabled", False)
                client_id = provider_config.get("client_id")
                client_secret = provider_config.get("client_secret")

                # Retain old secret if no new secret was provided
                if not client_secret:
                    client_secret = old_provider_config.get("client_secret")
                else:
                    client_secret = self.encryption_adapter.encrypt(client_secret)

                # Validate if enabled
                if is_enabled:
                    errors = []
                    if not client_id:
                        errors.append(
                            {
                                "loc": ["body", "oauth_config", provider, "client_id"],
                                "msg": "Client ID is required when enabled.",
                                "type": "value_error.missing",
                            }
                        )
                    if not client_secret:
                        errors.append(
                            {
                                "loc": [
                                    "body",
                                    "oauth_config",
                                    provider,
                                    "client_secret",
                                ],
                                "msg": "Client Secret is required when enabled.",
                                "type": "value_error.missing",
                            }
                        )

                    if errors:
                        raise ProjectError(str(errors))

                final_config[provider] = {
                    "enabled": is_enabled,
                    "client_id": client_id,
                    "client_secret": client_secret,
                }

            project.oauth_config = final_config
            project.updated_at = datetime.now(UTC)
            return UpdateOauthDTO(
                project=await self.uow.project_command_repo.save(project)
            )
