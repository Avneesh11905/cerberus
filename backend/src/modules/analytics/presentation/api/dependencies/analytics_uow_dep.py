from src.modules.analytics.infrastructure.database.repositories.analytics_uow import (
    SQLAnalyticsUnitOfWork,
)


async def get_analytics_uow():
    yield SQLAnalyticsUnitOfWork()
