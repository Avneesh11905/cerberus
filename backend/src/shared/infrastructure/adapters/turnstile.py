import httpx

from src.core.config.security import TurnstileSettings


class CloudflareTurnstileAdapter:
    def __init__(self, settings: TurnstileSettings, is_development: bool):
        self.secret_key = settings.SECRET_KEY
        self.verify_url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
        self.is_development = is_development

    async def verify_token(self, token: str, ip: str | None = None) -> bool:
        if not self.secret_key:
            # If secret key is not configured, bypass in development, otherwise fail.
            return self.is_development

        if self.is_development and token == "dummy-token":  # nosec B105
            return True

        data = {"secret": self.secret_key, "response": token}
        if ip:
            data["remoteip"] = ip

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.verify_url, data=data, timeout=5.0)
                if response.status_code == 200:
                    result = response.json()
                    return result.get("success", False)
                return False
            except httpx.RequestError:
                # Fail closed on network errors
                return False
