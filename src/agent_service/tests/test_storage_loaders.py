"""
Tests for storage loaders and abstraction layer.
"""

import os
import tempfile
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

from agent_service.llms.prompts.exceptions import PromptStorageError
from agent_service.llms.prompts.models import StorageConfig
from agent_service.llms.prompts.stores import (
    GCSPromptStore,
    InMemoryPromptStore,
    LocalPromptStore,
)
from agent_service.llms.prompts.stores.loaders import (
    GCSStorageLoader,
    LocalStorageLoader,
    StorageLoader,
)


class TestStorageLoader:
    """Test the StorageLoader protocol and base functionality."""

    def test_storage_loader_protocol(self):
        """Test that StorageLoader is a proper protocol."""
        # Should be able to create a mock that implements the protocol
        mock_loader = Mock(spec=StorageLoader)
        assert hasattr(mock_loader, "write_file")
        assert hasattr(mock_loader, "read_file")
        assert hasattr(mock_loader, "delete_file")
        assert hasattr(mock_loader, "list_files")
        assert hasattr(mock_loader, "exists")
        assert hasattr(mock_loader, "get_stats")


class TestLocalStorageLoader:
    """Test LocalStorageLoader functionality."""

    def test_create_local_store(self):
        """Test creating a local storage loader."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StorageConfig(storage_type="local", local_path=temp_dir)

            loader = LocalStorageLoader(config)

            assert str(loader.base_path) == temp_dir

    def test_create_local_store_with_invalid_config(self):
        """Test creating local store with invalid configuration."""
        # Test with wrong storage type
        config = StorageConfig(
            storage_type="gcs",
            gcs_bucket="test-bucket",
            gcs_credentials="/path/to/creds.json",
        )

        with pytest.raises(
            PromptStorageError, match="local_path is required for LocalStorageLoader"
        ):
            LocalStorageLoader(config)

    def test_create_local_store_with_missing_path(self):
        """Test creating local store with missing local path."""
        config = StorageConfig(storage_type="local")

        with pytest.raises(
            PromptStorageError, match="local_path is required for LocalStorageLoader"
        ):
            LocalStorageLoader(config)

    def test_create_local_store_creates_directory(self):
        """Test that local store creation creates the directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = os.path.join(temp_dir, "new_prompts")

            config = StorageConfig(storage_type="local", local_path=new_dir)

            loader = LocalStorageLoader(config)

            assert os.path.exists(new_dir)
            assert str(loader.base_path) == new_dir

    def test_create_local_store_with_existing_directory(self):
        """Test creating local store with existing directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StorageConfig(storage_type="local", local_path=temp_dir)

            loader = LocalStorageLoader(config)

            assert str(loader.base_path) == temp_dir


class TestGCSStorageLoader:
    """Test GCSStorageLoader functionality."""

    @patch("google.cloud.storage.Client")
    def test_create_gcs_store(self, mock_client_class):
        """Test creating a GCS storage loader."""
        # Mock the GCS client
        mock_client = Mock()
        mock_client_class.from_service_account_json.return_value = mock_client

        config = StorageConfig(
            storage_type="gcs",
            gcs_bucket="test-bucket",
            gcs_credentials="/path/to/credentials.json",
        )

        loader = GCSStorageLoader(config)

        assert loader.bucket_name == "test-bucket"
        assert loader.credentials_path == "/path/to/credentials.json"
        mock_client_class.from_service_account_json.assert_called_once_with(
            "/path/to/credentials.json"
        )

    def test_create_gcs_store_with_invalid_config(self):
        """Test creating GCS store with invalid configuration."""
        # Test with wrong storage type
        config = StorageConfig(storage_type="local", local_path="/tmp/prompts")

        with pytest.raises(
            PromptStorageError, match="gcs_bucket is required for GCSStorageLoader"
        ):
            GCSStorageLoader(config)

    def test_create_gcs_store_with_missing_bucket(self):
        """Test creating GCS store with missing bucket."""
        config = StorageConfig(storage_type="gcs")

        with pytest.raises(
            PromptStorageError, match="gcs_bucket is required for GCSStorageLoader"
        ):
            GCSStorageLoader(config)

    def test_create_gcs_store_with_missing_credentials(self):
        """Test creating GCS store with missing credentials."""
        config = StorageConfig(storage_type="gcs", gcs_bucket="test-bucket")

        with pytest.raises(
            PromptStorageError, match="gcs_credentials is required for GCSStorageLoader"
        ):
            GCSStorageLoader(config)

    @patch("google.cloud.storage.Client")
    def test_create_gcs_store_with_emulator(self, mock_client_class):
        """Test creating GCS store with emulator configuration."""
        mock_client = Mock()
        # When using emulator, regular Client() constructor is used, not from_service_account_json
        mock_client_class.return_value = mock_client

        config = StorageConfig(
            storage_type="gcs",
            gcs_bucket="test-bucket",
            gcs_credentials="/path/to/credentials.json",
        )

        # Set emulator environment variable
        with patch.dict(os.environ, {"STORAGE_EMULATOR_HOST": "localhost:4443"}):
            loader = GCSStorageLoader(config)

            assert loader.bucket_name == "test-bucket"
            # When using emulator, regular Client() constructor is called, not from_service_account_json
            mock_client_class.assert_called_once_with()
            mock_client_class.from_service_account_json.assert_not_called()

    @patch("google.cloud.storage.Client")
    def test_create_gcs_store_handles_client_error(self, mock_client_class):
        """Test handling of GCS client creation errors."""
        mock_client_class.from_service_account_json.side_effect = Exception(
            "GCS client error"
        )

        config = StorageConfig(
            storage_type="gcs",
            gcs_bucket="test-bucket",
            gcs_credentials="/path/to/credentials.json",
        )

        with pytest.raises(PromptStorageError, match="Failed to initialize GCS client"):
            GCSStorageLoader(config)


class TestStorageLoaderIntegration:
    """Test integration between storage loaders and stores."""

    def test_local_storage_loader_integration(self):
        """Test local storage loader with actual store operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StorageConfig(storage_type="local", local_path=temp_dir)

            loader = LocalStorageLoader(config)

            # Test basic loader operations
            test_content = "Hello {{name}}!"
            test_path = "test_prompt/1.0.yaml"

            # Write file
            loader.write_file(test_path, test_content)

            # Verify file exists
            assert loader.exists(test_path)

            # Read file
            content = loader.read_file(test_path)
            assert content == test_content

    @patch("google.cloud.storage.Client")
    def test_gcs_storage_loader_integration(self, mock_client_class):
        """Test GCS storage loader with mocked store operations."""
        # Mock GCS client and bucket
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_client_class.from_service_account_json.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        config = StorageConfig(
            storage_type="gcs",
            gcs_bucket="test-bucket",
            gcs_credentials="/path/to/credentials.json",
        )

        loader = GCSStorageLoader(config)

        # Verify loader is properly configured
        assert loader.bucket_name == "test-bucket"
        assert loader.credentials_path == "/path/to/credentials.json"
        assert loader.client == mock_client


