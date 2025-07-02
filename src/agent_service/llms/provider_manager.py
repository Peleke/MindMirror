"""
Provider manager for MindMirror LLM integration.

This module provides the ProviderManager class that integrates the provider
factory with the existing MindMirror system and provides high-level management
functions for LLM providers. NO hardcoded defaults - fail fast if config missing.
"""

import logging
from typing import Any, Dict, List, Optional

from langchain_core.language_models import BaseLanguageModel

from agent_service.app.config import get_settings
from .providers.base import BaseProvider
from .providers.factory import ProviderFactory, get_factory

logger = logging.getLogger(__name__)


class ProviderManager:
    """
    High-level manager for LLM providers in MindMirror.

    Integrates the provider factory with the existing system and provides
    convenient methods for model management and configuration.
    NO hardcoded defaults - uses settings and fails fast if config missing.
    """

    def __init__(self):
        """Initialize the provider manager."""
        self._factory: ProviderFactory = get_factory()
        self._settings = get_settings()
        self._validate_configuration()

    def _validate_configuration(self):
        """Validate that required configuration is present."""
        # This will raise if LLM_PROVIDER is not set
        provider = self._settings.llm_provider

        # This will raise if provider-specific model is not set
        model = self._settings.llm_model

        # Validate provider exists
        if not self._factory.get_provider(provider):
            available_providers = self._factory.list_providers()
            raise ValueError(
                f"Provider '{provider}' not found. Available providers: {available_providers}"
            )

        logger.info(f"Validated configuration: provider={provider}, model={model}")

    def get_default_config(self) -> Dict[str, Any]:
        """
        Get configuration for the configured provider and model.

        Returns:
            Configuration dictionary based on settings

        Raises:
            ValueError: If configuration is missing or invalid
        """
        return self.create_config_from_env()

    def create_model(
        self, config: Optional[Dict[str, Any]] = None
    ) -> BaseLanguageModel:
        """
        Create a model using provided config or settings.

        Args:
            config: Optional configuration dictionary. If None, uses settings.

        Returns:
            Configured language model instance

        Raises:
            ValueError: If configuration is missing or invalid
        """
        if config is None:
            config = self.create_config_from_env()

        # Ensure provider is specified
        if "provider" not in config:
            raise ValueError("Provider must be specified in configuration")

        return self._factory.create_model(config)

    def create_model_for_provider(
        self, provider_name: str, model_name: str, **kwargs
    ) -> BaseLanguageModel:
        """
        Create a model for a specific provider and model.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model
            **kwargs: Additional configuration parameters

        Returns:
            Configured language model instance

        Raises:
            ValueError: If provider not found
        """
        if not self._factory.get_provider(provider_name):
            raise ValueError(f"Provider '{provider_name}' not found")

        config = {
            "provider": provider_name,
            "model": model_name,
            "temperature": self._settings.llm_temperature,
            "max_tokens": self._settings.llm_max_tokens,
            "streaming": self._settings.llm_streaming,
        }
        config.update(kwargs)

        # Add provider-specific settings
        if provider_name == "openai":
            api_key = self._settings.llm_api_key  # This will raise if missing
            config["api_key"] = api_key
        elif provider_name == "ollama":
            base_url = self._settings.llm_base_url  # This will raise if missing
            config["base_url"] = base_url
        elif provider_name == "gemini":
            api_key = self._settings.llm_api_key  # This will raise if missing
            config["api_key"] = api_key

        return self._factory.create_model(config)

    def list_available_providers(self) -> List[str]:
        """
        Get list of all available providers.

        Returns:
            List of provider names
        """
        return self._factory.list_providers()

    def list_available_models(self, provider_name: str) -> List[str]:
        """
        Get list of available models for a provider.

        Args:
            provider_name: Name of the provider

        Returns:
            List of model names

        Raises:
            ValueError: If provider not found
        """
        provider = self._factory.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider '{provider_name}' not found")

        return provider.get_supported_models()

    def get_provider_info(self, provider_name: str) -> Dict[str, Any]:
        """
        Get information about a provider.

        Args:
            provider_name: Name of the provider

        Returns:
            Provider information dictionary

        Raises:
            ValueError: If provider not found
        """
        provider = self._factory.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider '{provider_name}' not found")

        return {
            "name": provider.provider_name,
            "supported_models": provider.get_supported_models(),
            "supports_streaming": provider.supports_streaming(),
            "supports_function_calling": provider.supports_function_calling(),
        }

    def get_model_info(self, provider_name: str, model_name: str) -> Dict[str, Any]:
        """
        Get information about a specific model.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model

        Returns:
            Model information dictionary

        Raises:
            ValueError: If provider or model not found
        """
        provider = self._factory.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider '{provider_name}' not found")

        return provider.get_model_info(model_name)

    def test_provider_health(self, provider_name: str) -> bool:
        """
        Test if a provider is healthy and can create models.

        Args:
            provider_name: Name of the provider to test

        Returns:
            True if provider is healthy, False otherwise
        """
        provider = self._factory.get_provider(provider_name)
        if not provider:
            return False

        return provider.test_connection()

    def get_best_available_provider(self) -> Optional[str]:
        """
        Get the best available provider that can create models.

        Returns:
            Name of a working provider or None if none available
        """
        # First try the configured provider
        configured_provider = self._settings.llm_provider
        if self.test_provider_health(configured_provider):
            return configured_provider

        # If configured provider fails, don't try others - fail fast
        logger.error(f"Configured provider '{configured_provider}' is not healthy")
        return None

    def register_custom_provider(self, provider: BaseProvider):
        """
        Register a custom provider.

        Args:
            provider: Provider instance to register
        """
        self._factory.register_provider(provider)
        logger.info(f"Registered custom provider: {provider.provider_name}")

    def get_current_provider(self) -> str:
        """
        Get the currently configured provider.

        Returns:
            Name of the current provider
        """
        return self._settings.llm_provider

    def get_current_model(self) -> str:
        """
        Get the currently configured model.

        Returns:
            Name of the current model
        """
        return self._settings.llm_model

    def create_config_from_env(self) -> Dict[str, Any]:
        """
        Create configuration from settings.

        Returns:
            Configuration dictionary based on application settings

        Raises:
            ValueError: If required configuration is missing
        """
        # Get provider and model from settings (these will raise if missing)
        provider = self._settings.llm_provider
        model = self._settings.llm_model

        config = {
            "provider": provider,
            "model": model,
            "temperature": self._settings.llm_temperature,
            "max_tokens": self._settings.llm_max_tokens,
            "streaming": self._settings.llm_streaming,
        }

        # Add provider-specific parameters (these will raise if missing when required)
        if provider == "openai":
            config["api_key"] = self._settings.llm_api_key
        elif provider == "ollama":
            config["base_url"] = self._settings.llm_base_url
        elif provider == "gemini":
            config["api_key"] = self._settings.llm_api_key
        else:
            raise ValueError(f"Unknown provider: {provider}")

        return config

    def create_model_with_fallback(
        self, config: Optional[Dict[str, Any]] = None
    ) -> BaseLanguageModel:
        """
        Create a model with the provided config or settings.
        NO fallback - fail fast if configuration is invalid.

        Args:
            config: Optional configuration dictionary. If None, uses settings-based config.

        Returns:
            Configured language model instance

        Raises:
            ValueError: If config is invalid or required settings missing
            RuntimeError: If model creation fails
        """
        if config is None:
            # Use settings-based configuration
            config = self.create_config_from_env()
        else:
            # Require explicit provider in config
            if "provider" not in config:
                raise ValueError("Provider must be specified in configuration")

        # Try to create model with provided config - no fallback
        try:
            return self._factory.create_model(config)
        except Exception as e:
            logger.error(f"Failed to create model with config {config}: {e}")
            raise RuntimeError(f"Model creation failed: {e}")


# Global provider manager instance
_provider_manager: Optional[ProviderManager] = None


def get_provider_manager() -> ProviderManager:
    """
    Get the global provider manager instance.

    Returns:
        ProviderManager instance
    """
    global _provider_manager
    if _provider_manager is None:
        _provider_manager = ProviderManager()
    return _provider_manager


def create_model_with_fallback(
    config: Optional[Dict[str, Any]] = None,
) -> BaseLanguageModel:
    """
    Convenience function to create a model using the global provider manager.

    Args:
        config: Optional configuration dictionary

    Returns:
        Configured language model instance
    """
    return get_provider_manager().create_model_with_fallback(config)
