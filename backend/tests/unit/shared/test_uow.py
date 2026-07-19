import pytest
from unittest.mock import AsyncMock

from src.shared.adapters.uow import SQLAlchemyUoWAdapter


@pytest.mark.asyncio
async def test_uow_commit_on_success():
    mock_session = AsyncMock()

    def mock_session_factory():
        return mock_session

    uow = SQLAlchemyUoWAdapter(session_factory=mock_session_factory)

    async with uow:
        # Access session inside context
        assert uow.session == mock_session

    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_not_called()
    mock_session.__aexit__.assert_called_once()


@pytest.mark.asyncio
async def test_uow_rollback_on_exception():
    mock_session = AsyncMock()

    def mock_session_factory():
        return mock_session

    uow = SQLAlchemyUoWAdapter(session_factory=mock_session_factory)

    with pytest.raises(ValueError, match="Test error"):
        async with uow:
            raise ValueError("Test error")

    mock_session.rollback.assert_called_once()
    mock_session.commit.assert_not_called()
    mock_session.__aexit__.assert_called_once()


@pytest.mark.asyncio
async def test_uow_session_accessed_outside_context():
    mock_session = AsyncMock()

    def mock_session_factory():
        return mock_session

    uow = SQLAlchemyUoWAdapter(session_factory=mock_session_factory)

    with pytest.raises(
        RuntimeError, match="UoW.session accessed before entering the context manager."
    ):
        _ = uow.session
