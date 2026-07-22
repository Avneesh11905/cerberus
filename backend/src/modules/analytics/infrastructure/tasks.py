import asyncio
import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import text

from src.core.celery_app import celery_app
from src.core.database import AsyncSessionLocal
from src.modules.analytics.domain.entities import AnalyticsEvent
from src.shared.domain.enums import EventType

logger = logging.getLogger(__name__)


@celery_app.task(name="record_analytics_event")
def record_analytics_event(
    event_type: str,
    project_id: str | None = None,
    tenant_id: str | None = None,
    user_id: str | None = None,
    metadata: dict[str, Any] | None = None,
):
    event = AnalyticsEvent(
        id=uuid4(),
        event_type=EventType(event_type),
        project_id=UUID(project_id) if project_id else None,
        tenant_id=UUID(tenant_id) if tenant_id else None,
        user_id=UUID(user_id) if user_id else None,
        metadata=metadata,
        timestamp=datetime.now(timezone.utc),
    )

    async def _save():
        from src.shared.infrastructure.adapters import SQLAlchemyUoWAdapter

        async with SQLAlchemyUoWAdapter() as uow:
            repo = uow.analytics_repo
            await repo.save_event(event)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        # If running inside an existing loop (e.g. testing context or newer celery),
        # create a task.
        loop.create_task(_save())
    else:
        loop.run_until_complete(_save())


@celery_app.task(name="aggregate_analytics")
def aggregate_analytics():
    """
    Computes daily rollups for projects and tenants by aggregating raw AnalyticsEvent rows.
    """

    async def _aggregate():
        async with AsyncSessionLocal() as session:
            try:
                # 1. Project-level aggregation
                await session.execute(
                    text("""
                    INSERT INTO daily_project_metrics (id, project_id, date, api_requests, active_users, login_successes, login_failures, registrations)
                    SELECT 
                        gen_random_uuid(),
                        project_id,
                        DATE(timestamp) as date,
                        COUNT(CASE WHEN event_type = 'API_REQUEST' THEN 1 END) as api_requests,
                        COUNT(DISTINCT user_id) as active_users,
                        COUNT(CASE WHEN event_type = 'LOGIN_SUCCESS' THEN 1 END) as login_successes,
                        COUNT(CASE WHEN event_type = 'LOGIN_FAILED' THEN 1 END) as login_failures,
                        COUNT(CASE WHEN event_type = 'REGISTRATION' THEN 1 END) as registrations
                    FROM analytics_events
                    WHERE project_id IS NOT NULL 
                      AND timestamp >= current_date - interval '1 day'
                      AND timestamp < current_date
                    GROUP BY project_id, DATE(timestamp)
                    ON CONFLICT (project_id, date) DO UPDATE 
                    SET api_requests = EXCLUDED.api_requests,
                        active_users = EXCLUDED.active_users,
                        login_successes = EXCLUDED.login_successes,
                        login_failures = EXCLUDED.login_failures,
                        registrations = EXCLUDED.registrations;
                """)
                )

                # 2. Tenant-level aggregation
                await session.execute(
                    text("""
                    INSERT INTO daily_tenant_metrics (id, tenant_id, date, api_requests, active_users, login_successes, login_failures, registrations)
                    SELECT 
                        gen_random_uuid(),
                        tenant_id,
                        DATE(timestamp) as date,
                        COUNT(CASE WHEN event_type = 'API_REQUEST' THEN 1 END) as api_requests,
                        COUNT(DISTINCT tenant_id) as active_users,
                        COUNT(CASE WHEN event_type = 'LOGIN_SUCCESS' THEN 1 END) as login_successes,
                        COUNT(CASE WHEN event_type = 'LOGIN_FAILED' THEN 1 END) as login_failures,
                        COUNT(CASE WHEN event_type = 'REGISTRATION' THEN 1 END) as registrations
                    FROM analytics_events
                    WHERE tenant_id IS NOT NULL 
                      AND timestamp >= current_date - interval '1 day'
                      AND timestamp < current_date
                    GROUP BY tenant_id, DATE(timestamp)
                    ON CONFLICT (tenant_id, date) DO UPDATE 
                    SET api_requests = EXCLUDED.api_requests,
                        active_users = EXCLUDED.active_users,
                        login_successes = EXCLUDED.login_successes,
                        login_failures = EXCLUDED.login_failures,
                        registrations = EXCLUDED.registrations;
                """)
                )

                await session.commit()
                logger.info("Successfully aggregated daily analytics metrics")
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to aggregate analytics: {e}")

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if not loop.is_running():
        loop.run_until_complete(_aggregate())
    else:
        loop.create_task(_aggregate())


@celery_app.task(name="purge_old_events")
def purge_old_events():
    """
    Purges old raw analytics events according to the retention policy.
    - General API events are kept for 90 days.
    - Security-relevant events (e.g. login failures) are kept for 1 year.
    """

    async def _purge():
        async with AsyncSessionLocal() as session:
            try:
                # Purge general events older than 90 days
                result_api = await session.execute(
                    text("""
                    DELETE FROM analytics_events 
                    WHERE event_type = 'API_REQUEST' 
                      AND timestamp < now() - interval '90 days'
                """)
                )

                # Purge security/other events older than 1 year
                result_sec = await session.execute(
                    text("""
                    DELETE FROM analytics_events 
                    WHERE event_type != 'API_REQUEST' 
                      AND timestamp < now() - interval '1 year'
                """)
                )

                await session.commit()
                api_count = getattr(result_api, "rowcount", 0)
                sec_count = getattr(result_sec, "rowcount", 0)
                logger.info(
                    f"Purged {api_count} API events and {sec_count} security events"
                )
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to purge analytics events: {e}")

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if not loop.is_running():
        loop.run_until_complete(_purge())
    else:
        loop.create_task(_purge())
