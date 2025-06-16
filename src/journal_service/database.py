from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.sql import text

from config import DATABASE_URL
from journal_service.models.sql.base import Base

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging in development
    future=True,
)

# Create session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """
    Initializes the database by creating all tables defined in the Base metadata.
    This is suitable for development but for production, Alembic is recommended.
    """
    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.drop_all
        )  # Optional: drop all tables for a clean slate
        # optional: seed data*
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS journal"))
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection function to provide database sessions.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
