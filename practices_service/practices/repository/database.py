from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
import uuid
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from practices.web.config import Config  # Get DB URL from config

# Models will be imported by the application elsewhere, registering themselves with Base.metadata
# Remove: from practices.repository.models import PracticeModel, PrescriptionModel, PrescribedMovementModel, SetModel

DATABASE_URL = Config.DATABASE_URL

engine = create_async_engine(
    DATABASE_URL,
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4()}__",
    },
)  # Removed echo=True

async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


Base.metadata.schema = "practices"  # Set the schema for all tables inheriting from this Base


async def init_db():
    """Initializes the database and creates tables if they don't exist."""
    import asyncio
    max_retries = 5
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                # Ensure schema exists
                await conn.execute(text('CREATE SCHEMA IF NOT EXISTS "practices"'))
                # await conn.run_sync(Base.metadata.drop_all) # Optional: drop all tables for a clean slate
                await conn.run_sync(Base.metadata.create_all)
            print("Database tables created (if they didn't exist).")
            return
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Database connection failed (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                print(f"Failed to connect to database after {max_retries} attempts")
                raise


async def close_db():
    """Closes the database engine."""
    await engine.dispose()
    print("Database engine disposed.")


__all__ = ["engine", "async_session_maker", "Base", "init_db", "close_db"]
