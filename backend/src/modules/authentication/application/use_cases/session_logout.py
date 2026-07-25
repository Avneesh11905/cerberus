from datetime import datetime, UTC

from src.core.config import TokenSettings
from src.modules.authentication.application.commands import SessionLogoutCommand
from src.modules.authentication.application.ports.authentication_unit_of_work import (
    AuthUoWPort,
)
from src.shared.application.ports import (
    CachePort,
)

"""
Terminates a user session securely.
It performs two distinct actions:
1. Revokes the long-lived refresh token in the database so no new access tokens can be minted.
2. Blacklists the short-lived access token in Redis (using its `jti`) until it expires naturally,
   preventing stolen tokens from being used immediately after logout.
"""


class SessionLogoutUseCase:
    """Handles logging out a user by revoking the refresh token and blacklisting the access token."""

    def __init__(
        self,
        uow: AuthUoWPort,
        cache: CachePort,
        token_settings: TokenSettings,
    ):
        self.uow = uow
        self._cache = cache
        self.token_settings = token_settings

    async def execute(self, command: SessionLogoutCommand) -> None:
        async with self.uow:
            """Revoke the refresh token and blacklist the access token by its already-verified jti.

        `jti` and `exp` must come from a pre-verified JWT payload (via `get_jwt_payload`
        dependency), never by re-decoding the raw token. This prevents blacklist poisoning where
        an attacker submits a crafted JWT with an arbitrary jti to exhaust Redis.
        """
            if command.refresh_token:
                await self.uow.refresh_token_repo.revoke(command.refresh_token)

            if command.jti and command.exp:
                now = int(datetime.now(UTC).timestamp())
                ttl = command.exp - now
                if ttl > 0:
                    max_ttl = self.token_settings.ACCESS_TOKEN_LIFETIME_MINUTES * 60
                    ttl = min(ttl, max_ttl)
                    await self._cache.set_string(f"blacklist:{command.jti}", "1", ttl)
