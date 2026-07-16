"""
Loads OAuth provider credentials (Client IDs and Secrets).
Provides configuration for Google, GitHub, and any future third-party identity providers.
"""

import os

from pydantic_settings import SettingsConfigDict

from .base import _BaseSettings


class OAuthSettings(_BaseSettings):
    """
    Dynamic OAuth Settings loader.
    Allows fetching any OAuth credentials from the environment automatically.
    """

    model_config = SettingsConfigDict(
        **(_BaseSettings.model_config | {"extra": "allow", "case_sensitive": True})
    )

    def get_credentials(self, provider: str) -> tuple[str, str]:
        """
        Retrieves the CLIENT_ID and CLIENT_SECRET for a given provider from the environment.
        Reads directly from os.environ rather than relying on pydantic's extra-field
        capture, which does not reliably populate model_extra for undeclared fields.
        """
        id_key = f"{provider.upper()}_CLIENT_ID"
        secret_key = f"{provider.upper()}_CLIENT_SECRET"

        client_id = os.environ.get(id_key)
        client_secret = os.environ.get(secret_key)

        if not client_id or not client_secret:
            raise ValueError(
                f"Missing OAuth credentials for provider: '{provider}'. "
                f"Please ensure {id_key} and {secret_key} are set in your .env file."
            )

        return client_id, client_secret
