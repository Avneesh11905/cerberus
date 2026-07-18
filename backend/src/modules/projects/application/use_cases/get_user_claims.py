from uuid import UUID
from src.modules.projects.application.use_cases import BaseProjectUseCase


class GetUserClaimsUseCase[SessionType](BaseProjectUseCase[SessionType]):
    def __init__(self, query_repository, project_user_repository):
        super().__init__(query_repository)
        self.project_user_repository = project_user_repository

    async def execute(
        self,
        session: SessionType,
        project_id: UUID,
        tenant_id: UUID | None,
        user_id: UUID,
    ) -> dict:
        project = await self._get_project_or_404(session, project_id, tenant_id)
        defaults = project.default_claims
        all_users = await self.project_user_repository.list_project_users(
            session, project_id, skip=0, limit=9999
        )
        target = next((u for u in all_users if str(u.id) == str(user_id)), None)
        overrides = getattr(target, "custom_claims", {}) or {}
        allowed = set(defaults.keys())
        effective = {**defaults, **{k: v for k, v in overrides.items() if k in allowed}}
        return {
            "default_claims": defaults,
            "user_overrides": overrides,
            "effective_claims": effective,
        }
