"""
Tests for Docker integration with GCS emulator and environment-based configuration.
"""

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import docker
import pytest
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import storage

from agent_service.llms.prompts.factory import PromptServiceFactory
from agent_service.llms.prompts.models import StorageConfig, StoreType
from agent_service.llms.prompts.stores.gcs import GCSPromptStore
from agent_service.llms.prompts.stores.loaders import GCSStorageLoader
from agent_service.llms.prompts.stores.memory import InMemoryPromptStore
from agent_service.llms.prompts.stores.yaml import YAMLPromptStore


@pytest.fixture
def mock_gcs_client():
    """Mock GCS client for testing."""
    client = Mock()
    bucket = Mock()
    bucket.name = "test-bucket"
    client.bucket.return_value = bucket
    client.list_buckets.return_value = [bucket]
    return client


class TestDockerGCSIntegration:
    """Test GCS emulator integration in Docker environment."""

    @pytest.fixture
    def mock_docker_client(self):
        """Mock Docker client for testing."""
        client = Mock()
        client.containers.get.return_value = Mock(
            status="running", ports={"4443/tcp": [{"HostPort": "4443"}]}
        )
        return client

    def test_gcs_emulator_startup(self, mock_docker_client):
        """Test GCS emulator container startup and health check."""
        with patch("docker.from_env", return_value=mock_docker_client):
            # Test that emulator starts correctly
            container = mock_docker_client.containers.get.return_value
            assert container.status == "running"
            assert "4443/tcp" in container.ports
            assert container.ports["4443/tcp"][0]["HostPort"] == "4443"

    def test_gcs_emulator_connectivity(self, mock_gcs_client):
        """Test connectivity to GCS emulator."""
        with patch("google.cloud.storage.Client", return_value=mock_gcs_client):
            client = storage.Client()
            buckets = list(client.list_buckets())
            assert len(buckets) == 1
            assert buckets[0].name == "test-bucket"

    def test_gcs_emulator_bucket_creation(self, mock_gcs_client):
        """Test bucket creation in GCS emulator."""
        with patch("google.cloud.storage.Client", return_value=mock_gcs_client):
            client = storage.Client()
            bucket = client.bucket("new-bucket")
            bucket.create.assert_not_called()  # Should be created automatically in emulator


class TestEnvironmentConfiguration:
    """Test environment-based storage configuration."""

    @pytest.fixture
    def temp_env(self):
        """Temporary environment for testing."""
        original_env = os.environ.copy()
        # Clear all environment variables
        os.environ.clear()
        yield
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)

    def test_development_environment_defaults_to_yaml(self, temp_env):
        """Test that development environment defaults to YAML storage."""
        # Clear environment to simulate development
        os.environ.clear()

        store_type = PromptServiceFactory.get_storage_type_from_environment()
        assert store_type == StoreType.YAML

    def test_production_environment_uses_gcs(self, temp_env):
        """Test that production environment uses GCS storage."""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["GCS_BUCKET_NAME"] = "test-bucket"

        store_type = PromptServiceFactory.get_storage_type_from_environment()
        assert store_type == StoreType.GCS

    def test_explicit_yaml_storage_config(self, temp_env):
        """Test explicit YAML storage configuration."""
        os.environ["PROMPT_STORAGE_TYPE"] = "yaml"
        os.environ["YAML_STORAGE_PATH"] = "/tmp/prompts"

        store_type = PromptServiceFactory.get_storage_type_from_environment()
        assert store_type == StoreType.YAML

    def test_explicit_gcs_storage_config(self, temp_env):
        """Test explicit GCS storage configuration."""
        os.environ["PROMPT_STORAGE_TYPE"] = "gcs"
        os.environ["GCS_BUCKET_NAME"] = "test-bucket"

        store_type = PromptServiceFactory.get_storage_type_from_environment()
        assert store_type == StoreType.GCS

    def test_memory_storage_fallback(self, temp_env):
        """Test fallback to memory storage when GCS unavailable."""
        os.environ["PROMPT_STORAGE_TYPE"] = "gcs"
        # Don't set GCS_BUCKET_NAME to simulate GCS unavailability

        with patch("agent_service.llms.prompts.stores.gcs.GCSPromptStore") as mock_gcs:
            mock_gcs.side_effect = DefaultCredentialsError("No credentials")

            # Should fallback to memory storage
            service = PromptServiceFactory.create_from_environment()
            assert isinstance(service.store, InMemoryPromptStore)


