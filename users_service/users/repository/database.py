import os
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
import ssl

from users.web.config import Config

SCHEMA_NAME = "users"

# Initialize engine and session factory at module level
DATABASE_URL = Config.DATABASE_URL
DB_ECHO = Config.DB_ECHO

# Build connect args with higher timeout and SSL for cloud DBs
connect_args = {
    "timeout": 30,
    "server_settings": {
        "jit": "off",
    },
}
try:
    url_lc = (DATABASE_URL or "").lower()
    if "localhost" not in url_lc and "127.0.0.1" not in url_lc:
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ssl_ctx  # type: ignore[assignment]
except Exception:
    pass

engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=DB_ECHO,
    pool_size=Config.DB_POOL_SIZE,
    max_overflow=Config.DB_MAX_OVERFLOW,
    pool_timeout=Config.DB_POOL_TIMEOUT,
    pool_recycle=Config.DB_POOL_RECYCLE,
    pool_pre_ping=Config.DB_POOL_PRE_PING,
    connect_args=connect_args,
)
async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all models in the users service."""

    pass


# Set the schema for all tables in this service
Base.metadata.schema = SCHEMA_NAME


async def init_db() -> None:
    """Initialize the database, ensure schema exists, and create tables if they don't exist."""
    async with engine.connect() as conn:  # Use connect() for individual DDL commands
        # Explicitly create schema if it doesn't exist from this connection's perspective
        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"))
        await conn.commit()  # Commit schema creation

    # Now proceed with create_all within its own transaction
    async with engine.begin() as conn:
        # The service_type enum should be created here by create_all due to `create_type=True` in the model
        # and `values_callable` ensuring correct labels.
        await conn.run_sync(Base.metadata.create_all)
        print(f"Database tables created/verified for schema '{SCHEMA_NAME}' using URL: {DATABASE_URL}")

    # Optionally, you could also re-run the ENUM type creation from the seeder here if create_all
    # proves unreliable for the ENUM across different startup scenarios, but it shouldn't be necessary
    # if the model definition is correct.
    # Example (if needed, but try without first):
    # async with engine.connect() as conn:
    #     await conn.execute(text(f"""
    #         DO $$
    #         BEGIN
    #             IF NOT EXISTS (SELECT 1 FROM pg_type typ JOIN pg_namespace ns ON ns.oid = typ.typnamespace WHERE typname = 'service_type' AND ns.nspname = '{SCHEMA_NAME}') THEN
    #                 CREATE TYPE {SCHEMA_NAME}.service_type AS ENUM ('meals', 'practice', 'shadow_boxing', 'fitness_db', 'programs');
    #             END IF;
    #         END$$;
    #     """))
    #     await conn.commit()
    #     print(f"ENUM type {SCHEMA_NAME}.service_type verified/created.")


async def close_db() -> None:
    """Close the database connection."""
    if engine:
        await engine.dispose()
        # No need to set engine to None if it's module-level and always defined
        print("Database connection closed")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to provide a database session via async_session_factory."""
    # async_session_factory is now guaranteed to be initialized
    async with async_session_factory() as session:
        yield session


__all__ = ["Base", "init_db", "close_db", "get_session", "engine", "SCHEMA_NAME", "async_session_factory"]
