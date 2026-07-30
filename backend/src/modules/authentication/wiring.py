from typing import Annotated

from fastapi import Depends

from src.core.config import get_settings
from src.core.container import app_container
from src.modules.authentication.application.ports.authentication_unit_of_work import (
    AuthUoWPort,
)
from src.modules.authentication.application.use_cases import (
    ListActiveSessionsUseCase,
    LocalLoginUseCase,
    LocalRegisterUseCase,
    LocalResendVerificationUseCase,
    LocalVerifyEmailUseCase,
    OAuthExchangeUseCase,
    PasswordChangeUseCase,
    PasswordResetExecuteUseCase,
    PasswordResetRequestUseCase,
    ProjectUserOAuthCallbackUseCase,
    ProjectUserOAuthLoginUrlUseCase,
    SessionLogoutAllUseCase,
    SessionLogoutUseCase,
    SessionRefreshUseCase,
    SessionRevokeUseCase,
    TenantOAuthCallbackUseCase,
    TenantOAuthLoginUrlUseCase,
)
from src.modules.authentication.presentation.api.dependencies.authentication_uow_dep import (
    get_auth_uow,
)
from src.shared.infrastructure.adapters import AsyncSQLLogger


def get_local_register_usecase(
    uow: Annotated[AuthUoWPort, Depends(get_auth_uow)],
) -> LocalRegisterUseCase:

    return LocalRegisterUseCase(
        uow=uow,
        hasher=app_container.password_hasher,
        logger=AsyncSQLLogger(LocalRegisterUseCase.__module__),
        email_sender=app_container.auth_email_sender,
        cache=app_container.cache_adapter,
        rate_limiter=app_container.rate_limiter,
        turnstile=app_container.turnstile_adapter,
        analytics=app_container.analytics_adapter,
        role_provisioning=app_container.role_provisioning,
    )


def get_local_login_usecase(
    uow: Annotated[AuthUoWPort, Depends(get_auth_uow)],
) -> LocalLoginUseCase:

    return LocalLoginUseCase(
        uow=uow,
        hasher=app_container.password_hasher,
        logger=AsyncSQLLogger(LocalLoginUseCase.__module__),
        email_sender=app_container.auth_email_sender,
        access_token=app_container.access_token_adapter,
        claims_provider=app_container.claims_provider,
        rate_limiter=app_container.rate_limiter,
        turnstile=app_container.turnstile_adapter,
        analytics=app_container.analytics_adapter,
        core_settings=get_settings().core,
    )


def get_password_change_usecase(
    uow: Annotated[AuthUoWPort, Depends(get_auth_uow)],
) -> PasswordChangeUseCase:

    return PasswordChangeUseCase(
        uow=uow,
        hasher=app_container.password_hasher,
        logger=AsyncSQLLogger(PasswordChangeUseCase.__module__),
    )


def get_project_user_oauth_callback_usecase(
    uow: Annotated[AuthUoWPort, Depends(get_auth_uow)],
) -> ProjectUserOAuthCallbackUseCase:
    return ProjectUserOAuthCallbackUseCase(
        uow=uow,
        email_sender=app_container.auth_email_sender,
        access_token=app_container.access_token_adapter,
        claims_provider=app_container.claims_provider,
        oauth_service=app_container.oauth_service,
        role_provisioning=app_container.role_provisioning,
    )


def get_tenant_oauth_callback_usecase(
    uow: Annotated[AuthUoWPort, Depends(get_auth_uow)],
) -> TenantOAuthCallbackUseCase:
    return TenantOAuthCallbackUseCase(
        uow=uow,
        oauth_service=app_container.oauth_service,
        access_token=app_container.access_token_adapter,
        claims_provider=app_container.claims_provider,
        email_sender=app_container.auth_email_sender,
    )


def get_local_resend_verification_usecase(
    uow: Annotated[AuthUoWPort, Depends(get_auth_uow)],
) -> LocalResendVerificationUseCase:

    return LocalResendVerificationUseCase(
        uow=uow,
        logger=AsyncSQLLogger(LocalResendVerificationUseCase.__module__),
        email_sender=app_container.auth_email_sender,
        cache=app_container.cache_adapter,
        rate_limiter=app_container.rate_limiter,
        turnstile=app_container.turnstile_adapter,
    )


def get_local_verify_email_usecase(
    uow: Annotated[AuthUoWPort, Depends(get_auth_uow)],
) -> LocalVerifyEmailUseCase:

    return LocalVerifyEmailUseCase(
        uow=uow,
        cache=app_container.cache_adapter,
        logger=AsyncSQLLogger(LocalVerifyEmailUseCase.__module__),
        email_sender=app_container.auth_email_sender,
        rate_limiter=app_container.rate_limiter,
        turnstile=app_container.turnstile_adapter,
        analytics=app_container.analytics_adapter,
    )


def get_password_reset_request_usecase(
    uow: Annotated[AuthUoWPort, Depends(get_auth_uow)],
) -> PasswordResetRequestUseCase:

    return PasswordResetRequestUseCase(
        uow=uow,
        email_sender=app_container.auth_email_sender,
        cache=app_container.cache_adapter,
        frontend_url=get_settings().url.FRONTEND_URL,
        rate_limiter=app_container.rate_limiter,
        turnstile=app_container.turnstile_adapter,
    )


