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
        # 1. Aggregate Tenant Metrics (Platform Adoption)
        tenant_query = text("""
            SELECT 
                COUNT(DISTINCT tenant_id) as total_tenants,
                COALESCE(SUM(api_requests), 0) as api_requests,
                COALESCE(SUM(registrations), 0) as registrations,
                COALESCE(SUM(login_successes), 0) as login_successes,
                COALESCE(SUM(login_failures), 0) as login_failures,
                COALESCE(SUM(active_users), 0) as active_users
            FROM daily_tenant_metrics
        """)
        tenant_res = await self._session.execute(tenant_query)
        tenant_row = tenant_res.fetchone()

        platform_metrics = PlatformAdoptionMetrics(
            total_tenants=int(tenant_row[0]) if tenant_row and tenant_row[0] else 0,
            api_requests=int(tenant_row[1]) if tenant_row and tenant_row[1] else 0,
            registrations=int(tenant_row[2]) if tenant_row and tenant_row[2] else 0,
            login_successes=int(tenant_row[3]) if tenant_row and tenant_row[3] else 0,
            login_failures=int(tenant_row[4]) if tenant_row and tenant_row[4] else 0,
            active_users=int(tenant_row[5]) if tenant_row and tenant_row[5] else 0,
        )

        # 2. Aggregate Project Metrics (End User Usage)
        project_query = text("""
            SELECT 
                COUNT(DISTINCT project_id) as total_projects,
                COALESCE(SUM(api_requests), 0) as api_requests,
                COALESCE(SUM(registrations), 0) as registrations,
                COALESCE(SUM(login_successes), 0) as login_successes,
                COALESCE(SUM(login_failures), 0) as login_failures,
                COALESCE(SUM(active_users), 0) as active_users
            FROM daily_project_metrics
        """)
        project_res = await self._session.execute(project_query)
        project_row = project_res.fetchone()

        end_user_metrics = EndUserUsageMetrics(
            total_projects=int(project_row[0]) if project_row and project_row[0] else 0,
            api_requests=int(project_row[1]) if project_row and project_row[1] else 0,
            registrations=int(project_row[2]) if project_row and project_row[2] else 0,
            login_successes=int(project_row[3])
            if project_row and project_row[3]
            else 0,
            login_failures=int(project_row[4]) if project_row and project_row[4] else 0,
            active_users=int(project_row[5]) if project_row and project_row[5] else 0,
        )

        return SystemAnalyticsEntity(
            platform_adoption=platform_metrics, end_user_usage=end_user_metrics
        )
