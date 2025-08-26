import asyncio
import logging
import os
import time
import uuid
from datetime import date, timedelta
from typing import Any, AsyncGenerator, Generator, Optional, Union
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from google.cloud import storage
from httpx import ASGITransport, AsyncClient
from shared.auth import CurrentUser
from shared.data_models import UserRole
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, sessionmaker
from starlette.requests import Request

from practices.repository.models import (
    ProgramModel,
    ProgramPracticeLinkModel,
    ProgramTagModel,
)
from practices.repository.models.base import Base
from practices.repository.models.enrollment import (
    EnrollmentStatus,
    ProgramEnrollmentModel,
)
from practices.repository.models.practice_instance import (
    MovementInstanceModel,
    PracticeInstanceModel,
    PrescriptionInstanceModel,
    SetInstanceModel,
)
from practices.repository.models.practice_template import (
    MovementTemplateModel,
    PracticeTemplateModel,
    PrescriptionTemplateModel,
    SetTemplateModel,
)
from practices.repository.models.progress import ScheduledPracticeModel
from practices.repository.repositories import (
    EnrollmentRepository,
    PracticeInstanceRepository,
    PracticeTemplateRepository,
    ProgramRepository,
)
from practices.repository.uow import UnitOfWork
from practices.repository.uow import get_uow as app_get_uow
from practices.service.services import (
    PracticeInstanceService,
    PracticeTemplateService,
    ProgramService,
)
from practices.web.app import app, create_app
from practices.web.config import Config

API_VERSION = Config.API_VERSION

TEST_DRIVER = "asyncpg"
TEST_USER = os.getenv("POSTGRES_USER", "postgres")
TEST_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
TEST_HOST = os.getenv("POSTGRES_HOST", "localhost")
TEST_POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
TEST_HTTP_PORT = os.getenv("HTTP_PORT", 8000)
TEST_DB = os.getenv("POSTGRES_DB", "swae")
TEST_SCHEMA = "practices"
TEST_ECHO = os.getenv("TEST_ECHO", "False").lower() == "true"
TEST_GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "swae-aa835")
TEST_GCS_BUCKET_NAME = f"{TEST_GCP_PROJECT_ID}-{str(uuid.uuid4())[:8]}"
TEST_VIDEO_NAME = "test.mp4"
BASE_URL = f"http://localhost:{TEST_HTTP_PORT}/api/{API_VERSION}"

# Define static user UUIDs for consistent testing
COACH_USER_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
CLIENT_USER_ID_ONE = uuid.UUID("22222222-2222-2222-2222-222222222222")  # Coached by COACH_USER_ID
CLIENT_USER_ID_TWO = uuid.UUID("33333333-3333-3333-3333-333333333333")  # Not coached by COACH_USER_ID
UNRELATED_USER_ID = uuid.UUID("44444444-4444-4444-4444-444444444444")

# Set environment variables for Config to pick up during tests
# This ensures the app uses the test database settings
os.environ["DB_USER"] = TEST_USER
os.environ["DB_PASSWORD"] = TEST_PASSWORD
os.environ["DB_HOST"] = TEST_HOST
os.environ["DB_PORT"] = str(TEST_POSTGRES_PORT)  # Must be string for os.getenv in Config if it were to parse int
os.environ["DB_NAME"] = TEST_DB
# Optionally, directly set the full DATABASE_URL if preferred to bypass Config's f-string construction for tests:
# os.environ["DATABASE_URL"] = f"postgresql+{TEST_DRIVER}://{TEST_USER}:{TEST_PASSWORD}@{TEST_HOST}:{TEST_POSTGRES_PORT}/{TEST_DB}"


logging.basicConfig(level=logging.WARNING)


