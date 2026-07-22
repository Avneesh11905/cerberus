"""
Implementation of the ClaimsProviderPort.
"""

from uuid import UUID

from src.modules.authentication.application.ports import (
    ClaimsProviderPort,
)
from src.modules.authentication.application.ports.authentication_unit_of_work import (
    AuthUoWPort,
)
from src.modules.authorization.domain.enums import GlobalRole
from src.shared.application.ports import CachePort


class ProjectClaimsProviderAdapter(ClaimsProviderPort):
    """
    Dynamically supplies the role and custom claims of the user, caching it for performance.
    """

    def __init__(self, cache: CachePort):
        self.cache = cache

    async def get_custom_claims(
        self, uow: AuthUoWPort, user_id: UUID
    ) -> dict[str, object]:
        user = await uow.user_query_repo.find_by_id(user_id)
        if not user:
            return {}

        if not user.project_id:
            return (
                {
                    "role": user.role.value
                    if isinstance(user.role, GlobalRole)
                    else user.role
                }
                if user.role
                else {}
            )

        claims: dict = {}

        cache_key = f"project:{user.project_id}:default_claims"
        defaults = await self.cache.get_dict(cache_key)
        if defaults is None:
            project = await uow.project_query_repo.get_by_id(user.project_id)
            defaults = project.default_claims if project else {}
            await self.cache.set_dict(cache_key, defaults, ttl=900)

        if defaults:
            claims.update(defaults)

        overrides = getattr(user, "custom_claims", {}) or {}
        if overrides:
            allowed = set(defaults.keys())
            claims.update({k: v for k, v in overrides.items() if k in allowed})

        return claims
