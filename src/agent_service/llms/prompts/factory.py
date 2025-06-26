"""
Prompt service factory with configurable storage backends.

This module provides a factory for creating prompt services with different
storage backends based on environment configuration.
"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from .models import PromptConfig, StoreType
from .service import PromptService
from .stores import (
    InMemoryPromptStore,
    YAMLPromptStore,
    GCSPromptStore,
    LocalPromptStore
)
from .stores.gcs import StorageLoader

logger = logging.getLogger(__name__)


class PromptServiceFactory:
    """
    Factory for creating prompt services with configurable storage backends.
    
    Supports environment-based configuration with dependency injection.
    """
    
    @staticmethod
    def create_from_environment() -> PromptService:
        """
        Create a prompt service based on environment variables.
        
        Environment Variables:
        - PROMPT_STORE_TYPE: Storage type (yaml, gcs, memory, local)
        - PROMPT_STORE_PATH: Path for local/YAML storage
        - GCS_BUCKET_NAME: GCS bucket name
        - GCS_EMULATOR_HOST: GCS emulator host (for local testing)
        - GCS_CREDENTIALS_FILE: Path to GCS credentials file
        
        Returns:
            Configured PromptService instance
        """
        store_type = os.getenv("PROMPT_STORE_TYPE", "").lower()
        
        # Default to GCS in production (Docker), YAML in development
        if not store_type:
            if os.getenv("ENVIRONMENT", "").lower() in ["production", "prod"]:
                store_type = "gcs"
            else:
                store_type = "yaml"
        
        logger.info(f"Creating prompt service with store type: {store_type}")
        
        if store_type == "yaml":
            return PromptServiceFactory._create_yaml_service()
        elif store_type == "gcs":
            return PromptServiceFactory._create_gcs_service()
        elif store_type == "memory":
            return PromptServiceFactory._create_memory_service()
        elif store_type == "local":
            return PromptServiceFactory._create_local_service()
        else:
            logger.warning(f"Unknown store type '{store_type}', falling back to memory")
            return PromptServiceFactory._create_memory_service()
    
    @staticmethod
    def _create_yaml_service() -> PromptService:
        """Create a YAML-based prompt service."""
        store_path = os.getenv("PROMPT_STORE_PATH", "./prompts")
        
        # Ensure the path exists
        Path(store_path).mkdir(parents=True, exist_ok=True)
        
        config = PromptConfig(
            store_type=StoreType.YAML,
            store_path=store_path,
            enable_caching=True,
            cache_size=100,
            cache_ttl=3600
        )
        
        store = YAMLPromptStore(store_path)
        logger.info(f"Created YAML prompt service at {store_path}")
        
        return PromptService(store=store, config=config)
    
    @staticmethod
    def _create_gcs_service() -> PromptService:
        """Create a GCS-based prompt service."""
        bucket_name = os.getenv("GCS_BUCKET_NAME", "local_gcs_bucket")
        emulator_host = os.getenv("GCS_EMULATOR_HOST", "localhost:4443")
        credentials_file = os.getenv("GCS_CREDENTIALS_FILE")
        
        # Create storage loader
        loader = StorageLoader(
            bucket_name=bucket_name,
            emulator_host=emulator_host,
            credentials_file=credentials_file
        )
        
        config = PromptConfig(
            store_type=StoreType.GCS,
            gcs_bucket=bucket_name,
            gcs_credentials=credentials_file,
            enable_caching=True,
            cache_size=100,
            cache_ttl=3600
        )
        
        store = GCSPromptStore(loader)
        logger.info(f"Created GCS prompt service with bucket {bucket_name}")
        
        return PromptService(store=store, config=config)
    
    @staticmethod
    def _create_memory_service() -> PromptService:
        """Create an in-memory prompt service."""
        config = PromptConfig(
            store_type=StoreType.MEMORY,
            enable_caching=False,  # No need for caching in memory
            cache_size=0,
            cache_ttl=0
        )
        
        store = InMemoryPromptStore()
        logger.info("Created in-memory prompt service")
        
        return PromptService(store=store, config=config)
    
    @staticmethod
    def _create_local_service() -> PromptService:
        """Create a local filesystem prompt service."""
        store_path = os.getenv("PROMPT_STORE_PATH", "./prompts")
        
        # Ensure the path exists
        Path(store_path).mkdir(parents=True, exist_ok=True)
        
        config = PromptConfig(
            store_type=StoreType.LOCAL,
            local_path=store_path,
            enable_caching=True,
            cache_size=100,
            cache_ttl=3600
        )
        
        store = LocalPromptStore(store_path)
        logger.info(f"Created local prompt service at {store_path}")
        
        return PromptService(store=store, config=config)
    
    @staticmethod
    def create_with_store(store_type: StoreType, **kwargs) -> PromptService:
        """
        Create a prompt service with a specific store type.
        
        Args:
            store_type: The type of store to use
            **kwargs: Additional configuration parameters
            
        Returns:
            Configured PromptService instance
        """
        if store_type == StoreType.YAML:
            store_path = kwargs.get("store_path", "./prompts")
            store = YAMLPromptStore(store_path)
        elif store_type == StoreType.GCS:
            bucket_name = kwargs.get("bucket_name", "local_gcs_bucket")
            emulator_host = kwargs.get("emulator_host", "localhost:4443")
            credentials_file = kwargs.get("credentials_file")
            
            loader = StorageLoader(
                bucket_name=bucket_name,
                emulator_host=emulator_host,
                credentials_file=credentials_file
            )
            store = GCSPromptStore(loader)
        elif store_type == StoreType.MEMORY:
            store = InMemoryPromptStore()
        elif store_type == StoreType.LOCAL:
            store_path = kwargs.get("store_path", "./prompts")
            store = LocalPromptStore(store_path)
        else:
            raise ValueError(f"Unsupported store type: {store_type}")
        
        config = PromptConfig(
            store_type=store_type,
            enable_caching=kwargs.get("enable_caching", True),
            cache_size=kwargs.get("cache_size", 100),
            cache_ttl=kwargs.get("cache_ttl", 3600),
            **{k: v for k, v in kwargs.items() if k not in ["enable_caching", "cache_size", "cache_ttl"]}
        )
        
        return PromptService(store=store, config=config)


# Convenience function for dependency injection
def get_prompt_service() -> PromptService:
    """
    Get a configured prompt service for dependency injection.
    
    This function can be used in FastAPI dependency injection or
    other DI frameworks.
    
    Returns:
        Configured PromptService instance
    """
    return PromptServiceFactory.create_from_environment() 