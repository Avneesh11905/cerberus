"""
Module: Github
"""

from src.core.config import oauth_settings
from src.modules.auth.infrastructure.oauth.registry import oauth_registry
from src.modules.auth.domain.entities import OAuthUserInfo

client_id, client_secret = oauth_settings.get_credentials("github")


@oauth_registry.register_provider(
    name="github",
    display_name="GitHub",
    scopes=["user:email"],
    access_token_url="https://github.com/login/oauth/access_token",
    access_token_params=None,
    authorize_url="https://github.com/login/oauth/authorize",
    authorize_params=None,
    api_base_url="https://api.github.com/",
    client_id=client_id,
    client_secret=client_secret,
    client_kwargs={"scope": "user:email"},
)
async def parse_github_user(provider, token) -> OAuthUserInfo:
    user_resp = await provider.get("user", token=token)
    github_user = user_resp.json()

    emails = (await provider.get("user/emails", token=token)).json()
    email = next((e for e in emails if e.get("primary")), None)
    if not email or not email.get("verified"):
        raise ValueError("GitHub email is not verified")

    return OAuthUserInfo(
        sub=str(github_user["id"]),
        email=email["email"],
        name=github_user.get("name") or github_user.get("login"),
        picture=github_user.get("avatar_url"),
        provider="github",
    )
