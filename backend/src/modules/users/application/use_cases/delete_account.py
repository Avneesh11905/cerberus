from datetime import datetime, timezone

from src.core.config import get_settings
from src.modules.users.application.commands.user_commands import DeleteAccountCommand
from src.modules.users.application.ports.users_unit_of_work import UserUoWPort
from src.shared.application.ports import CachePort


class DeleteAccountUseCase:
    def __init__(self, uow: UserUoWPort, cache: CachePort):
        self.uow = uow
        self.cache = cache

    async def execute(
        self,
        command: DeleteAccountCommand,
    ) -> None:
        async with self.uow:
            # 1. Delete user from database
            await self.uow.profile_repo.delete_user(command.user_id)
            await self.cache.delete_key(f"user_profile:{command.user_id}")

            # 2. Blacklist the current access token
            if command.jwt_jti and command.jwt_exp:
                now = int(datetime.now(timezone.utc).timestamp())
                ttl = command.jwt_exp - now
                if ttl > 0:
                    max_ttl = get_settings().token.ACCESS_TOKEN_LIFETIME_MINUTES * 60
                    ttl = min(ttl, max_ttl)
                    await self.cache.set_string(
                        f"blacklist:{command.jwt_jti}", "1", ttl
                    )
