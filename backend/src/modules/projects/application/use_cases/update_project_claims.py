from datetime import datetime, timezone

from src.modules.projects.application.commands.project_commands import (
    UpdateProjectClaimsCommand,
)
from src.modules.projects.application.dtos.project_dtos import UpdateProjectClaimsDTO
from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort
from src.modules.projects.application.use_cases import BaseProjectUseCase

MAX_CLAIM_KEYS = 10
RESERVED_KEYS = {
    "sub",
    "email",
    "role",
    "exp",
    "iat",
    "jti",
    "project_id",
    "is_verified",
    "family_id",
}


class UpdateProjectClaimsUseCase(BaseProjectUseCase):
    def __init__(self, uow: ProjectUoWPort, cache):
        self.uow = uow
        self.cache = cache
        super().__init__()
        self.cache = cache

    async def execute(
        self, command: UpdateProjectClaimsCommand
    ) -> UpdateProjectClaimsDTO:
        async with self.uow:
            if len(command.default_claims) > MAX_CLAIM_KEYS:
                raise ValueError(f"Maximum {MAX_CLAIM_KEYS} claim keys allowed")
            forbidden = set(command.default_claims.keys()) & RESERVED_KEYS
            if forbidden:
                raise ValueError(f"Reserved claim keys cannot be used: {forbidden}")

            project = await self._get_project_or_404(
                self.uow, command.project_id, command.user_id
            )
            project.default_claims = command.default_claims
            project.updated_at = datetime.now(timezone.utc)

            saved = await self.uow.project_command_repo.save(project)
            await self.cache.delete(
                f"project:{command.project_id}:command.default_claims"
            )
            return UpdateProjectClaimsDTO(project=saved)
