from uuid import UUID

from src.modules.auth.application.ports import (
    PasswordHasherPort,
    RefreshTokenRepositoryPort,
    UserQueryRepositoryPort,
    UserCommandRepositoryPort,
)
from src.modules.auth.domain.exceptions import (
    InvalidCredentialsException,
    SamePasswordException,
)
from src.shared.application.ports import (
    LoggerPort,
    UoWPort,
)


class ChangePasswordUseCase[SessionType]:
    """Handles updating a user's password when they are already authenticated."""

    def __init__(
        self,
        user_query_repo: UserQueryRepositoryPort[SessionType],
        user_command_repo: UserCommandRepositoryPort[SessionType],
        hasher: PasswordHasherPort,
        logger: LoggerPort,
        refresh_repo: RefreshTokenRepositoryPort[SessionType],
    ):
        self._user_query_repo = user_query_repo
        self._user_command_repo = user_command_repo
        self._hasher = hasher
        self._logger = logger
        self._refresh_repo = refresh_repo

    async def execute(
        self,
        uow: UoWPort[SessionType],
        user_id: UUID,
        current_password: str | None,
        new_password: str,
    ) -> None:
        stored_hash = await self._user_query_repo.find_password_hash(
            uow.session, user_id
        )

        if stored_hash:
            # User already has a local password — they MUST provide the current one correctly.
            if not current_password or not await self._hasher.verify_password(
                current_password, stored_hash
            ):
                await self._logger.warning(
                    f"Failed password change attempt for user {user_id}"
                )
                raise InvalidCredentialsException()

            # Reject if the new password is the same as the existing one.
            # Uses hash comparison instead of raw strings to correctly handle rehash scenarios.
            if await self._hasher.verify_password(new_password, stored_hash):
                raise SamePasswordException()
        # If no stored_hash (OAuth user setting their first local password):
        # skip both checks — there is no current password to verify or compare against.

        # Hash and update the new password
        new_hash = await self._hasher.hash_password(new_password)
        await self._user_command_repo.update_password(uow.session, user_id, new_hash)

        # Revoke all sessions
        await self._refresh_repo.revoke_all_for_user(uow.session, user_id)

        await self._logger.info(f"User {user_id} updated their password successfully")
