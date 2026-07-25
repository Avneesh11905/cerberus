from datetime import datetime, UTC

from src.core.config import TokenSettings
from src.modules.authentication.application.commands import SessionLogoutAllCommand
from src.modules.authentication.application.ports.authentication_unit_of_work import (
    AuthUoWPort,
)
from src.shared.application.ports import (
    CachePort,
)

"""
Terminates ALL sessions for a user.
Revokes every active refresh token family for the authenticated user and
blacklists the current access token in Redis.
"""


class SessionLogoutAllUseCase:
    """Revokes every active session for a user (logout from all devices)."""

    def __init__(
        self,
        uow: AuthUoWPort,
        cache: CachePort,
        token_settings: TokenSettings,
    ):
        self.uow = uow
        self._cache = cache
        self.token_settings = token_settings

    async def execute(self, command: SessionLogoutAllCommand) -> None:
        async with self.uow:
            """Revoke all refresh tokens and optionally blacklist the current access token.

        `jti` and `exp` must come from a pre-verified JWT payload (via `get_jwt_payload`
        dependency), never by re-decoding the raw token. This prevents blacklist poisoning.
        """
            # Revoke all token families for this user in the database
            await self.uow.refresh_token_repo.revoke_all_for_user(command.user_id)

            # Blacklist the current access token by its already-verified jti
            if command.jti and command.exp:
                now = int(datetime.now(UTC).timestamp())
                ttl = command.exp - now
                if ttl > 0:
                    max_ttl = self.token_settings.ACCESS_TOKEN_LIFETIME_MINUTES * 60
                    ttl = min(ttl, max_ttl)
                    await self._cache.set_string(f"blacklist:{command.jti}", "1", ttl)