@pytest.fixture(scope="function")
def docker_compose_up_down() -> Generator[None, None, None]:
    """Start docker-compose before tests and tear it down after.

    This fixture manages the lifecycle of a Docker container running the test database.
    It ensures that the container is started before tests are run and stopped afterwards.
    """
    import docker

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
    """Create an asynchronous SQLAlchemy engine for database interactions.

    This fixture initializes the database engine and ensures it is disposed of
    after the tests are completed.
    """
    db_url = f"postgresql+{TEST_DRIVER}://{TEST_USER}:{TEST_PASSWORD}@{TEST_HOST}:{TEST_POSTGRES_PORT}/{TEST_DB}"
    logging.info(f"Creating engine with URL: {db_url}")
    engine = create_async_engine(
        db_url,
        echo=TEST_ECHO,
        connect_args={"ssl": "disable"},
        pool_size=10,
        max_overflow=20,
    )
    try:
        yield engine
    finally:
        logging.info("Disposing engine.")
        await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create a new SQLAlchemy session for each test.

    This fixture provides an asynchronous session that can be used to interact
    with the database during tests.
    """
    async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session_factory() as session_:
        logging.info(f"Session created: {session_}")
        try:
            yield session_
        finally:
            logging.info(f"Closing session: {session_}")
            await session_.close()


@pytest_asyncio.fixture(scope="function")
async def create_tables(engine: AsyncEngine) -> AsyncGenerator[None, None]:
    """Create all tables in the database.

    This fixture ensures that all tables are created in the database before tests are run.
    It first drops the schema if it exists to ensure a clean state.
    """
    async with engine.begin() as conn:
        logging.info(f"Dropping schema {TEST_SCHEMA} if exists...")
        await conn.execute(text(f"DROP SCHEMA IF EXISTS {TEST_SCHEMA} CASCADE"))
        logging.info(f"Creating schema {TEST_SCHEMA}...")
        await conn.execute(text(f"CREATE SCHEMA {TEST_SCHEMA}"))
        logging.info(f"Creating all tables in schema {TEST_SCHEMA}...")
        await conn.run_sync(Base.metadata.create_all)
        logging.info("Tables created.")
    yield


@pytest_asyncio.fixture(scope="function")
def test_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Provide a test-specific SQLAlchemy async_sessionmaker.

    This sessionmaker is bound to the function-scoped test engine.
    """
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def uow(test_session_maker: async_sessionmaker[AsyncSession]) -> AsyncGenerator[UnitOfWork, None]:
    """Provide a unit of work for the test session."""
    async with test_session_maker() as session:
        uow = UnitOfWork(session)
        yield uow


