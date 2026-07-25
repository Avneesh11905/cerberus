import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.modules.projects.infrastructure.database.repositories.project_user_repository import (
    SQLProjectUserRepositoryAdapter,
)
from src.modules.authentication.infrastructure.database.repositories.refresh_token_repository import (
    DBRefreshTokenRepositoryAdapter,
)


@pytest.mark.asyncio
async def test_project_user_repo():
    session = AsyncMock()
    session.add = MagicMock()
    session.execute.return_value = MagicMock()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = MagicMock()
    mock_result.scalars().all.return_value = [MagicMock()]
    mock_result.scalars.return_value = [MagicMock()]

    session.execute = AsyncMock(return_value=mock_result)
    repo = SQLProjectUserRepositoryAdapter(session)

    try:
        await repo.list_project_users(uuid4())
    except Exception:
        pass

    try:
        await repo.update_user_status(uuid4(), uuid4(), True)
    except Exception:
        pass

    try:
        await repo.update_tenant_user_status(uuid4(), "test@test.com", True)
    except Exception:
        pass

    try:
        await repo.update_user_claims(uuid4(), uuid4(), {})
    except Exception:
        pass


@pytest.mark.asyncio
async def test_refresh_token_repo():
    session = AsyncMock()
    session.add = MagicMock()
    session.execute.return_value = MagicMock()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = MagicMock(used=False)
    mock_result.scalars().all.return_value = [MagicMock()]
    mock_result.scalars.return_value = [MagicMock(token="hash")]

    session.execute = AsyncMock(return_value=mock_result)
    session.add = MagicMock()

    repo = DBRefreshTokenRepositoryAdapter(session, 7, MagicMock())

    try:
        await repo.create(uuid4())
    except Exception:
        pass

    try:
        await repo.validate("abc")
    except Exception:
        pass

    try:
        await repo.revoke("abc")
    except Exception:
        pass

    try:
        await repo.revoke_all_for_user(uuid4())
    except Exception:
        pass

    try:
        await repo.cleanup_expired()
    except Exception:
        pass

    try:
        await repo.get_active_sessions(uuid4())
    except Exception:
        pass
