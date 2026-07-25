from src.modules.users.application.commands.user_commands import UpdateProfileCommand
from src.modules.users.application.dtos.user_profile_dto import UserProfileDTO
from src.modules.users.application.ports.users_unit_of_work import UserUoWPort
from src.modules.users.domain.entities import UserProfile
from src.modules.users.domain.exceptions import UserNotFoundException
from src.shared.application.ports import CachePort


class UpdateProfileUseCase:
    def __init__(self, uow: UserUoWPort, cache: CachePort):
        self.uow = uow
        self.cache = cache

    async def execute(
        self,
        command: UpdateProfileCommand,
    ) -> UserProfileDTO:
        async with self.uow:
            cache_key = f"user_profile:{command.user_id}"
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
                profile = UserProfile(**cached_data)
            else:
                fetched_profile = await self.uow.profile_repo.get_profile(
                    command.user_id
                )
                if not fetched_profile:
                    raise UserNotFoundException()
                profile = fetched_profile

            profile.update_info(
                name=PersonName(command.name) if command.name else None,
                picture=HttpsUrl(command.picture) if command.picture else None,
                receive_updates=command.receive_updates,
            )
            updated = await self.uow.profile_repo.save_profile(profile)

            await self.cache.delete_key(f"user_profile:{command.user_id}")

            return UserProfileDTO(
                id=updated.id,
                email=updated.email.value,
                receive_updates=updated.receive_updates,
                login_methods=updated.login_methods,
                role=updated.role
                if isinstance(updated.role, str)
                else (updated.role.value if updated.role else None),
                name=updated.name.value if updated.name else None,
                picture=updated.picture.value if updated.picture else None,
            )