@pytest_asyncio.fixture(scope="function")
async def seed_db(session: AsyncSession, create_tables: None) -> AsyncGenerator[dict[str, Any], None]:
    """Seed the database with initial data for testing."""
    logging.info("Seeding database...")

    # Define users
    coach_user = CurrentUser(id=COACH_USER_ID, roles=[UserRole(role="coach", domain="practices")])
    coach2_user = CurrentUser(id=uuid.uuid4(), roles=[UserRole(role="coach", domain="practices")])
    client_user_one = CurrentUser(
        id=CLIENT_USER_ID_ONE, roles=[UserRole(role="client", domain="practices")]
    )  # Coached by coach_user
    client_user_two = CurrentUser(
        id=CLIENT_USER_ID_TWO, roles=[UserRole(role="client", domain="practices")]
    )  # Not coached by coach_user
    unrelated_client_user = CurrentUser(id=UNRELATED_USER_ID, roles=[UserRole(role="client", domain="practices")])

    # === Create Programs ===
    program = ProgramModel(
        id_=uuid.uuid4(),
        name="Basic Training Program",
        description="A foundational program for beginners",
        level="beginner",
        user_id=coach_user.id,
    )
    
    program2 = ProgramModel(
        id_=uuid.uuid4(),
        name="Intermediate Training Program", 
        description="An intermediate program for progression",
        level="intermediate",
        user_id=coach2_user.id,
    )

    # === Create Practice Templates ===
    practice_template = PracticeTemplateModel(
        id_=uuid.uuid4(),
        title="Push Day Workout",
        description="Upper body push movements",
        user_id=coach_user.id,
        duration=60.0,
    )

    practice_template2 = PracticeTemplateModel(
        id_=uuid.uuid4(),
        title="Pull Day Workout",
        description="Upper body pull movements", 
        user_id=coach_user.id,
        duration=45.0,
    )

    practice_template3 = PracticeTemplateModel(
        id_=uuid.uuid4(),
        title="Leg Day Workout",
        description="Lower body movements",
        user_id=coach_user.id,
        duration=50.0,
    )

    # === Create Template Hierarchy ===
    # 2. Prescription Template (part of the practice template)
    prescription_template = PrescriptionTemplateModel(
        id_=uuid.uuid4(),
        practice_template_id=practice_template.id_,
        name="Main Workout",
        block="workout",
        position=0,
        prescribed_rounds=3,
    )
    # Add a second prescription template for variety
    warmup_prescription_template = PrescriptionTemplateModel(
        id_=uuid.uuid4(),
        practice_template_id=practice_template.id_,
        name="Warm-up",
        block="warmup",
        position=1,
    )

    # 3. Movement Template (part of the prescription template)
    movement_template = MovementTemplateModel(
        id_=uuid.uuid4(),
        prescription_template_id=prescription_template.id_,
        name="Barbell Squat",
        position=0,
        metric_unit="iterative",
        metric_value=8,
        prescribed_sets=3,
        exercise_id=str(uuid.uuid4()),  # Mock exercise DB ID
    )
    movement_template2 = MovementTemplateModel(
        id_=uuid.uuid4(),
        prescription_template_id=prescription_template.id_,
        name="Bench Press",
        position=1,
        metric_unit="iterative",
        metric_value=10,
        prescribed_sets=3,
    )

    # 4. Set Templates (part of the movement template)
    set_templates = [
        SetTemplateModel(
            id_=uuid.uuid4(),
            movement_template_id=movement_template.id_,
            position=i,
            reps=8,
            load_value=135 + (i * 10),
            load_unit="pounds",
            rest_duration=90,
        )
        for i in range(3)
    ]
    movement_template.sets = set_templates
    prescription_template.movements = [movement_template, movement_template2]
    practice_template.prescriptions = [prescription_template, warmup_prescription_template]

    # === Create Program Practice Links ===
    practice_link1 = ProgramPracticeLinkModel(
        id_=uuid.uuid4(),
        program_id=program.id_,
        practice_template_id=practice_template.id_,
        sequence_order=1,
        interval_days_after=2,
    )

    practice_link2 = ProgramPracticeLinkModel(
        id_=uuid.uuid4(),
        program_id=program.id_,
        practice_template_id=practice_template2.id_,
        sequence_order=2,
        interval_days_after=2,
    )

    # === Create Instance Hierarchy (for client_user_one from the template) ===
    # 1. Practice Instance
    practice_instance = PracticeInstanceModel(
        id_=uuid.uuid4(),
        user_id=client_user_one.id,
        template_id=practice_template.id_,
        date=date.today(),
        title=practice_template.title,
    )

    # 2. Prescription Instance
    prescription_instance = PrescriptionInstanceModel(
        id_=uuid.uuid4(),
        practice_instance_id=practice_instance.id_,
        template_id=prescription_template.id_,
        name=prescription_template.name,
        block=prescription_template.block,
        position=prescription_template.position,
    )

    # 3. Movement Instance
    movement_instance = MovementInstanceModel(
        id_=uuid.uuid4(),
        prescription_instance_id=prescription_instance.id_,
        template_id=movement_template.id_,
        name=movement_template.name,
        position=movement_template.position,
        metric_unit=movement_template.metric_unit,
        metric_value=movement_template.metric_value,
        exercise_id=movement_template.exercise_id,
    )
    movement_instance2 = MovementInstanceModel(
        id_=uuid.uuid4(),
        prescription_instance_id=prescription_instance.id_,
        template_id=movement_template2.id_,
        name=movement_template2.name,
        position=movement_template2.position,
        metric_unit=movement_template2.metric_unit,
        metric_value=movement_template2.metric_value,
    )

    # 4. Set Instances
    set_instances = [
        SetInstanceModel(
            id_=uuid.uuid4(),
            movement_instance_id=movement_instance.id_,
            template_id=st.id_,
            position=st.position,
            reps=st.reps,
            load_value=st.load_value,
            load_unit=st.load_unit,
        )
        for st in set_templates
    ]
    movement_instance.sets = set_instances
    prescription_instance.movements = [movement_instance, movement_instance2]
    practice_instance.prescriptions = [prescription_instance]

    # === Create Enrollments ===
    enrollment_one = ProgramEnrollmentModel(
        id_=uuid.uuid4(),
        program_id=program.id_,
        user_id=client_user_one.id,
        status=EnrollmentStatus.ACTIVE,
        current_practice_link_id=practice_link1.id_,  # Start at first practice
    )
    enrollment_two = ProgramEnrollmentModel(
        id_=uuid.uuid4(),
        program_id=program.id_,
        user_id=client_user_two.id,
        status=EnrollmentStatus.ACTIVE,
        current_practice_link_id=practice_link1.id_,  # Start at first practice
    )
    # Add enrollment for unrelated client that tests expect
    enrollment_unrelated = ProgramEnrollmentModel(
        id_=uuid.uuid4(),
        program_id=program2.id_,
        user_id=unrelated_client_user.id,
        status=EnrollmentStatus.ACTIVE,
        current_practice_link_id=practice_link2.id_,
    )

    # Create a scheduled practice for progress tracking
    scheduled_practice = ScheduledPracticeModel(
        id_=uuid.uuid4(),
        enrollment_id=enrollment_one.id_,
        practice_template_id=practice_template.id_,
        practice_instance_id=practice_instance.id_,
        scheduled_date=date.today(),
    )

    # Add all entities to session
    session.add_all([
        # Programs and links
        program,
        program2,
        practice_link1,
        practice_link2,
        # Templates
        practice_template,
        practice_template2,
        practice_template3,
        prescription_template,
        warmup_prescription_template,
        movement_template,
        movement_template2,
        *set_templates,
        # Instances
        practice_instance,
        prescription_instance,
        movement_instance,
        movement_instance2,
        *set_instances,
        # Enrollments and scheduled practices
        enrollment_one,
        enrollment_two,
        enrollment_unrelated,
        scheduled_practice,
    ])

    await session.commit()
    logging.info("Database seeded successfully!")

    yield {
        # Flatten users to top level to match test expectations
        "coach_user": coach_user,
        "coach2_user": coach2_user,
        "client_user_one": client_user_one,
        "client_user_two": client_user_two,
        "unrelated_client_user": unrelated_client_user,
        # Rest of the data
        "programs": [program, program2],
        "practice_templates": [practice_template, practice_template2, practice_template3],
        "prescription_templates": [prescription_template, warmup_prescription_template],
        "movement_templates": [movement_template, movement_template2],
        "set_templates": set_templates,
        "practice_links": [practice_link1, practice_link2],
        "practice_instances": [practice_instance],
        "prescription_instances": [prescription_instance],
        "movement_instances": [movement_instance, movement_instance2],
        "set_instances": set_instances,
        "enrollments": [enrollment_one, enrollment_two, enrollment_unrelated],
        "scheduled_practices": [scheduled_practice],
    }


