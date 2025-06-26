"""
Tests for storage loaders and abstraction layer.
"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from agent_service.llms.prompts.stores.loaders import (
    StorageLoader,
    LocalStorageLoader,
    GCSStorageLoader
)
from agent_service.llms.prompts.models import StorageConfig
from agent_service.llms.prompts.stores import (
    InMemoryPromptStore,
    LocalPromptStore,
    GCSPromptStore
)


class TestStorageLoader:
    """Test the StorageLoader protocol and base functionality."""
    
    def test_storage_loader_protocol(self):
        """Test that StorageLoader is a proper protocol."""
        # Should be able to create a mock that implements the protocol
        mock_loader = Mock(spec=StorageLoader)
        assert hasattr(mock_loader, 'create_store')
        assert callable(mock_loader.create_store)


class TestLocalStorageLoader:
    """Test LocalStorageLoader functionality."""
    
    def test_create_local_store(self):
        """Test creating a local prompt store."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StorageConfig(
                storage_type="local",
                local_path=temp_dir
            )
            
            loader = LocalStorageLoader()
            store = loader.create_store(config)
            
            assert isinstance(store, LocalPromptStore)
            assert store.base_path == temp_dir
    
    def test_create_local_store_with_invalid_config(self):
        """Test creating local store with invalid configuration."""
        # Test with wrong storage type
        config = StorageConfig(
            storage_type="gcs",
            gcs_bucket="test-bucket",
            gcs_credentials="/path/to/creds.json"
        )
        
        loader = LocalStorageLoader()
        with pytest.raises(ValueError, match="LocalStorageLoader requires local storage type"):
            loader.create_store(config)
    
    def test_create_local_store_with_missing_path(self):
        """Test creating local store with missing local path."""
        config = StorageConfig(storage_type="local")
        
        loader = LocalStorageLoader()
        with pytest.raises(ValueError, match="local_path is required"):
            loader.create_store(config)
    
    def test_create_local_store_creates_directory(self):
        """Test that local store creation creates the directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = os.path.join(temp_dir, "new_prompts")
            
            config = StorageConfig(
                storage_type="local",
                local_path=new_dir
            )
            
            loader = LocalStorageLoader()
            store = loader.create_store(config)
            
            assert os.path.exists(new_dir)
            assert isinstance(store, LocalPromptStore)
    
    def test_create_local_store_with_existing_directory(self):
        """Test creating local store with existing directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StorageConfig(
                storage_type="local",
                local_path=temp_dir
            )
            
            loader = LocalStorageLoader()
            store = loader.create_store(config)
            
            assert isinstance(store, LocalPromptStore)
            assert store.base_path == temp_dir


class TestGCSStorageLoader:
    """Test GCSStorageLoader functionality."""
    
    @patch('agent_service.llms.prompts.stores.loaders.storage')
    def test_create_gcs_store(self, mock_storage):
        """Test creating a GCS prompt store."""
        # Mock the GCS client
        mock_client = Mock()
        mock_storage.Client.return_value = mock_client
        
        config = StorageConfig(
            storage_type="gcs",
            gcs_bucket="test-bucket",
            gcs_credentials="/path/to/credentials.json"
        )
        
        loader = GCSStorageLoader()
        store = loader.create_store(config)
        
        assert isinstance(store, GCSPromptStore)
        assert store.bucket_name == "test-bucket"
        mock_storage.Client.assert_called_once_with(
            project=None,
            credentials="/path/to/credentials.json"
        )
    
    @patch('agent_service.llms.prompts.stores.loaders.storage')
    def test_create_gcs_store_with_project(self, mock_storage):
        """Test creating GCS store with project specified."""
        mock_client = Mock()
        mock_storage.Client.return_value = mock_client
        
        config = StorageConfig(
            storage_type="gcs",
            gcs_bucket="test-bucket",
            gcs_credentials="/path/to/credentials.json"
        )
        
        loader = GCSStorageLoader(project_id="my-project")
        store = loader.create_store(config)
        
        assert isinstance(store, GCSPromptStore)
        mock_storage.Client.assert_called_once_with(
            project="my-project",
            credentials="/path/to/credentials.json"
        )
    
    def test_create_gcs_store_with_invalid_config(self):
        """Test creating GCS store with invalid configuration."""
        # Test with wrong storage type
        config = StorageConfig(
            storage_type="local",
            local_path="/tmp/prompts"
        )
        
        loader = GCSStorageLoader()
        with pytest.raises(ValueError, match="GCSStorageLoader requires GCS storage type"):
            loader.create_store(config)
    
    def test_create_gcs_store_with_missing_bucket(self):
        """Test creating GCS store with missing bucket."""
        config = StorageConfig(storage_type="gcs")
        
        loader = GCSStorageLoader()
        with pytest.raises(ValueError, match="gcs_bucket is required"):
            loader.create_store(config)
    
    def test_create_gcs_store_with_missing_credentials(self):
        """Test creating GCS store with missing credentials."""
        config = StorageConfig(
            storage_type="gcs",
            gcs_bucket="test-bucket"
        )
        
        loader = GCSStorageLoader()
        with pytest.raises(ValueError, match="gcs_credentials is required"):
            loader.create_store(config)
    
    @patch('agent_service.llms.prompts.stores.loaders.storage')
    def test_create_gcs_store_with_emulator(self, mock_storage):
        """Test creating GCS store with emulator configuration."""
        mock_client = Mock()
        mock_storage.Client.return_value = mock_client
        
        config = StorageConfig(
            storage_type="gcs",
            gcs_bucket="test-bucket",
            gcs_credentials="/path/to/credentials.json"
        )
        
        # Set emulator environment variable
        with patch.dict(os.environ, {'STORAGE_EMULATOR_HOST': 'localhost:4443'}):
            loader = GCSStorageLoader()
            store = loader.create_store(config)
            
            assert isinstance(store, GCSPromptStore)
            # Should use anonymous credentials with emulator
            mock_storage.Client.assert_called_once_with(
                project=None,
                credentials=None
            )
    
    @patch('agent_service.llms.prompts.stores.loaders.storage')
    def test_create_gcs_store_handles_client_error(self, mock_storage):
        """Test handling of GCS client creation errors."""
        mock_storage.Client.side_effect = Exception("GCS client error")
        
        config = StorageConfig(
            storage_type="gcs",
            gcs_bucket="test-bucket",
            gcs_credentials="/path/to/credentials.json"
        )
        
        loader = GCSStorageLoader()
        with pytest.raises(Exception, match="GCS client error"):
            loader.create_store(config)


