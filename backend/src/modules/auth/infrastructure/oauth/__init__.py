import importlib
import logging
import pkgutil

from src.modules.auth.infrastructure.oauth import providers

from .registry import oauth_registry

logger = logging.getLogger(__name__)


def _discover_providers():
    """
    Dynamically loads all modules inside the `providers` package.
    This triggers their @oauth_registry.register_provider decorators.
    """
    package = providers
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        try:
            importlib.import_module(f"{package.__name__}.{module_name}")
        except Exception as e:
            logger.error(
                f"[OAuthAutoDiscovery] Failed to load provider '{module_name}': {e}"
            )


_discover_providers()

PROVIDERS = oauth_registry.providers
PARSERS = oauth_registry.parsers
PROVIDER_METADATA = oauth_registry.metadata
oauth = oauth_registry.oauth

__all__ = ["PROVIDERS", "PARSERS", "PROVIDER_METADATA", "oauth"]