class TestStorageLoaderFactory:
    """Test storage loader factory pattern."""

    def test_get_loader_for_local(self):
        """Test getting local storage loader."""
        config = StorageConfig(storage_type="local", local_path="/tmp/prompts")

        loader = LocalStorageLoader(config)
        assert isinstance(loader, LocalStorageLoader)

    @patch("google.cloud.storage.Client")
    def test_get_loader_for_gcs(self, mock_client_class):
        """Test getting GCS storage loader."""
        mock_client = Mock()
        mock_client_class.from_service_account_json.return_value = mock_client

        config = StorageConfig(
            storage_type="gcs",
            gcs_bucket="test-bucket",
            gcs_credentials="/path/to/creds.json",
        )

        loader = GCSStorageLoader(config)
        assert isinstance(loader, GCSStorageLoader)

    def test_get_loader_for_invalid_type(self):
        """Test getting loader for invalid storage type."""
        with pytest.raises(ValueError, match="storage_type must be one of"):
            StorageConfig(storage_type="invalid")


class TestStorageLoaderErrorHandling:
    """Test error handling in storage loaders."""

    def test_local_storage_loader_permission_error(self):
        """Test local storage loader with permission errors."""
        # Try to create store in a directory we can't write to
        config = StorageConfig(storage_type="local", local_path="/root/forbidden")

        with pytest.raises(
            PromptStorageError, match="Failed to create storage directory"
        ):
            LocalStorageLoader(config)

    def test_gcs_storage_loader_credentials_error(self):
        """Test GCS storage loader with invalid credentials."""
        config = StorageConfig(
            storage_type="gcs",
            gcs_bucket="test-bucket",
            gcs_credentials="/nonexistent/credentials.json",
        )

        with pytest.raises(PromptStorageError, match="Failed to initialize GCS client"):
            GCSStorageLoader(config)

    def test_storage_loader_config_validation(self):
        """Test that storage loaders validate configuration properly."""
        # Test local loader with GCS config
        gcs_config = StorageConfig(
            storage_type="gcs",
            gcs_bucket="test-bucket",
            gcs_credentials="/path/to/creds.json",
        )

        with pytest.raises(
            PromptStorageError, match="local_path is required for LocalStorageLoader"
        ):
            LocalStorageLoader(gcs_config)

        # Test GCS loader with local config
        local_config = StorageConfig(storage_type="local", local_path="/tmp/prompts")

        with pytest.raises(
            PromptStorageError, match="gcs_bucket is required for GCSStorageLoader"
        ):
            GCSStorageLoader(local_config)
