import dataclasses
from uuid import UUID

from src.core.exceptions import TurnstileVerificationFailed
from src.modules.authentication.application.commands import (
    PasswordResetExecuteCommand,
)
from src.modules.authentication.application.ports import (
    PasswordHasherPort,
)
from src.modules.authentication.application.ports.authentication_unit_of_work import (
    AuthUoWPort,
)
from src.shared.application.ports import (
    AnalyticsEventPort,
    CachePort,
    RateLimiterPort,
    TurnstilePort,
)

"""
Completes the password reset lifecycle.
Takes a secure UUID token generated during the 'Request Reset' phase.
If the token is valid in the ephemeral cache (Redis), it hashes the new password,
commits it to the database, and immediately invalidates the token to prevent reuse.
"""


class PasswordResetExecuteUseCase:
    """Handles validating the token and updating the password."""

    def __init__(
        self,
        uow: AuthUoWPort,
        cache: CachePort,
        hasher: PasswordHasherPort,
        rate_limiter: RateLimiterPort,
        turnstile: TurnstilePort,
        analytics: AnalyticsEventPort,
    ):
        self.uow = uow
        self.cache = cache
        self.hasher = hasher
        self.rate_limiter = rate_limiter
        self.turnstile = turnstile
        self.analytics = analytics

    async def execute(self, command: PasswordResetExecuteCommand) -> bool:
        async with self.uow:
            limit_key = f"{command.client_meta.ip_address if command.client_meta else 'unknown'}:pwd_reset"

            # Turnstile Verification (bypassed if project_id is present via API Key)
            if command.is_challenged and not command.project_id:
                if not command.turnstile_token:
                    await self.rate_limiter.record_failure(limit_key)
                    raise TurnstileVerificationFailed(
                        "CAPTCHA challenge failed or missing"
                    )

                is_valid = await self.turnstile.verify_token(
                    command.turnstile_token,
                    command.client_meta.ip_address if command.client_meta else None,
                )
                if not is_valid:
                    await self.rate_limiter.record_failure(limit_key)
                    raise TurnstileVerificationFailed("CAPTCHA verification failed")

            user_id = await self.cache.get_string(f"pwd_reset:{command.token}")
            if not user_id:
                if command.is_challenged:
                    await self.rate_limiter.record_captcha_success(limit_key)
                await self.rate_limiter.record_failure(limit_key)
                return False

            hashed_password = await self.hasher.hash_password(command.new_password)
            user_id_uuid = UUID(user_id)
            await self.uow.user_command_repo.update_password(
                user_id_uuid, hashed_password
            )

            # Invalidate all active sessions for the user
            await self.uow.refresh_token_repo.revoke_all_for_user(user_id_uuid)

            # Invalidate the token
            await self.cache.delete_key(f"pwd_reset:{command.token}")

        if command.is_challenged:
            await self.rate_limiter.record_success(limit_key)

        self.analytics.record_event(
            project_id=None,  # System wide event or attach to project if we had it in payload
            event_type="PASSWORD_RESET",
            user_id=user_id_uuid,
            metadata=dataclasses.asdict(command.client_meta)
            if command.client_meta
            else None,
        )
        return True
