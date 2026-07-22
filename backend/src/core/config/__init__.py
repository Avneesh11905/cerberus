from functools import lru_cache

from pydantic_settings import BaseSettings

from .app import CookieSettings, CoreSettings, LogSettings, URLSettings
from .auth import (
    AccountSettings,
    RateLimitSettings,
    TokenSettings,
    VerificationSettings,
)
from .database import DatabaseSettings as DatabaseSettings
from .email import EmailSettings as EmailSettings
from .oauth import OAuthSettings as OAuthSettings
from .security import SecuritySettings, TurnstileSettings


class AppConfig(BaseSettings):
    url: URLSettings = URLSettings()
    core: CoreSettings = CoreSettings()
    oauth: OAuthSettings = OAuthSettings()
    database: DatabaseSettings = DatabaseSettings()  # type: ignore
    email: EmailSettings = EmailSettings()  # type: ignore
    token: TokenSettings = TokenSettings()
    rate_limit: RateLimitSettings = RateLimitSettings()
    verification: VerificationSettings = VerificationSettings()
    log: LogSettings = LogSettings()
    security: SecuritySettings = SecuritySettings()  # type: ignore
    turnstile: TurnstileSettings = TurnstileSettings()
    account: AccountSettings = AccountSettings()

    @property
    def cookie(self) -> CookieSettings:
        return CookieSettings(env=self.core.ENV)


@lru_cache()
def get_settings() -> AppConfig:
    return AppConfig()
