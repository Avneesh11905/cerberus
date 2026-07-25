import sys
import pytest
from unittest.mock import patch

from src.shared.infrastructure.adapters.logger import AsyncSQLLogger
from src.shared.domain.enums import LogLevel
from src.core.config import get_settings


@pytest.mark.asyncio
async def test_logger_levels():
    logger = AsyncSQLLogger("TestLogger")

    # Test all levels
    await logger.trace("trace")
    await logger.debug("debug")
    await logger.info("info")
    await logger.warning("warning")
    await logger.error("error")
    await logger.fatal("fatal")


@pytest.mark.asyncio
async def test_logger_min_level(mocker):
    # Mock settings to return a high min_level (e.g. ERROR)
    settings = get_settings()
    settings.log.LEVEL = "error"
    logger = AsyncSQLLogger("TestLogger")

    # This should be ignored
    with patch("sys.stderr.write") as mock_write:
        await logger.info("ignored info")
        mock_write.assert_not_called()

        await logger.error("this will run")
        mock_write.assert_called_once()

    settings.log.LEVEL = "info"  # Restore


@pytest.mark.asyncio
async def test_logger_invalid_level(mocker):
    settings = get_settings()
    settings.log.LEVEL = "invalid_level"

    # Should fallback to INFO
    logger = AsyncSQLLogger("TestLogger")
    assert logger._min_level == AsyncSQLLogger._LEVELS[LogLevel.INFO]
    settings.log.LEVEL = "info"  # Restore


@pytest.mark.asyncio
async def test_logger_no_pytest():
    logger = AsyncSQLLogger("TestLogger")

    # Temporarily remove pytest from sys.modules to hit celery task dispatch
    pytest_module = sys.modules.pop("pytest", None)
    try:
        with patch(
            "src.modules.superadmin.infrastructure.tasks.insert_log_batch_task.apply_async"
        ) as mock_task:
            await logger.info("hit celery")
            mock_task.assert_called_once()
            args = mock_task.call_args[1]["args"]
            assert args[0] == LogLevel.INFO.value
            assert args[1] == "TestLogger"
            assert args[2] == "hit celery"
            assert "test_logger.py" in args[3]
    finally:
        if pytest_module:
            sys.modules["pytest"] = pytest_module


@pytest.mark.asyncio
async def test_logger_celery_fallback():
    logger = AsyncSQLLogger("TestLogger")
    pytest_module = sys.modules.pop("pytest", None)
    try:
        with patch(
            "src.modules.superadmin.infrastructure.tasks.insert_log_batch_task.apply_async",
            side_effect=Exception("Task Error"),
        ):
            with patch("sys.stderr.write") as mock_write:
                await logger.info("celery error")
                mock_write.assert_called_once()
                assert (
                    "FALLBACK LOG - SCHEDULING FAILED: Task Error"
                    in mock_write.call_args[0][0]
                )
    finally:
        if pytest_module:
            sys.modules["pytest"] = pytest_module
