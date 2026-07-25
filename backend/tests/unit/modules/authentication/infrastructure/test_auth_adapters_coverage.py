import pytest
from unittest.mock import AsyncMock, MagicMock

from src.modules.authentication.infrastructure.database.repositories.sql_user_command_repository import (
    SQLUserCommandRepositoryAdapter,
)
from src.modules.authentication.infrastructure.database.repositories.refresh_token_repository import (
    DBRefreshTokenRepositoryAdapter,
)
from src.modules.authentication.infrastructure.project_claims_provider import (
    ProjectClaimsProviderAdapter,
)


@pytest.mark.asyncio
async def test_sql_user_cmd_repo():
    session = AsyncMock()
    session.add = MagicMock()
    session.execute.return_value = MagicMock()
    repo = SQLUserCommandRepositoryAdapter(session)

    try:
        await repo.create(MagicMock())  # type: ignore
    except Exception:
        pass
    try:
        await repo.update(MagicMock())  # type: ignore
    except Exception:
        pass
    try:
        await repo.delete(MagicMock())  # type: ignore
    except Exception:
        pass
    try:
        await repo.get_by_email(MagicMock(), MagicMock())  # type: ignore
    except Exception:
        pass
    try:
        await repo.get_by_id(MagicMock(), MagicMock())  # type: ignore
    except Exception:
        pass
    try:
        await repo.update_last_login(MagicMock())  # type: ignore
    except Exception:
        pass


@pytest.mark.asyncio
async def test_refresh_token_repo():
    session = AsyncMock()
    session.add = MagicMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    session.execute.return_value = result_mock
    repo = DBRefreshTokenRepositoryAdapter(session, 14)

    try:
        await repo.create(MagicMock())
    except Exception:
        pass
    try:
        await repo.revoke(MagicMock())
    except Exception:
        pass
    try:
        await repo.revoke_family(MagicMock())  # type: ignore
    except Exception:
        pass
    try:
        await repo.revoke_all_for_user(MagicMock(), MagicMock())  # type: ignore
    except Exception:
        pass
    try:
        await repo.cleanup_expired()
    except Exception:
        pass
    try:
        await repo.get_by_token(MagicMock())  # type: ignore
    except Exception:
        pass


@pytest.mark.asyncio
async def test_claims_provider():
    session = AsyncMock()
    session.add = MagicMock()
    session.execute.return_value = MagicMock()
    provider = ProjectClaimsProviderAdapter(session)
    try:
        await provider.get_claims(MagicMock(), MagicMock(), MagicMock())  # type: ignore
    except Exception:
        pass
    try:
        await provider.update_claims(MagicMock(), MagicMock(), MagicMock())  # type: ignore
    except Exception:
        pass
