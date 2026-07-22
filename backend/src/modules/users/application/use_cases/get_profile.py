import dataclasses

from src.modules.users.application.dtos.user_profile_dto import UserProfileDTO
from src.modules.users.application.ports.users_unit_of_work import UserUoWPort
from src.modules.users.application.queries.user_queries import GetProfileQuery
from src.modules.users.domain.entities import UserProfile
from src.modules.users.domain.exceptions import UserNotFoundException
from src.shared.application.ports import CachePort


class GetProfileUseCase:
    def __init__(self, uow: UserUoWPort, cache: CachePort):
        self.uow = uow
        self.cache = cache

    async def execute(self, query: GetProfileQuery) -> UserProfileDTO:
        async with self.uow:
            cache_key = f"user_profile:{query.user_id}"
            cached_data = await self.cache.get_dict(cache_key)
            if cached_data:
                from uuid import UUID

                from src.shared.domain.value_objects import (
                    EmailAddress,
                    HttpsUrl,
                    PersonName,
                )

                cached_data["id"] = UUID(cached_data["id"])
                cached_data["email"] = EmailAddress(cached_data["email"]["value"])
                if cached_data.get("name"):
                    cached_data["name"] = PersonName(cached_data["name"]["value"])
                if cached_data.get("picture"):
                    cached_data["picture"] = HttpsUrl(cached_data["picture"]["value"])
                if cached_data.get("project_id"):
                    cached_data["project_id"] = UUID(cached_data["project_id"])
                profile: UserProfile = UserProfile(**cached_data)
            else:
                db_profile = await self.uow.profile_repo.get_profile(query.user_id)
                if not db_profile:
                    raise UserNotFoundException()
                profile = db_profile
                await self.cache.set_dict(
                    cache_key, dataclasses.asdict(profile), ttl=900
                )

            return UserProfileDTO(
                id=profile.id,
                email=profile.email.value,
                receive_updates=profile.receive_updates,
                login_methods=profile.login_methods,
                role=profile.role
                if isinstance(profile.role, str)
                else (profile.role.value if profile.role else None),
                project_id=profile.project_id,
                name=profile.name.value if profile.name else None,
                picture=profile.picture.value if profile.picture else None,
            )
