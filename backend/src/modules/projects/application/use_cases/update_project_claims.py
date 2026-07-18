from datetime import datetime, timezone
from src.modules.projects.application.use_cases import BaseProjectUseCase
from src.modules.projects.domain.entities import ProjectEntity

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


class UpdateProjectClaimsUseCase[SessionType](BaseProjectUseCase[SessionType]):
    def __init__(self, query_repository, command_repository, cache):
        super().__init__(query_repository)
        self.command_repository = command_repository
        self.cache = cache

    async def execute(
        self, session: SessionType, project_id, user_id, default_claims
    ) -> ProjectEntity:
        if len(default_claims) > MAX_CLAIM_KEYS:
            raise ValueError(f"Maximum {MAX_CLAIM_KEYS} claim keys allowed")
        forbidden = set(default_claims.keys()) & RESERVED_KEYS
        if forbidden:
            raise ValueError(f"Reserved claim keys cannot be used: {forbidden}")

        project = await self._get_project_or_404(session, project_id, user_id)
        project.default_claims = default_claims
        project.updated_at = datetime.now(timezone.utc)

        saved = await self.command_repository.save(session, project)
        await self.cache.delete(f"project:{project_id}:default_claims")
        return saved
