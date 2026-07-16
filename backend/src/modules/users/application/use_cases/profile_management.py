"""
Module: User Profile Management Use Cases
"""

from datetime import datetime, timezone
from typing import Optional, TypeVar
from uuid import UUID

from src.core.config import token_settings
from src.modules.users.application.ports.user_profile_repository import (
    UserProfileRepositoryPort,
)
from src.modules.users.domain.exceptions import UserNotFoundException
from src.modules.users.domain.profile import UserProfile
from src.shared.application.ports.cache import CachePort

SessionType = TypeVar("SessionType")


class ProfileManagementUseCase:
    def __init__(self, profile_repository: UserProfileRepositoryPort, cache: CachePort):
        self.profile_repository = profile_repository
        self.cache = cache

    async def get_profile(self, session: SessionType, user_id: UUID) -> UserProfile:
        cache_key = f"user_profile:{user_id}"
        cached_data = await self.cache.get_dict(cache_key)
        if cached_data:
            return UserProfile(**cached_data)

        profile = await self.profile_repository.get_profile(session, user_id)
        if not profile:
            raise UserNotFoundException()

        await self.cache.set_dict(cache_key, profile.model_dump(), ttl=900)
        return profile

    async def update_profile(
        self,
        session: SessionType,
        user_id: UUID,
        name: Optional[str] = None,
        picture: Optional[str] = None,
        receive_updates: Optional[bool] = None,
    ) -> UserProfile:
        profile = await self.get_profile(session, user_id)
        profile.update_info(name=name, picture=picture, receive_updates=receive_updates)
        updated = await self.profile_repository.save_profile(session, profile)

        await self.cache.delete_key(f"user_profile:{user_id}")
        return updated

    async def delete_account(
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
