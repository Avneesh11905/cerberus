from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from sqlalchemy import func, select

from src.core.celery_app import celery_app
from src.core.models import SystemLog
from src.shared.infrastructure.adapters.task_runner import CeleryTaskRunnerAdapter


@pytest.mark.asyncio
async def test_celery_task_runner_adapter():
    adapter = CeleryTaskRunnerAdapter()

    # Create a fake celery task
    mock_task = MagicMock()
    mock_task.delay = MagicMock()

    adapter.add_task(mock_task, "arg1", kwarg1="value1")
    mock_task.delay.assert_called_once_with("arg1", kwarg1="value1")

    # Pass a normal function
    def normal_func():
        pass

    with pytest.raises(ValueError, match="is not a Celery task"):
        adapter.add_task(normal_func)


@pytest.mark.asyncio
async def test_celery_app_config():
    # Verify beat schedule contains our expected tasks
    schedule = celery_app.conf.beat_schedule
    assert "clean-expired-tokens-daily" in schedule
    assert schedule["clean-expired-tokens-daily"]["task"] == "clean_expired_tokens"

    assert "clean-unverified-users-daily" in schedule
    assert (
        schedule["clean-unverified-users-daily"]["task"]
        == "clean_unverified_and_deleted_users"
    )

    assert "clean-old-system-logs-daily" in schedule
    assert schedule["clean-old-system-logs-daily"]["task"] == "clean_old_system_logs"

    assert "aggregate-analytics-daily" in schedule
    assert schedule["aggregate-analytics-daily"]["task"] == "aggregate_analytics"

    assert "purge-old-analytics-events-daily" in schedule
    assert schedule["purge-old-analytics-events-daily"]["task"] == "purge_old_events"


@pytest.mark.asyncio
async def test_clean_old_system_logs(db_session, infra_containers, monkeypatch):
    # Patch AsyncSessionLocal to just return an async context manager yielding db_session
    from contextlib import asynccontextmanager

    from src.core.config import get_settings
    from src.modules.superadmin.infrastructure import tasks as tasks_module

    @asynccontextmanager
    async def get_test_session():
        yield db_session

    monkeypatch.setattr(tasks_module, "AsyncSessionLocal", get_test_session)

    # Insert one old log and one new log
    old_date = datetime.now(timezone.utc) - timedelta(
        days=get_settings().log.RETENTION_DAYS + 5
    )
    new_date = datetime.now(timezone.utc)

    old_log = SystemLog(
        level="INFO",
        source="test",
        message="old log",
        file="test.py",
        line=1,
        created_at=old_date,
    )
    new_log = SystemLog(
        level="INFO",
        source="test",
        message="new log",
        file="test.py",
        line=1,
        created_at=new_date,
    )

    db_session.add_all([old_log, new_log])
    await db_session.commit()

    # Call the async helper directly
    await tasks_module._clean_old_system_logs_async()

    # Verify only the old log was deleted
    logs = (await db_session.execute(select(SystemLog))).scalars().all()
    # It seems the test is adding 2 logs, but maybe others exist.
    # Just verify old_log is gone and new_log is present.
    log_messages = [log.message for log in logs]
    assert "old log" not in log_messages
    assert "new log" in log_messages


@pytest.mark.asyncio
async def test_insert_log_batch_task(db_session, infra_containers, monkeypatch):
    # Patch AsyncSessionLocal to use db_session
    from contextlib import asynccontextmanager

    from src.modules.superadmin.infrastructure import tasks as tasks_module

    @asynccontextmanager
    async def get_test_session():
        yield db_session

    monkeypatch.setattr(tasks_module, "AsyncSessionLocal", get_test_session)

    # Clean table first
    logs_before = (await db_session.execute(select(func.count(SystemLog.id)))).scalar()

    # Create fake requests mimicking Celery Batches Request
    req1 = MagicMock()
    req1.args = ("ERROR", "auth", "login failed", "auth.py", 42)
    req1.kwargs = {}

    req2 = MagicMock()
    req2.args = ()
    req2.kwargs = {
        "level": "INFO",
        "source": "api",
        "message": "ping",
        "filename": "api.py",
        "lineno": 10,
    }

    # Execute batched task's async helper
    await tasks_module._insert_log_batch_task_async([req1, req2])

    # Check db
    logs_after = (await db_session.execute(select(func.count(SystemLog.id)))).scalar()
    assert logs_after == logs_before + 2

    # Verify content
    logs = (
        (
            await db_session.execute(
                select(SystemLog).order_by(SystemLog.created_at.desc()).limit(2)
            )
        )
        .scalars()
        .all()
    )

    messages = [log.message for log in logs]
    assert "login failed" in messages
    assert "ping" in messages
