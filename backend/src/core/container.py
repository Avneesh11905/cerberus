"""
Shared Infrastructure Container
Instantiates cross-cutting infrastructure adapters exactly once.
"""

from pathlib import Path
from redis.asyncio import Redis
import os

from src.core.config import (
    core_settings,
    database_settings,
    email_settings,
    security_settings,
    token_settings,
    turnstile_settings,
    url_settings,
)

from src.core.database import AsyncSessionLocal
from src.modules.analytics.adapters import SQLAnalyticsRepositoryAdapter
from src.modules.users.adapters import SQLUserProfileRepositoryAdapter
from src.modules.auth.adapters import (
    Argon2PasswordHasherAdapter,
    AuthEmailServiceAdapter,
    DBRefreshTokenRepositoryAdapter,
    JWTAccessTokenAdapter,
    RoleClaimsProviderAdapter,
    SQLUserQueryRepositoryAdapter,
    SQLUserCommandRepositoryAdapter,
    SQLUserMaintenanceRepositoryAdapter,
)
from src.modules.projects.adapters import (
    SQLProjectCommandRepositoryAdapter,
    SQLProjectQueryRepositoryAdapter,
    SQLProjectUserRepositoryAdapter,
)
from src.modules.superadmin.adapters import (
    SQLSystemAnalyticsRepositoryAdapter,
    SQLSystemLogRepositoryAdapter,
    SQLTenantRepositoryAdapter,
)
from src.shared.application.ports import SharedEmailClientPort
from src.shared.adapters import (
    CeleryAnalyticsAdapter,
    ApiKeyAdapter,
    RedisCacheAdapter,
    ResendEmailClientAdapter,
    FernetEncryptionAdapter,
    AsyncSQLLogger,
    RedisRateLimiterAdapter,
    RsaKeyAdapter,
    CeleryTaskRunnerAdapter,
    CloudflareTurnstileAdapter,
    SMTPEmailClientAdapter,
)


class AppContainer:
    def __init__(self):
        # =====================================================================
        # 1. TASK RUNNER
        # =====================================================================
        self.task_runner = CeleryTaskRunnerAdapter()

        # =====================================================================
        # 2. CACHE ADAPTER
        # =====================================================================
        redis_client = Redis.from_url(
            database_settings.CACHE_URL, decode_responses=True
        )
        self.cache_adapter = RedisCacheAdapter(client=redis_client)

        # =====================================================================
        # 3. EMAIL CLIENT
        # =====================================================================
        self.email_client: SharedEmailClientPort
        if core_settings.ENV == "test":
            self.email_client = SMTPEmailClientAdapter(
                smtp_host=os.environ.get("SMTP_HOST", "localhost"),
                smtp_port=int(os.environ.get("SMTP_PORT", 1025)),
                from_email=email_settings.FROM,
                reply_to=email_settings.REPLY_TO,
            )
        else:
            self.email_client = ResendEmailClientAdapter(
                api_key=email_settings.API_KEY,
                from_email=email_settings.FROM,
                reply_to=email_settings.REPLY_TO,
            )

        # =====================================================================
        # 4. ENCRYPTION ADAPTER
        # =====================================================================
        self.encryption_adapter = FernetEncryptionAdapter(
            key=security_settings.ENCRYPTION_KEY
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
            settings=turnstile_settings,
            is_development=core_settings.ENV == "development",
        )

        # =====================================================================
        # 7. MODULE SINGLETONS (Repositories & Use Cases)
        # =====================================================================

        # Authentication

        self.access_token_adapter = JWTAccessTokenAdapter(
            private_key=security_settings.JWT_PRIVATE_KEY,
            public_key=security_settings.JWT_PUBLIC_KEY,
            lifetime_minutes=token_settings.ACCESS_TOKEN_LIFETIME_MINUTES,
        )

        self.refresh_token_repo = DBRefreshTokenRepositoryAdapter(
            lifetime_days=token_settings.REFRESH_TOKEN_LIFETIME_DAYS,
            cache=self.cache_adapter,
        )

        self.auth_email_sender = AuthEmailServiceAdapter(
            email_client=self.email_client,
            from_email=email_settings.FROM,
            templates_dir=Path(__file__).parent.parent
            / "shared"
            / "templates"
            / "emails",
            logger=AsyncSQLLogger("EmailSender"),
            proj_name="Cerberus",
            template_name=email_settings.TEMPLATE_NAME,
            frontend_url=url_settings.FRONTEND_URL,
            task_runner=self.task_runner,
        )

        self.user_query_repo = SQLUserQueryRepositoryAdapter()
        self.user_command_repo = SQLUserCommandRepositoryAdapter()
        self.user_maintenance_repo = SQLUserMaintenanceRepositoryAdapter()
        self.password_hasher = Argon2PasswordHasherAdapter()

        self.claims_provider = RoleClaimsProviderAdapter(
            cache=self.cache_adapter, user_query_repo=self.user_query_repo
        )

        # Projects CQRS
        self.project_query_repo = SQLProjectQueryRepositoryAdapter(
            encryption_adapter=self.encryption_adapter
        )
        self.project_command_repo = SQLProjectCommandRepositoryAdapter(
            encryption_adapter=self.encryption_adapter
        )
        self.project_user_repo = SQLProjectUserRepositoryAdapter()

        # Superadmin
        self.superadmin_tenant_repo = SQLTenantRepositoryAdapter()
        self.superadmin_log_repo = SQLSystemLogRepositoryAdapter()
        self.superadmin_analytics_repo = SQLSystemAnalyticsRepositoryAdapter()

        # Users
        self.user_profile_repo = SQLUserProfileRepositoryAdapter(
            refresh_repo=self.refresh_token_repo
        )

        # Analytics
        self.analytics_repo = SQLAnalyticsRepositoryAdapter(
            session_factory=AsyncSessionLocal
        )


app_container = AppContainer()
