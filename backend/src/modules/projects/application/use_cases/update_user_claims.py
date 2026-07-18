from src.modules.projects.application.use_cases import BaseProjectUseCase
from src.modules.projects.domain.exceptions import ProjectNotFoundError
from src.modules.users.domain.entities import UserProfile

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


class UpdateUserClaimsUseCase[SessionType](BaseProjectUseCase[SessionType]):
    def __init__(self, query_repository, project_user_repository, cache):
        super().__init__(query_repository)
        self.project_user_repository = project_user_repository
        self.cache = cache

    async def execute(
        self, session: SessionType, project_id, tenant_id, user_id, overrides
    ) -> UserProfile:
        forbidden = set(overrides.keys()) & RESERVED_KEYS
        if forbidden:
            raise ValueError(f"Reserved keys cannot be used: {forbidden}")

        project = await self._get_project_or_404(session, project_id, tenant_id)
        allowed = set(project.default_claims.keys())
        unknown = set(overrides.keys()) - allowed
        if unknown:
            raise ValueError(
                f"Keys not defined in project schema cannot be used: {unknown}"
            )

        user = await self.project_user_repository.update_user_claims(
            session, project_id, user_id, overrides
        )
        if not user:
            raise ProjectNotFoundError("User not found in this project")

        await self.cache.delete(f"user_profile:{user_id}:custom_claims")
        return user
