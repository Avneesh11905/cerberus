"""
Implementation of the ClaimsProviderPort.
"""

from uuid import UUID

from src.modules.auth.authentication.application.ports import (
    ClaimsProviderPort,
    UserQueryRepositoryPort,
)
from src.shared.application.ports import CachePort


class RoleClaimsProviderAdapter[SessionType](ClaimsProviderPort[SessionType]):
    """
    Dynamically supplies the role of the user, caching it for performance.
    """

    def __init__(
        self, cache: CachePort, user_query_repo: UserQueryRepositoryPort[SessionType]
    ):
        self.cache = cache
        self.user_query_repo = user_query_repo

    async def get_custom_claims(
        self, session: SessionType, user_id: UUID
    ) -> dict[str, object]:
        cache_key = f"user_profile:{user_id}:role"
        cached_role = await self.cache.get_string(cache_key)

        if cached_role:
            return {"role": cached_role}

        user = await self.user_query_repo.find_by_id(session, user_id)
        if not user:
            # We silently return empty claims if not found here (though shouldn't happen)
            return {}

        # Cache for 15 minutes
        await self.cache.set_string(cache_key, user.role.value, ttl=900)
        return {"role": user.role.value}