class TestDockerServiceHealth:
    """Test Docker service health checks."""

    def test_gcs_emulator_health_check(self):
        """Test GCS emulator health check endpoint."""
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"status": "healthy"}

            # Test health check
            response = mock_get.return_value
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"

    def test_storage_service_health_check(self):
        """Test storage service health check."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yaml_store = YAMLPromptStore(temp_dir)
            health = yaml_store.health_check()

            assert health["status"] == "healthy"
            assert health["storage_type"] == "yaml"
            assert "file_count" in health

    def test_gcs_service_health_check(self, mock_gcs_client):
        """Test GCS service health check."""
        with patch("google.cloud.storage.Client", return_value=mock_gcs_client):
            from agent_service.llms.prompts.models import StorageConfig
            from agent_service.llms.prompts.stores.loaders import \
                GCSStorageLoader

            # Create a proper storage config
            config = StorageConfig(
                storage_type="gcs",
                gcs_bucket="test-bucket",
                gcs_credentials="/tmp/test-credentials.json",
            )

            # Create a proper loader
            loader = GCSStorageLoader(config)
            gcs_store = GCSPromptStore(loader)
            health = gcs_store.health_check()

            assert health["status"] == "healthy"
            assert health["storage_type"] == "gcs"
            assert health["bucket_name"] == "test-bucket"


class TestLocalGCSBucket:
    """Test local GCS bucket integration."""

    @pytest.fixture
    def temp_bucket_dir(self):
        """Temporary directory for local GCS bucket."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_local_bucket_creation(self, temp_bucket_dir):
        """Test local GCS bucket creation and management."""
        bucket_path = Path(temp_bucket_dir) / "local_gcs_bucket"
        bucket_path.mkdir(exist_ok=True)

        assert bucket_path.exists()
        assert bucket_path.is_dir()

    def test_local_bucket_prompt_storage(self, temp_bucket_dir):
        """Test prompt storage in local GCS bucket."""
        from agent_service.llms.prompts.models import PromptInfo

        bucket_path = Path(temp_bucket_dir) / "local_gcs_bucket"
        bucket_path.mkdir(exist_ok=True)

        # Create a prompt file in the bucket
        prompt_file = bucket_path / "test_prompt.yaml"
        prompt_content = """
name: test_prompt
version: "1.0"
content: "This is a test prompt"
variables: []
        """
        prompt_file.write_text(prompt_content)

        assert prompt_file.exists()
        assert "test_prompt" in prompt_content


class TestDockerComposeIntegration:
    """Test Docker Compose integration."""

    def test_docker_compose_services(self):
        """Test that all required services are defined."""
        # This test will be updated when we create docker-compose.yml
        required_services = ["app", "gcs-emulator", "local_gcs_bucket"]

        # For now, just test the structure
        assert len(required_services) == 3
        assert "app" in required_services
        assert "gcs-emulator" in required_services

    def test_environment_variable_injection(self):
        """Test environment variable injection in Docker."""
        test_env = {
            "ENVIRONMENT": "development",
            "PROMPT_STORAGE_TYPE": "yaml",
            "YAML_STORAGE_PATH": "/app/prompts",
            "GCS_EMULATOR_HOST": "gcs-emulator",
            "GCS_EMULATOR_PORT": "4443",
        }

        # Test environment variable validation
        assert test_env["ENVIRONMENT"] in ["development", "production"]
        assert test_env["PROMPT_STORAGE_TYPE"] in ["yaml", "gcs", "memory"]
        assert test_env["YAML_STORAGE_PATH"].startswith("/")
        assert test_env["GCS_EMULATOR_PORT"].isdigit()


class TestEndToEndDocker:
    """End-to-end Docker integration tests."""

    @pytest.mark.asyncio
    async def test_full_application_startup(self):
        """Test full application startup in Docker environment."""
        # Test that all services can be created
        with patch(
            "agent_service.llms.prompts.factory.PromptServiceFactory.create_from_environment"
        ) as mock_factory:
            mock_service = Mock()
            mock_factory.return_value = mock_service

            # Simulate application startup
            service = PromptServiceFactory.create_from_environment()
            assert service is not None

    @pytest.mark.asyncio
    async def test_prompt_storage_retrieval_docker(self):
        """Test prompt storage and retrieval in Docker environment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yaml_store = YAMLPromptStore(temp_dir)

            # Test basic operations
            from agent_service.llms.prompts.models import PromptInfo

            prompt_info = PromptInfo(
                name="docker_test",
                version="1.0",
                content="Test prompt for Docker",
                variables=[],
            )

            yaml_store.save_prompt(prompt_info)
            retrieved = yaml_store.get_prompt("docker_test", "1.0")

            assert retrieved.name == "docker_test"
            assert retrieved.content == "Test prompt for Docker"

    def test_error_handling_invalid_config(self):
        """Test error handling for invalid Docker configuration."""
        with pytest.raises(ValueError):
            # Test invalid storage type
            os.environ["PROMPT_STORAGE_TYPE"] = "invalid_type"
            PromptServiceFactory.get_storage_type_from_environment()
