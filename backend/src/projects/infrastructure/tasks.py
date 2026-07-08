import asyncio

from fastapi import FastAPI
from sqlalchemy import select

from src.shared.adapters.logger import AsyncSQLLogger
from src.shared.infrastructure.sql.connection import AsyncSessionLocal
from src.shared.infrastructure.sql.tables import Project

logger = AsyncSQLLogger("ProjectConfigSyncTask")
_sync_task: asyncio.Task | None = None


async def _periodic_project_config_sync(app: FastAPI):
    """Background task: syncs allowed_origins and environments from all projects to app state every 5 seconds."""
    while True:
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Project.id, Project.allowed_origins, Project.environment)
                )
                projects_data = result.all()

                dynamic_origins: set[str] = set()
                project_environments: dict[str, str] = {}

                for project_id, origins, environment in projects_data:
                    project_environments[str(project_id)] = environment
                    if origins:
                        dynamic_origins.update(origins)

                # Atomic update of the global in-memory state
                app.state.dynamic_cors_origins = dynamic_origins
                app.state.project_environments = project_environments
        except asyncio.CancelledError:
            break
        except Exception as e:
            await logger.error(f"Project config sync failed: {e}")

        # Sleep for 5 seconds
        try:
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            break


def start_project_config_sync_task(app: FastAPI):
    """Starts the periodic background task for project config sync."""
    global _sync_task
    if _sync_task is None:
        _sync_task = asyncio.create_task(_periodic_project_config_sync(app))


def stop_project_config_sync_task():
    """Stops the periodic background task for project config sync."""
    global _sync_task
    if _sync_task is not None:
        _sync_task.cancel()
        _sync_task = None
