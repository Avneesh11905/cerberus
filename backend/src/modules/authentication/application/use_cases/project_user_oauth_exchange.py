import dataclasses
from uuid import UUID

from src.modules.authentication.application.commands import OAuthExchangeCommand
from src.modules.authentication.application.ports.authentication_unit_of_work import (
    AuthUoWPort,
)
from src.modules.authentication.domain.exceptions import OAuthFailedException
from src.shared.application.ports import CachePort


class OAuthExchangeUseCase:
    """
    Redeems the short-lived one-time code for session tokens and user profile.
    """

    def __init__(self, uow: AuthUoWPort, cache: CachePort):
        self.uow = uow
        self._cache = cache

    async def execute(
        self, command: OAuthExchangeCommand
    ) -> tuple[str, bool, str, dict | None]:
        async with self.uow:
            """
        Redeems the short-lived one-time code for session tokens.

        Returns:
            (refresh_token, is_new_user, access_token, user_profile_dict)
        """
            data = await self._cache.get_dict(f"exchange_code:{command.code}")
            if not data:
                raise OAuthFailedException("Invalid or expired exchange code")

            # One-time use — delete immediately before returning tokens
            await self._cache.delete_key(f"exchange_code:{command.code}")

            refresh_token: str = data["refresh_token"]
            is_new_user: bool = data.get("is_new_user", False)
            access_token: str = data.get("access_token", "")
            user_id_str: str | None = data.get("user_id")

            profile_dict = None
            if user_id_str:
                profile = await self.uow.user_query_repo.find_by_id(UUID(user_id_str))
                if profile:
                    profile_dict = dataclasses.asdict(profile)

            return refresh_token, is_new_user, access_token, profile_dict
