"""
Backfill live metrics tables from raw analytics_events.

Runs the same UPSERT logic as record_analytics_event Celery task but
processes all historical rows already in analytics_events.

Usage:
  # Inside the container (recommended — has correct DB hostname):
  docker exec cerberus-cerb-fastapi-1 python scripts/backfill_analytics.py

  # From the host (needs --env-file to supply DB URL):
  uv run scripts/backfill_analytics.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Ensure the backend root (the folder containing 'src/') is on the path so
# that `from src.xxx import yyy` works when running the script directly with
# `python scripts/backfill_analytics.py` or `uv run scripts/backfill_analytics.py`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import date
from src.core.database import AsyncSessionLocal
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

# How many events to commit in a single transaction (tune as needed)
BATCH_SIZE = 500

# All columns for each live metrics table (must match DB schema exactly)
_PROJECT_COLS = [
    "api_requests",
    "login_successes",
    "login_failures",
    "registrations",
    "active_users",
    "emails_sent",
    "emails_failed",
]
_TENANT_COLS = [
    "api_requests",
    "login_successes",
    "login_failures",
    "registrations",
    "active_users",
    "emails_sent",
    "emails_failed",
    "projects_created",
]
_SYSTEM_COLS = [
    "tenants_onboarded",
    "tenant_suspensions",
    "api_key_rotations",
    "jwt_key_rotations",
]


def _project_upsert(col: str) -> str:
    """
    UPSERT into live_project_metrics.
    Inserts a full row of zeros then increments only `col`.
    Uses `excluded` so the target col is always bumped by exactly 1,
    regardless of whether it was a fresh INSERT or an existing row.
    """
    all_cols = ", ".join(_PROJECT_COLS)
    zeros = ", ".join("0" for _ in _PROJECT_COLS)
    return f"""
        INSERT INTO live_project_metrics
            (id, project_id, date, {all_cols})
        VALUES
            (gen_random_uuid(), :pid, :day, {zeros})
        ON CONFLICT (project_id, date) DO UPDATE
            SET {col} = live_project_metrics.{col} + 1
    """


def _tenant_upsert(col: str) -> str:
    all_cols = ", ".join(_TENANT_COLS)
    zeros = ", ".join("0" for _ in _TENANT_COLS)
    return f"""
        INSERT INTO live_tenant_metrics
            (id, tenant_id, date, {all_cols})
        VALUES
            (gen_random_uuid(), :tid, :day, {zeros})
        ON CONFLICT (tenant_id, date) DO UPDATE
            SET {col} = live_tenant_metrics.{col} + 1
    """


def _system_upsert(col: str) -> str:
    all_cols = ", ".join(_SYSTEM_COLS)
    zeros = ", ".join("0" for _ in _SYSTEM_COLS)
    return f"""
        INSERT INTO live_system_metrics
            (id, date, {all_cols})
        VALUES
            (gen_random_uuid(), :day, {zeros})
        ON CONFLICT (date) DO UPDATE
            SET {col} = live_system_metrics.{col} + 1
    """


async def backfill():
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

    # ── Process events in isolated per-event savepoints ───────────────────────
    # Each event is wrapped in a SAVEPOINT so a single failure only rolls back
    # that one event, never the whole batch.
    processed = 0
    errors = 0
    batch_num = 0

    async with AsyncSessionLocal() as session:
        for i, row in enumerate(rows):
            event_type = row.event_type
            project_id = str(row.project_id) if row.project_id else None
            tenant_id = str(row.tenant_id) if row.tenant_id else None
            day: date = row.day

            resolved_tenant_id = tenant_id or (
                project_to_tenant.get(project_id) if project_id else None
            )

            await session.execute(text("SAVEPOINT sp_event"))
            try:
                # Project-level UPSERT
                if project_id and event_type in _PROJECT_EVENT_MAP:
                    col = _PROJECT_EVENT_MAP[event_type]
                    await session.execute(
                        text(_project_upsert(col)),
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
                        text(_tenant_upsert(col)),
                        {"tid": resolved_tenant_id, "day": day},
                    )

                # System-level UPSERT
                if event_type in _SYSTEM_EVENT_MAP:
                    col = _SYSTEM_EVENT_MAP[event_type]
                    await session.execute(
                        text(_system_upsert(col)),
                        {"day": day},
                    )

                await session.execute(text("RELEASE SAVEPOINT sp_event"))
                processed += 1

            except Exception as exc:  # noqa: BLE001
                await session.execute(text("ROLLBACK TO SAVEPOINT sp_event"))
                await session.execute(text("RELEASE SAVEPOINT sp_event"))
                logger.warning("Skipped event %s/%s: %s", event_type, row.id, exc)
                errors += 1

            # Commit in batches to avoid holding a huge transaction in memory
            if (i + 1) % BATCH_SIZE == 0:
                await session.commit()
                batch_num += 1
                logger.info(
                    "  … committed batch %d (%d/%d events, %d errors so far)",
                    batch_num,
                    i + 1,
                    len(rows),
                    errors,
                )

        # Commit any remainder
        await session.commit()
        logger.info("✅ Backfill complete: %d processed, %d skipped", processed, errors)

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
