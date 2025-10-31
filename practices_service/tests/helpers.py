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

from practices.repository.base import Base
from practices.repository.models import (
    Block,
    LoadUnit,
    MetricUnit,
    MovementClass,
    MovementTaskModel,
    PrescribedMovementModel,
    SetModel,
)
from tests.conftest import (
    TEST_DB,
    TEST_HTTP_PORT,
    TEST_PASSWORD,
    TEST_POSTGRES_PORT,
    TEST_SCHEMA,
    TEST_USER,
)

TEST_ECHO = os.getenv("TEST_ECHO", "False").lower() == "true"


async def create_tables(engine: AsyncEngine) -> None:
    """Create the database tables."""
    async with engine.begin() as conn:
        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {TEST_SCHEMA}"))
        await conn.run_sync(Base.metadata.create_all)
        if os.path.exists("db/scripts/triggers"):
            for trigger in os.listdir("db/scripts/triggers"):
                with open(f"db/scripts/triggers/{trigger}", "r") as f:
                    trigger_ddl = DDL(f.read())
                    await conn.execute(trigger_ddl)
    await engine.dispose()
    print("Database tables created")


async def seed_db(engine: AsyncEngine, num_tasks: int = 10) -> None:
    """Seed the database with test data."""
    async_session = async_sessionmaker(engine)
    async with async_session() as session:
        # Create `num_tasks` MovementTasks
        for i in range(num_tasks):
            movement_task = MovementTaskModel(
                title=f"Test Movement Task {i+1}",
                description=f"Test Movement Task {i+1} Description",
                duration=random.uniform(10, 60),
                complete=False,
                movements=[
                    PrescribedMovementModel(
                        name=f"Test Prescribed Movement {j+1}",
                        description=f"Test Prescribed Movement {j+1} Description",
                        metric_unit=random.choice(list(MetricUnit)),
                        metric_value=random.uniform(1, 10),
                        prescribed_sets=random.randint(1, 10),
                        block=random.choice(list(Block)),
                        movement_class=random.choice(list(MovementClass)),
                        sets=[
                            SetModel(
                                reps=random.randint(1, 10),
                                duration=random.uniform(1, 10),
                                perceived_exertion=random.randint(1, 4),
                                load_value=random.uniform(1, 10),
                                load_unit=random.choice(list(LoadUnit)),
                            )
                            for _ in range(random.randint(1, 10))
                        ],
                    )
                    for j in range(random.randint(1, 10))
                ],
            )
            await session.flush()
        await session.commit()


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

    # Run the async function
    engine = create_async_engine(
        f"postgresql+asyncpg://{TEST_USER}:{TEST_PASSWORD}@localhost:{TEST_POSTGRES_PORT}/{TEST_DB}",
        echo=TEST_ECHO,
    )
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
    uvicorn.run("practices.web.app:app", host="0.0.0.0", port=TEST_HTTP_PORT, reload=True)


if __name__ == "__main__":
    main()
