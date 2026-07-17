from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from src.core.config import token_settings
from src.modules.users.application.ports import UserProfileRepositoryPort
from src.shared.application.ports import CachePort


class DeleteAccountUseCase[SessionType]:
    def __init__(self, profile_repository: UserProfileRepositoryPort, cache: CachePort):
        self.profile_repository = profile_repository
        self.cache = cache

    async def execute(
        self,
        session: SessionType,
        user_id: UUID,
        jwt_jti: Optional[str],
        jwt_exp: Optional[int],
    ) -> None:
        # 1. Delete user from database
        await self.profile_repository.delete_user(session, user_id)
        await self.cache.delete_key(f"user_profile:{user_id}")

        # 2. Blacklist the current access token
        if jwt_jti and jwt_exp:
            now = int(datetime.now(timezone.utc).timestamp())
            ttl = jwt_exp - now
            if ttl > 0:
                max_ttl = token_settings.ACCESS_TOKEN_LIFETIME_MINUTES * 60
                ttl = min(ttl, max_ttl)
                await self.cache.set_string(f"blacklist:{jwt_jti}", "1", ttl)
