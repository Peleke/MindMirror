"""Test configuration and constants for the users service."""

import logging
import os
import time
import uuid
from typing import Any, AsyncGenerator, Dict, Generator, Optional

import docker
import pytest
import pytest_asyncio
from fastapi import Request
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from users.repository.database import Base
from users.repository.models import (
    AssociationStatusModel,
    CoachClientAssociationModel,
    DomainModel,
    RoleModel,
    SchedulableModel,
    ServiceEnum,
    ServiceModel,
    UserModel,
    UserServicesModel,
)
from users.repository.repositories import (
    SchedulableRepository,
    ServiceRepository,
    UserRepository,
)
from users.repository.uow import UnitOfWork
from users.web.app import app

# Test database configuration
TEST_DB = os.getenv("TEST_DB_NAME", "users_db")
TEST_USER = os.getenv("TEST_DB_USER", "users_user")
TEST_PASSWORD = os.getenv("TEST_DB_PASSWORD", "users_password")
TEST_HOST = os.getenv("TEST_DB_HOST", "localhost")
TEST_SCHEMA = "users"
TEST_POSTGRES_PORT = int(os.getenv("TEST_POSTGRES_PORT", 5433))
TEST_HTTP_PORT = int(os.getenv("TEST_HTTP_PORT", 8001))
TEST_ECHO = os.getenv("TEST_ECHO", "False").lower() == "true"

# Test environment variables
TEST_DATABASE_URL = f"postgresql+asyncpg://{TEST_USER}:{TEST_PASSWORD}@{TEST_HOST}:{TEST_POSTGRES_PORT}/{TEST_DB}"

# Set environment variables for Config to pick up during tests
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["HTTP_PORT"] = str(TEST_HTTP_PORT)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def docker_compose_up_down() -> Generator[None, None, None]:
    """Start docker-compose before tests and tear it down after.

    This fixture manages the lifecycle of a Docker container running the test database.
    It ensures that the container is started before tests are run and stopped afterwards.
    """
    client = None
    container = None
    try:
        # Try common Docker socket paths
        sockets_to_try = ["unix:///var/run/docker.sock", f"unix://{os.path.expanduser('~')}/.docker/run/docker.sock"]
        for sock_path in sockets_to_try:
            try:
                client = docker.DockerClient(base_url=sock_path)
                client.ping()  # Check if client is responsive
                logging.info(f"Successfully connected to Docker at {sock_path}")
                break
            except Exception:
                logging.warning(f"Failed to connect to Docker at {sock_path}")

        if not client or not client.ping():
            logging.error("Could not connect to Docker. Please ensure Docker is running and accessible.")
            pytest.skip("Docker not available", allow_module_level=True)
            return

        # Check if container already exists
        try:
            container = client.containers.get("practices_test_db")
            if container.status == "running":
                logging.info("Reusing existing running practices_test_db container.")
            else:
                logging.info("Found existing practices_test_db container, stopping and removing.")
                container.stop()
                container.remove()
                raise docker.errors.NotFound(
                    f"Container practices_test_db not found. Please ensure the container is running and accessible."
                )  # Force re-creation
        except docker.errors.NotFound:
            logging.info("Starting new practices_test_db container.")
            container = client.containers.run(
                image="postgres:latest",
                name="practices_test_db",
                environment={
                    "POSTGRES_USER": TEST_USER,
                    "POSTGRES_PASSWORD": TEST_PASSWORD,
                    "POSTGRES_DB": TEST_DB,
                },
                ports={"5432/tcp": TEST_POSTGRES_PORT},
                detach=True,
            )
            logging.info(f"Waiting for practices_test_db container to be ready (PID: {container.id[:12]})...")
            # Improved readiness check
            max_retries = 10
            retry_delay = 3  # seconds
            for i in range(max_retries):
                time.sleep(retry_delay)
                container.reload()  # Refresh container state
                if container.status == "running":
                    # Check logs for PostgreSQL readiness
                    logs = container.logs(tail=50).decode("utf-8")
                    if "database system is ready to accept connections" in logs:
                        logging.info("PostgreSQL in practices_test_db is ready.")
                        break
                    else:
                        logging.info(
                            f"PostgreSQL not ready yet (attempt {i+1}/{max_retries}). Current status: {container.status}"
                        )
                else:
                    logging.warning(
                        f"Container practices_test_db status is {container.status} (attempt {i+1}/{max_retries})."
                    )
                if i == max_retries - 1:
                    logs = container.logs().decode("utf-8")
                    logging.error(f"Container practices_test_db did not become ready. Logs:\n{logs}")
                    pytest.fail("Test DB container did not become ready.")

        yield

    # tear down the container
    finally:
        if container and os.getenv("PYTEST_KEEP_DB_CONTAINER", "false").lower() != "true":
            try:
                logging.info(f"Stopping and removing practices_test_db container (ID: {container.id[:12]}).")
                container.stop()
                container.remove()
            except docker.errors.NotFound:
                logging.warning("practices_test_db container not found during teardown (already removed?).")
            except docker.errors.APIError as e:
                logging.warning(f"APIError during container teardown (already being removed or Docker issue?): {e}")
        elif container:
            logging.info("PYTEST_KEEP_DB_CONTAINER is set to true. practices_test_db container will not be removed.")
        if client:
            client.close()


