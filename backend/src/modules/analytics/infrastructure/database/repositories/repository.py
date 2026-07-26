from datetime import date
from typing import cast
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.analytics.domain.entities import AnalyticsEvent
from src.modules.analytics.infrastructure.models import (
    AnalyticsEventModel,
    LiveProjectMetricModel,
    LiveTenantMetricModel,
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
    ) -> dict:
        """
        Returns:
          - metrics: list of daily rows from live_project_metrics
          - totals: accurate period totals queried directly from analytics_events
                    (uses COUNT DISTINCT for active_users to avoid inflation)
        """
        # 1. Time-series from live table (always up-to-date)
        result = await self.session.execute(
            select(LiveProjectMetricModel)
            .where(LiveProjectMetricModel.project_id == project_id)
            .where(LiveProjectMetricModel.date >= start_date)
            .where(LiveProjectMetricModel.date <= end_date)
            .order_by(LiveProjectMetricModel.date)
        )
        db_metrics = result.scalars().all()

        from datetime import timedelta

        metrics_dict = {}
        curr = start_date
        while curr <= end_date:
            metrics_dict[curr] = {
                "date": curr,
                "api_requests": 0,
                "login_successes": 0,
                "login_failures": 0,
                "registrations": 0,
                "active_users": 0,
            }
            curr += timedelta(days=1)

        for m in db_metrics:
            m_date = cast(date, m.date)
            if m_date in metrics_dict:
                metrics_dict[m_date]["api_requests"] = m.api_requests or 0
                metrics_dict[m_date]["login_successes"] = m.login_successes or 0
                metrics_dict[m_date]["login_failures"] = m.login_failures or 0
                metrics_dict[m_date]["registrations"] = m.registrations or 0
                metrics_dict[m_date]["active_users"] = m.active_users or 0

        metrics = list(metrics_dict.values())

        # 2. Accurate totals from raw events for the period
        totals_stmt = (
            select(
                func.count()
                .filter(AnalyticsEventModel.event_type == "API_REQUEST")
                .label("api_requests"),
                func.count()
                .filter(AnalyticsEventModel.event_type == "LOGIN_SUCCESS")
                .label("login_successes"),
                func.count()
                .filter(AnalyticsEventModel.event_type == "LOGIN_FAILED")
                .label("login_failures"),
                func.count()
                .filter(AnalyticsEventModel.event_type == "REGISTRATION")
                .label("registrations"),
                func.count(func.distinct(AnalyticsEventModel.user_id)).label(
                    "active_users"
                ),
            )
            .where(AnalyticsEventModel.project_id == project_id)
            # Exclude the tenant themselves so admin actions don't inflate end-user counts
            .where(
                (AnalyticsEventModel.user_id != AnalyticsEventModel.tenant_id)
                | AnalyticsEventModel.tenant_id.is_(None)
            )
            .where(func.date(AnalyticsEventModel.timestamp) >= start_date)
            .where(func.date(AnalyticsEventModel.timestamp) <= end_date)
        )
        totals_row = (await self.session.execute(totals_stmt)).first()

        totals = {
            "api_requests": int(totals_row.api_requests or 0) if totals_row else 0,
            "login_successes": int(totals_row.login_successes or 0)
            if totals_row
            else 0,
            "login_failures": int(totals_row.login_failures or 0) if totals_row else 0,
            "registrations": int(totals_row.registrations or 0) if totals_row else 0,
            "active_users": int(totals_row.active_users or 0) if totals_row else 0,
        }

        return {"metrics": metrics, "totals": totals}

    async def get_tenant_metrics(
        self, tenant_id: UUID, start_date: date, end_date: date
    ) -> dict:
        """
        Returns:
          - metrics: list of daily rows from live_tenant_metrics
          - totals: accurate period totals queried directly from analytics_events
        """
        # 1. Time-series from live table
        result = await self.session.execute(
            select(LiveTenantMetricModel)
            .where(LiveTenantMetricModel.tenant_id == tenant_id)
            .where(LiveTenantMetricModel.date >= start_date)
            .where(LiveTenantMetricModel.date <= end_date)
            .order_by(LiveTenantMetricModel.date)
        )
        db_metrics = result.scalars().all()

        from datetime import timedelta

        metrics_dict = {}
        curr = start_date
        while curr <= end_date:
            metrics_dict[curr] = {
                "date": curr,
                "api_requests": 0,
                "login_successes": 0,
                "login_failures": 0,
                "registrations": 0,
                "emails_sent": 0,
                "emails_failed": 0,
                "projects_created": 0,
                "active_users": 0,
            }
            curr += timedelta(days=1)

        for m in db_metrics:
            m_date = cast(date, m.date)
            if m_date in metrics_dict:
                metrics_dict[m_date]["api_requests"] = m.api_requests or 0
                metrics_dict[m_date]["login_successes"] = m.login_successes or 0
                metrics_dict[m_date]["login_failures"] = m.login_failures or 0
                metrics_dict[m_date]["registrations"] = m.registrations or 0
                metrics_dict[m_date]["emails_sent"] = getattr(m, "emails_sent", 0) or 0
                metrics_dict[m_date]["emails_failed"] = (
                    getattr(m, "emails_failed", 0) or 0
                )
                metrics_dict[m_date]["projects_created"] = (
                    getattr(m, "projects_created", 0) or 0
                )
                metrics_dict[m_date]["active_users"] = m.active_users or 0

        metrics = list(metrics_dict.values())

        # 2. Accurate totals from raw project events for the period.
        #    Scoped to project_id IS NOT NULL so the tenant's own Cerberus admin
        #    logins (which have tenant_id but no project_id) are excluded.
        totals_stmt = (
            select(
                func.count()
                .filter(AnalyticsEventModel.event_type == "API_REQUEST")
                .label("api_requests"),
                func.count()
                .filter(AnalyticsEventModel.event_type == "LOGIN_SUCCESS")
                .label("login_successes"),
                func.count()
                .filter(AnalyticsEventModel.event_type == "LOGIN_FAILED")
                .label("login_failures"),
                func.count()
                .filter(AnalyticsEventModel.event_type == "REGISTRATION")
                .label("registrations"),
                func.count()
                .filter(AnalyticsEventModel.event_type == "PROJECT_CREATED")
                .label("projects_created"),
                func.count(func.distinct(AnalyticsEventModel.user_id)).label(
                    "active_users"
                ),
            )
            .where(AnalyticsEventModel.tenant_id == tenant_id)
            # Only count events from the tenant's projects, not the tenant's own
            # Cerberus dashboard activity (which has no project_id).
            .where(AnalyticsEventModel.project_id.is_not(None))
            # Exclude the tenant themselves so admin actions don't inflate end-user counts
            .where(AnalyticsEventModel.user_id != tenant_id)
            .where(func.date(AnalyticsEventModel.timestamp) >= start_date)
            .where(func.date(AnalyticsEventModel.timestamp) <= end_date)
        )
        totals_row = (await self.session.execute(totals_stmt)).first()

        totals = {
            "api_requests": int(totals_row.api_requests or 0) if totals_row else 0,
            "login_successes": int(totals_row.login_successes or 0)
            if totals_row
            else 0,
            "login_failures": int(totals_row.login_failures or 0) if totals_row else 0,
            "registrations": int(totals_row.registrations or 0) if totals_row else 0,
            "projects_created": int(totals_row.projects_created or 0)
            if totals_row
            else 0,
            "active_users": int(totals_row.active_users or 0) if totals_row else 0,
        }

        return {"metrics": metrics, "totals": totals}
