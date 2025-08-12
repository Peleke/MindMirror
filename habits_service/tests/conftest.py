from __future__ import annotations

import os
import uuid
import importlib
import pytest
from sqlalchemy import text

from habits_service.habits_service.app.db.models import Base
from habits_service.habits_service.app.config import get_settings


@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
def configure_test_db():
    """Configure env for tests: set DATABASE_URL/SCHEMA, clear settings cache, reload session module."""
    # Prefer DATABASE_URL from env; if unset, default to local compose Postgres
    # Force tests to use local compose Postgres to avoid hitting Supabase by mistake
    db_url = "postgresql+asyncpg://postgres:postgres@postgres:5432/cyborg_coach"
    test_schema = f"habits_test_{uuid.uuid4().hex[:8]}"
    os.environ["DATABASE_URL"] = db_url
    os.environ["DATABASE_SCHEMA"] = test_schema

    print(f"[tests] Using DATABASE_URL={db_url}")
    print(f"[tests] Using DATABASE_SCHEMA={test_schema}")

    # Clear settings cache so new env takes effect
    try:
        get_settings.cache_clear()  # type: ignore[attr-defined]
    except Exception:
        pass

    # Reload session module so engine/session bind to updated settings
    import habits_service.habits_service.app.db.session as session_module  # noqa

    importlib.reload(session_module)

    return test_schema


@pytest.fixture(scope="function", autouse=True)
async def prepare_schema(configure_test_db):
    # Import session module after configure step
    import habits_service.habits_service.app.db.session as session_module

    schema = os.environ.get("DATABASE_SCHEMA")
    assert schema, "DATABASE_SCHEMA must be set for tests"

    async with session_module.engine.begin() as conn:
        await conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
        await conn.execute(text(f"CREATE SCHEMA {schema}"))
        await conn.run_sync(Base.metadata.create_all)
    print(f"[tests] Prepared schema {schema}")
    yield
    async with session_module.engine.begin() as conn:
        await conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
    print(f"[tests] Dropped schema {schema}")


@pytest.fixture()
async def db_session():
    import habits_service.habits_service.app.db.session as session_module

    async with session_module.async_session_maker() as session:
        yield session

