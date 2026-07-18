"""
Implementation of the ClaimsProviderPort.
"""

from uuid import UUID

from src.modules.auth.authentication.application.ports import (
    ClaimsProviderPort,
    UserQueryRepositoryPort,
)
from src.shared.application.ports import CachePort


from src.modules.projects.application.ports import ProjectQueryRepositoryPort


class ProjectClaimsProviderAdapter[SessionType](ClaimsProviderPort[SessionType]):
    """
    Dynamically supplies the role and custom claims of the user, caching it for performance.
    """

    def __init__(
        self,
        cache: CachePort,
        user_query_repo: UserQueryRepositoryPort[SessionType],
        project_query_repo: ProjectQueryRepositoryPort[SessionType],
    ):
        self.cache = cache
        self.user_query_repo = user_query_repo
        self.project_query_repo = project_query_repo

    async def get_custom_claims(
        self, session: SessionType, user_id: UUID
    ) -> dict[str, object]:
        user = await self.user_query_repo.find_by_id(session, user_id)
        if not user:
            return {}

        if not user.project_id:
            return {"role": user.role.value} if user.role else {}

        claims: dict = {}

        cache_key = f"project:{user.project_id}:default_claims"
        defaults = await self.cache.get_json(cache_key)
        if defaults is None:
            project = await self.project_query_repo.get_by_id(session, user.project_id)
            defaults = project.default_claims if project else {}
            await self.cache.set_json(cache_key, defaults, ttl=900)

        if defaults:
            claims.update(defaults)

        overrides = getattr(user, "custom_claims", {}) or {}
        if overrides:
            allowed = set(defaults.keys())
            claims.update({k: v for k, v in overrides.items() if k in allowed})

        return claims
