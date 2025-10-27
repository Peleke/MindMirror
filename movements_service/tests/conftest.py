import os
import asyncio
import pytest
import asyncpg


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


async def ensure_database_exists():
    host = os.getenv("DB_HOST", os.getenv("PGHOST", "localhost"))
    port = int(os.getenv("DB_PORT", os.getenv("PGPORT", "5432")))
    user = os.getenv("DB_USER", os.getenv("PGUSER", "postgres"))
    password = os.getenv("DB_PASSWORD", os.getenv("PGPASSWORD", "postgres"))
    dbname = os.getenv("DB_NAME", os.getenv("PGDATABASE", "swae_movements"))

    try:
        # Try connect directly to target DB
        conn = await asyncpg.connect(host=host, port=port, user=user, password=password, database=dbname)
        await conn.close()
        return
    except asyncpg.InvalidCatalogNameError:
        pass
    except Exception:
        # If other error (e.g., auth), don't try to create
        return

    # Connect to 'postgres' maintenance DB to create the target database
    try:
        conn = await asyncpg.connect(host=host, port=port, user=user, password=password, database="postgres")
        try:
            await conn.execute(f'CREATE DATABASE "{dbname}"')
        except asyncpg.DuplicateDatabaseError:
            pass
        finally:
            await conn.close()
    except Exception:
        # Best effort only; tests may still fail if DB cannot be created
        pass


@pytest.fixture(scope="session", autouse=True)
def _ensure_db_created_before_tests(event_loop):
    event_loop.run_until_complete(ensure_database_exists()) 