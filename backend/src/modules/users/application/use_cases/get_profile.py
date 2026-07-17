from uuid import UUID

from src.modules.users.application.ports import UserProfileRepositoryPort
from src.modules.users.domain.exceptions import UserNotFoundException
from src.modules.users.domain.entities import UserProfile
from src.shared.application.ports import CachePort


class GetProfileUseCase[SessionType]:
    def __init__(self, profile_repository: UserProfileRepositoryPort, cache: CachePort):
        self.profile_repository = profile_repository
        self.cache = cache

    async def execute(self, session: SessionType, user_id: UUID) -> UserProfile:
        cache_key = f"user_profile:{user_id}"
        cached_data = await self.cache.get_dict(cache_key)
        if cached_data:
            return UserProfile(**cached_data)

        profile = await self.profile_repository.get_profile(session, user_id)
        if not profile:
            raise UserNotFoundException()

        await self.cache.set_dict(cache_key, profile.model_dump(mode="json"), ttl=900)
        return profile
