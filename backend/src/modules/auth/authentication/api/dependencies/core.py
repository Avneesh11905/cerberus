from typing import Annotated
from fastapi import Depends
from src.core.container import app_container
from src.modules.projects.application.ports import ProjectQueryRepositoryPort
from src.modules.auth.authentication.application.ports import AccessTokenPort


def get_project_repository() -> ProjectQueryRepositoryPort:
    return app_container.project_query_repo


def get_access_token_adapter() -> AccessTokenPort:
    return app_container.access_token_adapter


ProjectQueryRepositoryDep = Annotated[
    ProjectQueryRepositoryPort, Depends(get_project_repository)
]
AccessTokenAdapterDep = Annotated[AccessTokenPort, Depends(get_access_token_adapter)]
