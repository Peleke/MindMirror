import asyncio
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator
from uuid import UUID

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)

from api import app
from shared.auth import CurrentUser, get_current_user
from shared.data_models import UserRole
from src.models.sql.base import Base
from src.models.sql.journal import JournalEntryModel
from src.uow import UnitOfWork, get_uow

# Test configuration
TEST_DRIVER = "asyncpg"
TEST_USER = os.getenv("POSTGRES_USER", "postgres")
TEST_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
TEST_HOST = os.getenv("POSTGRES_HOST", "localhost")
TEST_POSTGRES_PORT = os.getenv(
    "POSTGRES_PORT", 5433
)  # Use a different port to avoid conflicts
TEST_HTTP_PORT = 8000
TEST_DB = os.getenv("POSTGRES_DB", "cyborg_coach_test")
TEST_SCHEMA = "journal"
TEST_ECHO = os.getenv("TEST_ECHO", "False").lower() == "true"
TEST_USER_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"  # A consistent test UUID

# Qdrant and Redis test configuration
TEST_QDRANT_PORT = 6334  # Different from production port 6333
TEST_REDIS_PORT = 6380   # Different from production port 6379
TEST_QDRANT_URL = f"http://localhost:{TEST_QDRANT_PORT}"
TEST_REDIS_URL = f"redis://localhost:{TEST_REDIS_PORT}/0"

# Set environment variables for the application's config to pick up during tests
# This is crucial for when the application code reads the DATABASE_URL
os.environ["DATABASE_URL"] = (
    f"postgresql+{TEST_DRIVER}://{TEST_USER}:{TEST_PASSWORD}@{TEST_HOST}:{TEST_POSTGRES_PORT}/{TEST_DB}"
)
os.environ["TESTING"] = "True"
os.environ["QDRANT_URL"] = TEST_QDRANT_URL
os.environ["REDIS_URL"] = TEST_REDIS_URL

