from src.modules.authentication.application.commands import SessionRefreshCommand
from src.modules.authentication.domain.entities import UserIdentity
from src.modules.authentication.application.ports import (
    AccessTokenPort,
    ClaimsProviderPort,
)
from src.modules.authentication.application.ports.authentication_unit_of_work import (
    AuthUoWPort,
)

"""
Maintains active user sessions securely without requiring re-authentication.
Validates an existing opaque refresh token against the database to ensure it hasn't
expired or been revoked. On success, it implements Refresh Token Rotation by
invalidating the old token and issuing a brand new (Access Token, Refresh Token) pair.
"""


class SessionRefreshUseCase:
    """Handles validating a refresh token and issuing a new access token."""

    def __init__(
        self,
        uow: AuthUoWPort,
        access_token: AccessTokenPort,
        claims_provider: ClaimsProviderPort,
    ):
        self.uow = uow
        self._access_token = access_token
        self._claims_provider = claims_provider

    async def execute(
        self, command: SessionRefreshCommand
    ) -> tuple[str | None, str | None, UserIdentity | None]:
        async with self.uow:
            """
        Validates the refresh token and returns (new_access_token, new_refresh_token).
        Returns (None, None) if the refresh token is invalid.
        """
            (
                user,
                new_refresh_token,
                family_id,
            ) = await self.uow.refresh_token_repo.validate(
                command.refresh_token, client_meta=command.client_meta
            )
            if not user:
                return None, None, None

            custom_claims = await self._claims_provider.get_custom_claims(
                self.uow, user.id
            )
            # Embed the family_id so the middleware can check it against the Redis blacklist
            combined_claims: dict[str, object] = {"family_id": str(family_id)}
            if custom_claims:
                combined_claims.update(custom_claims)
            private_key_override = (
                await self.uow.project_key_repo.get_private_key(user.project_id)
                if user.project_id
                else None
            )
            access_token = self._access_token.create(
                user,
                extra_claims=combined_claims,
                private_key_override=private_key_override,
            )
            return access_token, new_refresh_token, user
