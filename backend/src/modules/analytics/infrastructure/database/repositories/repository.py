from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.analytics.domain.entities import AnalyticsEvent
from src.modules.analytics.infrastructure.models import (
    AnalyticsEventModel,
    DailyProjectMetricModel,
    DailyTenantMetricModel,
)


class SQLAnalyticsRepositoryAdapter:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_event(self, event: AnalyticsEvent) -> None:
        model = AnalyticsEventModel(
            id=event.id,
            project_id=event.project_id,
            tenant_id=event.tenant_id,
            user_id=event.user_id,
            event_type=event.event_type.value,
            timestamp=event.timestamp,
            metadata_payload=event.metadata,
        )
        self.session.add(model)
        await self.session.commit()

    async def get_project_metrics(
        self, project_id: UUID, start_date: date, end_date: date
    ) -> list:
        result = await self.session.execute(
            select(DailyProjectMetricModel)
            .where(DailyProjectMetricModel.project_id == project_id)
            .where(DailyProjectMetricModel.date >= start_date)
            .where(DailyProjectMetricModel.date <= end_date)
            .order_by(DailyProjectMetricModel.date)
        )
        return list(result.scalars().all())

    async def get_tenant_metrics(
        self, tenant_id: UUID, start_date: date, end_date: date
    ) -> list:
        result = await self.session.execute(
            select(DailyTenantMetricModel)
            .where(DailyTenantMetricModel.tenant_id == tenant_id)
            .where(DailyTenantMetricModel.date >= start_date)
            .where(DailyTenantMetricModel.date <= end_date)
            .order_by(DailyTenantMetricModel.date)
        )
        return list(result.scalars().all())
