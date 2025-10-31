import asyncio
import atexit
import os
import random
import time
import uuid
from typing import Optional

import docker
import uvicorn
from sqlalchemy import DDL, text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from tests.conftest import (
    TEST_DATABASE_URL,
    TEST_DB,
    TEST_HTTP_PORT,
    TEST_PASSWORD,
    TEST_POSTGRES_PORT,
    TEST_SCHEMA,
    TEST_USER,
)
from users.repository.database import Base
from users.repository.models import (
    SchedulableModel,
    ServiceEnum,
    ServiceModel,
    UserModel,
    UserServicesModel,
)

TEST_ECHO = os.getenv("TEST_ECHO", "False").lower() == "true"


async def create_tables(engine: AsyncEngine) -> None:
    """Create the database tables."""
    async with engine.begin() as conn:
        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {TEST_SCHEMA}"))

        # Create the service enum type
        await conn.execute(
            text(
                """
            CREATE TYPE users.service_type AS ENUM (
                'meals',
                'practice', 
                'shadow_boxing',
                'fitness_db',
                'programs'
            )
        """
            )
        )

        await conn.run_sync(Base.metadata.create_all)

        # Create the automatic timestamp update function
        await conn.execute(
            text(
                """
            CREATE OR REPLACE FUNCTION users.update_modified_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.modified_at = clock_timestamp();
                RETURN NEW;
            END;
            $$ language 'plpgsql'
        """
            )
        )

        # Add triggers for timestamp updates
        triggers = [
            "CREATE TRIGGER update_users_modified_at BEFORE UPDATE ON users.users FOR EACH ROW EXECUTE FUNCTION users.update_modified_at_column()",
            "CREATE TRIGGER update_services_modified_at BEFORE UPDATE ON users.services FOR EACH ROW EXECUTE FUNCTION users.update_modified_at_column()",
            "CREATE TRIGGER update_user_services_modified_at BEFORE UPDATE ON users.user_services FOR EACH ROW EXECUTE FUNCTION users.update_modified_at_column()",
            "CREATE TRIGGER update_schedulables_modified_at BEFORE UPDATE ON users.schedulables FOR EACH ROW EXECUTE FUNCTION users.update_modified_at_column()",
        ]

        for trigger in triggers:
            await conn.execute(text(trigger))

    await engine.dispose()
    print("Database tables created")


async def seed_db(engine: AsyncEngine, num_users: int = 5) -> None:
    """Seed the database with test data."""
    async_session = async_sessionmaker(engine)
    async with async_session() as session:
        # Create default services first
        services_data = [
            ("meals", "Meals", "Nutrition and meal planning service", ServiceEnum.MEALS),
            ("practice", "Practice", "General practice and skill development", ServiceEnum.PRACTICE),
            ("shadow_boxing", "Shadow Boxing", "Boxing training and technique practice", ServiceEnum.SHADOW_BOXING),
            ("fitness_db", "Fitness DB", "Workout and exercise tracking", ServiceEnum.FITNESS_DB),
            ("programs", "Programs", "Structured learning and training programs", ServiceEnum.PROGRAMS),
        ]

        services = []
        for service_id, name, description, service_type in services_data:
            service = ServiceModel(service_id=service_id, name=name, description=description, service_type=service_type)
            session.add(service)
            services.append(service)

        await session.flush()

        # Create test users
        users = []
        for i in range(num_users):
            user = UserModel(supabase_id=f"test_supabase_user_{i+1}", keycloak_id=None)  # Not using keycloak yet
            session.add(user)
            users.append(user)

        await session.flush()

        # Link users to random services
        for user in users:
            # Each user gets linked to 2-4 random services
            linked_services = random.sample(services, random.randint(2, 4))
            for service in linked_services:
                user_service = UserServicesModel(user_id=user.id_, service_id=service.service_id, active=True)
                session.add(user_service)

        await session.flush()

        # Create some schedulable items for testing
        for user in users:
            user_services = [us for us in user.service_links if us.active]
            for user_service in user_services:
                # Create 1-3 schedulables per service for this user
                for j in range(random.randint(1, 3)):
                    schedulable = SchedulableModel(
                        name=f"Test Task {j+1} for {user_service.service.name}",
                        description=f"Sample schedulable task from {user_service.service.name} service",
                        entity_id=uuid.uuid4(),  # Simulated foreign key to external service
                        completed=random.choice([True, False]),
                        user_id=user.id_,
                        service_id=user_service.service_id,
                    )
                    session.add(schedulable)

        await session.commit()
        print(f"Database seeded with {num_users} users and sample data")


def main() -> None:
    # Initialize Docker client
    client = docker.DockerClient(base_url=os.getenv("DOCKER_HOST", "unix:///var/run/docker.sock"))

    # Stop and remove container if it exists
    try:
        container = client.containers.get(TEST_DB)
        container.stop()
        container.remove()
        print(f"Removed existing container: {TEST_DB}")
    except docker.errors.NotFound:
        print(f"No existing container named {TEST_DB}")

    # Start a new container
    container = client.containers.run(
        image="postgres:latest",
        name=TEST_DB,
        environment={
            "POSTGRES_USER": TEST_USER,
            "POSTGRES_PASSWORD": TEST_PASSWORD,
            "POSTGRES_DB": TEST_DB,
        },
        ports={"5432/tcp": TEST_POSTGRES_PORT},
        detach=True,
    )
    print(f"Started container: {TEST_DB}")

    # Wait for container to be ready
    time.sleep(2.5)
    print("Database container is ready")

    # Set environment variables for the app to use test database
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    os.environ["HTTP_PORT"] = str(TEST_HTTP_PORT)

    # Run the async function
    engine = create_async_engine(TEST_DATABASE_URL, echo=TEST_ECHO)
    asyncio.run(create_tables(engine))
    asyncio.run(seed_db(engine))

    # Register shutdown handler to stop and remove container
    def cleanup_container() -> None:
        try:
            container = client.containers.get(TEST_DB)
            container.stop()
            container.remove()
            print(f"Stopped and removed container: {TEST_DB}")
        except Exception as e:
            print(f"Error cleaning up container: {e}")

    atexit.register(cleanup_container)

    # Use import string instead of app object to enable reload
    print(f"Starting server on port {TEST_HTTP_PORT}")
    uvicorn.run("users.web.app:app", host="0.0.0.0", port=TEST_HTTP_PORT, reload=True)


if __name__ == "__main__":
    main()