logging.basicConfig(level=logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


@pytest.fixture(scope="session")
def docker_services():
    """
    Manages Docker containers for test services (PostgreSQL, Qdrant, Redis).
    Session scope ensures they start once and tear down after all tests.
    """
    import docker

    client = None
    containers = {}
    container_configs = {
        "postgres": {
            "name": "cyborg_coach_test_db",
            "image": "postgres:13",
            "environment": {
                "POSTGRES_USER": TEST_USER,
                "POSTGRES_PASSWORD": TEST_PASSWORD,
                "POSTGRES_DB": TEST_DB,
            },
            "ports": {"5432/tcp": TEST_POSTGRES_PORT},
            "ready_log": "database system is ready to accept connections"
        },
        "qdrant": {
            "name": "cyborg_coach_test_qdrant",
            "image": "qdrant/qdrant:latest",
            "ports": {"6333/tcp": TEST_QDRANT_PORT},
            "ready_log": "Qdrant gRPC listening on"
        },
        "redis": {
            "name": "cyborg_coach_test_redis", 
            "image": "redis:7-alpine",
            "ports": {"6379/tcp": TEST_REDIS_PORT},
            "ready_log": "Ready to accept connections"
        }
    }

    try:
        # Connect to Docker
        try:
            client = docker.from_env()
            client.ping()
            logging.info("Successfully connected to Docker.")
        except Exception as e:
            logging.error(
                f"Could not connect to Docker. Please ensure Docker is running. Error: {e}"
            )
            pytest.skip("Docker not available", allow_module_level=True)
            return

        # Start all containers
        for service_name, config in container_configs.items():
            logging.info(f"Starting {service_name} container: {config['name']}")
            
            container = client.containers.run(
                image=config["image"],
                name=config["name"],
                environment=config.get("environment", {}),
                ports=config["ports"],
                detach=True,
                remove=True,  # Ensure container is removed on stop
            )
            containers[service_name] = container

            # Wait for the service to be ready
            logging.info(f"Waiting for {service_name} to be ready...")
            max_retries = 30
            retry_delay = 2
            
            for i in range(max_retries):
                time.sleep(retry_delay)
                container.reload()
                
                if container.status != "running":
                    pytest.fail(f"{service_name} container exited unexpectedly.")

                logs = container.logs().decode("utf-8")
                if config["ready_log"] in logs:
                    logging.info(f"{service_name} is ready.")
                    break
                    
                if i == max_retries - 1:
                    logging.error(f"{service_name} did not become ready. Logs:\n{logs}")
                    pytest.fail(f"{service_name} container did not become ready.")

        yield containers

    finally:
        # Stop all containers
        for service_name, container in containers.items():
            if container:
                logging.info(f"Stopping {service_name} container.")
                container.stop()
        if client:
            client.close()


@pytest.fixture(scope="session") 
def docker_compose_up_down(docker_services):
    """
    Backward compatibility fixture for existing tests.
    Maps to the new docker_services fixture.
    """
    yield docker_services["postgres"]


@pytest_asyncio.fixture(scope="function")
async def engine(docker_compose_up_down) -> AsyncGenerator[AsyncEngine, None]:
    """
    Creates an async SQLAlchemy engine for the test database.
    Function scope to ensure isolation, though engine could be session-scoped.
    """
    db_url = os.environ["DATABASE_URL"]
    engine = create_async_engine(db_url, echo=TEST_ECHO)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def create_tables(engine: AsyncEngine):
    """
    Drops and recreates the test schema and all tables for each test function,
    ensuring a clean slate.
    """
    async with engine.begin() as conn:
        await conn.execute(text(f"DROP SCHEMA IF EXISTS {TEST_SCHEMA} CASCADE"))
        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {TEST_SCHEMA}"))
        # Base.metadata.schema is set in models/sql/base.py
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture(scope="function")
async def user() -> CurrentUser:
    """Provides a test user object consistent with the one used in client auth."""
    return CurrentUser(
        id=UUID(TEST_USER_ID), roles=[UserRole(role="user", domain="coaching")]
    )


@pytest_asyncio.fixture(scope="function")
async def test_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """
    Provides a test-specific SQLAlchemy async_sessionmaker.
    """
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def session(
    test_session_maker: async_sessionmaker[AsyncSession], create_tables
) -> AsyncGenerator[AsyncSession, None]:
    """
    Provides an isolated database session for a single test.
    Manages transaction rollback on error.
    """
    async with test_session_maker() as session_instance:
        try:
            yield session_instance
            await session_instance.commit()
        except Exception:
            await session_instance.rollback()
            raise
        finally:
            await session_instance.close()


@pytest_asyncio.fixture(scope="function")
async def uow(
    test_session_maker: async_sessionmaker[AsyncSession], create_tables
) -> AsyncGenerator[UnitOfWork, None]:
    """Provides a UnitOfWork instance configured with a test-specific session factory.

    This UoW is suitable for use in tests that directly interact with services or repositories.
    """
    test_uow = UnitOfWork(session_factory=test_session_maker)
    logging.debug(f"Test UoW created with session factory: {test_session_maker}")
    yield test_uow
    # No explicit cleanup needed here for the UoW instance itself,
    # as its sessions are managed by its __aenter__/__aexit__ and the factory is function-scoped.


@pytest_asyncio.fixture(scope="function")
async def client(
    test_session_maker: async_sessionmaker[AsyncSession], create_tables
) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an HTTP client for testing API endpoints.

    This fixture yields an AsyncClient that can be used to make requests to the API
    during tests. For GraphQL tests, this will point to the GraphQL endpoint.
    It also overrides the UoW dependency for proper test isolation.
    """

    async def override_get_uow() -> AsyncGenerator[UnitOfWork, None]:
        # Use the test_session_maker from the outer fixture scope
        uow_instance = UnitOfWork(session_factory=test_session_maker)
        logging.debug(
            f"Overridden UoW created with session factory: {test_session_maker} for client request"
        )
        try:
            yield uow_instance
        finally:
            # Ensure session is closed if __aexit__ wasn't reached or UoW wasn't used with 'async with'
            if (
                uow_instance._session
            ):  # Accessing protected member for cleanup in test override
                logging.debug(
                    f"Cleaning up overridden UoW session: {uow_instance._session}"
                )
                await uow_instance.close()

    async def override_get_current_user() -> CurrentUser:
        """A test-specific override for the current user dependency."""
        return CurrentUser(
            id=UUID(TEST_USER_ID), roles=[UserRole(role="user", domain="coaching")]
        )

    app.dependency_overrides[get_uow] = override_get_uow
    app.dependency_overrides[get_current_user] = override_get_current_user

    # A dummy JWT and headers to simulate an authenticated request from a gateway
    dummy_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXN1YmplY3QifQ.s-0-gH8G0-t9P1-r_Gg_y_g"
    headers = {"Authorization": f"Bearer {dummy_jwt}", "x-internal-id": TEST_USER_ID}

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url=f"http://localhost:{TEST_HTTP_PORT}",
            headers=headers,
        ) as client_instance:
            yield client_instance
    finally:
        del app.dependency_overrides[get_uow]  # Clean up the override
        del app.dependency_overrides[get_current_user]


@pytest_asyncio.fixture(scope="function")
async def seed_db(uow: UnitOfWork, create_tables) -> AsyncGenerator[dict, None]:
    """
    Seeds the database with initial data for testing.
    Uses the UoW pattern for proper transaction management.
    """
    async with uow:
        # Entry 1: Gratitude
        gratitude_entry = JournalEntryModel(
            id=uuid.uuid4(),
            user_id=TEST_USER_ID,
            entry_type="GRATITUDE",
            payload={
                "grateful_for": [
                    "good coffee",
                    "a productive morning",
                    "supportive teammates",
                ],
                "excited_about": [
                    "the weekend",
                    "new project features",
                    "team collaboration",
                ],
                "focus": "shipping this feature",
                "affirmation": "I build reliable systems.",
            },
            created_at=datetime.now(timezone.utc),
        )

        # Entry 2: Freeform
        freeform_entry = JournalEntryModel(
            id=uuid.uuid4(),
            user_id=TEST_USER_ID,
            entry_type="FREEFORM",
            payload="Just writing down some thoughts about the project architecture.",
            created_at=datetime.now(timezone.utc),
        )

        # Entry 3: Another user's entry
        other_user_entry = JournalEntryModel(
            id=uuid.uuid4(),
            user_id="other-user-456",
            entry_type="REFLECTION",
            payload={
                "what_went_well": "Completed a major refactor.",
                "what_did_not_go_well": "Tests took longer than expected.",
                "how_to_improve": "Allocate more time for testing next time.",
            },
            created_at=datetime.now(timezone.utc),
        )

        uow.session.add_all([gratitude_entry, freeform_entry, other_user_entry])
        await uow.session.flush()

        await uow.session.refresh(gratitude_entry)
        await uow.session.refresh(freeform_entry)
        await uow.session.refresh(other_user_entry)

        # UoW will automatically commit the transaction when exiting the async with block

    yield {
        "user_id": TEST_USER_ID,
        "gratitude_entry": gratitude_entry,
        "freeform_entry": freeform_entry,
        "other_user_entry": other_user_entry,
    }


@pytest_asyncio.fixture(scope="function")
async def qdrant_client(docker_services):
    """
    Provides a test Qdrant client connected to the test container.
    Function scope to ensure clean state per test.
    """
    from src.vector_stores.qdrant_client import QdrantClient
    
    # Wait a moment for Qdrant to be fully ready
    await asyncio.sleep(1)
    
    client = QdrantClient(qdrant_url=TEST_QDRANT_URL)
    
    # Verify connection
    health = await client.health_check()
    if not health:
        pytest.fail("Qdrant test container is not healthy")
    
    yield client
    
    # Cleanup: Delete all test collections
    try:
        collections = client.get_client().get_collections()
        for collection in collections.collections:
            if "test" in collection.name.lower():
                await client.delete_collection(collection.name)
                logging.info(f"Cleaned up test collection: {collection.name}")
    except Exception as e:
        logging.warning(f"Error cleaning up Qdrant collections: {e}")


@pytest_asyncio.fixture(scope="function")
async def redis_client(docker_services):
    """
    Provides a test Redis client connected to the test container.
    Function scope to ensure clean state per test.
    """
    import redis.asyncio as redis
    
    client = redis.from_url(TEST_REDIS_URL)
    
    # Verify connection
    try:
        await client.ping()
    except Exception as e:
        pytest.fail(f"Redis test container is not accessible: {e}")
    
    yield client
    
    # Cleanup: Flush test database
    try:
        await client.flushdb()
        logging.info("Cleaned up Redis test database")
    except Exception as e:
        logging.warning(f"Error cleaning up Redis: {e}")
    finally:
        await client.close()


@pytest_asyncio.fixture(scope="function") 
async def celery_app(redis_client):
    """
    Provides a test Celery app configured for testing.
    Uses the test Redis instance as broker and result backend.
    """
    from src.tasks import create_celery_app
    
    # Override Celery configuration for testing
    test_config = {
        'broker_url': TEST_REDIS_URL,
        'result_backend': TEST_REDIS_URL,
        'task_always_eager': True,  # Execute tasks synchronously in tests
        'task_eager_propagates': True,  # Propagate exceptions in eager mode
        'task_store_eager_result': True,  # Store results even in eager mode
    }
    
    app = create_celery_app()
    app.conf.update(test_config)
    
    yield app
