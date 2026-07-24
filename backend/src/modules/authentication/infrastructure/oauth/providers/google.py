"""
Module: Google
"""

from src.core.config import get_settings
from src.modules.authentication.domain.entities import OAuthUserInfo
from src.modules.authentication.infrastructure.oauth.registry import oauth_registry
from src.shared.domain.value_objects import EmailAddress, HttpsUrl

client_id, client_secret = get_settings().oauth.get_credentials("google")


@oauth_registry.register_provider(
    name="google",
    display_name="Google",
    scopes=["openid", "email", "profile"],
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=client_id,
    client_secret=client_secret,
    client_kwargs={"scope": "openid email profile"},
)
async def parse_google_user(provider, token) -> OAuthUserInfo:
    google_info = token.get("userinfo")
    if not google_info:
        google_info = await provider.userinfo(token=token)
    google_info = dict(google_info)
    if not google_info.get("email_verified"):
        raise ValueError("Google email not verified")

    return OAuthUserInfo(
        sub=google_info["sub"],
        email=EmailAddress(value=google_info["email"]),
        name=google_info.get("name"),
        picture=HttpsUrl(value=google_info["picture"])
        if google_info.get("picture")
        else None,
        provider="google",
    )