@pytest.fixture(autouse=True)
def mock_users_service():
    """Mocks the users_service_client for testing authorization checks.
    This mock will be active for all tests automatically.
    """
    with patch(
        "practices.web.graphql.enrollment_resolvers.users_service_client", new_callable=AsyncMock
    ) as mock_client, patch(
        "practices.web.graphql.resolvers.users_service_client", new_callable=AsyncMock
    ) as mock_client_resolvers:

        async def verify_relationship(coach_id: uuid.UUID, client_id: uuid.UUID, domain: str) -> bool:
            # The main coach is only associated with client one
            if coach_id == COACH_USER_ID and client_id == CLIENT_USER_ID_ONE:
                logging.debug(f"Mock verify_relationship: TRUE for coach {coach_id} and client {client_id}")
                return True
            logging.debug(f"Mock verify_relationship: FALSE for coach {coach_id} and client {client_id}")
            return False

        mock_client.verify_coach_client_relationship.side_effect = verify_relationship
        mock_client_resolvers.verify_coach_client_relationship.side_effect = verify_relationship
        yield mock_client


@pytest.fixture(scope="session")
def user_ids() -> dict[str, uuid.UUID]:
    """Provides a dictionary of static test user UUIDs."""
    return {
        "coach": COACH_USER_ID,
        "client_one": CLIENT_USER_ID_ONE,
        "client_two": CLIENT_USER_ID_TWO,
        "unrelated": UNRELATED_USER_ID,
    }


