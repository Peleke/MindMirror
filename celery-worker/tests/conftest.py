import asyncio
import logging
import os
import time
from typing import AsyncGenerator
from uuid import UUID

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from pytest_celery import (
    CeleryBackendCluster,
    CeleryBrokerCluster,
    RedisTestBackend,
    RedisTestBroker,
)
from celery import Celery
from unittest.mock import AsyncMock, MagicMock, patch

from src.celery_app import create_celery_app
from src.config import Config

# Test configuration for celery-worker
TEST_QDRANT_PORT = 6334  # Different from production port 6333
TEST_QDRANT_URL = f"http://localhost:{TEST_QDRANT_PORT}"

# Set environment variables for the application's config
os.environ["TESTING"] = "true"
os.environ["QDRANT_HOST"] = "localhost"
os.environ["QDRANT_PORT"] = "6333"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test_mindmirror"

logging.basicConfig(level=logging.INFO)


@pytest.fixture
def config():
    """Test configuration fixture."""
    # Ensure we're in testing mode
    Config.TESTING = True
    return Config


@pytest.fixture
def mock_qdrant_client():
    """Mock Qdrant client for testing."""
    mock_client = MagicMock()
    mock_client.get_collections.return_value = MagicMock(collections=[])
    mock_client.create_collection.return_value = True
    mock_client.upsert.return_value = MagicMock(status="completed")
    mock_client.search.return_value = []
    return mock_client


@pytest.fixture
def mock_journal_client():
    """Mock journal client for testing."""
    mock_client = AsyncMock()
    mock_client.get_entry_by_id.return_value = {
        "id": "test-entry-id",
        "content": "Test journal entry content",
        "entry_type": "FREEFORM",
        "created_at": "2024-01-01T00:00:00Z",
        "user_id": "test-user-id",
    }
    return mock_client


@pytest.fixture
def mock_embedding_service():
    """Mock embedding service for testing."""
    mock_service = AsyncMock()
    mock_service.get_embedding.return_value = [0.1] * Config.VECTOR_SIZE
    mock_service.get_embeddings.return_value = [[0.1] * Config.VECTOR_SIZE]
    return mock_service


@pytest.fixture
def test_celery_app():
    """Create a test Celery app."""
    app = Celery("test_worker")
    app.conf.update(
        broker_url="memory://",
        result_backend="cache+memory://",
        task_always_eager=True,
        task_eager_propagates=True,
    )
    return app


@pytest.fixture
def mock_journal_entry():
    """Mock journal entry data."""
    return {
        "id": "628b77ec-dad0-4481-9d97-05b2481c260f",
        "user_id": "test-user-123",
        "tradition": "stoicism",
        "content": "Today I practiced mindfulness and gratitude.",
        "entry_type": "FREEFORM",
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:00:00Z",
    }


@pytest.fixture
def mock_vector_embedding():
    """Mock vector embedding."""
    return [0.1, 0.2, 0.3] * (Config.VECTOR_SIZE // 3) + [0.1] * (
        Config.VECTOR_SIZE % 3
    )


@pytest.fixture
def celery_config():
    """Celery configuration for tests."""
    return {
        "broker_url": "memory://",
        "result_backend": "cache+memory://",
        "task_always_eager": True,  # Execute tasks synchronously
        "task_eager_propagates": True,  # Propagate exceptions in eager mode
        "task_track_started": True,
        "broker_connection_retry_on_startup": True,
        "include": [
            "src.tasks.journal_tasks",
            "src.tasks.tradition_tasks",
            "src.tasks.health_tasks",
        ],
    }


@pytest.fixture
def celery_app(celery_config):
    """
    Creates a Celery app for testing with proper configuration.
    """
    app = create_celery_app()
    app.conf.update(celery_config)

    # Apply task routes for testing
    app.conf.task_routes = {
        "celery_worker.tasks.index_journal_entry_task": {
            "priority": 5,
            "routing_key": "indexing",
        },
        "celery_worker.tasks.batch_index_journal_entries_task": {
            "priority": 3,
            "routing_key": "indexing",
        },
        "celery_worker.tasks.health_check_task": {
            "priority": 7,
            "routing_key": "monitoring",
        },
        "celery_worker.tasks.reindex_user_entries_task": {
            "priority": 2,
            "routing_key": "maintenance",
        },
    }

    return app


@pytest.fixture(scope="session")
def docker_services():
    """
    Manages Docker containers for test services (Qdrant).
    Redis is now managed automatically by the pytest-celery plugin.
    Session scope ensures they start once and tear down after all tests.
    """
    import docker

    client = None
    containers = {}
    container_configs = {
        "qdrant": {
            "name": "celery_worker_test_qdrant",
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

    from src.clients.qdrant_client import CeleryQdrantClient

    client = CeleryQdrantClient(host="localhost", port=TEST_QDRANT_PORT)

    # Verify connection
    health = await client.health_check()
    if not health:
        pytest.fail("Could not connect to test Qdrant instance")

    yield client

    # Cleanup: delete any test collections
    try:
        # Access the underlying client to get the list of collections
        response = client.client.get_collections()
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
    Provides an HTTP client for testing the celery-worker API.
    """
    from src.app import app

    # Create test client
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture(scope="function")
async def user():
    """Provides a test user object."""
    return {
        "id": str(UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")),
        "roles": [{"role": "user", "domain": "coaching"}],
    }


@pytest.fixture
def mock_pubsub_client():
    """Mock Pub/Sub client for testing."""
    mock_client = MagicMock()
    mock_client.publish_message.return_value = "test-message-id"
    mock_client.publish_journal_indexing.return_value = "test-message-id"
    mock_client.publish_journal_batch_indexing.return_value = "test-message-id"
    mock_client.publish_journal_reindex.return_value = "test-message-id"
    mock_client.publish_tradition_rebuild.return_value = "test-message-id"
    mock_client.publish_health_check.return_value = "test-message-id"
    return mock_client


@pytest.fixture
def sample_pubsub_message():
    """Sample Pub/Sub message data for testing."""
    return {
        "entry_id": "test-entry-123",
        "user_id": "test-user-456",
        "tradition": "canon-default",
        "task_type": "journal_indexing",
        "metadata": {"source": "test"},
    }


@pytest.fixture
def sample_pubsub_attributes():
    """Sample Pub/Sub message attributes for testing."""
    return {
        "message_id": "test-message-id-123",
        "publish_time": "2024-01-01T00:00:00Z",
        "x-goog-version": "v1",
    }
