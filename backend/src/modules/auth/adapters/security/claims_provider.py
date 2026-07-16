"""
Implementation of the ClaimsProviderPort.
"""

from uuid import UUID

from src.modules.auth.application.ports.repository.user import UserRepositoryPort
from src.modules.auth.application.ports.security.claims_provider import (
    ClaimsProviderPort,
)
from src.shared.application.ports.cache import CachePort


class NullClaimsProviderAdapter[SessionType](ClaimsProviderPort[SessionType]):
    """Returns no extra claims."""

    async def get_custom_claims(
        self, session: SessionType, user_id: UUID
    ) -> dict[str, object]:
        return {}


class RoleClaimsProviderAdapter[SessionType](ClaimsProviderPort[SessionType]):
    """
    Dynamically supplies the role of the user, caching it for performance.
    """

    def __init__(self, cache: CachePort, user_repo: UserRepositoryPort[SessionType]):
        self.cache = cache
        self.user_repo = user_repo

    async def get_custom_claims(
        self, session: SessionType, user_id: UUID
    ) -> dict[str, object]:
        cache_key = f"user_profile:{user_id}:role"
        cached_role = await self.cache.get_string(cache_key)

        if cached_role:
            return {"role": cached_role}

        user = await self.user_repo.find_by_id(session, user_id)
        if not user:
            # We silently return empty claims if not found here (though shouldn't happen)
            return {}

        # Cache for 15 minutes
        await self.cache.set_string(cache_key, user.role.value, ttl=900)
        return {"role": user.role.value}
