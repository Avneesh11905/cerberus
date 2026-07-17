from src.modules.analytics.application.use_cases import (
    GetProjectMetricsUseCase,
    GetTenantMetricsUseCase,
)
from src.core.container import app_container


class AnalyticsUsecaseContainer:
    def __init__(self):
        self.get_project_metrics_usecase = GetProjectMetricsUseCase(
            repository=app_container.analytics_repo
        )
        self.get_tenant_metrics_usecase = GetTenantMetricsUseCase(
            repository=app_container.analytics_repo
        )


analytics_usecase_container = AnalyticsUsecaseContainer()
