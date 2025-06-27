"""
Tests for prompt factory.

These tests verify that the PromptFactory correctly creates
stores and services based on configuration.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

# If PromptFactory does not exist, comment out or fix the import
try:
    from agent_service.llms.prompts.factory import PromptFactory
except ImportError:
    PromptFactory = None

from agent_service.llms.prompts.models import PromptConfig, StoreType
from agent_service.llms.prompts.service import PromptService
from agent_service.llms.prompts.stores.memory import InMemoryPromptStore
from agent_service.llms.prompts.exceptions import PromptConfigError


class TestPromptFactory:
    """Test PromptFactory implementation."""
    
    def test_factory_initialization(self):
        """Test factory initialization."""
        factory = PromptFactory()
        assert factory is not None
    
    def test_create_memory_store(self):
        """Test creating memory store."""
        config = PromptConfig(store_type=StoreType.MEMORY)
        
        store = PromptFactory.create_store(config)
        
        assert isinstance(store, InMemoryPromptStore)
    
    def test_create_memory_store_with_config(self):
        """Test creating memory store with configuration."""
        config = PromptConfig(
            store_type=StoreType.MEMORY,
            cache_size=500,
            cache_ttl=1800
        )
        
        store = PromptFactory.create_store(config)
        
        assert isinstance(store, InMemoryPromptStore)
    
    def test_create_local_store_not_implemented(self):
        """Test that local store creation raises error (not implemented yet)."""
        config = PromptConfig(
            store_type=StoreType.LOCAL,
            store_path="/tmp/prompts"
        )
        
        with pytest.raises(NotImplementedError):
            PromptFactory.create_store(config)
    
    def test_create_gcs_store_not_implemented(self):
        """Test that GCS store creation raises error (not implemented yet)."""
        config = PromptConfig(
            store_type=StoreType.GCS,
            gcs_bucket="test-bucket"
        )
        
        with pytest.raises(NotImplementedError):
            PromptFactory.create_store(config)
    
    def test_create_firestore_not_implemented(self):
        """Test that Firestore creation raises error (not implemented yet)."""
        config = PromptConfig(
            store_type=StoreType.FIRESTORE,
            firestore_collection="prompts"
        )
        
        with pytest.raises(NotImplementedError):
            PromptFactory.create_store(config)
    
    def test_create_service_with_memory_store(self):
        """Test creating service with memory store."""
        config = PromptConfig(
            store_type=StoreType.MEMORY,
            cache_size=100,
            cache_ttl=3600,
            enable_caching=True,
            enable_validation=True
        )
        
        service = PromptFactory.create_service(config)
        
        assert isinstance(service, PromptService)
        assert isinstance(service.store, InMemoryPromptStore)
        assert service.config == config
        assert service._cache is not None
        assert service._cache.maxsize == 100
    
    def test_create_service_without_caching(self):
        """Test creating service without caching."""
        config = PromptConfig(
            store_type=StoreType.MEMORY,
            enable_caching=False
        )
        
        service = PromptFactory.create_service(config)
        
        assert isinstance(service, PromptService)
        assert service._cache is None
    
    def test_create_service_without_validation(self):
        """Test creating service without validation."""
        config = PromptConfig(
            store_type=StoreType.MEMORY,
            enable_validation=False
        )
        
        service = PromptFactory.create_service(config)
        
        assert isinstance(service, PromptService)
        assert service.config.enable_validation is False
    
    def test_create_service_from_dict_config(self):
        """Test creating service from dictionary configuration."""
        config_dict = {
            'store_type': 'memory',
            'cache_size': 200,
            'cache_ttl': 7200,
            'enable_caching': True,
            'enable_validation': True
        }
        
        service = PromptFactory.create_service_from_dict(config_dict)
        
        assert isinstance(service, PromptService)
        assert service.config.store_type == StoreType.MEMORY
        assert service.config.cache_size == 200
        assert service.config.cache_ttl == 7200
        assert service.config.enable_caching is True
        assert service.config.enable_validation is True
    
    def test_create_service_from_dict_invalid_store_type(self):
        """Test creating service with invalid store type."""
        config_dict = {
            'store_type': 'invalid_store',
            'enable_caching': False
        }
        
        with pytest.raises(PromptConfigError):
            PromptFactory.create_service_from_dict(config_dict)
    
    def test_create_service_from_dict_missing_required_fields(self):
        """Test creating service with missing required fields."""
        config_dict = {
            'store_type': 'local'  # Missing store_path
        }
        
        with pytest.raises(PromptConfigError):
            PromptFactory.create_service_from_dict(config_dict)
    
    def test_create_service_from_env(self):
        """Test creating service from environment variables."""
        env_vars = {
            'PROMPT_STORE_TYPE': 'memory',
            'PROMPT_CACHE_SIZE': '150',
            'PROMPT_CACHE_TTL': '5400',
            'PROMPT_ENABLE_CACHING': 'true',
            'PROMPT_ENABLE_VALIDATION': 'true'
        }
        
        with patch.dict('os.environ', env_vars):
            service = PromptFactory.create_service_from_env()
            
            assert isinstance(service, PromptService)
            assert service.config.store_type == StoreType.MEMORY
            assert service.config.cache_size == 150
            assert service.config.cache_ttl == 5400
            assert service.config.enable_caching is True
            assert service.config.enable_validation is True
    
    def test_create_service_from_env_defaults(self):
        """Test creating service from environment with defaults."""
        with patch.dict('os.environ', {}, clear=True):
            service = PromptFactory.create_service_from_env()
            
            assert isinstance(service, PromptService)
            assert service.config.store_type == StoreType.MEMORY
            assert service.config.cache_size == 1000  # Default
            assert service.config.cache_ttl == 3600    # Default
            assert service.config.enable_caching is True
            assert service.config.enable_validation is True
    
    def test_create_service_from_env_invalid_values(self):
        """Test creating service from environment with invalid values."""
        env_vars = {
            'PROMPT_STORE_TYPE': 'invalid',
            'PROMPT_CACHE_SIZE': 'not_a_number'
        }
        
        with patch.dict('os.environ', env_vars):
            with pytest.raises(PromptConfigError):
                PromptFactory.create_service_from_env()
    
    def test_get_default_config(self):
        """Test getting default configuration."""
        config = PromptFactory.get_default_config()
        
        assert isinstance(config, PromptConfig)
        assert config.store_type == StoreType.MEMORY
        assert config.cache_size == 1000
        assert config.cache_ttl == 3600
        assert config.enable_caching is True
        assert config.enable_validation is True
    
    def test_validate_config(self):
        """Test config validation."""
        # Valid config
        config = PromptConfig(store_type=StoreType.MEMORY)
        PromptFactory.validate_config(config)
        
        # Invalid config
        with pytest.raises(PromptConfigError):
            PromptFactory.validate_config(None)
    
    def test_create_service_with_custom_store(self):
        """Test creating service with custom store."""
        custom_store = Mock()
        config = PromptConfig(store_type=StoreType.MEMORY)
        
        service = PromptFactory.create_service_with_store(custom_store, config)
        
        assert isinstance(service, PromptService)
        assert service.store == custom_store
        assert service.config == config
    
    def test_factory_singleton_behavior(self):
        """Test that factory can be used as singleton."""
        factory1 = PromptFactory()
        factory2 = PromptFactory()
        
        # Should be different instances (not singleton)
        assert factory1 is not factory2
    
    def test_create_service_with_environment_prefix(self):
        """Test creating service with custom environment prefix."""
        env_vars = {
            'CUSTOM_PROMPT_STORE_TYPE': 'memory',
            'CUSTOM_PROMPT_CACHE_SIZE': '300'
        }
        
        with patch.dict('os.environ', env_vars):
            service = PromptFactory.create_service_from_env(prefix='CUSTOM_PROMPT_')
            
            assert isinstance(service, PromptService)
            assert service.config.store_type == StoreType.MEMORY
            assert service.config.cache_size == 300
    
    def test_create_service_with_override_config(self):
        """Test creating service with override configuration."""
        base_config = PromptConfig(
            store_type=StoreType.MEMORY,
            cache_size=100,
            enable_caching=True
        )
        
        override_config = PromptConfig(
            store_type=StoreType.MEMORY,
            cache_size=200,
            enable_caching=False
        )
        
        service = PromptFactory.create_service_with_override(base_config, override_config)
        
        assert isinstance(service, PromptService)
        assert service.config.cache_size == 200  # Overridden
        assert service.config.enable_caching is False  # Overridden
        assert service.config.store_type == StoreType.MEMORY  # Same
    
    def test_factory_error_handling(self):
        """Test factory error handling."""
        # Test with invalid store type
        config = PromptConfig(store_type=StoreType.LOCAL, store_path="/tmp/prompts")
        with pytest.raises(NotImplementedError):
            PromptFactory.create_store(config)
        
        # Test with None config
        with pytest.raises(PromptConfigError):
            PromptFactory.create_service(None)
        
        # Test with invalid config type
        with pytest.raises(PromptConfigError):
            PromptFactory.create_service("invalid_config") 