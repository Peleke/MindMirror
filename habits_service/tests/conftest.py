from __future__ import annotations

import os
import uuid
import importlib
import pytest
from sqlalchemy import text

from habits_service.habits_service.app.db.models import Base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool


@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function")
async def db_session() -> AsyncSession:
    """Function-scoped engine + session bound to the current event loop.
    Uses the compose Postgres and a fixed schema 'habits' which is dropped/created per test.
    """
    db_url = "postgresql+asyncpg://postgres:postgres@postgres:5432/cyborg_coach"
    schema = f"habits_test_{uuid.uuid4().hex[:8]}"
    print(f"[tests] Using DATABASE_URL={db_url}")
    print(f"[tests] Using DATABASE_SCHEMA={schema}")

    engine = create_async_engine(
        db_url,
        future=True,
        poolclass=NullPool,
        execution_options={"schema_translate_map": {"habits": schema}},
    )
    # Prepare schema and tables
    async with engine.begin() as conn:
        await conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
        await conn.execute(text(f"CREATE SCHEMA {schema}"))
        await conn.run_sync(Base.metadata.create_all)
    print(f"[tests] Prepared schema {schema}")

    SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    async with SessionLocal() as session:
        yield session

    # Teardown
    async with engine.begin() as conn:
        await conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
    await engine.dispose()
    print(f"[tests] Dropped schema {schema} and disposed engine")


# remove old prepare_schema and module-based db_session

