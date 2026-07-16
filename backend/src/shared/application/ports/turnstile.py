from typing import Protocol


class TurnstilePort(Protocol):
    """
    Port for verifying Cloudflare Turnstile tokens.
    """

    async def verify_token(self, token: str, ip: str | None = None) -> bool:
        """
        Verify the given Turnstile token with Cloudflare.
        Returns True if successful, False otherwise.
        """
        ...
