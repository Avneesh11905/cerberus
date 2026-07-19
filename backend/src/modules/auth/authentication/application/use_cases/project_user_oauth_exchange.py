from uuid import UUID

from src.shared.application.ports import CachePort
from src.modules.users.application.ports.user_profile_repository import (
    UserProfileRepositoryPort,
)
from src.modules.auth.authentication.domain.exceptions import OAuthFailedException


class OAuthExchangeUseCase[SessionType]:
    """
    Redeems the short-lived one-time code for session tokens and user profile.
    """

    def __init__(self, cache: CachePort, user_profile_repo: UserProfileRepositoryPort):
        self._cache = cache
        self._user_profile_repo = user_profile_repo

    async def execute(
        self, session: SessionType, code: str
    ) -> tuple[str, bool, str, dict | None]:
        """
        Redeems the short-lived one-time code for session tokens.

        Returns:
            (refresh_token, is_new_user, access_token, user_profile_dict)
        """
        data = await self._cache.get_dict(f"exchange_code:{code}")
        if not data:
            raise OAuthFailedException("Invalid or expired exchange code")

        # One-time use — delete immediately before returning tokens
        await self._cache.delete_key(f"exchange_code:{code}")

        refresh_token: str = data["refresh_token"]
        is_new_user: bool = data.get("is_new_user", False)
        access_token: str = data.get("access_token", "")
        user_id_str: str | None = data.get("user_id")

        profile_dict = None
        if user_id_str:
            profile = await self._user_profile_repo.get_profile(
                session, UUID(user_id_str)
            )
            if profile:
                profile_dict = profile.model_dump()

        return refresh_token, is_new_user, access_token, profile_dict
