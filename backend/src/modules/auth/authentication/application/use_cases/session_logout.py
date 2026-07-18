"""
Terminates a user session securely.
It performs two distinct actions:
1. Revokes the long-lived refresh token in the database so no new access tokens can be minted.
2. Blacklists the short-lived access token in Redis (using its `jti`) until it expires naturally,
   preventing stolen tokens from being used immediately after logout.
"""

from datetime import datetime, timezone

from src.core.config import TokenSettings
from src.modules.auth.authentication.application.ports import RefreshTokenRepositoryPort
from src.shared.application.ports import (
    CachePort,
    UoWPort,
)


class SessionLogoutUseCase[SessionType]:
    """Handles logging out a user by revoking the refresh token and blacklisting the access token."""

    def __init__(
        self,
        refresh_repo: RefreshTokenRepositoryPort,
        cache: CachePort,
        token_settings: TokenSettings,
    ):
        self._refresh_repo = refresh_repo
        self._cache = cache
        self.token_settings = token_settings

    async def execute(
        self,
        uow: UoWPort[SessionType],
        refresh_token: str | None,
        jti: str | None = None,
        exp: int | None = None,
    ) -> None:
        """Revoke the refresh token and blacklist the access token by its already-verified jti.

        `jti` and `exp` must come from a pre-verified JWT payload (via `get_jwt_payload`
        dependency), never by re-decoding the raw token. This prevents blacklist poisoning where
        an attacker submits a crafted JWT with an arbitrary jti to exhaust Redis.
        """
        if refresh_token:
            await self._refresh_repo.revoke(uow.session, refresh_token)

        if jti and exp:
            now = int(datetime.now(timezone.utc).timestamp())
            ttl = exp - now
            if ttl > 0:
                max_ttl = self.token_settings.ACCESS_TOKEN_LIFETIME_MINUTES * 60
                ttl = min(ttl, max_ttl)
                await self._cache.set_string(f"blacklist:{jti}", "1", ttl)
