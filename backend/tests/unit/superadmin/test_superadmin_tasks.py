import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.modules.superadmin.infrastructure.tasks import (
    _clean_old_system_logs_async,
    _insert_log_batch_task_async,
)


@pytest.mark.asyncio
@patch("src.modules.superadmin.infrastructure.tasks.AsyncSessionLocal")
async def test_clean_old_system_logs(mock_session_local):
    mock_session = AsyncMock()
    mock_session_local.return_value.__aenter__.return_value = mock_session

    # First batch returns some ids, second returns empty
    mock_result_1 = MagicMock()
    mock_result_1.scalars().all.return_value = [1, 2]

    mock_result_2 = MagicMock()
    mock_result_2.scalars().all.return_value = []

    mock_session.execute.side_effect = [
        mock_result_1,  # Select
        MagicMock(rowcount=2),  # Delete
        mock_result_2,  # Select (empty)
    ]

    await _clean_old_system_logs_async()
    assert mock_session.commit.call_count == 1


@pytest.mark.asyncio
@patch("src.modules.superadmin.infrastructure.tasks.AsyncSessionLocal")
async def test_clean_old_system_logs_exception(mock_session_local):
    mock_session = AsyncMock()
    mock_session_local.return_value.__aenter__.return_value = mock_session
    mock_session.execute.side_effect = Exception("DB error")

    await _clean_old_system_logs_async()
    assert mock_session.commit.call_count == 0


@pytest.mark.asyncio
@patch("src.modules.superadmin.infrastructure.tasks.AsyncSessionLocal")
async def test_insert_log_batch(mock_session_local):
    mock_session = AsyncMock()
    mock_session.add_all = MagicMock()
    mock_session_local.return_value.__aenter__.return_value = mock_session

    req1 = MagicMock()
    req1.args = ["INFO", "src", "msg", "file.py", 10]

    req2 = MagicMock()
    req2.args = []
    req2.kwargs = {
        "level": "ERROR",
        "source": "src",
        "message": "msg",
        "filename": "file.py",
        "lineno": 20,
    }

    await _insert_log_batch_task_async([req1, req2])

    mock_session.add_all.assert_called_once()
    assert mock_session.commit.call_count == 1


@pytest.mark.asyncio
@patch("src.modules.superadmin.infrastructure.tasks.AsyncSessionLocal")
async def test_insert_log_batch_empty(mock_session_local):
    await _insert_log_batch_task_async([])
    mock_session_local.assert_not_called()


@pytest.mark.asyncio
@patch("src.modules.superadmin.infrastructure.tasks.AsyncSessionLocal")
async def test_insert_log_batch_exception(mock_session_local):
    mock_session = AsyncMock()
    mock_session.add_all = MagicMock()
    mock_session_local.return_value.__aenter__.return_value = mock_session
    mock_session.commit.side_effect = Exception("DB error")

    req1 = MagicMock()
    req1.args = ["INFO", "src", "msg", "file.py", 10]

    await _insert_log_batch_task_async([req1])
    assert mock_session.commit.call_count == 1
