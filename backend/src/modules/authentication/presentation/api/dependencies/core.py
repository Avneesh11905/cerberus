from typing import Annotated

from fastapi import Depends

from src.core.container import app_container
from src.modules.authentication.application.ports import AccessTokenPort


def get_access_token_adapter() -> AccessTokenPort:
    return app_container.access_token_adapter


AccessTokenAdapterDep = Annotated[AccessTokenPort, Depends(get_access_token_adapter)]