@pytest_asyncio.fixture(scope="function")
async def engine(docker_compose_up_down: None) -> AsyncGenerator[AsyncEngine, None]:
    logger.info(f"Creating engine with URL: {TEST_DATABASE_URL}")
    db_engine = create_async_engine(TEST_DATABASE_URL, echo=TEST_ECHO)
    try:
        yield db_engine
    finally:
        logger.info("Disposing engine.")
        await db_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        logger.info(f"Dropping schema {TEST_SCHEMA} if exists...")
        await conn.execute(text(f"DROP SCHEMA IF EXISTS {TEST_SCHEMA} CASCADE"))
        logger.info(f"Creating schema {TEST_SCHEMA}...")
        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {TEST_SCHEMA}"))

        # Create the service enum type
        await conn.execute(
            text(
                f"""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'service_type' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = '{TEST_SCHEMA}')) THEN
                    CREATE TYPE {TEST_SCHEMA}.service_type AS ENUM ('meals', 'practice', 'sleep', 'shadow_boxing', 'fitness_db', 'programs');
                END IF;
            END$$;
        """
            )
        )
        # Create the role, domain, and association status enum types
        for enum_name, enum_values in {
            "role_enum": "('coach', 'client', 'admin')",
            "domain_enum": "('practices', 'meals', 'sleep', 'system')",
            "association_status_enum": "('pending', 'accepted', 'rejected', 'terminated')",
        }.items():
            await conn.execute(
                text(
                    f"""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{enum_name}' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = '{TEST_SCHEMA}')) THEN
                        CREATE TYPE {TEST_SCHEMA}.{enum_name} AS ENUM {enum_values};
                END IF;
            END$$;
        """
            )
        )

        logger.info(f"Creating all tables in schema {TEST_SCHEMA}...")
        await conn.run_sync(Base.metadata.create_all)

        # Create the automatic timestamp update function
        await conn.execute(
            text(
                f"""
            CREATE OR REPLACE FUNCTION {TEST_SCHEMA}.update_modified_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.modified_at = clock_timestamp();
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """
            )
        )

        # Add triggers for timestamp updates
        triggers = [
            f"CREATE TRIGGER update_users_modified_at BEFORE UPDATE ON {TEST_SCHEMA}.users FOR EACH ROW EXECUTE FUNCTION {TEST_SCHEMA}.update_modified_at_column()",
            f"CREATE TRIGGER update_services_modified_at BEFORE UPDATE ON {TEST_SCHEMA}.services FOR EACH ROW EXECUTE FUNCTION {TEST_SCHEMA}.update_modified_at_column()",
            f"CREATE TRIGGER update_user_services_modified_at BEFORE UPDATE ON {TEST_SCHEMA}.user_services FOR EACH ROW EXECUTE FUNCTION {TEST_SCHEMA}.update_modified_at_column()",
            f"CREATE TRIGGER update_schedulables_modified_at BEFORE UPDATE ON {TEST_SCHEMA}.schedulables FOR EACH ROW EXECUTE FUNCTION {TEST_SCHEMA}.update_modified_at_column()",
            f"CREATE TRIGGER update_coach_client_associations_modified_at BEFORE UPDATE ON {TEST_SCHEMA}.coach_client_associations FOR EACH ROW EXECUTE FUNCTION {TEST_SCHEMA}.update_modified_at_column()",
        ]

        for trigger_sql in triggers:
            await conn.execute(text(trigger_sql))

    logger.info("Tables created.")
    yield
    # Teardown can be added here if needed, but usually handled by dropping schema


