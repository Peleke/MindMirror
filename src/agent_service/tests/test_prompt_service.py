"""
Tests for prompt service.

These tests verify that the PromptService correctly orchestrates
storage operations, caching, and provides a high-level interface
for prompt management.
"""

import pytest
from unittest.mock import Mock, patch
from typing import List, Optional
from datetime import datetime

from agent_service.llms.prompts.service import PromptService
from agent_service.llms.prompts.models import PromptInfo, PromptConfig, StoreType
from agent_service.llms.prompts.stores.memory import InMemoryPromptStore
from agent_service.llms.prompts.exceptions import PromptNotFoundError, PromptValidationError


class TestPromptService:
    """Test PromptService implementation."""
    
    @pytest.fixture
    def mock_store(self):
        """Create a mock store for testing."""
        return Mock(spec=InMemoryPromptStore)
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return PromptConfig(
            store_type=StoreType.MEMORY,
            cache_size=100,
            cache_ttl=3600,
            enable_validation=True,
            enable_caching=True
        )
    
    @pytest.fixture
    def service(self, mock_store, config):
        """Create a PromptService with mock store."""
        return PromptService(store=mock_store, config=config)
    
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
    
    def test_service_initialization(self, mock_store, config):
        """Test service initialization."""
        service = PromptService(store=mock_store, config=config)
        
        assert service.store == mock_store
        assert service.config == config
        assert service._cache is not None
        assert service._cache.maxsize == 100
    
    def test_service_initialization_without_cache(self, mock_store):
        """Test service initialization without caching."""
        config = PromptConfig(
            store_type=StoreType.MEMORY,
            enable_caching=False
        )
        service = PromptService(store=mock_store, config=config)
        
        assert service._cache is None
    
    def test_get_prompt_with_cache_hit(self, service, sample_prompt_info):
        """Test getting a prompt with cache hit."""
        # Setup cache
        cache_key = f"test_prompt:1.0"
        service._cache[cache_key] = sample_prompt_info
        
        # Mock store to ensure it's not called
        service.store.get_prompt.return_value = sample_prompt_info
        
        result = service.get_prompt("test_prompt", "1.0")
        
        assert result == sample_prompt_info
        service.store.get_prompt.assert_not_called()
    
    def test_get_prompt_with_cache_miss(self, service, sample_prompt_info):
        """Test getting a prompt with cache miss."""
        # Mock store response
        service.store.get_prompt.return_value = sample_prompt_info
        
        result = service.get_prompt("test_prompt", "1.0")
        
        assert result == sample_prompt_info
        service.store.get_prompt.assert_called_once_with("test_prompt", "1.0")
        
        # Check that result is cached
        cache_key = f"test_prompt:1.0"
        assert service._cache[cache_key] == sample_prompt_info
    
    def test_get_prompt_without_version(self, service, sample_prompt_info):
        """Test getting a prompt without version (should get latest)."""
        # Mock store responses
        service.store.get_latest_version.return_value = "1.0"
        service.store.get_prompt.return_value = sample_prompt_info
        
        result = service.get_prompt("test_prompt")
        
        assert result == sample_prompt_info
        service.store.get_latest_version.assert_called_once_with("test_prompt")
        service.store.get_prompt.assert_called_once_with("test_prompt", "1.0")
    
    def test_get_prompt_not_found(self, service):
        """Test getting a non-existent prompt."""
        service.store.get_prompt.side_effect = PromptNotFoundError("Prompt not found")
        
        with pytest.raises(PromptNotFoundError, match="Prompt not found"):
            service.get_prompt("nonexistent", "1.0")
    
    def test_save_prompt(self, service, sample_prompt_info):
        """Test saving a prompt."""
        service.save_prompt(sample_prompt_info)
        
        service.store.save_prompt.assert_called_once_with(sample_prompt_info)
        
        # Check that cache is invalidated
        cache_key = f"test_prompt:1.0"
        assert cache_key not in service._cache
    
    def test_save_prompt_invalidates_cache(self, service, sample_prompt_info):
        """Test that saving a prompt invalidates cache."""
        # First, cache the prompt
        cache_key = f"test_prompt:1.0"
        service._cache[cache_key] = sample_prompt_info
        
        # Save the prompt
        service.save_prompt(sample_prompt_info)
        
        # Check that cache is cleared
        assert cache_key not in service._cache
    
    def test_save_prompt_without_validation(self, service, sample_prompt_info):
        """Test saving a prompt without validation."""
        config = PromptConfig(
            store_type=StoreType.MEMORY,
            enable_validation=False
        )
        service = PromptService(store=service.store, config=config)
        
        # Should not raise validation errors
        service.save_prompt(sample_prompt_info)
        service.store.save_prompt.assert_called_once_with(sample_prompt_info)
    
    def test_delete_prompt(self, service):
        """Test deleting a prompt."""
        service.delete_prompt("test_prompt", "1.0")
        
        service.store.delete_prompt.assert_called_once_with("test_prompt", "1.0")
        
        # Check that cache is invalidated
        cache_key = f"test_prompt:1.0"
        assert cache_key not in service._cache
    
    def test_delete_prompt_without_version(self, service):
        """Test deleting a prompt without version."""
        service.store.get_latest_version.return_value = "1.0"
        
        service.delete_prompt("test_prompt")
        
        service.store.get_latest_version.assert_called_once_with("test_prompt")
        service.store.delete_prompt.assert_called_once_with("test_prompt", "1.0")
    
    def test_list_prompts(self, service, sample_prompt_info):
        """Test listing prompts."""
        service.store.list_prompts.return_value = [sample_prompt_info]
        
        result = service.list_prompts()
        
        assert result == [sample_prompt_info]
        service.store.list_prompts.assert_called_once()
    
    def test_get_latest_version(self, service):
        """Test getting latest version."""
        service.store.get_latest_version.return_value = "1.0"
        
        result = service.get_latest_version("test_prompt")
        
        assert result == "1.0"
        service.store.get_latest_version.assert_called_once_with("test_prompt")
    
    def test_search_prompts(self, service, sample_prompt_info):
        """Test searching prompts."""
        criteria = {"name_pattern": "test*"}
        service.store.search_prompts.return_value = [sample_prompt_info]
        
        result = service.search_prompts(criteria)
        
        assert result == [sample_prompt_info]
        service.store.search_prompts.assert_called_once_with(criteria)
    
    def test_get_prompt_versions(self, service):
        """Test getting prompt versions."""
        versions = ["1.0", "1.1", "2.0"]
        service.store.get_prompt_versions.return_value = versions
        
        result = service.get_prompt_versions("test_prompt")
        
        assert result == versions
        service.store.get_prompt_versions.assert_called_once_with("test_prompt")
    
    def test_exists(self, service):
        """Test checking if prompt exists."""
        service.store.exists.return_value = True
        
        result = service.exists("test_prompt", "1.0")
        
        assert result is True
        service.store.exists.assert_called_once_with("test_prompt", "1.0")
    
    def test_get_stats(self, service):
        """Test getting statistics."""
        stats = {"total_prompts": 10, "total_versions": 15}
        service.store.get_stats.return_value = stats
        
        result = service.get_stats()
        
        assert result == stats
        service.store.get_stats.assert_called_once()
    
    def test_render_prompt(self, service, sample_prompt_info):
        """Test rendering a prompt."""
        # Mock store responses
        service.store.get_latest_version.return_value = "1.0"
        service.store.get_prompt.return_value = sample_prompt_info
        
        # Mock Jinja2 template rendering
        with patch('agent_service.llms.prompts.service.Template') as mock_template:
            mock_template.return_value.render.return_value = "Hello John!"
            
            result = service.render_prompt("test_prompt", {"name": "John"})
            
            assert result == "Hello John!"
            service.store.get_latest_version.assert_called_once_with("test_prompt")
            service.store.get_prompt.assert_called_once_with("test_prompt", "1.0")
            mock_template.assert_called_once_with("Hello {{ name }}!")
    
    def test_render_prompt_with_version(self, service, sample_prompt_info):
        """Test rendering a prompt with specific version."""
        service.store.get_prompt.return_value = sample_prompt_info
        
        with patch('agent_service.llms.prompts.service.Template') as mock_template:
            mock_template.return_value.render.return_value = "Hello John!"
            
            result = service.render_prompt("test_prompt", {"name": "John"}, version="1.0")
            
            assert result == "Hello John!"
            service.store.get_prompt.assert_called_once_with("test_prompt", "1.0")
    
    def test_render_prompt_not_found(self, service):
        """Test rendering a non-existent prompt."""
        service.store.get_prompt.side_effect = PromptNotFoundError("Prompt not found")
        
        with pytest.raises(PromptNotFoundError, match="Prompt not found"):
            service.render_prompt("nonexistent", {"name": "John"})
    
    def test_render_prompt_template_error(self, service, sample_prompt_info):
        """Test rendering a prompt with template error."""
        service.store.get_prompt.return_value = sample_prompt_info
        
        with patch('agent_service.llms.prompts.service.Template') as mock_template:
            mock_template.side_effect = Exception("Template error")
            
            with pytest.raises(Exception, match="Template error"):
                service.render_prompt("test_prompt", {"name": "John"})
    
    def test_cache_eviction(self, service):
        """Test that cache eviction works correctly."""
        # Fill the cache beyond its size
        for i in range(150):  # More than cache size of 100
            cache_key = f"prompt_{i}:1.0"
            service._cache[cache_key] = Mock()
        
        # Cache should not exceed max size
        assert len(service._cache) <= 100
    
    def test_cache_ttl(self, service, sample_prompt_info):
        """Test cache TTL functionality."""
        # This would require more complex time-based testing
        # For now, just verify the cache is used
        service.store.get_prompt.return_value = sample_prompt_info
        
        # First call should cache
        result1 = service.get_prompt("test_prompt", "1.0")
        
        # Second call should use cache
        result2 = service.get_prompt("test_prompt", "1.0")
        
        assert result1 == result2
        # Store should only be called once
        service.store.get_prompt.assert_called_once()
    
    def test_clear_cache(self, service, sample_prompt_info):
        """Test clearing the cache."""
        # Add something to cache
        cache_key = f"test_prompt:1.0"
        service._cache[cache_key] = sample_prompt_info
        
        # Clear cache
        service.clear_cache()
        
        # Cache should be empty
        assert len(service._cache) == 0
    
    def test_get_cache_stats(self, service):
        """Test getting cache statistics."""
        # Add some items to cache
        for i in range(5):
            cache_key = f"prompt_{i}:1.0"
            service._cache[cache_key] = Mock()
        
        stats = service.get_cache_stats()
        
        assert 'size' in stats
        assert 'maxsize' in stats
        assert 'hits' in stats
        assert 'misses' in stats
        assert stats['size'] == 5
        assert stats['maxsize'] == 100
    
    def test_service_without_cache_stats(self, mock_store):
        """Test cache stats when caching is disabled."""
        config = PromptConfig(
            store_type=StoreType.MEMORY,
            enable_caching=False
        )
        service = PromptService(store=mock_store, config=config)
        
        stats = service.get_cache_stats()
        
        assert stats['size'] == 0
        assert stats['maxsize'] == 0
        assert stats['hits'] == 0
        assert stats['misses'] == 0 