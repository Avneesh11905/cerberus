"""
Lists all active sessions for a user.
"""

from uuid import UUID

from src.modules.auth.application.ports import RefreshTokenRepositoryPort
from src.modules.auth.domain.session import ActiveSession
from src.shared.application.ports.uow import UoWPort


class ListSessionsUseCase[SessionType]:
    """Lists all active sessions for a user."""

    def __init__(self, refresh_repo: RefreshTokenRepositoryPort[SessionType]):
        self._refresh_repo = refresh_repo

    async def execute(
        self, uow: UoWPort[SessionType], user_id: UUID, current_token: str | None = None
    ) -> list[ActiveSession]:
        """
        Get all active devices/sessions for the user.
        """
        return await self._refresh_repo.get_active_sessions(
            uow.session, user_id, current_token
        )
