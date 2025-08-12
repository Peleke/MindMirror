from __future__ import annotations

import os
import uuid
import importlib
import pytest
import pytest_asyncio
from sqlalchemy import text
import importlib

from habits_service.habits_service.app.db.models import Base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool


# Rely on pytest-asyncio default loop handling to avoid cross-loop issues


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncSession:
    """Function-scoped session bound to a fresh engine tied to the current loop.
    Also rewires the app's global engine/session to target a unique schema so GraphQL paths use the same connection.
    """
    db_url = "postgresql+asyncpg://postgres:postgres@postgres:5432/cyborg_coach"
    schema = f"habits_test_{uuid.uuid4().hex[:8]}"
    print(f"[tests] Using DATABASE_URL={db_url}")
    print(f"[tests] Using DATABASE_SCHEMA={schema}")

    # Point app settings to this schema and URL, then reload session so its engine is created in this test's loop
    os.environ["DATABASE_URL"] = db_url
    os.environ["DATABASE_SCHEMA"] = schema
    from habits_service.habits_service.app.config import get_settings as _get_settings
    _get_settings.cache_clear()
    from habits_service.habits_service.app.db import session as session_module
    importlib.reload(session_module)

    # Build a test-scoped engine with schema translation so GraphQL and repos share it
    test_engine = create_async_engine(
        db_url,
        future=True,
        poolclass=NullPool,
        execution_options={"schema_translate_map": {"habits": schema}},
    )
    session_module.engine = test_engine
    session_module.async_session_maker = async_sessionmaker(bind=test_engine, expire_on_commit=False, class_=AsyncSession)

    # Prepare schema and tables using the test engine
    async with test_engine.begin() as conn:
        await conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
        await conn.execute(text(f"CREATE SCHEMA {schema}"))
        await conn.run_sync(Base.metadata.create_all)
    print(f"[tests] Prepared schema {schema}")

    SessionLocal = session_module.async_session_maker
    async with SessionLocal() as session:
        yield session

    # Teardown
    async with test_engine.begin() as conn:
        await conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
    await test_engine.dispose()
    print(f"[tests] Dropped schema {schema} and disposed engine")


# remove old prepare_schema and module-based db_session

