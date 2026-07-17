"""
Completes the password reset lifecycle.
Takes a secure UUID token generated during the 'Request Reset' phase.
If the token is valid in the ephemeral cache (Redis), it hashes the new password,
commits it to the database, and immediately invalidates the token to prevent reuse.
"""

from uuid import UUID

from src.core.exceptions import TurnstileVerificationFailed
from src.modules.auth.application.ports import (
    RefreshTokenRepositoryPort,
    UserCommandRepositoryPort,
    PasswordHasherPort,
)
from src.shared.domain.entities import ClientMetadata
from src.shared.application.ports import (
    AnalyticsEventPort,
    CachePort,
    RateLimiterPort,
    TurnstilePort,
    UoWPort,
)


class ExecutePasswordResetUseCase[SessionType]:
    """Handles validating the token and updating the password."""

    def __init__(
        self,
        user_command_repo: UserCommandRepositoryPort[SessionType],
        cache: CachePort,
        hasher: PasswordHasherPort,
        refresh_repo: RefreshTokenRepositoryPort,
        rate_limiter: RateLimiterPort,
        turnstile: TurnstilePort,
        analytics: AnalyticsEventPort,
    ):
        self.user_command_repo = user_command_repo
        self.cache = cache
        self.hasher = hasher
        self.refresh_repo = refresh_repo
        self.rate_limiter = rate_limiter
        self.turnstile = turnstile
        self.analytics = analytics

    async def execute(
        self,
        uow: UoWPort[SessionType],
        token: str,
        new_password: str,
        client_meta: ClientMetadata | None = None,
        is_challenged: bool = False,
        turnstile_token: str | None = None,
    ) -> bool:
        limit_key = f"{client_meta.ip_address if client_meta else 'unknown'}:pwd_reset"

        if is_challenged:
            if not turnstile_token:
                await self.rate_limiter.record_failure(limit_key)
                raise TurnstileVerificationFailed("CAPTCHA challenge failed or missing")

            is_valid = await self.turnstile.verify_token(
                turnstile_token, client_meta.ip_address if client_meta else None
            )
            if not is_valid:
                await self.rate_limiter.record_failure(limit_key)
                raise TurnstileVerificationFailed("CAPTCHA verification failed")

        user_id = await self.cache.get_string(f"pwd_reset:{token}")
        if not user_id:
            if is_challenged:
                await self.rate_limiter.record_captcha_success(limit_key)
            await self.rate_limiter.record_failure(limit_key)
            return False

        hashed_password = await self.hasher.hash_password(new_password)
        user_id_uuid = UUID(user_id)
        await self.user_command_repo.update_password(
            uow.session, user_id_uuid, hashed_password
        )

        # Invalidate all active sessions for the user
        await self.refresh_repo.revoke_all_for_user(uow.session, user_id_uuid)

        # Invalidate the token
        await self.cache.delete_key(f"pwd_reset:{token}")

        if is_challenged:
            await self.rate_limiter.record_success(limit_key)

        self.analytics.record_event(
            project_id=None,  # System wide event or attach to project if we had it in payload
            event_type="PASSWORD_RESET",
            user_id=user_id_uuid,
            metadata=client_meta.model_dump() if client_meta else None,
        )
        return True
