from src.core.container import app_container
from src.shared.application.ports import CachePort
from src.modules.projects.application.ports import ProjectQueryRepositoryPort
from src.modules.auth.application.ports import AccessTokenPort


def get_cache_adapter() -> CachePort:
    return app_container.cache_adapter


def get_project_repository() -> ProjectQueryRepositoryPort:
    return app_container.project_query_repo


def get_access_token_adapter() -> AccessTokenPort:
    return app_container.access_token_adapter
