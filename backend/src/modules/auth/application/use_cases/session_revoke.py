"""
Revokes a specific session (device logout).
"""

from uuid import UUID

from src.modules.auth.application.ports import RefreshTokenRepositoryPort
from src.modules.auth.domain.exceptions import SessionNotFoundException
from src.shared.application.ports import UoWPort


class SessionRevokeUseCase[SessionType]:
    """Revokes a specific session family, logging out that device."""

    def __init__(self, refresh_repo: RefreshTokenRepositoryPort):
        self._refresh_repo = refresh_repo

    async def execute(
        self, uow: UoWPort[SessionType], user_id: UUID, family_id: UUID
    ) -> None:
        """
        Revokes a session by family_id.
        Verifies that the session actually belongs to the user to prevent IDOR.
        """
        # Fetch active sessions to verify ownership
        sessions = await self._refresh_repo.get_active_sessions(uow.session, user_id)
        if not any(s.family_id == family_id for s in sessions):
            raise SessionNotFoundException()

        await self._refresh_repo.revoke_by_family(uow.session, family_id)
