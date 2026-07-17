from typing import Optional
from uuid import UUID
from src.modules.users.application.ports import UserProfileRepositoryPort
from src.modules.users.domain.exceptions import UserNotFoundException
from src.modules.users.domain.entities import UserProfile
from src.shared.application.ports import CachePort


class UpdateProfileUseCase[SessionType]:
    def __init__(self, profile_repository: UserProfileRepositoryPort, cache: CachePort):
        self.profile_repository = profile_repository
        self.cache = cache

    async def execute(
        self,
        session: SessionType,
        user_id: UUID,
        name: Optional[str] = None,
        picture: Optional[str] = None,
        receive_updates: Optional[bool] = None,
    ) -> UserProfile:
        cache_key = f"user_profile:{user_id}"
        cached_data = await self.cache.get_dict(cache_key)
        if cached_data:
            profile = UserProfile(**cached_data)
        else:
            fetched_profile = await self.profile_repository.get_profile(
                session, user_id
            )
            if not fetched_profile:
                raise UserNotFoundException()
            profile = fetched_profile

        profile.update_info(name=name, picture=picture, receive_updates=receive_updates)
        updated = await self.profile_repository.save_profile(session, profile)

        await self.cache.delete_key(f"user_profile:{user_id}")
        return updated