def get_password_reset_execute_usecase(
    uow: Annotated[AuthUoWPort, Depends(get_auth_uow)],
) -> PasswordResetExecuteUseCase:
    return PasswordResetExecuteUseCase(
        uow=uow,
        hasher=app_container.password_hasher,
        cache=app_container.cache_adapter,
        rate_limiter=app_container.rate_limiter,
        turnstile=app_container.turnstile_adapter,
        analytics=app_container.analytics_adapter,
    )


def get_session_logout_usecase(
    uow: Annotated[AuthUoWPort, Depends(get_auth_uow)],
) -> SessionLogoutUseCase:
    return SessionLogoutUseCase(
        uow=uow,
        cache=app_container.cache_adapter,
        token_settings=get_settings().token,
    )


def get_session_logout_all_usecase(
    uow: Annotated[AuthUoWPort, Depends(get_auth_uow)],
) -> SessionLogoutAllUseCase:
    return SessionLogoutAllUseCase(
        uow=uow,
        cache=app_container.cache_adapter,
        token_settings=get_settings().token,
    )


def get_session_refresh_usecase(
    uow: Annotated[AuthUoWPort, Depends(get_auth_uow)],
) -> SessionRefreshUseCase:
    return SessionRefreshUseCase(
        uow=uow,
        access_token=app_container.access_token_adapter,
        claims_provider=app_container.claims_provider,
    )


def get_list_active_sessions_usecase(
    uow: Annotated[AuthUoWPort, Depends(get_auth_uow)],
) -> ListActiveSessionsUseCase:
    return ListActiveSessionsUseCase(uow=uow)


def get_session_revoke_usecase(
    uow: Annotated[AuthUoWPort, Depends(get_auth_uow)],
) -> SessionRevokeUseCase:
    return SessionRevokeUseCase(uow=uow)


def get_project_user_oauth_login_url_usecase(
    uow: Annotated[AuthUoWPort, Depends(get_auth_uow)],
) -> ProjectUserOAuthLoginUrlUseCase:
    return ProjectUserOAuthLoginUrlUseCase(
        uow=uow,
        api_key_adapter=app_container.api_key_adapter,
        oauth_service=app_container.oauth_service,
    )


def get_tenant_oauth_login_url_usecase(
    uow: Annotated[AuthUoWPort, Depends(get_auth_uow)],
) -> TenantOAuthLoginUrlUseCase:
    return TenantOAuthLoginUrlUseCase(
        uow=uow,
        oauth_service=app_container.oauth_service,
    )


def get_oauth_exchange_usecase(
    uow: Annotated[AuthUoWPort, Depends(get_auth_uow)],
) -> OAuthExchangeUseCase:
    return OAuthExchangeUseCase(
        uow=uow,
        cache=app_container.cache_adapter,
    )


LocalRegisterUseCaseDep = Annotated[
    LocalRegisterUseCase, Depends(get_local_register_usecase)
]
LocalLoginUseCaseDep = Annotated[LocalLoginUseCase, Depends(get_local_login_usecase)]
PasswordChangeUseCaseDep = Annotated[
    PasswordChangeUseCase, Depends(get_password_change_usecase)
]
ProjectUserOAuthCallbackUseCaseDep = Annotated[
    ProjectUserOAuthCallbackUseCase, Depends(get_project_user_oauth_callback_usecase)
]
ProjectUserOAuthLoginUrlUseCaseDep = Annotated[
    ProjectUserOAuthLoginUrlUseCase, Depends(get_project_user_oauth_login_url_usecase)
]
TenantOAuthLoginUrlUseCaseDep = Annotated[
    TenantOAuthLoginUrlUseCase, Depends(get_tenant_oauth_login_url_usecase)
]
TenantOAuthCallbackUseCaseDep = Annotated[
    TenantOAuthCallbackUseCase, Depends(get_tenant_oauth_callback_usecase)
]
LocalResendVerificationUseCaseDep = Annotated[
    LocalResendVerificationUseCase,
    Depends(get_local_resend_verification_usecase),
]
LocalVerifyEmailUseCaseDep = Annotated[
    LocalVerifyEmailUseCase, Depends(get_local_verify_email_usecase)
]
PasswordResetRequestUseCaseDep = Annotated[
    PasswordResetRequestUseCase, Depends(get_password_reset_request_usecase)
]
PasswordResetExecuteUseCaseDep = Annotated[
    PasswordResetExecuteUseCase, Depends(get_password_reset_execute_usecase)
]
SessionSessionLogoutUseCaseDep = Annotated[
    SessionLogoutUseCase, Depends(get_session_logout_usecase)
]
SessionSessionLogoutAllUseCaseDep = Annotated[
    SessionLogoutAllUseCase, Depends(get_session_logout_all_usecase)
]
SessionRefreshUseCaseDep = Annotated[
    SessionRefreshUseCase, Depends(get_session_refresh_usecase)
]
ListActiveSessionsUseCaseDep = Annotated[
    ListActiveSessionsUseCase, Depends(get_list_active_sessions_usecase)
]
SessionRevokeUseCaseDep = Annotated[
    SessionRevokeUseCase, Depends(get_session_revoke_usecase)
]
OAuthExchangeUseCaseDep = Annotated[
    OAuthExchangeUseCase, Depends(get_oauth_exchange_usecase)
]
