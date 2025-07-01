import asyncio
import logging
import os
import time
from typing import AsyncGenerator
from uuid import UUID

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from shared.auth import CurrentUser, UserRole, get_current_user

from agent_service.app.clients.qdrant_client import QdrantClient
from agent_service.app.main import app

# Test configuration for agent service
TEST_QDRANT_PORT = 6334  # Different from production port 6333
TEST_QDRANT_URL = f"http://localhost:{TEST_QDRANT_PORT}"

# Set environment variables for the application's config
os.environ["TESTING"] = "True"
os.environ["QDRANT_URL"] = TEST_QDRANT_URL
os.environ["OPENAI_API_KEY"] = "test"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost/test"
os.environ["QDRANT_URL"] = "http://test"

logging.basicConfig(level=logging.INFO)


@pytest.fixture(scope="session")
def docker_services():
    """
    Manages Docker containers for test services (Qdrant).
    Session scope ensures they start once and tear down after all tests.
    """
    import docker

    client = None
    containers = {}
    container_configs = {
        "qdrant": {
            "name": "agent_service_test_qdrant",
            "image": "qdrant/qdrant:latest",
            "ports": {"6333/tcp": TEST_QDRANT_PORT},
            "ready_log": "Qdrant gRPC listening on",
        },
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


@pytest.fixture(scope="function")
async def qdrant_client(docker_services):
    """
    Provides a QdrantClient instance connected to the test Qdrant container.
    """
    # Wait a moment for Qdrant to be fully ready
    await asyncio.sleep(1)

    client = QdrantClient(url=TEST_QDRANT_URL)

    # Verify connection
    health = await client.health_check()
    if not health:
        pytest.fail("Could not connect to test Qdrant instance")

    yield client

    # Cleanup: delete any test collections
    try:
        # Access the underlying client to get the list of collections
        response = client.get_client().get_collections()
        collections = response.collections
        for collection in collections:
            # A simple safeguard to avoid deleting non-test collections
            if "test" in collection.name.lower():
                await client.delete_collection(collection.name)
    except Exception as e:
        logging.warning(f"Error cleaning up test collections: {e}")


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Provides an HTTP client for testing the agent service API.
    """
    from shared.auth import CurrentUser, UserRole, get_current_user

    from agent_service.app.main import app

    async def override_get_current_user() -> CurrentUser:
        return CurrentUser(
            id=UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6"),
            roles=[UserRole(role="user", domain="coaching")],
        )

    # Apply overrides
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Create test client
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def user() -> CurrentUser:
    """Provides a test user object consistent with the one used in client auth."""
    return CurrentUser(
        id=UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6"),
        roles=[UserRole(role="user", domain="coaching")],
    )
