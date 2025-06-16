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

from journal_service.models.sql.base import Base
from journal_service.models.sql.journal import JournalEntryModel
from journal_service.uow import UnitOfWork, get_uow
from journal_service.web.app import app
from shared.auth import CurrentUser, get_current_user
from shared.data_models import UserRole

# Test configuration
TEST_DRIVER = "asyncpg"
TEST_USER = os.getenv("POSTGRES_USER", "postgres")
TEST_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
TEST_HOST = os.getenv("POSTGRES_HOST", "localhost")
TEST_POSTGRES_PORT = os.getenv(
    "POSTGRES_PORT", 5433
)  # Use a different port to avoid conflicts
TEST_DB = os.getenv("POSTGRES_DB", "journal_service_test")
TEST_SCHEMA = "journal"
TEST_ECHO = os.getenv("TEST_ECHO", "False").lower() == "true"
TEST_USER_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"  # A consistent test UUID

# Set environment variables for the application's config to pick up during tests
os.environ["DATABASE_URL"] = (
    f"postgresql+{TEST_DRIVER}://{TEST_USER}:{TEST_PASSWORD}@{TEST_HOST}:{TEST_POSTGRES_PORT}/{TEST_DB}"
)
os.environ["TESTING"] = "True"

logging.basicConfig(level=logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


@pytest.fixture(scope="session")
def docker_services():
    """
    Manages Docker containers for test services (PostgreSQL).
    Session scope ensures they start once and tear down after all tests.
    """
    import docker

    client = None
    containers = {}
    container_configs = {
        "postgres": {
            "name": "journal_service_test_db",
            "image": "postgres:13",
            "environment": {
                "POSTGRES_USER": TEST_USER,
                "POSTGRES_PASSWORD": TEST_PASSWORD,
                "POSTGRES_DB": TEST_DB,
            },
            "ports": {"5432/tcp": TEST_POSTGRES_PORT},
            "ready_log": "database system is ready to accept connections",
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


@pytest_asyncio.fixture(scope="function")
async def engine(docker_services) -> AsyncGenerator[AsyncEngine, None]:
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
    Creates a session maker for the test database.
    """
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture(scope="function")
async def session(
    test_session_maker: async_sessionmaker[AsyncSession], create_tables
) -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a database session for testing.
    Function scope ensures each test gets a fresh session.
    """
    async with test_session_maker() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def uow(
    test_session_maker: async_sessionmaker[AsyncSession], create_tables
) -> AsyncGenerator[UnitOfWork, None]:
    """
    Provides a Unit of Work instance for testing.
    """
    async with test_session_maker() as session:
        uow = UnitOfWork(session)
        try:
            yield uow
        finally:
            await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(
    test_session_maker: async_sessionmaker[AsyncSession], create_tables
) -> AsyncGenerator[AsyncClient, None]:
    """
    Provides an HTTP client for testing the journal service GraphQL API.
    """

    # Override dependencies to use test database
    async def override_get_uow() -> AsyncGenerator[UnitOfWork, None]:
        # Use the test_session_maker from the outer fixture scope
        async with test_session_maker() as session:
            uow = UnitOfWork(session)
            try:
                yield uow
            finally:
                await session.rollback()

    async def override_get_current_user() -> CurrentUser:
        return CurrentUser(
            id=UUID(TEST_USER_ID), roles=[UserRole(role="user", domain="coaching")]
        )

    # Apply overrides
    app.dependency_overrides[get_uow] = override_get_uow
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Create test client
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def seed_db(uow: UnitOfWork, create_tables) -> AsyncGenerator[dict, None]:
    """
    Seeds the test database with sample journal entries for testing.
    """
    # Create sample journal entries
    gratitude_entry = JournalEntryModel(
        id=uuid.uuid4(),
        user_id=TEST_USER_ID,
        entry_type="GRATITUDE",
        payload={
            "grateful_for": ["good health", "supportive friends", "a sunny day"],
            "excited_about": ["upcoming vacation", "new project", "learning to bake"],
            "focus": "complete the quarterly report",
            "affirmation": "I am capable and resilient",
            "mood": "optimistic",
        },
        created_at=datetime.now(timezone.utc),
    )

    reflection_entry = JournalEntryModel(
        id=uuid.uuid4(),
        user_id=TEST_USER_ID,
        entry_type="REFLECTION",
        payload={
            "wins": [
                "finished a major project",
                "got a new high score",
                "cooked a great meal",
            ],
            "improvements": ["procrastinated less", "exercised more"],
            "mood": "accomplished",
        },
        created_at=datetime.now(timezone.utc),
    )

    freeform_entry = JournalEntryModel(
        id=uuid.uuid4(),
        user_id=TEST_USER_ID,
        entry_type="FREEFORM",
        payload="Today was a productive day. I managed to finish most of my tasks and even had time for a walk.",
        created_at=datetime.now(timezone.utc),
    )

    # Entry for a different user (to test isolation)
    other_user_entry = JournalEntryModel(
        id=uuid.uuid4(),
        user_id="other-user-456",
        entry_type="FREEFORM",
        payload="This entry should not be visible to the test user.",
        created_at=datetime.now(timezone.utc),
    )

    # Add entries to database
    async with uow:
        uow.session.add(gratitude_entry)
        uow.session.add(reflection_entry)
        uow.session.add(freeform_entry)
        uow.session.add(other_user_entry)
        await uow.commit()

    yield {
        "gratitude_entry": gratitude_entry,
        "reflection_entry": reflection_entry,
        "freeform_entry": freeform_entry,
        "other_user_entry": other_user_entry,
    }
