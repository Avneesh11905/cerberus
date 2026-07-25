import pytest
import asyncio
from unittest.mock import MagicMock, patch

from src.modules.projects.infrastructure.tasks import (
    _periodic_project_config_sync,
    start_project_config_sync_task,
    stop_project_config_sync_task,
)


@pytest.mark.asyncio
async def test_periodic_project_config_sync():
    app = MagicMock()
    app.state.dynamic_cors_origins = set()
    app.state.project_environments = {}

    with patch(
        "src.modules.projects.infrastructure.tasks.AsyncSessionLocal"
    ) as mock_session_maker:
        mock_session = mock_session_maker.return_value.__aenter__.return_value
        mock_result = MagicMock()
        mock_result.all.return_value = [
            ("project-1", ["https://example.com"], "development"),
            ("project-2", None, "production"),
        ]
        mock_session.execute.return_value = mock_result

        # Create task and cancel it immediately so it runs once and breaks
        task = asyncio.create_task(_periodic_project_config_sync(app))
        await asyncio.sleep(0.1)  # Let it run one iteration
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        assert "https://example.com" in app.state.dynamic_cors_origins
        assert app.state.project_environments["project-1"] == "development"
        assert app.state.project_environments["project-2"] == "production"


@pytest.mark.asyncio
async def test_start_stop_sync_task():
    app = MagicMock()
    start_project_config_sync_task(app)
    from src.modules.projects.infrastructure.tasks import _sync_task

    assert _sync_task is not None

    stop_project_config_sync_task()
    from src.modules.projects.infrastructure.tasks import _sync_task

    assert _sync_task is None
