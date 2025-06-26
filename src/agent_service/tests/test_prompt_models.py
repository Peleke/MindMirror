"""
Tests for enhanced prompt models.

These tests verify that the enhanced data models correctly handle
validation, serialization, versioning, and edge cases.
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from agent_service.llms.prompts.models import (
    PromptInfo, PromptConfig, PromptSearchCriteria, PromptStats, StoreType
)
from agent_service.llms.prompts.exceptions import PromptValidationError


class TestPromptInfo:
    """Test PromptInfo data model."""
    
    def test_prompt_info_creation(self):
        """Test creating a valid PromptInfo."""
        info = PromptInfo(
            name="test_prompt",
            version="1.0",
            content="Hello {{ name }}!",
            metadata={"category": "greeting"},
            variables=["name"]
        )
        
        assert info.name == "test_prompt"
        assert info.version == "1.0"
        assert info.content == "Hello {{ name }}!"
        assert info.metadata == {"category": "greeting"}
        assert info.variables == ["name"]
        assert info.created_at is not None
        assert info.updated_at is not None
    
    def test_prompt_info_auto_extract_variables(self):
        """Test that variables are automatically extracted from content."""
        info = PromptInfo(
            name="test_prompt",
            version="1.0",
            content="Hello {{ name }}! You have {{ count }} messages from {{ sender }}."
        )
        
        assert "name" in info.variables
        assert "count" in info.variables
        assert "sender" in info.variables
        assert len(info.variables) == 3
    
    def test_prompt_info_validation_name(self):
        """Test name validation."""
        # Valid names
        valid_names = ["test", "test_prompt", "test-prompt", "test.prompt", "test123"]
        for name in valid_names:
            info = PromptInfo(name=name, version="1.0", content="Test content")
            assert info.name == name
        
        # Invalid names
        invalid_names = ["", None, "test/name", "test\\name", "test*name", "a" * 101]
        for name in invalid_names:
            with pytest.raises(PromptValidationError):
                PromptInfo(name=name, version="1.0", content="Test content")
    
    def test_prompt_info_validation_version(self):
        """Test version validation."""
        # Valid versions
        valid_versions = ["1.0", "2.1", "1.0.0", "10.5.2", "1"]
        for version in valid_versions:
            info = PromptInfo(name="test", version=version, content="Test content")
            assert info.version == version
        
        # Invalid versions
        invalid_versions = ["", None, "1.0.0.0", "invalid", "1-0"]
        for version in invalid_versions:
            with pytest.raises(PromptValidationError):
                PromptInfo(name="test", version=version, content="Test content")
    
    def test_prompt_info_validation_content(self):
        """Test content validation."""
        # Valid content
        info = PromptInfo(name="test", version="1.0", content="Valid content")
        assert info.content == "Valid content"
        
        # Invalid content
        invalid_contents = ["", None]
        for content in invalid_contents:
            with pytest.raises(PromptValidationError):
                PromptInfo(name="test", version="1.0", content=content)
    
    def test_prompt_info_validation_metadata(self):
        """Test metadata validation."""
        # Valid metadata
        valid_metadata = [{"key": "value"}, {}, {"nested": {"key": "value"}}]
        for metadata in valid_metadata:
            info = PromptInfo(name="test", version="1.0", content="Test", metadata=metadata)
            assert info.metadata == metadata
        
        # Invalid metadata
        with pytest.raises(PromptValidationError):
            PromptInfo(name="test", version="1.0", content="Test", metadata="not a dict")
    
    def test_prompt_info_validation_variables(self):
        """Test variables validation."""
        # Valid variables
        valid_variables = [["var1"], ["var1", "var2"], []]
        for variables in valid_variables:
            info = PromptInfo(name="test", version="1.0", content="Test", variables=variables)
            assert info.variables == variables
        
        # Invalid variables
        with pytest.raises(PromptValidationError):
            PromptInfo(name="test", version="1.0", content="Test", variables="not a list")
    
    def test_prompt_info_validation_timestamps(self):
        """Test timestamp validation."""
        # Valid timestamps
        valid_timestamp = "2024-01-15T10:30:00"
        info = PromptInfo(
            name="test",
            version="1.0",
            content="Test",
            created_at=valid_timestamp,
            updated_at=valid_timestamp
        )
        assert info.created_at == valid_timestamp
        assert info.updated_at == valid_timestamp
        
        # Invalid timestamps
        invalid_timestamp = "invalid-timestamp"
        with pytest.raises(PromptValidationError):
            PromptInfo(
                name="test",
                version="1.0",
                content="Test",
                created_at=invalid_timestamp,
                updated_at=invalid_timestamp
            )
    
    def test_prompt_info_serialization(self):
        """Test serialization and deserialization."""
        info = PromptInfo(
            name="test_prompt",
            version="1.0",
            content="Hello {{ name }}!",
            metadata={"category": "greeting"},
            variables=["name"]
        )
        
        # Serialize
        data = info.to_dict()
        assert data["name"] == "test_prompt"
        assert data["version"] == "1.0"
        assert data["content"] == "Hello {{ name }}!"
        assert data["metadata"] == {"category": "greeting"}
        assert data["variables"] == ["name"]
        
        # Deserialize
        restored = PromptInfo.from_dict(data)
        assert restored == info
    
    def test_prompt_info_update_content(self):
        """Test updating prompt content with version increment."""
        info = PromptInfo(
            name="test_prompt",
            version="1.0",
            content="Original content",
            metadata={"category": "test"}
        )
        
        updated = info.update_content("New content")
        
        assert updated.name == info.name
        assert updated.version == "1.1"  # Incremented
        assert updated.content == "New content"
        assert updated.metadata == info.metadata
        assert updated.created_at == info.created_at
        assert updated.updated_at != info.updated_at  # Updated timestamp
    
    def test_prompt_info_update_metadata(self):
        """Test updating prompt metadata with version increment."""
        info = PromptInfo(
            name="test_prompt",
            version="1.0",
            content="Test content",
            metadata={"category": "old"}
        )
        
        new_metadata = {"category": "new", "priority": "high"}
        updated = info.update_metadata(new_metadata)
        
        assert updated.name == info.name
        assert updated.version == "1.1"  # Incremented
        assert updated.content == info.content
        assert updated.metadata == new_metadata
        assert updated.created_at == info.created_at
        assert updated.updated_at != info.updated_at  # Updated timestamp
    
    def test_prompt_info_version_increment(self):
        """Test version increment logic."""
        # Test standard increment
        info = PromptInfo(name="test", version="1.0", content="Test")
        updated = info.update_content("New content")
        assert updated.version == "1.1"
        
        # Test with patch version
        info = PromptInfo(name="test", version="1.0.0", content="Test")
        updated = info.update_content("New content")
        assert updated.version == "1.1"
        
        # Test with single number
        info = PromptInfo(name="test", version="1", content="Test")
        updated = info.update_content("New content")
        assert updated.version == "1.1"
    
    def test_prompt_info_equality(self):
        """Test equality comparison."""
        info1 = PromptInfo(name="test", version="1.0", content="Test content")
        info2 = PromptInfo(name="test", version="1.0", content="Test content")
        info3 = PromptInfo(name="test", version="1.0", content="Different content")
        
        assert info1 == info2
        assert info1 != info3
        assert info1 != "not a PromptInfo"
    
    def test_prompt_info_hash(self):
        """Test hash functionality."""
        info1 = PromptInfo(name="test", version="1.0", content="Test content")
        info2 = PromptInfo(name="test", version="1.0", content="Test content")
        info3 = PromptInfo(name="test", version="1.1", content="Test content")
        
        assert hash(info1) == hash(info2)
        assert hash(info1) != hash(info3)


class TestPromptConfig:
    """Test PromptConfig data model."""
    
    def test_prompt_config_creation(self):
        """Test creating a valid PromptConfig."""
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
    
    def test_prompt_config_validation_store_type(self):
        """Test store type validation."""
        # Valid store types - only test MEMORY which has no requirements
        config = PromptConfig(store_type=StoreType.MEMORY)
        assert config.store_type == StoreType.MEMORY
        
        # Test that invalid store type raises error
        with pytest.raises(PromptValidationError):
            PromptConfig(store_type="invalid")
    
    def test_prompt_config_validation_required_fields(self):
        """Test required field validation."""
        # LOCAL store requires store_path
        with pytest.raises(PromptValidationError):
            PromptConfig(store_type=StoreType.LOCAL)
        
        # GCS store requires gcs_bucket
        with pytest.raises(PromptValidationError):
            PromptConfig(store_type=StoreType.GCS)
        
        # FIRESTORE store requires firestore_collection
        with pytest.raises(PromptValidationError):
            PromptConfig(store_type=StoreType.FIRESTORE)
        
        # MEMORY store has no requirements
        config = PromptConfig(store_type=StoreType.MEMORY)
        assert config.store_type == StoreType.MEMORY
    
    def test_prompt_config_validation_cache_settings(self):
        """Test cache settings validation."""
        # Valid cache settings
        config = PromptConfig(store_type=StoreType.MEMORY, cache_size=100, cache_ttl=60)
        assert config.cache_size == 100
        assert config.cache_ttl == 60
        
        # Invalid cache size
        with pytest.raises(PromptValidationError):
            PromptConfig(store_type=StoreType.MEMORY, cache_size=0)
        
        # Invalid cache TTL
        with pytest.raises(PromptValidationError):
            PromptConfig(store_type=StoreType.MEMORY, cache_ttl=-1)
    
    def test_prompt_config_serialization(self):
        """Test serialization and deserialization."""
        config = PromptConfig(
            store_type=StoreType.LOCAL,
            store_path="/tmp/prompts",
            gcs_prefix="custom/",
            cache_size=500,
            cache_ttl=1800,
            enable_validation=False,
            enable_caching=False
        )
        
        # Serialize
        data = config.to_dict()
        assert data["store_type"] == "local"
        assert data["store_path"] == "/tmp/prompts"
        assert data["gcs_prefix"] == "custom/"
        assert data["cache_size"] == 500
        assert data["cache_ttl"] == 1800
        assert data["enable_validation"] is False
        assert data["enable_caching"] is False
        
        # Deserialize
        restored = PromptConfig.from_dict(data)
        assert restored.store_type == config.store_type
        assert restored.store_path == config.store_path
        assert restored.gcs_prefix == config.gcs_prefix
        assert restored.cache_size == config.cache_size
        assert restored.cache_ttl == config.cache_ttl
        assert restored.enable_validation == config.enable_validation
        assert restored.enable_caching == config.enable_caching


class TestPromptSearchCriteria:
    """Test PromptSearchCriteria data model."""
    
    def test_prompt_search_criteria_creation(self):
        """Test creating a valid PromptSearchCriteria."""
        criteria = PromptSearchCriteria(
            name_pattern="test*",
            version_pattern="1.*",
            metadata_filters={"category": "greeting"},
            content_pattern="Hello",
            limit=10,
            offset=5
        )
        
        assert criteria.name_pattern == "test*"
        assert criteria.version_pattern == "1.*"
        assert criteria.metadata_filters == {"category": "greeting"}
        assert criteria.content_pattern == "Hello"
        assert criteria.limit == 10
        assert criteria.offset == 5
    
    def test_prompt_search_criteria_validation(self):
        """Test search criteria validation."""
        # Valid criteria
        criteria = PromptSearchCriteria(limit=10, offset=5)
        assert criteria.limit == 10
        assert criteria.offset == 5
        
        # Invalid limit
        with pytest.raises(PromptValidationError):
            PromptSearchCriteria(limit=0)
        
        # Invalid offset
        with pytest.raises(PromptValidationError):
            PromptSearchCriteria(offset=-1)
        
        # Invalid offset vs limit
        with pytest.raises(PromptValidationError):
            PromptSearchCriteria(limit=5, offset=10)
    
    def test_prompt_search_criteria_serialization(self):
        """Test serialization with datetime handling."""
        from datetime import datetime
        
        created_after = datetime(2024, 1, 1, 12, 0, 0)
        updated_before = datetime(2024, 12, 31, 23, 59, 59)
        
        criteria = PromptSearchCriteria(
            name_pattern="test*",
            created_after=created_after,
            updated_before=updated_before,
            limit=20
        )
        
        data = criteria.to_dict()
        assert data["name_pattern"] == "test*"
        assert data["created_after"] == "2024-01-01T12:00:00"
        assert data["updated_before"] == "2024-12-31T23:59:59"
        assert data["limit"] == 20


class TestPromptStats:
    """Test PromptStats data model."""
    
    def test_prompt_stats_creation(self):
        """Test creating a valid PromptStats."""
        stats = PromptStats(
            total_prompts=100,
            total_versions=150,
            cache_hits=80,
            cache_misses=20,
            render_count=100,
            storage_size_bytes=1024
        )
        
        assert stats.total_prompts == 100
        assert stats.total_versions == 150
        assert stats.cache_hits == 80
        assert stats.cache_misses == 20
        assert stats.render_count == 100
        assert stats.storage_size_bytes == 1024
    
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
        """Test serialization with datetime handling."""
        from datetime import datetime
        
        last_updated = datetime(2024, 1, 15, 10, 30, 0)
        stats = PromptStats(
            total_prompts=50,
            cache_hits=40,
            cache_misses=10,
            last_updated=last_updated
        )
        
        data = stats.to_dict()
        assert data["total_prompts"] == 50
        assert data["cache_hits"] == 40
        assert data["cache_misses"] == 10
        assert data["last_updated"] == "2024-01-15T10:30:00"


class TestStoreType:
    """Test StoreType enum."""
    
    def test_store_type_values(self):
        """Test StoreType enum values."""
        assert StoreType.LOCAL.value == "local"
        assert StoreType.GCS.value == "gcs"
        assert StoreType.MEMORY.value == "memory"
        assert StoreType.FIRESTORE.value == "firestore"
    
    def test_store_type_comparison(self):
        """Test StoreType comparison."""
        assert StoreType.LOCAL == StoreType.LOCAL
        assert StoreType.LOCAL != StoreType.GCS
        assert StoreType.LOCAL in StoreType
        # Test that we can access enum values
        assert StoreType.LOCAL.value == "local"
        assert StoreType.GCS.value == "gcs" 