@pytest_asyncio.fixture(scope="function")
async def session(engine: AsyncEngine, tables: None) -> AsyncGenerator[AsyncSession, None]:
    """Provides a single session for a test function, with tables created."""
    async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session_factory() as session_:
        logger.info(f"DB Session created for test: {session_}")
        try:
            yield session_
        finally:
            logger.info(f"Closing DB session for test: {session_}")
            await session_.close()


@pytest_asyncio.fixture(scope="function")
async def uow(engine: AsyncEngine, tables: None) -> AsyncGenerator[UnitOfWork, None]:
    """Provides a UnitOfWork instance for a test function.

    The UoW uses its own session factory based on the engine.
    The `tables` fixture ensures the schema and tables are created before UoW is used.
    """
    uow_session_factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
    # The UnitOfWork itself will manage the lifecycle of its session.
    # No need for 'async with' here as the UoW object is returned,
    # and tests will use 'async with uow_instance:'
    yield UnitOfWork(session_factory=uow_session_factory)


@pytest_asyncio.fixture(scope="function")
async def user_repository(uow: UnitOfWork) -> AsyncGenerator[UserRepository, None]:
    """Provides a UserRepository that shares the session of the given UnitOfWork.

    This repository is intended to be used *within* an 'async with uow:' block in tests,
    ensuring that repository operations and the UoW's commit/rollback operate on the same session.
    """
    async with uow:  # Ensure UoW context is active to get its session
        # uow.users is already a UserRepository initialized with uow.session
        # If uow.users is not automatically initialized or accessible, then create one:
        yield UserRepository(session=uow.session)


@pytest_asyncio.fixture(scope="function")
async def service_repository(uow: UnitOfWork) -> AsyncGenerator[ServiceRepository, None]:
    """Provides a ServiceRepository that shares the session of the given UnitOfWork."""
    async with uow:
        yield ServiceRepository(session=uow.session)


@pytest_asyncio.fixture(scope="function")
async def schedulable_repository(uow: UnitOfWork) -> AsyncGenerator[SchedulableRepository, None]:
    """Provides a SchedulableRepository that shares the session of the given UnitOfWork."""
    async with uow:
        yield SchedulableRepository(session=uow.session)


