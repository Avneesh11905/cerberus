"""
Terminates ALL sessions for a user.
Revokes every active refresh token family for the authenticated user and
blacklists the current access token in Redis.
"""
from datetime import datetime, timezone
from uuid import UUID

from src.authentication.core.ports import RefreshTokenRepositoryPort
from src.shared.core.ports.cache import CachePort
from src.shared.core.ports.uow import UoWPort
from src.shared.config import token_settings


class LogoutAllUseCase[SessionType]:
    """Revokes every active session for a user (logout from all devices)."""

    def __init__(self, refresh_repo: RefreshTokenRepositoryPort, cache: CachePort):
        self._refresh_repo = refresh_repo
        self._cache = cache

    async def execute(
        self,
        uow: UoWPort[SessionType],
        user_id: UUID,
        jti: str | None = None,
        exp: int | None = None,
    ) -> None:
        """Revoke all refresh tokens and optionally blacklist the current access token.

        `jti` and `exp` must come from a pre-verified JWT payload (via `get_jwt_payload`
        dependency), never by re-decoding the raw token. This prevents blacklist poisoning.
        """
        # Revoke all token families for this user in the database
        await self._refresh_repo.revoke_all_for_user(uow.session, user_id)

        # Blacklist the current access token by its already-verified jti
        if jti and exp:
            now = int(datetime.now(timezone.utc).timestamp())
            ttl = exp - now
            if ttl > 0:
                max_ttl = token_settings.ACCESS_TOKEN_LIFETIME_MINUTES * 60
                ttl = min(ttl, max_ttl)
                await self._cache.set_string(f"blacklist:{jti}", "1", ttl)
