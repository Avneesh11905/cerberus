from src.modules.projects.application.commands.project_commands import (
    UpdateUserClaimsCommand,
)
from src.modules.projects.application.dtos.project_dtos import UpdateUserClaimsDTO
from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort
from src.modules.projects.application.use_cases import BaseProjectUseCase
from src.modules.projects.domain.exceptions import ProjectNotFoundError

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


class UpdateUserClaimsUseCase(BaseProjectUseCase):
    def __init__(self, uow: ProjectUoWPort, cache):
        self.uow = uow
        self.cache = cache
        super().__init__()
        self.cache = cache

    async def execute(self, command: UpdateUserClaimsCommand) -> UpdateUserClaimsDTO:
        async with self.uow:
            forbidden = set(command.overrides.keys()) & RESERVED_KEYS
            if forbidden:
                raise ValueError(f"Reserved keys cannot be used: {forbidden}")

            project = await self._get_project_or_404(
                self.uow, command.project_id, command.tenant_id
            )
            allowed = set(project.default_claims.keys())
            unknown = set(command.overrides.keys()) - allowed
            if unknown:
                raise ValueError(
                    f"Keys not defined in project schema cannot be used: {unknown}"
                )

            user = await self.uow.project_user_repo.update_user_claims(
                command.project_id, command.user_id, command.overrides
            )
            if not user:
                raise ProjectNotFoundError("User not found in this project")

            await self.cache.delete(f"user_profile:{command.user_id}:custom_claims")
            return UpdateUserClaimsDTO(user=user)
