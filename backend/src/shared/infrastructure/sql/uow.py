from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.sql.connection import AsyncSessionLocal


class SQLAlchemyUnitOfWork:
    """
    A Unit of Work pattern implementation for SQLAlchemy AsyncSession.
    It encapsulates the database session and manages the transaction boundary.
    """
    def __init__(self, session_factory=AsyncSessionLocal):
        self.session_factory = session_factory
        self.session: AsyncSession = None # type: ignore

    async def __aenter__(self):
        self.session = self.session_factory()
        await self.session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, traceback):
        try:
            if exc_type is not None:
                await self.session.rollback()
            else:
                await self.session.commit()
        finally:
            await self.session.__aexit__(exc_type, exc_val, traceback)

async def get_uow():
    """FastAPI dependency to inject the Unit of Work."""
    yield SQLAlchemyUnitOfWork()
