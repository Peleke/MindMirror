import asyncio
import logging
import os
import time
import uuid
from datetime import date, datetime
from typing import Any, AsyncGenerator, Generator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from meals.repository.models import (
    FoodItemModel,
    MealFoodModel,
    MealModel,
    UserGoalsModel,
    WaterConsumptionModel,
)
from meals.repository.models.base import Base
from meals.repository.models.enums import MealType
from meals.repository.repositories import (
    FoodItemRepository,
    MealRepository,
    UserGoalsRepository,
    WaterConsumptionRepository,
)
from meals.repository.uow import UnitOfWork
from meals.repository.uow import get_uow as app_get_uow
from meals.web.app import app
from meals.web.graphql.dependencies import get_uow as meals_app_get_uow

# Test configuration
TEST_DRIVER = "asyncpg"
TEST_USER = os.getenv("POSTGRES_USER", "postgres")
TEST_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
TEST_HOST = os.getenv("POSTGRES_HOST", "localhost")
TEST_POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
TEST_HTTP_PORT = os.getenv("HTTP_PORT", 8001)  # Different port from practices
TEST_DB = os.getenv("POSTGRES_DB", "swae")
TEST_SCHEMA = "meals"
TEST_ECHO = os.getenv("TEST_ECHO", "False").lower() == "true"

# Set environment variables for Config to pick up during tests
os.environ["DB_USER"] = TEST_USER
os.environ["DB_PASSWORD"] = TEST_PASSWORD
os.environ["DB_HOST"] = TEST_HOST
os.environ["DB_PORT"] = str(TEST_POSTGRES_PORT)
os.environ["DB_NAME"] = TEST_DB

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
            container = client.containers.get("meals_test_db")
            if container.status == "running":
                logging.info("Reusing existing running meals_test_db container.")
            else:
                logging.info("Found existing meals_test_db container, stopping and removing.")
                container.stop()
                container.remove()
                raise docker.errors.NotFound(
                    f"Container meals_test_db not found. Please ensure the container is running and accessible."
                )  # Force re-creation
        except docker.errors.NotFound:
            logging.info("Starting new meals_test_db container.")
            container = client.containers.run(
                image="postgres:latest",
                name="meals_test_db",
                environment={
                    "POSTGRES_USER": TEST_USER,
                    "POSTGRES_PASSWORD": TEST_PASSWORD,
                    "POSTGRES_DB": TEST_DB,
                },
                ports={"5432/tcp": TEST_POSTGRES_PORT},
                detach=True,
            )
            logging.info(f"Waiting for meals_test_db container to be ready (PID: {container.id[:12]})...")
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
                        logging.info("PostgreSQL in meals_test_db is ready.")
                        break
                    else:
                        logging.info(
                            f"PostgreSQL not ready yet (attempt {i+1}/{max_retries}). Current status: {container.status}"
                        )
                else:
                    logging.warning(
                        f"Container meals_test_db status is {container.status} (attempt {i+1}/{max_retries})."
                    )
                if i == max_retries - 1:
                    logs = container.logs().decode("utf-8")
                    logging.error(f"Container meals_test_db did not become ready. Logs:\n{logs}")
                    pytest.fail("Test DB container did not become ready.")

        yield

    # tear down the container
    finally:
        if container and os.getenv("PYTEST_KEEP_DB_CONTAINER", "false").lower() != "true":
            try:
                logging.info(f"Stopping and removing meals_test_db container (ID: {container.id[:12]}).")
                container.stop()
                container.remove()
            except docker.errors.NotFound:
                logging.warning("meals_test_db container not found during teardown (already removed?).")
            except docker.errors.APIError as e:
                logging.warning(f"APIError during container teardown (already being removed or Docker issue?): {e}")
        elif container:
            logging.info("PYTEST_KEEP_DB_CONTAINER is set to true. meals_test_db container will not be removed.")
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
    engine = create_async_engine(db_url, echo=TEST_ECHO)
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
        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {TEST_SCHEMA}"))
        logging.info(f"Creating all tables in schema {TEST_SCHEMA}...")
        await conn.run_sync(Base.metadata.create_all)
        logging.info("Tables created.")
    yield


