from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.superadmin.application.ports import (
    SystemAnalyticsRepositoryPort,
)
from src.modules.superadmin.domain.entities import (
    EndUserUsageMetrics,
    PlatformAdoptionMetrics,
    SystemAnalyticsEntity,
)


class SQLSystemAnalyticsRepositoryAdapter(SystemAnalyticsRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_global_analytics(
        self,
    ) -> SystemAnalyticsEntity:
        # ── 1. Platform Adoption (Tenant-level) ──────────────────────────────
        #
        # These metrics describe how tenants (customers of Cerberus) are using
        # the platform itself.  All events here come from tenant-scoped actions
        # (dashboard logins, key rotations, project creation, etc.) which have
        # tenant_id set but NO project_id.
        #
        # We query analytics_events directly because live_project_metrics only
        # covers events that are scoped to a project_id, which excludes all
        # tenant-level activity.

        total_tenants_query = text("SELECT COUNT(id) FROM tenants")
        total_tenants = (await self._session.execute(total_tenants_query)).scalar() or 0

        total_projects_query = text("SELECT COUNT(id) FROM projects")
        total_projects = (
            await self._session.execute(total_projects_query)
        ).scalar() or 0

        # All auth/API events platform-wide (tenant logins + project-user events)
        platform_events_query = text("""
            SELECT
                COUNT(*) FILTER (WHERE event_type = 'API_REQUEST')       AS api_requests,
                COUNT(*) FILTER (WHERE event_type = 'LOGIN_SUCCESS')      AS login_successes,
                COUNT(*) FILTER (WHERE event_type = 'LOGIN_FAILED')       AS login_failures,
                COUNT(*) FILTER (WHERE event_type = 'REGISTRATION')       AS registrations,
                COUNT(*) FILTER (WHERE event_type = 'EMAIL_SENT')         AS emails_sent,
                COUNT(*) FILTER (WHERE event_type = 'PROJECT_CREATED')    AS projects_created
            FROM analytics_events
        """)
        pe_res = await self._session.execute(platform_events_query)
        pe_row = pe_res.fetchone()

        # Active tenants = distinct tenant_id with any event in the last 30 days
        active_tenants_query = text("""
            SELECT COUNT(DISTINCT tenant_id)
            FROM analytics_events
            WHERE tenant_id IS NOT NULL
              AND timestamp >= now() - interval '30 days'
        """)
        active_tenants = (
            await self._session.execute(active_tenants_query)
        ).scalar() or 0

        platform_metrics = PlatformAdoptionMetrics(
            total_tenants=int(total_tenants),
            api_requests=int(pe_row.api_requests or 0) if pe_row else 0,
            registrations=int(pe_row.registrations or 0) if pe_row else 0,
            login_successes=int(pe_row.login_successes or 0) if pe_row else 0,
            login_failures=int(pe_row.login_failures or 0) if pe_row else 0,
            active_users=int(active_tenants),
        )

        # ── 2. End-User Usage (Project-scoped) ───────────────────────────────
        #
        # These metrics describe end-user activity inside tenant projects.
        # Events here have a project_id set.

        # Total registered users across all projects
        total_users_query = text("""
            SELECT COUNT(DISTINCT user_id)
            FROM analytics_events
            WHERE event_type = 'REGISTRATION'
              AND project_id IS NOT NULL
        """)
        total_users = (await self._session.execute(total_users_query)).scalar() or 0

        # Project-scoped auth/API events
        project_events_query = text("""
            SELECT
                COUNT(*) FILTER (WHERE event_type = 'API_REQUEST')    AS api_requests,
                COUNT(*) FILTER (WHERE event_type = 'LOGIN_SUCCESS')   AS login_successes,
                COUNT(*) FILTER (WHERE event_type = 'LOGIN_FAILED')    AS login_failures
            FROM analytics_events
            WHERE project_id IS NOT NULL
        """)
        proj_res = await self._session.execute(project_events_query)
        proj_row = proj_res.fetchone()

        # Active end-users in the last 30 days (exclude the tenant themselves)
        project_active_users_query = text("""
            SELECT COUNT(DISTINCT user_id)
            FROM analytics_events
            WHERE project_id IS NOT NULL
              AND user_id IS NOT NULL
              AND (user_id != tenant_id OR tenant_id IS NULL)
              AND timestamp >= now() - interval '30 days'
        """)
        project_active_users = (
            await self._session.execute(project_active_users_query)
        ).scalar() or 0

        end_user_metrics = EndUserUsageMetrics(
            total_projects=int(total_projects),
            api_requests=int(proj_row.api_requests or 0) if proj_row else 0,
            registrations=int(total_users),
            login_successes=int(proj_row.login_successes or 0) if proj_row else 0,
            login_failures=int(proj_row.login_failures or 0) if proj_row else 0,
            active_users=int(project_active_users),
        )

        return SystemAnalyticsEntity(
            platform_adoption=platform_metrics, end_user_usage=end_user_metrics
        )

    async def get_global_timeseries(self, days: int = 30) -> list[dict]:
        from datetime import date, timedelta

        start_date = date.today() - timedelta(days=days)

        # Aggregate ALL analytics_events by day (not filtered by project_id).
        # This gives the superadmin a true picture of all platform activity —
        # both tenant logins and end-user project activity — over time.
        query = text("""
            SELECT
                timestamp::date                                                   AS date,
                COUNT(*) FILTER (WHERE event_type = 'API_REQUEST')               AS api_requests,
                COUNT(DISTINCT user_id) FILTER (WHERE timestamp >= now() - interval '30 days')
                                                                                  AS active_users,
                COUNT(*) FILTER (WHERE event_type = 'LOGIN_SUCCESS')              AS login_successes,
                COUNT(*) FILTER (WHERE event_type = 'LOGIN_FAILED')               AS login_failures,
                COUNT(*) FILTER (WHERE event_type = 'REGISTRATION')               AS registrations,
                COUNT(*) FILTER (WHERE event_type = 'EMAIL_SENT')                 AS emails_sent,
                COUNT(*) FILTER (WHERE event_type = 'EMAIL_FAILED')               AS emails_failed,
                COUNT(*) FILTER (WHERE event_type = 'PROJECT_CREATED')            AS projects_created
            FROM analytics_events
            WHERE timestamp::date >= :start_date
            GROUP BY timestamp::date
            ORDER BY timestamp::date
        """)
        res = await self._session.execute(query, {"start_date": start_date})
        rows = res.fetchall()

        # Pre-fill every day with zeros so the chart always has a full 30-day x-axis
        metrics_dict: dict[date, dict] = {}
        curr = start_date
        while curr <= date.today():
            metrics_dict[curr] = {
                "date": curr.isoformat(),
                "api_requests": 0,
                "active_users": 0,
                "login_successes": 0,
                "login_failures": 0,
                "registrations": 0,
                "emails_sent": 0,
                "emails_failed": 0,
                "projects_created": 0,
            }
            curr += timedelta(days=1)

        for row in rows:
            if row.date in metrics_dict:
                metrics_dict[row.date]["api_requests"] = int(row.api_requests or 0)
                metrics_dict[row.date]["active_users"] = int(row.active_users or 0)
                metrics_dict[row.date]["login_successes"] = int(
                    row.login_successes or 0
                )
                metrics_dict[row.date]["login_failures"] = int(row.login_failures or 0)
                metrics_dict[row.date]["registrations"] = int(row.registrations or 0)
                metrics_dict[row.date]["emails_sent"] = int(row.emails_sent or 0)
                metrics_dict[row.date]["emails_failed"] = int(row.emails_failed or 0)
                metrics_dict[row.date]["projects_created"] = int(
                    row.projects_created or 0
                )

        return list(metrics_dict.values())