class TestStorageLoaderIntegration:
    """Test integration between storage loaders and stores."""
    
    def test_local_storage_loader_integration(self):
        """Test local storage loader with actual store operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StorageConfig(
                storage_type="local",
                local_path=temp_dir
            )
            
            loader = LocalStorageLoader()
            store = loader.create_store(config)
            
            # Test basic store operations
            from agent_service.llms.prompts.models import PromptInfo
            
            prompt = PromptInfo(
                name="test_prompt",
                version="1.0",
                content="Hello {{name}}!",
                description="Test prompt"
            )
            
            # Save prompt
            store.save_prompt(prompt)
            
            # Verify prompt exists
            assert store.exists("test_prompt")
            
            # Retrieve prompt
            retrieved = store.get_prompt("test_prompt")
            assert retrieved.name == "test_prompt"
            assert retrieved.content == "Hello {{name}}!"
    
    @patch('agent_service.llms.prompts.stores.loaders.storage')
    def test_gcs_storage_loader_integration(self, mock_storage):
        """Test GCS storage loader with mocked store operations."""
        # Mock GCS client and bucket
        mock_client = Mock()
        mock_bucket = Mock()
        mock_storage.Client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        
        config = StorageConfig(
            storage_type="gcs",
            gcs_bucket="test-bucket",
            gcs_credentials="/path/to/credentials.json"
        )
        
        loader = GCSStorageLoader()
        store = loader.create_store(config)
        
        # Verify store is properly configured
        assert isinstance(store, GCSPromptStore)
        assert store.bucket_name == "test-bucket"
        assert store.client == mock_client
        assert store.bucket == mock_bucket


class TestStorageLoaderFactory:
    """Test storage loader factory pattern."""
    
    def test_get_loader_for_local(self):
        """Test getting local storage loader."""
        from agent_service.llms.prompts.stores.loaders import get_storage_loader
        
        loader = get_storage_loader("local")
        assert isinstance(loader, LocalStorageLoader)
    
    def test_get_loader_for_gcs(self):
        """Test getting GCS storage loader."""
        from agent_service.llms.prompts.stores.loaders import get_storage_loader
        
        loader = get_storage_loader("gcs")
        assert isinstance(loader, GCSStorageLoader)
    
    def test_get_loader_for_invalid_type(self):
        """Test getting loader for invalid storage type."""
        from agent_service.llms.prompts.stores.loaders import get_storage_loader
        
        with pytest.raises(ValueError, match="Unsupported storage type"):
            get_storage_loader("invalid")
    
    def test_get_loader_case_insensitive(self):
        """Test that storage type is case insensitive."""
        from agent_service.llms.prompts.stores.loaders import get_storage_loader
        
        # Test uppercase
        loader = get_storage_loader("LOCAL")
        assert isinstance(loader, LocalStorageLoader)
        
        # Test mixed case
        loader = get_storage_loader("Gcs")
        assert isinstance(loader, GCSStorageLoader)


class TestStorageLoaderErrorHandling:
    """Test error handling in storage loaders."""
    
    def test_local_storage_loader_permission_error(self):
        """Test local storage loader with permission errors."""
        # Try to create store in a directory we can't write to
        config = StorageConfig(
            storage_type="local",
            local_path="/root/forbidden"
        )
        
        loader = LocalStorageLoader()
        with pytest.raises((OSError, PermissionError)):
            loader.create_store(config)
    
    def test_gcs_storage_loader_credentials_error(self):
        """Test GCS storage loader with invalid credentials."""
        config = StorageConfig(
            storage_type="gcs",
            gcs_bucket="test-bucket",
            gcs_credentials="/nonexistent/credentials.json"
        )
        
        loader = GCSStorageLoader()
        with pytest.raises(FileNotFoundError):
            loader.create_store(config)
    
    def test_storage_loader_config_validation(self):
        """Test that storage loaders validate configuration properly."""
        # Test local loader with GCS config
        local_loader = LocalStorageLoader()
        gcs_config = StorageConfig(
            storage_type="gcs",
            gcs_bucket="test-bucket",
            gcs_credentials="/path/to/creds.json"
        )
        
        with pytest.raises(ValueError, match="LocalStorageLoader requires local storage type"):
            local_loader.create_store(gcs_config)
        
        # Test GCS loader with local config
        gcs_loader = GCSStorageLoader()
        local_config = StorageConfig(
            storage_type="local",
            local_path="/tmp/prompts"
        )
        
        with pytest.raises(ValueError, match="GCSStorageLoader requires GCS storage type"):
            gcs_loader.create_store(local_config) 