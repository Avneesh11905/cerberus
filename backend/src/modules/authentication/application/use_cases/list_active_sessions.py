from src.modules.authentication.application.commands import ListActiveSessionsQuery
from src.modules.authentication.application.ports.authentication_unit_of_work import (
    AuthUoWPort,
)
from src.modules.authentication.domain.entities import ActiveSession

"""
Lists all active sessions for a user.
"""


class ListActiveSessionsUseCase:
    """Lists all active sessions for a user."""

    def __init__(self, uow: AuthUoWPort):
        self.uow = uow

    async def execute(self, command: ListActiveSessionsQuery) -> list[ActiveSession]:
        async with self.uow:
            """
        Get all active devices/sessions for the user.
        """
            return await self.uow.refresh_token_repo.get_active_sessions(
                command.user_id, command.current_token
            )
