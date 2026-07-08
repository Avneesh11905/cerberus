from authlib.integrations.starlette_client import OAuth

from src.authentication.infrastructure.oauth.registry import oauth_registry


def get_dynamic_oauth_client(provider: str, client_id: str, client_secret: str):
    """
    Creates an ephemeral OAuth client using registered provider metadata.
    Adding a provider module with metadata/parser support enables tenant credentials
    without a database migration or a new branch here.
    """
    metadata = oauth_registry.metadata.get(provider)
    if not metadata:
        raise ValueError(f"Provider {provider} not supported for dynamic config")

    oauth = OAuth()
    config = dict(metadata.authlib_config)
    config["client_id"] = client_id
    config["client_secret"] = client_secret
    oauth.register(name=provider, **config)

    return getattr(oauth, provider)
