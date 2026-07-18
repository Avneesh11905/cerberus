import asyncio
from sqlalchemy import text
from src.core.database import engine, Base


async def drop():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version"))


if __name__ == "__main__":
    asyncio.run(drop())
