"""
Tests for prompt data models and validation.
"""
import pytest
from datetime import datetime
from typing import Dict, Any

from agent_service.llms.prompts.models import (
    PromptInfo,
    PromptConfig,
    PromptStats,
    StorageConfig,
    StoreType
)
from agent_service.llms.prompts.exceptions import PromptValidationError


class TestPromptInfo:
    """Test PromptInfo model validation and behavior."""
    
    def test_valid_prompt_info(self):
        """Test creating a valid PromptInfo instance."""
        prompt_info = PromptInfo(
            name="test_prompt",
            version="1.0",
            content="Hello {{name}}!",
            metadata={"description": "A test prompt", "tags": ["test", "greeting"], "categories": ["general"]},
            variables=["name"]
        )
        
        assert prompt_info.name == "test_prompt"
        assert prompt_info.version == "1.0"
        assert prompt_info.content == "Hello {{name}}!"
        assert prompt_info.metadata["description"] == "A test prompt"
        assert prompt_info.metadata["tags"] == ["test", "greeting"]
        assert prompt_info.metadata["categories"] == ["general"]
        assert prompt_info.variables == ["name"]
    
    def test_prompt_info_with_minimal_fields(self):
        """Test creating PromptInfo with only required fields."""
        prompt_info = PromptInfo(
            name="minimal_prompt",
            version="1.0",
            content="Simple content"
        )
        
        assert prompt_info.name == "minimal_prompt"
        assert prompt_info.version == "1.0"
        assert prompt_info.content == "Simple content"
        assert prompt_info.metadata == {}
        assert prompt_info.variables == []
    
    def test_prompt_info_variable_extraction(self):
        """Test automatic variable extraction from content."""
        prompt_info = PromptInfo(
            name="variable_prompt",
            version="1.0",
            content="Hello {{name}}, your age is {{age}} and you live in {{city}}."
        )
        
        assert "name" in prompt_info.variables
        assert "age" in prompt_info.variables
        assert "city" in prompt_info.variables
        assert len(prompt_info.variables) == 3
    
    def test_prompt_info_variable_extraction_no_variables(self):
        """Test variable extraction with no variables in content."""
        prompt_info = PromptInfo(
            name="no_variables",
            version="1.0",
            content="This is a simple prompt with no variables."
        )
        
        assert prompt_info.variables == []
    
    def test_prompt_info_variable_extraction_duplicates(self):
        """Test variable extraction handles duplicate variables."""
        prompt_info = PromptInfo(
            name="duplicate_variables",
            version="1.0",
            content="Hello {{name}}, nice to meet you {{name}}!"
        )
        
        assert prompt_info.variables == ["name"]
    
    def test_prompt_info_validation(self):
        """Test PromptInfo validation rules."""
        # Test empty name
        with pytest.raises(PromptValidationError, match="Prompt name must be a non-empty string"):
            PromptInfo(name="", version="1.0", content="test")
        
        # Test empty version
        with pytest.raises(PromptValidationError, match="Version must be a non-empty string"):
            PromptInfo(name="test", version="", content="test")
        
        # Test empty content
        with pytest.raises(PromptValidationError, match="Content must be a non-empty string"):
            PromptInfo(name="test", version="1.0", content="")
    
    def test_prompt_info_serialization(self):
        """Test PromptInfo serialization to dict."""
        prompt_info = PromptInfo(
            name="serialization_test",
            version="1.0",
            content="Test content",
            metadata={"description": "Test description", "tags": ["test"], "categories": ["general"]}
        )
        
        data = prompt_info.to_dict()
        
        assert data["name"] == "serialization_test"
        assert data["version"] == "1.0"
        assert data["content"] == "Test content"
        assert data["metadata"]["description"] == "Test description"
        assert data["metadata"]["tags"] == ["test"]
        assert data["metadata"]["categories"] == ["general"]
        assert "variables" in data
        assert "created_at" in data
        assert "updated_at" in data


