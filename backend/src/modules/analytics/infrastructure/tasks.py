import asyncio
import logging
from datetime import datetime, date, UTC
from uuid import UUID, uuid4
from pydantic import JsonValue

from sqlalchemy import text

from src.core.celery_app import celery_app
from src.core.database import AsyncSessionLocal
from src.modules.analytics.domain.entities import AnalyticsEvent
from src.shared.domain.enums import EventType

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Event → column mapping for live_project_metrics
# ---------------------------------------------------------------------------
_PROJECT_EVENT_MAP: dict[str, str] = {
    "API_REQUEST": "api_requests",
    "LOGIN_SUCCESS": "login_successes",
    "LOGIN_FAILED": "login_failures",
    "REGISTRATION": "registrations",
    "EMAIL_SENT": "emails_sent",
    "EMAIL_FAILED": "emails_failed",
}

# ---------------------------------------------------------------------------
# Event → column mapping for live_tenant_metrics.
#
# These are ONLY populated when the event has BOTH a project_id AND a
# tenant_id (resolved from the project). This ensures tenant analytics show
# project-level activity — not the tenant's own Cerberus admin logins.
# ---------------------------------------------------------------------------
_TENANT_EVENT_MAP: dict[str, str] = {
    "API_REQUEST": "api_requests",
    "LOGIN_SUCCESS": "login_successes",
    "LOGIN_FAILED": "login_failures",
    "REGISTRATION": "registrations",
    "EMAIL_SENT": "emails_sent",
    "EMAIL_FAILED": "emails_failed",
    "PROJECT_CREATED": "projects_created",
}

# ---------------------------------------------------------------------------
# Events that update live_system_metrics
# ---------------------------------------------------------------------------
_SYSTEM_EVENT_MAP: dict[str, str] = {
    "TENANT_ONBOARDED": "tenants_onboarded",
    "TENANT_SUSPENDED": "tenant_suspensions",
    "API_KEY_ROTATED": "api_key_rotations",
    "JWT_KEY_ROTATED": "jwt_key_rotations",
}

_SYSTEM_SSE_EVENTS = set(_SYSTEM_EVENT_MAP.keys()) | {
    "PROJECT_CREATED",
    "REGISTRATION",
    "LOGIN_SUCCESS",
    "LOGIN_FAILED",
    "API_REQUEST",
    "EMAIL_SENT",
    "EMAIL_FAILED",
}


async def _resolve_tenant_id_for_project(session, project_id: str) -> str | None:
    """
    Look up the tenant_id that owns the given project.
    Returns None if the project doesn't exist.
    This is a lightweight indexed lookup — projects.id is the PK.
    """
    row = await session.execute(
        text("SELECT tenant_id FROM projects WHERE id = :pid LIMIT 1"),
        {"pid": project_id},
    )
    result = row.fetchone()
    return str(result[0]) if result and result[0] else None


