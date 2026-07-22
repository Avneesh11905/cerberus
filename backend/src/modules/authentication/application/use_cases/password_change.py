from src.modules.authentication.application.commands import PasswordChangeCommand
from src.modules.authentication.application.ports import (
    PasswordHasherPort,
)
from src.modules.authentication.application.ports.authentication_unit_of_work import (
    AuthUoWPort,
)
from src.modules.authentication.domain.exceptions import (
    InvalidCredentialsException,
    SamePasswordException,
)
from src.shared.application.ports import (
    LoggerPort,
)


class PasswordChangeUseCase:
    """Handles updating a user's password when they are already authenticated."""

    def __init__(
        self,
        uow: AuthUoWPort,
        hasher: PasswordHasherPort,
        logger: LoggerPort,
    ):
        self.uow = uow
        self._hasher = hasher
        self._logger = logger

    async def execute(self, command: PasswordChangeCommand) -> None:
        async with self.uow:
            stored_hash = await self.uow.user_query_repo.find_password_hash(
                command.user_id
            )

            if stored_hash:
                # User already has a local password — they MUST provide the current one correctly.
                if (
                    not command.current_password
                    or not await self._hasher.verify_password(
                        command.current_password, stored_hash
                    )
                ):
                    await self._logger.warning(
                        f"Failed password change attempt for user {command.user_id}"
                    )
                    raise InvalidCredentialsException()

                # Reject if the new password is the same as the existing one.
                # Uses hash comparison instead of raw strings to correctly handle rehash scenarios.
                if await self._hasher.verify_password(
                    command.new_password, stored_hash
                ):
                    raise SamePasswordException()
            # If no stored_hash (OAuth user setting their first local password):
            # skip both checks — there is no current password to verify or compare against.

            # Hash and update the new password
            new_hash = await self._hasher.hash_password(command.new_password)
            await self.uow.user_command_repo.update_password(command.user_id, new_hash)

            # Revoke all sessions
            await self.uow.refresh_token_repo.revoke_all_for_user(command.user_id)

            await self._logger.info(
                f"User {command.user_id} updated their password successfully"
            )