@pytest_asyncio.fixture(scope="function")
async def test_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Provides a test-specific SQLAlchemy async_sessionmaker.

    This sessionmaker is bound to the function-scoped test engine.
    """
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def uow(test_session_maker: async_sessionmaker[AsyncSession]) -> AsyncGenerator[UnitOfWork, None]:
    """Provides a UnitOfWork instance configured with a test-specific session factory.

    This UoW is suitable for use in tests that directly interact with services or repositories.
    """
    test_uow = UnitOfWork(session_factory=test_session_maker)
    logging.debug(f"Test UoW created with session factory: {test_session_maker}")
    yield test_uow
    # No explicit cleanup needed here for the UoW instance itself,
    # as its sessions are managed by its __aenter__/__aexit__ and the factory is function-scoped.


@pytest_asyncio.fixture(scope="function")
async def client(test_session_maker: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncClient, None]:
    """Provide an HTTP client for testing API endpoints.

    This fixture yields an AsyncClient that can be used to make requests to the API
    during tests. For GraphQL tests, this will point to the GraphQL endpoint.
    It also overrides the UoW dependency for proper test isolation.
    """

    async def override_get_uow() -> AsyncGenerator[UnitOfWork, None]:
        # Use the test_session_maker from the outer fixture scope
        uow_instance = UnitOfWork(session_factory=test_session_maker)
        logging.debug(f"Overridden UoW created with session factory: {test_session_maker} for client request")
        try:
            yield uow_instance
        finally:
            # Ensure session is closed if __aexit__ wasn't reached or UoW wasn't used with 'async with'
            if uow_instance._session:  # Accessing protected member for cleanup in test override
                logging.debug(f"Cleaning up overridden UoW session: {uow_instance._session}")
                await uow_instance.close()

    app.dependency_overrides[meals_app_get_uow] = override_get_uow

    try:
        # TEST_HTTP_PORT is defined at the top of this conftest.py (e.g., 8001 for meals)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url=f"http://localhost:{TEST_HTTP_PORT}"
        ) as client_instance:
            yield client_instance
    finally:
        del app.dependency_overrides[meals_app_get_uow]  # Clean up the override


@pytest_asyncio.fixture(scope="function")
async def seed_db(session: AsyncSession, create_tables: None) -> AsyncGenerator[dict[str, Any], None]:
    """Seed the database with test data.

    This fixture populates the database with predefined test data, including
    food items, meals, user goals, and water consumption records to facilitate testing.
    """
    logging.info("Seeding database...")

    TEST_USER_ID_FOR_FIXTURE = "test-user-123"  # Same as user_goals user_id for consistency

    # Create test food items
    apple = FoodItemModel(
        name="Apple",
        serving_size=100.0,
        serving_unit="g",
        calories=52.0,
        protein=0.3,
        carbohydrates=14.0,
        fat=0.2,
        fiber=2.4,
        sugar=10.4,
        vitamin_d=0.0,
        calcium=6.0,
        iron=0.12,
        potassium=107.0,
        user_id=TEST_USER_ID_FOR_FIXTURE,  # User specific
        notes="Crisp red apple from fixture",
    )
    session.add(apple)

    chicken_breast = FoodItemModel(
        name="Chicken Breast",
        serving_size=100.0,
        serving_unit="g",
        calories=165.0,
        protein=31.0,
        carbohydrates=0.0,
        fat=3.6,
        saturated_fat=1.0,
        cholesterol=85.0,
        sodium=74.0,
        potassium=256.0,
        iron=0.7,
        user_id=TEST_USER_ID_FOR_FIXTURE,  # User specific
        notes="Skinless chicken breast from fixture",
    )
    session.add(chicken_breast)
    await session.flush()  # Flush after adding all food items

    oatmeal = FoodItemModel(
        name="Oatmeal",
        serving_size=100.0,
        serving_unit="g",
        calories=389.0,
        protein=16.9,
        carbohydrates=66.3,
        fat=6.9,
        fiber=10.6,
        sugar=0.0,
        iron=4.7,
        calcium=54.0,
        potassium=429.0,
        user_id=None,  # Public item
        notes="Plain oatmeal from fixture",
    )
    session.add(oatmeal)
    await session.flush()  # Flush after adding all food items

    # Create test meal
    test_meal = MealModel(
        name="Breakfast",
        type=MealType.BREAKFAST,
        date=datetime.now(),
        notes="Healthy breakfast",
        user_id="test-user-123",
    )
    session.add(test_meal)
    await session.flush()  # Ensure test_meal.id_ is populated before creating MealFoodModel instances

    # Create meal-food relationships
    meal_food1 = MealFoodModel(
        meal_id=test_meal.id_,
        food_item_id=apple.id_,
        quantity=150.0,
        serving_unit="g",
    )
    session.add(meal_food1)

    meal_food2 = MealFoodModel(
        meal_id=test_meal.id_,
        food_item_id=oatmeal.id_,
        quantity=50.0,
        serving_unit="g",
    )
    session.add(meal_food2)

    # Create user goals
    user_goals = UserGoalsModel(
        user_id="test-user-123",
        daily_calorie_goal=2000.0,
        daily_water_goal=2000.0,
        daily_protein_goal=150.0,
        daily_carbs_goal=250.0,
        daily_fat_goal=67.0,
    )
    session.add(user_goals)

    # Create water consumption records
    water1 = WaterConsumptionModel(
        user_id="test-user-123",
        quantity=500.0,
        consumed_at=datetime.now(),
    )
    session.add(water1)

    water2 = WaterConsumptionModel(
        user_id="test-user-123",
        quantity=300.0,
        consumed_at=datetime.now(),
    )
    session.add(water2)

    await session.commit()
    logging.info("Database seeding committed.")

    # Refresh all models to get their updated state and relationships
    await session.refresh(apple)
    await session.refresh(chicken_breast)
    await session.refresh(oatmeal)
    await session.refresh(test_meal)
    await session.refresh(meal_food1)
    await session.refresh(meal_food2)
    await session.refresh(user_goals)
    await session.refresh(water1)
    await session.refresh(water2)

    logging.info("Refreshed seeded models.")

    yield {
        "apple": apple,
        "chicken_breast": chicken_breast,
        "oatmeal": oatmeal,
        "test_meal": test_meal,
        "meal_food1": meal_food1,
        "meal_food2": meal_food2,
        "user_goals": user_goals,
        "water1": water1,
        "water2": water2,
    }


@pytest_asyncio.fixture(scope="function")
async def food_item_repository(uow: UnitOfWork) -> AsyncGenerator[FoodItemRepository, None]:
    """Provide a FoodItemRepository for testing."""
    async with uow as uow_instance:
        repo = FoodItemRepository(uow_instance.session)
        yield repo


@pytest_asyncio.fixture(scope="function")
async def meal_repository(uow: UnitOfWork) -> AsyncGenerator[MealRepository, None]:
    """Provide a MealRepository for testing."""
    async with uow as uow_instance:
        repo = MealRepository(uow_instance.session)
        yield repo


@pytest_asyncio.fixture(scope="function")
async def user_goals_repository(uow: UnitOfWork) -> AsyncGenerator[UserGoalsRepository, None]:
    """Provide a UserGoalsRepository for testing."""
    async with uow as uow_instance:
        repo = UserGoalsRepository(uow_instance.session)
        yield repo


@pytest_asyncio.fixture(scope="function")
async def water_consumption_repository(uow: UnitOfWork) -> AsyncGenerator[WaterConsumptionRepository, None]:
    """Provide a WaterConsumptionRepository for testing."""
    async with uow as uow_instance:
        repo = WaterConsumptionRepository(uow_instance.session)
        yield repo
