"""
Prompt factory implementation.

This module provides the PromptFactory class that creates
stores and services based on configuration.
"""

import os
from typing import Dict, Any, Optional
from copy import deepcopy

from .models import PromptConfig, StoreType
from .service import PromptService
from .stores.memory import InMemoryPromptStore
from .exceptions import PromptConfigError


class PromptFactory:
    """
    Factory for creating prompt stores and services.
    
    This factory provides methods to create stores and services
    based on configuration, environment variables, or dictionaries.
    """
    
    # Default environment variable prefix
    DEFAULT_ENV_PREFIX = "PROMPT_"
    
    # Environment variable mappings
    ENV_MAPPINGS = {
        'store_type': 'STORE_TYPE',
        'store_path': 'STORE_PATH',
        'gcs_bucket': 'GCS_BUCKET',
        'gcs_prefix': 'GCS_PREFIX',
        'firestore_collection': 'FIRESTORE_COLLECTION',
        'cache_size': 'CACHE_SIZE',
        'cache_ttl': 'CACHE_TTL',
        'enable_validation': 'ENABLE_VALIDATION',
        'enable_caching': 'ENABLE_CACHING'
    }
    
    @classmethod
    def create_store(cls, config: PromptConfig):
        """Create a store based on configuration."""
        if not isinstance(config, PromptConfig):
            raise PromptConfigError("config must be a PromptConfig object")
        
        if config.store_type == StoreType.MEMORY:
            return InMemoryPromptStore()
        elif config.store_type == StoreType.LOCAL:
            raise NotImplementedError("Local store not implemented yet")
        elif config.store_type == StoreType.GCS:
            raise NotImplementedError("GCS store not implemented yet")
        elif config.store_type == StoreType.FIRESTORE:
            raise NotImplementedError("Firestore not implemented yet")
        else:
            raise PromptConfigError(f"Unknown store type: {config.store_type}")
    
    @classmethod
    def create_service(cls, config: PromptConfig) -> PromptService:
        """Create a service based on configuration."""
        if not isinstance(config, PromptConfig):
            raise PromptConfigError("config must be a PromptConfig object")
        
        store = cls.create_store(config)
        return PromptService(store=store, config=config)
    
    @classmethod
    def create_service_with_store(cls, store, config: PromptConfig) -> PromptService:
        """Create a service with a custom store."""
        if not isinstance(config, PromptConfig):
            raise PromptConfigError("config must be a PromptConfig object")
        
        return PromptService(store=store, config=config)
    
    @classmethod
    def create_service_from_dict(cls, config_dict: Dict[str, Any]) -> PromptService:
        """Create a service from dictionary configuration."""
        if not isinstance(config_dict, dict):
            raise PromptConfigError("config_dict must be a dictionary")
        
        try:
            config = PromptConfig.from_dict(config_dict)
            return cls.create_service(config)
        except Exception as e:
            raise PromptConfigError(f"Failed to create service from dict: {str(e)}")
    
    @classmethod
    def create_service_from_env(cls, prefix: Optional[str] = None) -> PromptService:
        """Create a service from environment variables."""
        if prefix is None:
            prefix = cls.DEFAULT_ENV_PREFIX
        
        config_dict = {}
        
        # Map environment variables to config
        for config_key, env_suffix in cls.ENV_MAPPINGS.items():
            env_key = f"{prefix}{env_suffix}"
            if env_key in os.environ:
                value = os.environ[env_key]
                
                # Convert string values to appropriate types
                if config_key in ['cache_size', 'cache_ttl']:
                    try:
                        config_dict[config_key] = int(value)
                    except ValueError:
                        raise PromptConfigError(f"Invalid integer value for {config_key}: {value}")
                elif config_key in ['enable_validation', 'enable_caching']:
                    config_dict[config_key] = value.lower() in ['true', '1', 'yes', 'on']
                else:
                    config_dict[config_key] = value
        
        # Use default config if no environment variables set
        if not config_dict:
            config = cls.get_default_config()
        else:
            try:
                config = PromptConfig.from_dict(config_dict)
            except Exception as e:
                raise PromptConfigError(f"Failed to create config from environment: {str(e)}")
        
        return cls.create_service(config)
    
    @classmethod
    def create_service_with_override(cls, base_config: PromptConfig, 
                                   override_config: PromptConfig) -> PromptService:
        """Create a service with override configuration."""
        if not isinstance(base_config, PromptConfig):
            raise PromptConfigError("base_config must be a PromptConfig object")
        if not isinstance(override_config, PromptConfig):
            raise PromptConfigError("override_config must be a PromptConfig object")
        
        # Merge configurations (override takes precedence)
        merged_dict = base_config.to_dict()
        override_dict = override_config.to_dict()
        
        for key, value in override_dict.items():
            if value is not None:  # Only override non-None values
                merged_dict[key] = value
        
        try:
            merged_config = PromptConfig.from_dict(merged_dict)
            return cls.create_service(merged_config)
        except Exception as e:
            raise PromptConfigError(f"Failed to merge configurations: {str(e)}")
    
    @classmethod
    def get_default_config(cls) -> PromptConfig:
        """Get default configuration."""
        return PromptConfig(
            store_type=StoreType.MEMORY,
            cache_size=1000,
            cache_ttl=3600,
            enable_validation=True,
            enable_caching=True
        )
    
    @classmethod
    def validate_config(cls, config: PromptConfig) -> None:
        """Validate configuration."""
        if not isinstance(config, PromptConfig):
            raise PromptConfigError("config must be a PromptConfig object")
        
        # Additional validation can be added here
        if config.store_type not in StoreType:
            raise PromptConfigError(f"Invalid store type: {config.store_type}")
    
    @classmethod
    def get_supported_store_types(cls) -> list:
        """Get list of supported store types."""
        return [StoreType.MEMORY]  # Only memory is implemented for now
    
    @classmethod
    def get_store_requirements(cls, store_type: StoreType) -> Dict[str, str]:
        """Get requirements for a specific store type."""
        requirements = {
            StoreType.MEMORY: {},
            StoreType.LOCAL: {"store_path": "Path to local directory"},
            StoreType.GCS: {"gcs_bucket": "GCS bucket name"},
            StoreType.FIRESTORE: {"firestore_collection": "Firestore collection name"}
        }
        
        return requirements.get(store_type, {})
    
    @classmethod
    def create_test_service(cls) -> PromptService:
        """Create a service suitable for testing."""
        config = PromptConfig(
            store_type=StoreType.MEMORY,
            cache_size=100,
            cache_ttl=300,
            enable_validation=True,
            enable_caching=True
        )
        
        return cls.create_service(config)
    
    @classmethod
    def create_production_service(cls, store_type: StoreType = StoreType.MEMORY,
                                **kwargs) -> PromptService:
        """Create a service suitable for production."""
        config = PromptConfig(
            store_type=store_type,
            cache_size=kwargs.get('cache_size', 10000),
            cache_ttl=kwargs.get('cache_ttl', 7200),
            enable_validation=kwargs.get('enable_validation', True),
            enable_caching=kwargs.get('enable_caching', True),
            **{k: v for k, v in kwargs.items() if k not in ['cache_size', 'cache_ttl', 'enable_validation', 'enable_caching']}
        )
        
        return cls.create_service(config)
    
    @classmethod
    def create_development_service(cls) -> PromptService:
        """Create a service suitable for development."""
        config = PromptConfig(
            store_type=StoreType.MEMORY,
            cache_size=500,
            cache_ttl=1800,
            enable_validation=True,
            enable_caching=True
        )
        
        return cls.create_service(config) 