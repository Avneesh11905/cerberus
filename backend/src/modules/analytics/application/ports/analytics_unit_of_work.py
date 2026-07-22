from typing import Protocol

from src.modules.analytics.application.ports.analytics_repository import (
    AnalyticsRepositoryPort,
)


class AnalyticsUoWPort[SessionType](Protocol):
    @property
    def session(self) -> SessionType: ...
    @property
    def analytics_repo(self) -> AnalyticsRepositoryPort: ...
    async def __aenter__(self): ...
    async def __aexit__(self, exc_type, exc_val, traceback): ...
