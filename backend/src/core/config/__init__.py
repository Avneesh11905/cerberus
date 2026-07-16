from .app import CookieSettings, CoreSettings, LogSettings, URLSettings
from .auth import (
    AccountSettings,
    RateLimitSettings,
    TokenSettings,
    VerificationSettings,
)
from .database import DatabaseSettings
from .email import EmailSettings
from .oauth import OAuthSettings
from .security import SecuritySettings, TurnstileSettings

url_settings = URLSettings()  # type: ignore
core_settings = CoreSettings()  # type: ignore
oauth_settings = OAuthSettings()  # type: ignore
database_settings = DatabaseSettings()  # type: ignore
email_settings = EmailSettings()  # type: ignore
token_settings = TokenSettings()  # type: ignore
rate_limit_settings = RateLimitSettings()  # type: ignore
verification_settings = VerificationSettings()  # type: ignore
log_settings = LogSettings()  # type: ignore
security_settings = SecuritySettings()  # type: ignore
turnstile_settings = TurnstileSettings()  # type: ignore
account_settings = AccountSettings()  # type: ignore
cookie_settings = CookieSettings(env=core_settings.ENV)
