from src.modules.analytics.infrastructure.database.repositories.analytics_uow import (
    SQLAnalyticsUnitOfWork,
)
from src.modules.analytics.application.ports.analytics_unit_of_work import  AnalyticsUoWPort
from typing import Annotated
from fastapi import Depends

async def get_analytics_uow():
    yield SQLAnalyticsUnitOfWork()

GetAnalyticsUoWDep = Annotated[AnalyticsUoWPort, Depends(get_analytics_uow)]