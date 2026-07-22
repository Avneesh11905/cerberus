from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import AsyncSessionLocal


class SQLAlchemyUoWAdapter:
    """Base SQLAlchemy Unit of Work"""

    def __init__(self, session_factory: Callable[[], AsyncSession] = AsyncSessionLocal):
        self.session_factory = session_factory
        self._session: AsyncSession | None = None

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("session accessed before entering context manager")
        return self._session

    async def __aenter__(self):
        self._session = self.session_factory()
        await self._session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, traceback):
        assert self._session is not None  # nosec B101
        try:
            if exc_type is not None:
                await self._session.rollback()
            else:
                await self._session.commit()
        finally:
            await self._session.__aexit__(exc_type, exc_val, traceback)
            self._session = None
