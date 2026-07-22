"""
Shared Infrastructure Container
Instantiates cross-cutting infrastructure adapters exactly once.
"""

import os
from pathlib import Path

from redis.asyncio import Redis

from src.core.config import AppConfig, get_settings
from src.modules.authentication.infrastructure.external.email_sender import (
    AuthEmailSenderAdapter,
)
from src.modules.authentication.infrastructure.project_claims_provider import (
    ProjectClaimsProviderAdapter,
)
from src.modules.authentication.infrastructure.security.access_token import (
    JWTAccessTokenAdapter,
)
from src.modules.authentication.infrastructure.security.oauth_service import (
    OAuthServiceAdapter,
)
from src.modules.authentication.infrastructure.security.password_hasher import (
    Argon2PasswordHasherAdapter,
)
from src.modules.authorization.application.services.role_provisioning import (
    RoleProvisioningService,
)
from src.shared.application.ports import SharedEmailClientPort
from src.shared.infrastructure.adapters import (
    ApiKeyAdapter,
    AsyncSQLLogger,
    CeleryAnalyticsAdapter,
    CeleryTaskRunnerAdapter,
    CloudflareTurnstileAdapter,
    FernetEncryptionAdapter,
    RedisCacheAdapter,
    RedisRateLimiterAdapter,
    ResendEmailClientAdapter,
    RsaKeyAdapter,
    SMTPEmailClientAdapter,
    RedisEventPublisherAdapter,
    RedisEventSubscriberAdapter,
)


class AppContainer:
    def __init__(self, config: AppConfig):
        self.config = config
        # =====================================================================
        # 1. TASK RUNNER
        # =====================================================================
        self.task_runner = CeleryTaskRunnerAdapter()

        # =====================================================================
        # 2. CACHE ADAPTER
        # =====================================================================
        redis_client = Redis.from_url(
            self.config.database.CACHE_URL, decode_responses=True
        )
        self.cache_adapter = RedisCacheAdapter(client=redis_client)
        self.event_publisher_adapter = RedisEventPublisherAdapter(
            redis_client=redis_client
        )
        self.event_subscriber_adapter = RedisEventSubscriberAdapter(
            redis_client=redis_client
        )

        # =====================================================================
        # 3. EMAIL CLIENT
        # =====================================================================
        self.email_client: SharedEmailClientPort
        if self.config.core.ENV == "test":
            self.email_client = SMTPEmailClientAdapter(
                smtp_host=os.environ.get("SMTP_HOST", "localhost"),
                smtp_port=int(os.environ.get("SMTP_PORT", 1025)),
                from_email=self.config.email.FROM,
                reply_to=self.config.email.REPLY_TO,
            )
        else:
            self.email_client = ResendEmailClientAdapter(
                api_key=self.config.email.API_KEY,
                from_email=self.config.email.FROM,
                reply_to=self.config.email.REPLY_TO,
            )

        # =====================================================================
        # 4. ENCRYPTION ADAPTER
        # =====================================================================
        self.encryption_adapter = FernetEncryptionAdapter(
            key=self.config.security.ENCRYPTION_KEY
        )

        # =====================================================================
        # 5. CRYPTO ADAPTERS
        # =====================================================================
        self.api_key_adapter = ApiKeyAdapter()
        self.rsa_key_adapter = RsaKeyAdapter()

        # =====================================================================
        # 6. ANALYTICS & RATE LIMITING
        # =====================================================================
        self.analytics_adapter = CeleryAnalyticsAdapter()
        self.rate_limiter = RedisRateLimiterAdapter(cache=self.cache_adapter)
        self.turnstile_adapter = CloudflareTurnstileAdapter(
            settings=self.config.turnstile,
            is_development=self.config.core.ENV == "development",
        )

        # =====================================================================
        # 7. MODULE SINGLETONS (Repositories & Use Cases)
        # =====================================================================

        # Authentication

        self.access_token_adapter = JWTAccessTokenAdapter(
            private_key=self.config.security.JWT_PRIVATE_KEY,
            public_key=self.config.security.JWT_PUBLIC_KEY,
            lifetime_minutes=self.config.token.ACCESS_TOKEN_LIFETIME_MINUTES,
        )

        self.auth_email_sender = AuthEmailSenderAdapter(
            email_client=self.email_client,
            from_email=self.config.email.FROM,
            templates_dir=Path(__file__).parent.parent / "templates" / "emails",
            logger=AsyncSQLLogger("EmailSender"),
            proj_name="Cerberus",
            template_name=self.config.email.TEMPLATE_NAME,
            frontend_url=self.config.url.FRONTEND_URL,
            task_runner=self.task_runner,
        )

        self.password_hasher = Argon2PasswordHasherAdapter()

        self.role_provisioning: RoleProvisioningService = RoleProvisioningService()

        # Projects CQRS

        self.claims_provider = ProjectClaimsProviderAdapter(
            cache=self.cache_adapter,
        )

        self.oauth_service = OAuthServiceAdapter(
            encryption_adapter=self.encryption_adapter,
        )

        # Superadmin

        # Users

        # Analytics


app_container = AppContainer(get_settings())
