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

# Set environment variables for the application's config to pick up during tests
# This is crucial for when the application code reads the DATABASE_URL
os.environ["DATABASE_URL"] = (
    f"postgresql+{TEST_DRIVER}://{TEST_USER}:{TEST_PASSWORD}@{TEST_HOST}:{TEST_POSTGRES_PORT}/{TEST_DB}"
)
os.environ["TESTING"] = "True"

logging.basicConfig(level=logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


@pytest.fixture(scope="session")
def docker_compose_up_down():
    """
    Manages a Docker container for the test database.
    'session' scope ensures it starts once and tears down after all tests.
    """
    import docker

    client = None
    container = None
    container_name = "cyborg_coach_test_db"

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

        # Start the container
        logging.info(f"Starting new {container_name} container.")
        container = client.containers.run(
            image="postgres:13",
            name=container_name,
            environment={
                "POSTGRES_USER": TEST_USER,
                "POSTGRES_PASSWORD": TEST_PASSWORD,
                "POSTGRES_DB": TEST_DB,
            },
            ports={"5432/tcp": TEST_POSTGRES_PORT},
            detach=True,
            remove=True,  # Ensure container is removed on stop
        )

        # Wait for the database to be ready
        logging.info(f"Waiting for {container_name} to be ready...")
        max_retries = 20
        retry_delay = 2
        for i in range(max_retries):
            time.sleep(retry_delay)
            container.reload()
            if container.status != "running":
                pytest.fail(f"{container_name} container exited unexpectedly.")

            logs = container.logs().decode("utf-8")
            if "database system is ready to accept connections" in logs:
                logging.info(f"PostgreSQL in {container_name} is ready.")
                break
            if i == max_retries - 1:
                logging.error(
                    f"Container {container_name} did not become ready. Logs:\n{logs}"
                )
                pytest.fail(
                    f"Test DB container ({container_name}) did not become ready."
                )

        yield

    finally:
        if container:
            logging.info(f"Stopping {container_name} container.")
            container.stop()
        if client:
            client.close()


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
async def test_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """
    Provides a test-specific SQLAlchemy async_sessionmaker.
    """
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def uow(
    test_session_maker: async_sessionmaker[AsyncSession],
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
