from typing import Annotated
from fastapi import Depends
from src.core.config import core_settings, token_settings, url_settings
from src.core.container import app_container
from src.shared.adapters import AsyncSQLLogger
from src.modules.auth.authentication.application.use_cases import (
    PasswordResetExecuteUseCase,
    ListActiveSessionsUseCase,
    LocalLoginUseCase,
    SessionLogoutAllUseCase,
    SessionLogoutUseCase,
    ProjectUserOAuthCallbackUseCase,
    SessionRefreshUseCase,
    LocalRegisterUseCase,
    LocalResendVerificationUseCase,
    PasswordResetRequestUseCase,
    SessionRevokeUseCase,
    LocalVerifyEmailUseCase,
    PasswordChangeUseCase,
    TenantOAuthCallbackUseCase,
    ProjectUserOAuthLoginUrlUseCase,
    TenantOAuthLoginUrlUseCase,
    OAuthExchangeUseCase,
)


def get_local_register_usecase() -> LocalRegisterUseCase:

    return LocalRegisterUseCase(
        user_query_repo=app_container.user_query_repo,
        user_command_repo=app_container.user_command_repo,
        hasher=app_container.password_hasher,
        logger=AsyncSQLLogger("RegisterLocalUseCase"),
        email_sender=app_container.auth_email_sender,
        cache=app_container.cache_adapter,
        rate_limiter=app_container.rate_limiter,
        turnstile=app_container.turnstile_adapter,
        analytics=app_container.analytics_adapter,
        role_provisioning=app_container.role_provisioning,
    )


def get_local_login_usecase() -> LocalLoginUseCase:

    return LocalLoginUseCase(
        user_query_repo=app_container.user_query_repo,
        user_command_repo=app_container.user_command_repo,
        user_profile_repo=app_container.user_profile_repo,
        refresh_repo=app_container.refresh_token_repo,
        hasher=app_container.password_hasher,
        logger=AsyncSQLLogger("LoginLocalUseCase"),
        email_sender=app_container.auth_email_sender,
        access_token=app_container.access_token_adapter,
        claims_provider=app_container.claims_provider,
        project_repo=app_container.project_query_repo,
        rate_limiter=app_container.rate_limiter,
        turnstile=app_container.turnstile_adapter,
        analytics=app_container.analytics_adapter,
        core_settings=core_settings,
    )


def get_password_change_usecase() -> PasswordChangeUseCase:

    return PasswordChangeUseCase(
        user_query_repo=app_container.user_query_repo,
        user_command_repo=app_container.user_command_repo,
        hasher=app_container.password_hasher,
        logger=AsyncSQLLogger("PasswordChangeUseCase"),
        refresh_repo=app_container.refresh_token_repo,
    )


def get_project_user_oauth_callback_usecase() -> ProjectUserOAuthCallbackUseCase:
    return ProjectUserOAuthCallbackUseCase(
        user_query_repo=app_container.user_query_repo,
        user_command_repo=app_container.user_command_repo,
        refresh_repo=app_container.refresh_token_repo,
        email_sender=app_container.auth_email_sender,
        access_token=app_container.access_token_adapter,
        claims_provider=app_container.claims_provider,
        project_query_repo=app_container.project_query_repo,
        oauth_service=app_container.oauth_service,
        role_provisioning=app_container.role_provisioning,
    )


def get_tenant_oauth_callback_usecase():
    return TenantOAuthCallbackUseCase(
        user_query_repo=app_container.user_query_repo,
        user_command_repo=app_container.user_command_repo,
        refresh_repo=app_container.refresh_token_repo,
        email_sender=app_container.auth_email_sender,
        access_token=app_container.access_token_adapter,
        claims_provider=app_container.claims_provider,
        oauth_service=app_container.oauth_service,
    )


def get_local_resend_verification_usecase() -> LocalResendVerificationUseCase:

    return LocalResendVerificationUseCase(
        user_query_repo=app_container.user_query_repo,
        logger=AsyncSQLLogger("LocalResendVerificationUseCase"),
        email_sender=app_container.auth_email_sender,
        cache=app_container.cache_adapter,
        rate_limiter=app_container.rate_limiter,
        turnstile=app_container.turnstile_adapter,
    )


def get_local_verify_email_usecase() -> LocalVerifyEmailUseCase:

    return LocalVerifyEmailUseCase(
        user_query_repo=app_container.user_query_repo,
        user_command_repo=app_container.user_command_repo,
        cache=app_container.cache_adapter,
        logger=AsyncSQLLogger("LocalVerifyEmailUseCase"),
        email_sender=app_container.auth_email_sender,
        refresh_repo=app_container.refresh_token_repo,
        rate_limiter=app_container.rate_limiter,
        turnstile=app_container.turnstile_adapter,
        analytics=app_container.analytics_adapter,
    )


def get_password_reset_request_usecase() -> PasswordResetRequestUseCase:

    return PasswordResetRequestUseCase(
        user_query_repo=app_container.user_query_repo,
        project_query_repo=app_container.project_query_repo,
        email_sender=app_container.auth_email_sender,
        cache=app_container.cache_adapter,
        frontend_url=url_settings.FRONTEND_URL,
        rate_limiter=app_container.rate_limiter,
        turnstile=app_container.turnstile_adapter,
    )


def get_password_reset_execute_usecase() -> PasswordResetExecuteUseCase:
    return PasswordResetExecuteUseCase(
        user_command_repo=app_container.user_command_repo,
        hasher=app_container.password_hasher,
        cache=app_container.cache_adapter,
        refresh_repo=app_container.refresh_token_repo,
        rate_limiter=app_container.rate_limiter,
        turnstile=app_container.turnstile_adapter,
        analytics=app_container.analytics_adapter,
    )


def get_session_logout_usecase() -> SessionLogoutUseCase:
    return SessionLogoutUseCase(
        refresh_repo=app_container.refresh_token_repo,
        cache=app_container.cache_adapter,
        token_settings=token_settings,
    )


def get_session_logout_all_usecase() -> SessionLogoutAllUseCase:
    return SessionLogoutAllUseCase(
        refresh_repo=app_container.refresh_token_repo,
        cache=app_container.cache_adapter,
        token_settings=token_settings,
    )


def get_session_refresh_usecase() -> SessionRefreshUseCase:
    return SessionRefreshUseCase(
        refresh_repo=app_container.refresh_token_repo,
        access_token=app_container.access_token_adapter,
        claims_provider=app_container.claims_provider,
        project_repo=app_container.project_query_repo,
    )


def get_list_active_sessions_usecase() -> ListActiveSessionsUseCase:
    return ListActiveSessionsUseCase(
        refresh_repo=app_container.refresh_token_repo,
    )


def get_session_revoke_usecase() -> SessionRevokeUseCase:
    return SessionRevokeUseCase(
        refresh_repo=app_container.refresh_token_repo,
    )


def get_project_user_oauth_login_url_usecase() -> ProjectUserOAuthLoginUrlUseCase:
    return ProjectUserOAuthLoginUrlUseCase(
        project_query_repo=app_container.project_query_repo,
        api_key_adapter=app_container.api_key_adapter,
        oauth_service=app_container.oauth_service,
    )


def get_tenant_oauth_login_url_usecase() -> TenantOAuthLoginUrlUseCase:
    return TenantOAuthLoginUrlUseCase(
        oauth_service=app_container.oauth_service,
    )


def get_oauth_exchange_usecase() -> OAuthExchangeUseCase:
    return OAuthExchangeUseCase(
        cache=app_container.cache_adapter,
        user_profile_repo=app_container.user_profile_repo,
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
