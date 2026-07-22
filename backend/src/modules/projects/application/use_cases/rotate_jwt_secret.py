from datetime import datetime, timezone

from src.modules.projects.application.commands.project_commands import (
    RotateJwtSecretCommand,
)
from src.modules.projects.application.dtos.project_dtos import RotateJwtSecretDTO
from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort

from .base_project import BaseProjectUseCase


from src.shared.application.ports import AnalyticsEventPort
from .base_project import BaseProjectUseCase


class RotateJwtSecretUseCase(BaseProjectUseCase):
    def __init__(self, uow: ProjectUoWPort, rsa_key_adapter, analytics: AnalyticsEventPort):
        self.uow = uow
        self.rsa_key_adapter = rsa_key_adapter
        self.analytics = analytics
        super().__init__()
        self.rsa_key_adapter = rsa_key_adapter

    async def execute(self, command: RotateJwtSecretCommand) -> RotateJwtSecretDTO:
        async with self.uow:
            project = await self._get_project_or_404(
                self.uow, command.project_id, command.user_id
            )
            private_pem, public_pem = await self.rsa_key_adapter.generate_keypair()
            project.private_key = private_pem
            project.public_key = public_pem
            project.updated_at = datetime.now(timezone.utc)
            await self.uow.project_command_repo.save(project)
            
            self.analytics.record_event(
                event_type="JWT_KEY_ROTATED",
                project_id=command.project_id,
                tenant_id=project.tenant_id,
                user_id=command.user_id,
            )
            
            return RotateJwtSecretDTO(public_pem=public_pem)