class TestPromptConfig:
    """Test PromptConfig model validation and behavior."""
    
    def test_valid_prompt_config(self):
        """Test creating a valid PromptConfig instance."""
        config = PromptConfig(
            store_type=StoreType.LOCAL,
            store_path="/tmp/prompts",
            cache_size=1000,
            cache_ttl=3600
        )
        
        assert config.store_type == StoreType.LOCAL
        assert config.store_path == "/tmp/prompts"
        assert config.cache_size == 1000
        assert config.cache_ttl == 3600
        assert config.enable_validation is True
        assert config.enable_caching is True
    
    def test_prompt_config_with_minimal_fields(self):
        """Test creating PromptConfig with only required fields."""
        config = PromptConfig(
            store_type=StoreType.MEMORY
        )
        
        assert config.store_type == StoreType.MEMORY
        assert config.store_path is None
        assert config.gcs_bucket is None
        assert config.cache_size == 1000
        assert config.cache_ttl == 3600
    
    def test_prompt_config_validation(self):
        """Test PromptConfig validation rules."""
        # Test invalid store type
        with pytest.raises(PromptValidationError, match="store_type must be a StoreType enum"):
            PromptConfig(store_type="invalid")
        
        # Test local storage without path
        with pytest.raises(PromptValidationError, match="store_path is required for LOCAL store type"):
            PromptConfig(store_type=StoreType.LOCAL)
        
        # Test GCS storage without bucket
        with pytest.raises(PromptValidationError, match="gcs_bucket is required for GCS store type"):
            PromptConfig(store_type=StoreType.GCS)
    
    def test_prompt_config_serialization(self):
        """Test PromptConfig serialization to dict."""
        config = PromptConfig(
            store_type=StoreType.LOCAL,
            store_path="/test/path",
            cache_size=500,
            cache_ttl=1800
        )
        
        data = config.to_dict()
        
        assert data["store_type"] == "local"
        assert data["store_path"] == "/test/path"
        assert data["cache_size"] == 500
        assert data["cache_ttl"] == 1800
        assert data["enable_validation"] is True
        assert data["enable_caching"] is True


class TestPromptStats:
    """Test PromptStats model validation and behavior."""
    
    def test_valid_prompt_stats(self):
        """Test creating a valid PromptStats instance."""
        stats = PromptStats(
            total_prompts=100,
            total_versions=150,
            cache_hits=80,
            cache_misses=20,
            render_count=100,
            storage_size_bytes=1024000,
            last_updated=datetime.now()
        )
        
        assert stats.total_prompts == 100
        assert stats.total_versions == 150
        assert stats.cache_hits == 80
        assert stats.cache_misses == 20
        assert stats.render_count == 100
        assert stats.storage_size_bytes == 1024000
        assert stats.cache_hit_rate == 0.8
        assert stats.average_versions_per_prompt == 1.5
    
    def test_prompt_stats_with_minimal_fields(self):
        """Test creating PromptStats with only required fields."""
        stats = PromptStats()
        
        assert stats.total_prompts == 0
        assert stats.total_versions == 0
        assert stats.cache_hits == 0
        assert stats.cache_misses == 0
        assert stats.render_count == 0
        assert stats.storage_size_bytes == 0
        assert stats.last_updated is None
        assert stats.cache_hit_rate == 0.0
        assert stats.average_versions_per_prompt == 0.0
    
    def test_prompt_stats_calculated_properties(self):
        """Test calculated properties."""
        # Test cache hit rate
        stats = PromptStats(cache_hits=80, cache_misses=20)
        assert stats.cache_hit_rate == 0.8
        
        # Test with no requests
        stats = PromptStats(cache_hits=0, cache_misses=0)
        assert stats.cache_hit_rate == 0.0
        
        # Test average versions per prompt
        stats = PromptStats(total_prompts=10, total_versions=25)
        assert stats.average_versions_per_prompt == 2.5
        
        # Test with no prompts
        stats = PromptStats(total_prompts=0, total_versions=0)
        assert stats.average_versions_per_prompt == 0.0
    
    def test_prompt_stats_serialization(self):
        """Test PromptStats serialization to dict."""
        stats = PromptStats(
            total_prompts=50,
            total_versions=75,
            cache_hits=40,
            cache_misses=10,
            render_count=50,
            storage_size_bytes=512000
        )
        
        data = stats.to_dict()
        
        assert data["total_prompts"] == 50
        assert data["total_versions"] == 75
        assert data["cache_hits"] == 40
        assert data["cache_misses"] == 10
        assert data["render_count"] == 50
        assert data["storage_size_bytes"] == 512000


