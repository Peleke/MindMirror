"""
Tests for in-memory prompt store.

These tests verify that the InMemoryPromptStore correctly implements
the PromptStore interface and handles all operations properly.
"""

import pytest
from unittest.mock import Mock
from typing import List
from datetime import datetime

from agent_service.llms.prompts.stores.memory import InMemoryPromptStore
from agent_service.llms.prompts.models import PromptInfo
from agent_service.llms.prompts.exceptions import PromptNotFoundError, PromptValidationError


class TestInMemoryPromptStore:
    """Test InMemoryPromptStore implementation."""
    
    @pytest.fixture
    def store(self):
        """Create a fresh in-memory store for each test."""
        return InMemoryPromptStore()
    
    @pytest.fixture
    def sample_prompt_info(self):
        """Create a sample PromptInfo for testing."""
        return PromptInfo(
            name="test_prompt",
            version="1.0",
            content="Hello {{ name }}!",
            metadata={"category": "greeting", "language": "en"},
            variables=["name"],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
    
    def test_store_initialization(self, store):
        """Test store initialization."""
        assert store._prompts == {}
        assert store._latest_versions == {}
        assert store._stats == {
            'total_prompts': 0,
            'total_versions': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'render_count': 0,
            'storage_size_bytes': 0
        }
    
    def test_save_prompt(self, store, sample_prompt_info):
        """Test saving a prompt."""
        store.save_prompt(sample_prompt_info)
        
        # Check that prompt is stored
        assert sample_prompt_info.name in store._prompts
        assert sample_prompt_info.version in store._prompts[sample_prompt_info.name]
        assert store._prompts[sample_prompt_info.name][sample_prompt_info.version] == sample_prompt_info
        
        # Check that latest version is updated
        assert store._latest_versions[sample_prompt_info.name] == sample_prompt_info.version
        
        # Check stats
        assert store._stats['total_prompts'] == 1
        assert store._stats['total_versions'] == 1
    
    def test_save_prompt_multiple_versions(self, store, sample_prompt_info):
        """Test saving multiple versions of the same prompt."""
        # Save first version
        store.save_prompt(sample_prompt_info)
        
        # Save second version
        v2_info = sample_prompt_info.update_content("Hello {{ name }}! How are you?")
        store.save_prompt(v2_info)
        
        # Check that both versions are stored
        assert len(store._prompts[sample_prompt_info.name]) == 2
        assert "1.0" in store._prompts[sample_prompt_info.name]
        assert "1.1" in store._prompts[sample_prompt_info.name]
        
        # Check that latest version is updated
        assert store._latest_versions[sample_prompt_info.name] == "1.1"
        
        # Check stats
        assert store._stats['total_prompts'] == 1
        assert store._stats['total_versions'] == 2
    
    def test_save_prompt_invalid_info(self, store):
        """Test saving invalid prompt info."""
        invalid_info = Mock()  # Not a PromptInfo
        
        with pytest.raises(PromptValidationError):
            store.save_prompt(invalid_info)
    
    def test_get_prompt_with_version(self, store, sample_prompt_info):
        """Test getting a prompt with specific version."""
        store.save_prompt(sample_prompt_info)
        
        retrieved = store.get_prompt("test_prompt", "1.0")
        assert retrieved == sample_prompt_info
    
    def test_get_prompt_without_version(self, store, sample_prompt_info):
        """Test getting a prompt without version (should get latest)."""
        store.save_prompt(sample_prompt_info)
        
        # Create and save a newer version
        v2_info = sample_prompt_info.update_content("Updated content")
        store.save_prompt(v2_info)
        
        # Get without version should return latest
        retrieved = store.get_prompt("test_prompt")
        assert retrieved == v2_info
        assert retrieved.version == "1.1"
    
    def test_get_prompt_not_found(self, store):
        """Test getting a non-existent prompt."""
        with pytest.raises(PromptNotFoundError, match="Prompt 'nonexistent' not found"):
            store.get_prompt("nonexistent", "1.0")
    
    def test_get_prompt_version_not_found(self, store, sample_prompt_info):
        """Test getting a non-existent version."""
        store.save_prompt(sample_prompt_info)
        
        with pytest.raises(PromptNotFoundError, match="Version '2.0' not found for prompt 'test_prompt'"):
            store.get_prompt("test_prompt", "2.0")
    
    def test_get_prompt_invalid_name(self, store):
        """Test getting prompt with invalid name."""
        with pytest.raises(PromptValidationError):
            store.get_prompt("", "1.0")
        
        with pytest.raises(PromptValidationError):
            store.get_prompt(None, "1.0")
    
    def test_get_latest_version(self, store, sample_prompt_info):
        """Test getting latest version of a prompt."""
        store.save_prompt(sample_prompt_info)
        
        latest = store.get_latest_version("test_prompt")
        assert latest == "1.0"
        
        # Add another version
        v2_info = sample_prompt_info.update_content("Updated content")
        store.save_prompt(v2_info)
        
        latest = store.get_latest_version("test_prompt")
        assert latest == "1.1"
    
    def test_get_latest_version_not_found(self, store):
        """Test getting latest version of non-existent prompt."""
        with pytest.raises(PromptNotFoundError, match="No versions found for prompt 'nonexistent'"):
            store.get_latest_version("nonexistent")
    
    def test_delete_prompt_with_version(self, store, sample_prompt_info):
        """Test deleting a specific version of a prompt."""
        store.save_prompt(sample_prompt_info)
        
        # Add another version
        v2_info = sample_prompt_info.update_content("Updated content")
        store.save_prompt(v2_info)
        
        # Delete specific version
        store.delete_prompt("test_prompt", "1.0")
        
        # Check that only the specific version is deleted
        assert "1.0" not in store._prompts["test_prompt"]
        assert "1.1" in store._prompts["test_prompt"]
        
        # Latest version should still be 1.1
        assert store._latest_versions["test_prompt"] == "1.1"
    
    def test_delete_prompt_without_version(self, store, sample_prompt_info):
        """Test deleting latest version of a prompt."""
        store.save_prompt(sample_prompt_info)
        
        # Add another version
        v2_info = sample_prompt_info.update_content("Updated content")
        store.save_prompt(v2_info)
        
        # Delete without version (should delete latest)
        store.delete_prompt("test_prompt")
        
        # Check that latest version is deleted
        assert "1.1" not in store._prompts["test_prompt"]
        assert "1.0" in store._prompts["test_prompt"]
        
        # Latest version should be updated to 1.0
        assert store._latest_versions["test_prompt"] == "1.0"
    
    def test_delete_prompt_not_found(self, store):
        """Test deleting non-existent prompt."""
        with pytest.raises(PromptNotFoundError, match="Prompt 'nonexistent' not found"):
            store.delete_prompt("nonexistent", "1.0")
    
    def test_delete_prompt_version_not_found(self, store, sample_prompt_info):
        """Test deleting non-existent version."""
        store.save_prompt(sample_prompt_info)
        
        with pytest.raises(PromptNotFoundError, match="Version '2.0' not found for prompt 'test_prompt'"):
            store.delete_prompt("test_prompt", "2.0")
    
    def test_delete_prompt_all_versions(self, store, sample_prompt_info):
        """Test deleting all versions of a prompt."""
        store.save_prompt(sample_prompt_info)
        
        # Add another version
        v2_info = sample_prompt_info.update_content("Updated content")
        store.save_prompt(v2_info)
        
        # Delete all versions
        store.delete_prompt("test_prompt", "1.0")
        store.delete_prompt("test_prompt", "1.1")
        
        # Check that prompt is completely removed
        assert "test_prompt" not in store._prompts
        assert "test_prompt" not in store._latest_versions
    
    def test_list_prompts(self, store, sample_prompt_info):
        """Test listing all prompts."""
        store.save_prompt(sample_prompt_info)
        
        # Create another prompt
        other_info = PromptInfo(
            name="other_prompt",
            version="1.0",
            content="Other content",
            metadata={},
            variables=[]
        )
        store.save_prompt(other_info)
        
        prompts = store.list_prompts()
        
        # Should return latest version of each prompt
        assert len(prompts) == 2
        prompt_names = [p.name for p in prompts]
        assert "test_prompt" in prompt_names
        assert "other_prompt" in prompt_names
    
    def test_list_prompts_empty(self, store):
        """Test listing prompts when store is empty."""
        prompts = store.list_prompts()
        assert prompts == []
    
    def test_search_prompts(self, store, sample_prompt_info):
        """Test searching prompts."""
        store.save_prompt(sample_prompt_info)
        
        # Create another prompt with different metadata
        other_info = PromptInfo(
            name="other_prompt",
            version="1.0",
            content="Other content",
            metadata={"category": "other"},
            variables=[]
        )
        store.save_prompt(other_info)
        
        # Search by category
        results = store.search_prompts({"metadata_filters": {"category": "greeting"}})
        assert len(results) == 1
        assert results[0].name == "test_prompt"
        
        # Search by name pattern
        results = store.search_prompts({"name_pattern": "test*"})
        assert len(results) == 1
        assert results[0].name == "test_prompt"
        
        # Search by content pattern
        results = store.search_prompts({"content_pattern": "Hello"})
        assert len(results) == 1
        assert results[0].name == "test_prompt"
    
    def test_get_prompt_versions(self, store, sample_prompt_info):
        """Test getting all versions of a prompt."""
        store.save_prompt(sample_prompt_info)
        
        # Add another version
        v2_info = sample_prompt_info.update_content("Updated content")
        store.save_prompt(v2_info)
        
        versions = store.get_prompt_versions("test_prompt")
        assert len(versions) == 2
        assert "1.0" in versions
        assert "1.1" in versions
    
    def test_get_prompt_versions_not_found(self, store):
        """Test getting versions of non-existent prompt."""
        with pytest.raises(PromptNotFoundError, match="Prompt 'nonexistent' not found"):
            store.get_prompt_versions("nonexistent")
    
    def test_exists(self, store, sample_prompt_info):
        """Test checking if prompt exists."""
        assert not store.exists("test_prompt")
        
        store.save_prompt(sample_prompt_info)
        assert store.exists("test_prompt")
        assert store.exists("test_prompt", "1.0")
        assert not store.exists("test_prompt", "2.0")
    
    def test_get_stats(self, store, sample_prompt_info):
        """Test getting store statistics."""
        # Initial stats
        stats = store.get_stats()
        assert stats['total_prompts'] == 0
        assert stats['total_versions'] == 0
        
        # After saving a prompt
        store.save_prompt(sample_prompt_info)
        stats = store.get_stats()
        assert stats['total_prompts'] == 1
        assert stats['total_versions'] == 1
        
        # After adding another version
        v2_info = sample_prompt_info.update_content("Updated content")
        store.save_prompt(v2_info)
        stats = store.get_stats()
        assert stats['total_prompts'] == 1
        assert stats['total_versions'] == 2
    
    def test_store_persistence(self, store, sample_prompt_info):
        """Test that store maintains data across operations."""
        store.save_prompt(sample_prompt_info)
        
        # Verify data is stored
        assert store.exists("test_prompt")
        retrieved = store.get_prompt("test_prompt")
        assert retrieved == sample_prompt_info
        
        # Add another prompt
        other_info = PromptInfo(
            name="other_prompt",
            version="1.0",
            content="Other content",
            metadata={},
            variables=[]
        )
        store.save_prompt(other_info)
        
        # Verify both prompts exist
        assert store.exists("test_prompt")
        assert store.exists("other_prompt")
        
        prompts = store.list_prompts()
        assert len(prompts) == 2 