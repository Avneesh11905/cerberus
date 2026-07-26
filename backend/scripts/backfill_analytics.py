"""
Backfill live metrics tables from raw analytics_events.

Runs the same UPSERT logic as record_analytics_event Celery task but
processes all historical rows already in analytics_events.

Usage (inside the backend container):
  python scripts/backfill_analytics.py
"""

import asyncio
import logging
from datetime import date

from sqlalchemy import text

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_PROJECT_EVENT_MAP = {
    "API_REQUEST": "api_requests",
    "LOGIN_SUCCESS": "login_successes",
    "LOGIN_FAILED": "login_failures",
    "REGISTRATION": "registrations",
    "EMAIL_SENT": "emails_sent",
    "EMAIL_FAILED": "emails_failed",
}

_TENANT_EVENT_MAP = {
    "API_REQUEST": "api_requests",
    "LOGIN_SUCCESS": "login_successes",
    "LOGIN_FAILED": "login_failures",
    "REGISTRATION": "registrations",
    "EMAIL_SENT": "emails_sent",
    "EMAIL_FAILED": "emails_failed",
    "PROJECT_CREATED": "projects_created",
}

_SYSTEM_EVENT_MAP = {
    "TENANT_ONBOARDED": "tenants_onboarded",
    "TENANT_SUSPENDED": "tenant_suspensions",
    "API_KEY_ROTATED": "api_key_rotations",
    "JWT_KEY_ROTATED": "jwt_key_rotations",
}


async def backfill():
    from src.core.database import AsyncSessionLocal  # noqa: PLC0415

    async with AsyncSessionLocal() as session:
        # ── Fetch all raw events ──────────────────────────────────────────────
        logger.info("Fetching all raw analytics events …")
        rows = (
            await session.execute(
                text(
                    """
                    SELECT id, event_type, project_id, tenant_id, user_id, timestamp::date as day
                    FROM analytics_events
                    ORDER BY timestamp
                    """
                )
            )
        ).fetchall()
        logger.info("Fetched %d events", len(rows))

        # ── Resolve project → tenant mapping (batch) ─────────────────────────
        project_ids = {str(r.project_id) for r in rows if r.project_id}
        project_to_tenant: dict[str, str] = {}
        if project_ids:
            res = await session.execute(
                text(
                    "SELECT id::text, tenant_id::text FROM projects WHERE id = ANY(:ids)"
                ),
                {"ids": list(project_ids)},
            )
            for pid, tid in res.fetchall():
                project_to_tenant[pid] = tid
        logger.info("Resolved %d project→tenant mappings", len(project_to_tenant))

        processed = 0
        errors = 0

        for row in rows:
            event_type = row.event_type
            project_id = str(row.project_id) if row.project_id else None
            tenant_id = str(row.tenant_id) if row.tenant_id else None
            day: date = row.day

            resolved_tenant_id = tenant_id or (
                project_to_tenant.get(project_id) if project_id else None
            )

            try:
                # Project-level UPSERT
                if project_id and event_type in _PROJECT_EVENT_MAP:
                    col = _PROJECT_EVENT_MAP[event_type]
                    await session.execute(
                        text(f"""
                        INSERT INTO live_project_metrics
                            (id, project_id, date, {col})
                        VALUES
                            (gen_random_uuid(), :pid, :day, 1)
                        ON CONFLICT (project_id, date) DO UPDATE
                            SET {col} = live_project_metrics.{col} + 1
                        """),
                        {"pid": project_id, "day": day},
                    )

                # Tenant-level UPSERT (only project-scoped events)
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
                            (gen_random_uuid(), :tid, :day, 1)
                        ON CONFLICT (tenant_id, date) DO UPDATE
                            SET {col} = live_tenant_metrics.{col} + 1
                        """),
                        {"tid": resolved_tenant_id, "day": day},
                    )

                # System-level UPSERT
                if event_type in _SYSTEM_EVENT_MAP:
                    col = _SYSTEM_EVENT_MAP[event_type]
                    await session.execute(
                        text(f"""
                        INSERT INTO live_system_metrics
                            (id, date, {col})
                        VALUES
                            (gen_random_uuid(), :day, 1)
                        ON CONFLICT (date) DO UPDATE
                            SET {col} = live_system_metrics.{col} + 1
                        """),
                        {"day": day},
                    )

                processed += 1
            except Exception as exc:  # noqa: BLE001
                logger.warning("Error on event %s/%s: %s", event_type, row.id, exc)
                errors += 1

        await session.commit()
        logger.info("✅ Backfill complete: %d processed, %d errors", processed, errors)

        # ── Print final row counts ────────────────────────────────────────────
        for table in (
            "live_project_metrics",
            "live_tenant_metrics",
            "live_system_metrics",
        ):
            cnt = (
                await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            ).scalar()
            logger.info("  %s: %d rows", table, cnt)


if __name__ == "__main__":
    asyncio.run(backfill())