@pytest.fixture
def auth_headers_for(user_ids: dict[str, uuid.UUID]):
    """Fixture to generate authentication headers for a user."""

    def _auth_headers_for(user_key: Union[str, CurrentUser]) -> dict[str, str]:
        """Generate authentication headers for a given user key or CurrentUser object."""
        user_id = None
        if isinstance(user_key, str):
            user_id = user_ids.get(user_key)
        elif isinstance(user_key, CurrentUser):
            user_id = user_key.id

        if not user_id:
            raise ValueError(f"Could not find user ID for key: {user_key}")

        # The test dependency override in the `client` fixture uses this
        # header to mock the CurrentUser object in the request context.
        return {"x-internal-id": str(user_id)}

    return _auth_headers_for


@pytest_asyncio.fixture(scope="function")
async def client(
    test_session_maker: async_sessionmaker[AsyncSession], user_ids: dict[str, uuid.UUID]
) -> AsyncGenerator[AsyncClient, None]:
    """Provides an HTTP client (TestClient) for making requests to the FastAPI app,
    with dependencies overridden for isolated testing.
    """
    from practices.web.graphql.dependencies import CustomContext, get_context

    # This dictionary maps user IDs to their roles for the mock user object.
    user_roles_map = {
        user_ids["coach"]: [UserRole(role="coach", domain="practices")],
        user_ids["client_one"]: [UserRole(role="client", domain="practices")],
        user_ids["client_two"]: [UserRole(role="client", domain="practices")],
        user_ids["unrelated"]: [UserRole(role="client", domain="practices")],
    }

    async def override_get_context(request: Request) -> CustomContext:
        """Override for the get_context dependency.

        This function creates a CustomContext with a mocked UnitOfWork and a
        mocked CurrentUser based on the 'x-internal-id' header from the incoming request.
        """
        user_id_str = request.headers.get("x-internal-id")
        user_id = uuid.UUID(user_id_str) if user_id_str else None

        # Create a mock CurrentUser
        mock_user = None
        if user_id and user_id in user_roles_map:
            mock_user = CurrentUser(id=user_id, roles=user_roles_map[user_id])

        # Create a test-specific UoW
        async with test_session_maker() as session:
            test_uow = UnitOfWork(session=session)
            context = CustomContext(uow=test_uow, current_user=mock_user)
            context.request = request
            return context

    # We must create a new app instance for each test function to ensure
    # that dependency overrides are isolated.
    test_app = create_app()
    test_app.dependency_overrides[get_context] = override_get_context

    # Use ASGITransport for making requests to the app
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Clear overrides after the test
    test_app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def practice_template_repository(
    uow: UnitOfWork,
) -> AsyncGenerator[PracticeTemplateRepository, None]:
    yield PracticeTemplateRepository(uow.session)


@pytest_asyncio.fixture(scope="function")
async def practice_instance_repository(
    uow: UnitOfWork,
) -> AsyncGenerator[PracticeInstanceRepository, None]:
    yield PracticeInstanceRepository(uow.session)


@pytest_asyncio.fixture(scope="function")
async def program_repository(
    uow: UnitOfWork,
) -> AsyncGenerator[ProgramRepository, None]:
    yield ProgramRepository(uow.session)


@pytest_asyncio.fixture(scope="function")
async def enrollment_repository(
    uow: UnitOfWork,
) -> AsyncGenerator[EnrollmentRepository, None]:
    yield EnrollmentRepository(uow.session)


@pytest_asyncio.fixture(scope="function")
async def sample_practice_id(seed_db) -> uuid.UUID:
    """Provides the ID of the first practice instance from the seeded data."""
    return seed_db["practice_instances"][0].id_


@pytest_asyncio.fixture(scope="function")
async def sample_program_id(seed_db) -> uuid.UUID:
    """Provides the ID of the first program from the seeded data."""
    return seed_db["programs"][0].id_