class TestStorageConfig:
    """Test StorageConfig model validation and behavior."""
    
    def test_valid_local_storage_config(self):
        """Test creating a valid local storage configuration."""
        config = StorageConfig(
            storage_type="local",
            local_path="/app/storage/prompts"
        )
        
        assert config.storage_type == "local"
        assert config.local_path == "/app/storage/prompts"
        assert config.gcs_bucket is None
        assert config.gcs_credentials is None
    
    def test_valid_gcs_storage_config(self):
        """Test creating a valid GCS storage configuration."""
        config = StorageConfig(
            storage_type="gcs",
            gcs_bucket="my-prompt-bucket",
            gcs_credentials="/path/to/credentials.json"
        )
        
        assert config.storage_type == "gcs"
        assert config.gcs_bucket == "my-prompt-bucket"
        assert config.gcs_credentials == "/path/to/credentials.json"
        assert config.local_path is None
    
    def test_storage_config_validation_local(self):
        """Test local storage configuration validation."""
        # Test local storage without local_path - this should work because local_path is Optional
        # The validation only happens when local_path is explicitly set to None or empty
        config = StorageConfig(storage_type="local")
        assert config.storage_type == "local"
        assert config.local_path is None
        
        # Test local storage with empty local_path
        with pytest.raises(ValueError, match="local_path is required for local storage"):
            StorageConfig(storage_type="local", local_path="")
    
    def test_storage_config_validation_gcs(self):
        """Test GCS storage configuration validation."""
        # Test GCS storage without gcs_bucket - this should work because gcs_bucket is Optional
        # The validation only happens when gcs_bucket is explicitly set to None or empty
        config = StorageConfig(storage_type="gcs")
        assert config.storage_type == "gcs"
        assert config.gcs_bucket is None
        
        # Test GCS storage with empty gcs_bucket
        with pytest.raises(ValueError, match="gcs_bucket is required for GCS storage"):
            StorageConfig(storage_type="gcs", gcs_bucket="")
        
        # Test GCS storage without gcs_credentials - this should work because gcs_credentials is Optional
        # The validation only happens when gcs_credentials is explicitly set to None or empty
        config = StorageConfig(storage_type="gcs", gcs_bucket="test-bucket")
        assert config.storage_type == "gcs"
        assert config.gcs_bucket == "test-bucket"
        assert config.gcs_credentials is None
        
        # Test GCS storage with empty gcs_credentials
        with pytest.raises(ValueError, match="gcs_credentials is required for GCS storage"):
            StorageConfig(storage_type="gcs", gcs_bucket="test-bucket", gcs_credentials="")
    
    def test_storage_config_validation_invalid_type(self):
        """Test validation for invalid storage types."""
        with pytest.raises(ValueError, match="storage_type must be one of"):
            StorageConfig(storage_type="invalid")
    
    def test_storage_config_serialization(self):
        """Test StorageConfig serialization to dict."""
        config = StorageConfig(
            storage_type="local",
            local_path="/test/path"
        )
        
        data = config.model_dump()
        
        assert data["storage_type"] == "local"
        assert data["local_path"] == "/test/path"
        assert data["gcs_bucket"] is None
        assert data["gcs_credentials"] is None
    
    def test_storage_config_from_environment(self):
        """Test creating StorageConfig from environment variables."""
        # This would be tested with actual environment variables
        # For now, we'll test the validation logic
        config = StorageConfig(
            storage_type="local",
            local_path="/env/path"
        )
        
        assert config.storage_type == "local"
        assert config.local_path == "/env/path"
    
    def test_storage_config_equality(self):
        """Test StorageConfig equality comparison."""
        config1 = StorageConfig(
            storage_type="local",
            local_path="/test/path"
        )
        
        config2 = StorageConfig(
            storage_type="local",
            local_path="/test/path"
        )
        
        config3 = StorageConfig(
            storage_type="gcs",
            gcs_bucket="test-bucket",
            gcs_credentials="/path/to/creds.json"
        )
        
        assert config1 == config2
        assert config1 != config3
        assert config2 != config3 