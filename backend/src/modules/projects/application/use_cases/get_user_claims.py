from src.modules.projects.application.dtos.project_dtos import GetUserClaimsDTO
from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort
from src.modules.projects.application.queries.project_queries import GetUserClaimsQuery
from src.modules.projects.application.use_cases import BaseProjectUseCase


class GetUserClaimsUseCase(BaseProjectUseCase):
    def __init__(self, uow: ProjectUoWPort):
        self.uow = uow
        super().__init__()

    async def execute(self, query: GetUserClaimsQuery) -> GetUserClaimsDTO:
        async with self.uow:
            project = await self._get_project_or_404(
                self.uow, query.project_id, query.tenant_id
            )
            defaults = project.default_claims or {}
            all_users, _ = await self.uow.project_user_repo.list_project_users(
                query.project_id, skip=0, limit=9999
            )
            target = next(
                (u for u in all_users if str(u.id) == str(query.user_id)), None
            )
            overrides = getattr(target, "custom_claims", {}) or {}
            allowed = set(defaults.keys())
            effective = {
                **defaults,
                **{k: v for k, v in overrides.items() if k in allowed},
            }
            return GetUserClaimsDTO(
                claims={
                    "default_claims": dict(defaults),
                    "user_overrides": dict(overrides),
                    "effective_claims": dict(effective),
                }
            )
