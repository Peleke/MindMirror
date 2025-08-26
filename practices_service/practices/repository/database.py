from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from practices.web.config import Config  # Get DB URL from config

# Models will be imported by the application elsewhere, registering themselves with Base.metadata
# Remove: from practices.repository.models import PracticeModel, PrescriptionModel, PrescribedMovementModel, SetModel

DATABASE_URL = Config.DATABASE_URL

engine = create_async_engine(DATABASE_URL)  # Removed echo=True

async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


Base.metadata.schema = "practices"  # Set the schema for all tables inheriting from this Base


async def init_db():
    """Initializes the database and creates tables if they don't exist."""
    async with engine.begin() as conn:
        # Ensure schema exists
        await conn.execute(text('CREATE SCHEMA IF NOT EXISTS "practices"'))
        # await conn.run_sync(Base.metadata.drop_all) # Optional: drop all tables for a clean slate
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created (if they didn't exist).")


async def close_db():
    """Closes the database engine."""
    await engine.dispose()
    print("Database engine disposed.")


__all__ = ["engine", "async_session_maker", "Base", "init_db", "close_db"]