@pytest_asyncio.fixture(scope="function")
async def test_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Provides a test-specific SQLAlchemy async_sessionmaker.

    This sessionmaker is bound to the function-scoped test engine.
    """
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def client(
    test_session_maker: async_sessionmaker[AsyncSession], tables: None
) -> AsyncGenerator[AsyncClient, None]:
    """Provides an HTTP client for the test suite.

    This fixture overrides the UoW dependency to ensure proper test isolation.
    """

    async def override_get_request_uow(request: Request) -> AsyncGenerator[UnitOfWork, None]:
        """Overrides the request-scoped UoW provider for tests."""
        uow = UnitOfWork(session_factory=test_session_maker)
        request.state.uow = uow  # Manually set on request state
        async with uow:
            yield uow

    # The dependency to override is the one that creates the UoW
    from users.web.graphql.dependencies import get_request_uow as app_get_request_uow

    app.dependency_overrides[app_get_request_uow] = override_get_request_uow

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client_instance:
            yield client_instance
    finally:
        del app.dependency_overrides[app_get_request_uow]  # Clean up the override


def create_auth_headers(user_id: str, supabase_jwt: str = "mock-jwt") -> Dict[str, str]:
    """Creates authentication headers for a given user ID."""
    return {"x-internal-id": str(user_id), "x-supabase-jwt": supabase_jwt}


@pytest_asyncio.fixture(scope="function")
async def seed_data(engine: AsyncEngine, tables: None) -> Dict[str, Any]:
    """Seeds initial data using a dedicated session and commits.
    Returns a dictionary of re-fetched entities.
    """
    _transient_seeded_entities: Dict[str, Any] = {}

    # Create a dedicated session factory for seeding to avoid conflicts
    seed_session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with seed_session_factory() as session:
    user_repo = UserRepository(session)
    service_repo = ServiceRepository(session)
    schedulable_repo = SchedulableRepository(session)

    try:
            # 1. Seed Services
            services_to_seed = {ServiceEnum.meals: {}, ServiceEnum.practice: {}}
        for enum_val, data_val in services_to_seed.items():
                service = await service_repo.create_service({"name": enum_val})
                _transient_seeded_entities[f"service_{enum_val.value}"] = service

            # 2. Seed Users
            user1_coach = await user_repo.create_user({"supabase_id": "coach_user_1"})
            user2_client = await user_repo.create_user({"supabase_id": "client_user_1"})
            user3_client = await user_repo.create_user({"supabase_id": "client_user_2"})
            _transient_seeded_entities["user1_coach"] = user1_coach
            _transient_seeded_entities["user2_client"] = user2_client
            _transient_seeded_entities["user3_client"] = user3_client

            # 3. Link Users to Services
            service_meals = _transient_seeded_entities["service_meals"]
            service_practice = _transient_seeded_entities["service_practice"]
            await user_repo.link_user_to_service(user1_coach.id_, service_meals.id_)
            await user_repo.link_user_to_service(user1_coach.id_, service_practice.id_)
            await user_repo.link_user_to_service(user2_client.id_, service_practice.id_)

            # 4. Assign Roles
            await user_repo.assign_role_to_user(user1_coach.id_, RoleModel.coach, DomainModel.practices)
            await user_repo.assign_role_to_user(user2_client.id_, RoleModel.client, DomainModel.practices)
            await user_repo.assign_role_to_user(user3_client.id_, RoleModel.client, DomainModel.practices)
            # Also give coach a role in another domain for testing
            await user_repo.assign_role_to_user(user1_coach.id_, RoleModel.coach, DomainModel.meals)
            await user_repo.assign_role_to_user(user2_client.id_, RoleModel.client, DomainModel.meals)

            # 5. Seed Associations
            # An ACCEPTED relationship between coach and client1 in PRACTICES
            assoc1_pending = await user_repo.create_association_request(
                coach_id=user1_coach.id_,
                client_id=user2_client.id_,
                requester_id=user1_coach.id_,
                domain=DomainModel.practices,
            )
            assoc1_accepted = await user_repo.update_association_status(
                assoc1_pending.id_, AssociationStatusModel.accepted
            )
            _transient_seeded_entities["assoc_accepted"] = assoc1_accepted

            # A PENDING request from coach to client2 in PRACTICES
            assoc2_pending = await user_repo.create_association_request(
                coach_id=user1_coach.id_,
                client_id=user3_client.id_,
                requester_id=user1_coach.id_,
                domain=DomainModel.practices,
            )
            _transient_seeded_entities["assoc_pending"] = assoc2_pending

            # A REJECTED request from coach to client1 in MEALS
            assoc3_pending = await user_repo.create_association_request(
                coach_id=user1_coach.id_,
                client_id=user2_client.id_,
                requester_id=user1_coach.id_,
                domain=DomainModel.meals,
            )
            assoc3_rejected = await user_repo.update_association_status(
                assoc3_pending.id_, AssociationStatusModel.rejected
            )
            _transient_seeded_entities["assoc_rejected"] = assoc3_rejected

            # 6. Seed Schedulables
            schedulable1 = await schedulable_repo.create_schedulable(
                {
                    "name": "Initial Consultation",
                    "description": "First meeting with the coach.",
                "entity_id": uuid.uuid4(),
                "completed": False,
                    "user_id": user1_coach.id_,
                    "service_id": service_practice.id_,
                }
            )
            _transient_seeded_entities["schedulable1"] = schedulable1

        await session.commit()
            logger.info("SEED_DATA: All data committed.")

    except Exception as e:
            logger.error(f"SEED_DATA: Error during seeding: {e}")
        await session.rollback()
        raise

    # Re-fetch all data in a new session to ensure it's clean and reflects committed state
    refetched_data: Dict[str, Any] = {}
    async with seed_session_factory() as read_session:
        user_repo_read = UserRepository(read_session)
        service_repo_read = ServiceRepository(read_session)
        schedulable_repo_read = SchedulableRepository(read_session)

        # Re-fetch users
        for key in ["user1_coach", "user2_client", "user3_client"]:
            user_model = _transient_seeded_entities[key]
            refetched_data[key] = await user_repo_read.get_user_by_id(user_model.id_)

        # Re-fetch services
        for key in ["service_meals", "service_practice"]:
            service_model = _transient_seeded_entities[key]
            refetched_data[key] = await service_repo_read.get_service_by_id(service_model.id_)

        # Re-fetch associations
        for key in ["assoc_accepted", "assoc_pending", "assoc_rejected"]:
            assoc_model = _transient_seeded_entities[key]
            refetched_data[key] = await user_repo_read.get_association_by_id(assoc_model.id_)

        # Re-fetch schedulables
        for key in ["schedulable1"]:
            sched_model = _transient_seeded_entities[key]
            refetched_data[key] = await schedulable_repo_read.get_schedulable_by_id(sched_model.id_)

    logger.info(f"SEED_DATA: Fixture returning with keys: {list(refetched_data.keys())}")
    return refetched_data
