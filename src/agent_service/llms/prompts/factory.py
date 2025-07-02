"""
Prompt service factory with configurable storage backends.

This module provides a factory for creating prompt services with different
storage backends based on environment configuration.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from .exceptions import PromptConfigError
from .models import PromptConfig, StorageConfig, StoreType
from .service import PromptService
from .stores import (GCSPromptStore, InMemoryPromptStore, LocalPromptStore,
                     YAMLPromptStore)
from .stores.loaders import GCSStorageLoader

logger = logging.getLogger(__name__)


class PromptServiceFactory:
    """
    Factory for creating prompt services with configurable storage backends.

    Supports environment-based configuration with dependency injection.
    """

    @staticmethod
    def get_storage_type_from_environment() -> StoreType:
        """
        Determine the storage type from environment variables.

        Environment Variables:
        - PROMPT_STORAGE_TYPE: Explicit storage type (yaml, gcs, memory, local)
        - ENVIRONMENT: Environment name (development, production)
        - GCS_BUCKET_NAME: GCS bucket name (required for GCS storage)

        Returns:
            StoreType enum value
        """
        # Check for explicit storage type configuration
        explicit_type = os.getenv("PROMPT_STORAGE_TYPE", "").lower()
        logger.debug(f"PROMPT_STORAGE_TYPE: '{explicit_type}'")

        if explicit_type:
            if explicit_type == "yaml":
                return StoreType.YAML
            elif explicit_type == "gcs":
                return StoreType.GCS
            elif explicit_type == "memory":
                return StoreType.MEMORY
            elif explicit_type == "local":
                return StoreType.LOCAL
            else:
                raise ValueError(f"Invalid storage type: {explicit_type}")

        # Check environment-based defaults
        environment = os.getenv("ENVIRONMENT", "").lower()
        gcs_bucket = os.getenv("GCS_BUCKET_NAME")
        logger.debug(f"ENVIRONMENT: '{environment}', GCS_BUCKET_NAME: '{gcs_bucket}'")

        if environment in ["production", "prod"]:
            # Production defaults to GCS if bucket is configured
            if gcs_bucket:
                logger.debug("Production environment with GCS bucket, returning GCS")
                return StoreType.GCS
            else:
                logger.warning(
                    "Production environment but no GCS_BUCKET_NAME, falling back to YAML"
                )
                return StoreType.YAML
        else:
            # Development defaults to YAML
            logger.debug("Development environment, returning YAML")
            return StoreType.YAML

    @staticmethod
    def create_store(config: PromptConfig):
        """Create a store based on configuration."""
        if config.store_type == StoreType.MEMORY:
            return InMemoryPromptStore()
        elif config.store_type == StoreType.YAML:
            store_path = config.store_path or "./prompts"
            return YAMLPromptStore(store_path)
        elif config.store_type == StoreType.LOCAL:
            store_path = config.store_path or "./prompts"
            return LocalPromptStore(base_path=store_path)
        elif config.store_type == StoreType.GCS:
            bucket_name = config.gcs_bucket or "local_gcs_bucket"
            credentials_file = getattr(config, "gcs_credentials", None)

            storage_config = StorageConfig(
                storage_type="gcs",
                gcs_bucket=bucket_name,
                gcs_credentials=credentials_file or "/tmp/default-credentials.json",
            )
            loader = GCSStorageLoader(storage_config)
            return GCSPromptStore(loader)
        else:
            raise NotImplementedError(f"Store type {config.store_type} not implemented")

    @staticmethod
    def create_service(config: PromptConfig) -> PromptService:
        """Create a prompt service with the given configuration."""
        if config is None:
            raise PromptConfigError("Config cannot be None")

        store = PromptServiceFactory.create_store(config)
        return PromptService(store=store, config=config)

    @staticmethod
    def create_service_from_dict(config_dict: Dict[str, Any]) -> PromptService:
        """Create a prompt service from dictionary configuration."""
        try:
            config = PromptConfig.from_dict(config_dict)
            return PromptServiceFactory.create_service(config)
        except Exception as e:
            raise PromptConfigError(f"Invalid configuration: {e}")

    @staticmethod
    def create_service_from_env(prefix: str = "PROMPT_") -> PromptService:
        """Create a prompt service from environment variables."""
        config_dict = {}

        # Map environment variables to config
        env_mapping = {
            f"{prefix}STORE_TYPE": "store_type",
            f"{prefix}STORE_PATH": "store_path",
            f"{prefix}CACHE_SIZE": "cache_size",
            f"{prefix}CACHE_TTL": "cache_ttl",
            f"{prefix}ENABLE_CACHING": "enable_caching",
            f"{prefix}ENABLE_VALIDATION": "enable_validation",
            "GCS_BUCKET_NAME": "gcs_bucket",
        }

        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert string values to appropriate types
                if config_key in ["cache_size", "cache_ttl"]:
                    try:
                        config_dict[config_key] = int(value)
                    except ValueError:
                        raise PromptConfigError(f"Invalid {config_key}: {value}")
                elif config_key in ["enable_caching", "enable_validation"]:
                    config_dict[config_key] = value.lower() in ["true", "1", "yes"]
                else:
                    config_dict[config_key] = value

        # Use defaults if no environment variables set
        if not config_dict:
            config_dict = PromptServiceFactory.get_default_config().to_dict()

        return PromptServiceFactory.create_service_from_dict(config_dict)

    @staticmethod
    def get_default_config() -> PromptConfig:
        """Get default configuration."""
        return PromptConfig(
            store_type=StoreType.MEMORY,
            cache_size=1000,
            cache_ttl=3600,
            enable_caching=True,
            enable_validation=True,
        )

    @staticmethod
    def validate_config(config: PromptConfig) -> bool:
        """Validate configuration."""
        if config is None:
            raise PromptConfigError("Config cannot be None")

        # The PromptConfig class validates itself in __post_init__
        return True

    @staticmethod
    def create_service_with_store(custom_store, config: PromptConfig) -> PromptService:
        """Create a service with a custom store."""
        if config is None:
            config = PromptServiceFactory.get_default_config()

        return PromptService(store=custom_store, config=config)

    @staticmethod
    def create_service_with_override(
        base_config: PromptConfig, override_config: Dict[str, Any]
    ) -> PromptService:
        """Create a service with overridden configuration."""
        if base_config is None:
            base_config = PromptServiceFactory.get_default_config()

        # Merge configurations
        base_dict = base_config.to_dict()

        # Handle case where override_config is a PromptConfig object
        if isinstance(override_config, PromptConfig):
            override_dict = override_config.to_dict()
        else:
            override_dict = override_config

        base_dict.update(override_dict)

        return PromptServiceFactory.create_service_from_dict(base_dict)

    @staticmethod
    def create_from_environment() -> PromptService:
        """
        Create a prompt service based on environment variables.

        Environment Variables:
        - PROMPT_STORAGE_TYPE: Storage type (yaml, gcs, memory, local)
        - PROMPT_STORE_PATH: Path for local/YAML storage
        - GCS_BUCKET_NAME: GCS bucket name
        - GCS_EMULATOR_HOST: GCS emulator host (for local testing)
        - GCS_CREDENTIALS_FILE: Path to GCS credentials file

        Returns:
            Configured PromptService instance
        """
        # Use the new method to determine storage type
        try:
            store_type = PromptServiceFactory.get_storage_type_from_environment()
        except Exception as e:
            logger.warning(
                f"Error determining storage type: {e}, falling back to memory"
            )
            return PromptServiceFactory._create_memory_service()

        logger.info(f"Creating prompt service with store type: {store_type}")

        try:
            if store_type == StoreType.YAML:
                return PromptServiceFactory._create_yaml_service()
            elif store_type == StoreType.GCS:
                return PromptServiceFactory._create_gcs_service()
            elif store_type == StoreType.MEMORY:
                return PromptServiceFactory._create_memory_service()
            elif store_type == StoreType.LOCAL:
                return PromptServiceFactory._create_local_service()
            else:
                logger.warning(
                    f"Unknown store type '{store_type}', falling back to memory"
                )
                return PromptServiceFactory._create_memory_service()
        except Exception as e:
            logger.warning(
                f"Error creating {store_type} service: {e}, falling back to memory"
            )
            return PromptServiceFactory._create_memory_service()

    @staticmethod
    def _create_yaml_service() -> PromptService:
        """Create a YAML-based prompt service."""
        store_path = os.getenv("YAML_STORAGE_PATH", "./prompts")

        # Ensure the path exists
        Path(store_path).mkdir(parents=True, exist_ok=True)

        config = PromptConfig(
            store_type=StoreType.YAML,
            store_path=store_path,
            enable_caching=True,
            cache_size=100,
            cache_ttl=3600,
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

        storage_config = StorageConfig(
            storage_type="gcs",
            gcs_bucket=bucket_name,
            gcs_credentials=credentials_file or "/tmp/default-credentials.json",
        )
        loader = GCSStorageLoader(storage_config)

        config = PromptConfig(
            store_type=StoreType.GCS,
            gcs_bucket=bucket_name,
            enable_caching=True,
            cache_size=100,
            cache_ttl=3600,
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
            cache_size=1,  # Minimum required value
            cache_ttl=0,
        )

        store = InMemoryPromptStore()
        logger.info("Created in-memory prompt service")

        return PromptService(store=store, config=config)

    @staticmethod
    def _create_local_service() -> PromptService:
        """Create a local filesystem prompt service."""
        store_path = os.getenv("YAML_STORAGE_PATH", "./prompts")

        # Ensure the path exists
        Path(store_path).mkdir(parents=True, exist_ok=True)

        config = PromptConfig(
            store_type=StoreType.LOCAL,
            store_path=store_path,
            enable_caching=True,
            cache_size=100,
            cache_ttl=3600,
        )

        store = LocalPromptStore(base_path=store_path)
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

            storage_config = StorageConfig(
                storage_type="gcs",
                gcs_bucket=bucket_name,
                gcs_credentials=credentials_file or "/tmp/default-credentials.json",
            )
            loader = GCSStorageLoader(storage_config)
            store = GCSPromptStore(loader)
        elif store_type == StoreType.MEMORY:
            store = InMemoryPromptStore()
        elif store_type == StoreType.LOCAL:
            store_path = kwargs.get("store_path", "./prompts")
            store = LocalPromptStore(base_path=store_path)
        else:
            raise ValueError(f"Unsupported store type: {store_type}")

        config = PromptConfig(
            store_type=store_type,
            enable_caching=kwargs.get("enable_caching", True),
            cache_size=kwargs.get("cache_size", 100),
            cache_ttl=kwargs.get("cache_ttl", 3600),
            gcs_bucket=kwargs.get("bucket_name") if store_type == StoreType.GCS else kwargs.get("gcs_bucket"),
            store_path=kwargs.get("store_path"),
            enable_validation=kwargs.get("enable_validation", True),
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


# Compatibility alias for tests
PromptFactory = PromptServiceFactory