@celery_app.task(name="record_analytics_event")
def record_analytics_event(
    event_type: str,
    project_id: str | None = None,
    tenant_id: str | None = None,
    user_id: str | None = None,
    metadata: dict[str, JsonValue] | None = None,
):
    event = AnalyticsEvent(
        id=uuid4(),
        event_type=EventType(event_type),
        project_id=UUID(project_id) if project_id else None,
        tenant_id=UUID(tenant_id) if tenant_id else None,
        user_id=UUID(user_id) if user_id else None,
        metadata=metadata,
        timestamp=datetime.now(UTC),
    )

    async def _save():
        from src.modules.analytics.infrastructure.database.repositories.analytics_uow import (
            SQLAnalyticsUnitOfWork,
        )

        async with SQLAnalyticsUnitOfWork() as uow:
            await uow.analytics_repo.save_event(event)

        today = date.today()

        async with AsyncSessionLocal() as session:
            try:
                # ── Resolve tenant_id from project (if not already provided) ───────
                # Project-scoped events emitted by use cases may not carry tenant_id.
                # We do a single indexed lookup so every project event can be rolled
                # up under the correct tenant without changing every call site.
                resolved_tenant_id: str | None = None
                if project_id:
                    resolved_tenant_id = (
                        tenant_id  # use caller-provided one if present
                        or await _resolve_tenant_id_for_project(session, project_id)
                    )

                # ── Project-level UPSERT ───────────────────────────────────────────
                if project_id and event_type in _PROJECT_EVENT_MAP:
                    col = _PROJECT_EVENT_MAP[event_type]
                    await session.execute(
                        text(f"""
                        INSERT INTO live_project_metrics
                            (id, project_id, date, {col})
                        VALUES
                            (gen_random_uuid(), :pid, :today, 1)
                        ON CONFLICT (project_id, date) DO UPDATE
                            SET {col} = live_project_metrics.{col} + 1
                        """),
                        {"pid": project_id, "today": today},
                    )

                # ── Tenant-level UPSERT ────────────────────────────────────────────
                # IMPORTANT: only fired when we have BOTH project_id AND tenant_id.
                # This keeps tenant analytics scoped to project activity exclusively.
                # A pure tenant admin login (tenant_id set, project_id NOT set) will
                # NOT reach this block — deliberately.
                if (
                    project_id
                    and resolved_tenant_id
                    and event_type in _TENANT_EVENT_MAP
                ):
                    col = _TENANT_EVENT_MAP[event_type]
                    await session.execute(
                        text(f"""
                        INSERT INTO live_tenant_metrics
                            (id, tenant_id, date, {col})
                        VALUES
                            (gen_random_uuid(), :tid, :today, 1)
                        ON CONFLICT (tenant_id, date) DO UPDATE
                            SET {col} = live_tenant_metrics.{col} + 1
                        """),
                        {"tid": resolved_tenant_id, "today": today},
                    )

                # ── System-level UPSERT ────────────────────────────────────────────
                if event_type in _SYSTEM_EVENT_MAP:
                    col = _SYSTEM_EVENT_MAP[event_type]
                    await session.execute(
                        text(f"""
                        INSERT INTO live_system_metrics
                            (id, date, {col})
                        VALUES
                            (gen_random_uuid(), :today, 1)
                        ON CONFLICT (date) DO UPDATE
                            SET {col} = live_system_metrics.{col} + 1
                        """),
                        {"today": today},
                    )

                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(
                    f"Failed to UPSERT live metrics for event {event_type}: {e}"
                )

        # ── Broadcast SSE via Redis Pub/Sub ───────────────────────────────────────
        from src.core.container import app_container

        publisher = app_container.event_publisher_adapter
        event_data = {
            "event_type": event_type,
            "project_id": project_id,
            "tenant_id": resolved_tenant_id if project_id else tenant_id,
            "user_id": user_id,
            "metadata": metadata,
            "timestamp": event.timestamp.isoformat(),
        }

        if project_id:
            await publisher.publish(f"analytics:project:{project_id}", event_data)
        if project_id and resolved_tenant_id:
            # Fan-out to tenant channel — only for project events
            await publisher.publish(
                f"analytics:tenant:{resolved_tenant_id}", event_data
            )
        if event_type in _SYSTEM_SSE_EVENTS:
            await publisher.publish("analytics:system:global", event_data)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        loop.create_task(_save())
    else:
        loop.run_until_complete(_save())


@celery_app.task(name="purge_old_events")
def purge_old_events():
    """
    Purges old raw analytics events according to the retention policy.
    - General API events are kept for 90 days.
    - Security-relevant events (e.g. login failures) are kept for 1 year.
    The live_*_metrics aggregate tables are NOT purged — they are permanent records.
    """

    async def _purge():
        async with AsyncSessionLocal() as session:
            try:
                result_api = await session.execute(
                    text("""
                    DELETE FROM analytics_events
                    WHERE event_type = 'API_REQUEST'
                      AND timestamp < now() - interval '90 days'
                """)
                )
                result_sec = await session.execute(
                    text("""
                    DELETE FROM analytics_events
                    WHERE event_type != 'API_REQUEST'
                      AND timestamp < now() - interval '1 year'
                """)
                )
                await session.commit()
                logger.info(
                    f"Purged {getattr(result_api, 'rowcount', 0)} API events and "
                    f"{getattr(result_sec, 'rowcount', 0)} security events"
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
