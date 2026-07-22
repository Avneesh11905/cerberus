from src.modules.authentication.application.commands import SessionRevokeCommand
from src.modules.authentication.application.ports.authentication_unit_of_work import (
    AuthUoWPort,
)
from src.modules.authentication.domain.exceptions import SessionNotFoundException

"""
Revokes a specific session (device logout).
"""


class SessionRevokeUseCase:
    """Revokes a specific session family, logging out that device."""

    def __init__(self, uow: AuthUoWPort):
        self.uow = uow

    async def execute(self, command: SessionRevokeCommand) -> None:
        async with self.uow:
            """
        Revokes a session by family_id.
        Verifies that the session actually belongs to the user to prevent IDOR.
        """
            # Fetch active sessions to verify ownership
            sessions = await self.uow.refresh_token_repo.get_active_sessions(
                command.user_id
            )
            if not any(s.family_id == command.family_id for s in sessions):
                raise SessionNotFoundException()

            await self.uow.refresh_token_repo.revoke_by_family(command.family_id)
