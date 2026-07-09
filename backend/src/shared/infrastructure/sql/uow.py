from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.sql.connection import AsyncSessionLocal


class SQLAlchemyUnitOfWork:
    """
    A Unit of Work pattern implementation for SQLAlchemy AsyncSession.
    It encapsulates the database session and manages the transaction boundary.

    Always use as an async context manager:
        async with uow:
            await repo.do_something(uow.session)
    """

    def __init__(self, session_factory=AsyncSessionLocal):
        self.session_factory = session_factory
        self._session: AsyncSession | None = None

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError(
                "UoW.session accessed before entering the context manager. "
                "Use 'async with uow:' before accessing uow.session."
            )
        return self._session

    async def __aenter__(self):
        self._session = self.session_factory()
        await self._session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, traceback):
        assert self._session is not None  # guaranteed: __aenter__ sets it before __aexit__ runs
        try:
            if exc_type is not None:
                await self._session.rollback()
            else:
                await self._session.commit()
        finally:
            await self._session.__aexit__(exc_type, exc_val, traceback)
            self._session = None


async def get_uow():
    """FastAPI dependency to inject the Unit of Work."""
    yield SQLAlchemyUnitOfWork()
