"""
Provider factory for managing LLM providers.

This module provides the ProviderFactory class that manages all available
LLM providers and provides a unified interface for model creation.
"""

import logging
from typing import Any, Dict, List, Optional, Type

from langchain_core.language_models import BaseLanguageModel

from .base import BaseProvider
from .gemini_provider import GeminiProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


class ProviderFactory:
    """
    Factory class for managing LLM providers.

    Provides a unified interface for creating models from different providers
    and managing provider configurations.
    """

    def __init__(self):
        """Initialize the provider factory with all available providers."""
        self._providers: Dict[str, BaseProvider] = {}
        self._register_default_providers()

    def _register_default_providers(self):
        """Register all default providers."""
        providers = [OpenAIProvider(), OllamaProvider(), GeminiProvider()]

        for provider in providers:
            self.register_provider(provider)

    def register_provider(self, provider: BaseProvider):
        """
        Register a new provider.

        Args:
            provider: Provider instance to register
        """
        self._providers[provider.provider_name] = provider
        logger.info(f"Registered provider: {provider.provider_name}")

    def get_provider(self, provider_name: str) -> Optional[BaseProvider]:
        """
        Get a provider by name.

        Args:
            provider_name: Name of the provider

        Returns:
            Provider instance or None if not found
        """
        return self._providers.get(provider_name)

    def list_providers(self) -> List[str]:
        """
        Get list of all registered provider names.

        Returns:
            List of provider names
        """
        return list(self._providers.keys())

    def create_model(self, config: Dict[str, Any]) -> BaseLanguageModel:
        """
        Create a model using the specified configuration.

        Args:
            config: Configuration dictionary containing provider and model parameters

        Returns:
            Configured language model instance

        Raises:
            ValueError: If provider is not specified or not found
            RuntimeError: If model creation fails
        """
        # Extract provider name from config
        provider_name = config.get("provider")
        if not provider_name:
            raise ValueError("Provider name must be specified in configuration")

        # Get provider
        provider = self.get_provider(provider_name)
        if not provider:
            available_providers = ", ".join(self.list_providers())
            raise ValueError(
                f"Provider '{provider_name}' not found. Available providers: {available_providers}"
            )

        # Create model using provider
        try:
            return provider.create_model(config)
        except Exception as e:
            logger.error(f"Failed to create model with provider '{provider_name}': {e}")
            raise RuntimeError(f"Model creation failed: {str(e)}")

    def get_supported_models(
        self, provider_name: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """
        Get supported models for all providers or a specific provider.

        Args:
            provider_name: Optional provider name to filter results

        Returns:
            Dictionary mapping provider names to lists of supported models
        """
        if provider_name:
            provider = self.get_provider(provider_name)
            if provider:
                return {provider_name: provider.get_supported_models()}
            return {}

        result = {}
        for name, provider in self._providers.items():
            result[name] = provider.get_supported_models()

        return result

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration for the specified provider.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if configuration is valid, False otherwise
        """
        provider_name = config.get("provider")
        if not provider_name:
            logger.error("Provider name not specified in configuration")
            return False

        provider = self.get_provider(provider_name)
        if not provider:
            logger.error(f"Provider '{provider_name}' not found")
            return False

        return provider.validate_config(config)

    def health_check(self, provider_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform health check for all providers or a specific provider.

        Args:
            provider_name: Optional provider name to check

        Returns:
            Dictionary containing health check results
        """
        if provider_name:
            return self._check_provider_health(provider_name)

        results = {}
        for name in self.list_providers():
            results[name] = self._check_provider_health(name)

        return results

    def _check_provider_health(self, provider_name: str) -> Dict[str, Any]:
        """
        Check health of a specific provider.

        Args:
            provider_name: Name of the provider to check

        Returns:
            Health check result dictionary
        """
        provider = self.get_provider(provider_name)
        if not provider:
            return {
                "status": "error",
                "message": f"Provider '{provider_name}' not found",
            }

        try:
            # Get test configuration
            test_config = provider._get_test_config()
            if not test_config:
                return {
                    "status": "warning",
                    "message": f"No API key available for provider '{provider_name}'",
                }

            # Add provider name to test config
            test_config["provider"] = provider_name

            # Try to create a model
            model = provider.create_model(test_config)

            return {
                "status": "healthy",
                "message": f"Provider '{provider_name}' is working correctly",
                "model_type": type(model).__name__,
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Provider '{provider_name}' health check failed: {str(e)}",
            }

    def get_provider_info(self, provider_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a provider.

        Args:
            provider_name: Name of the provider

        Returns:
            Dictionary containing provider information
        """
        provider = self.get_provider(provider_name)
        if not provider:
            return {}

        return {
            "name": provider.provider_name,
            "supported_models": provider.get_supported_models(),
            "health_status": self._check_provider_health(provider_name),
        }

    def get_model_info(self, provider_name: str, model_name: str) -> Dict[str, Any]:
        """
        Get information about a specific model from a provider.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model

        Returns:
            Dictionary containing model information
        """
        provider = self.get_provider(provider_name)
        if not provider:
            return {}

        if hasattr(provider, "get_model_info"):
            return provider.get_model_info(model_name)

        return {}

    def create_config_template(
        self, provider_name: str, model_name: str
    ) -> Dict[str, Any]:
        """
        Create a configuration template for a specific provider and model.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model

        Returns:
            Configuration template dictionary
        """
        provider = self.get_provider(provider_name)
        if not provider:
            return {}

        # Base template
        template = {
            "provider": provider_name,
            "model": model_name,
            "temperature": 0.7,
            "max_tokens": 1000,
            "streaming": False,
        }

        # Add provider-specific parameters
        if provider_name == "openai":
            template.update({"api_key": "your-openai-api-key-here"})
        elif provider_name == "ollama":
            template.update(
                {"base_url": "http://localhost:11434"}  # Default Ollama URL
            )
        elif provider_name == "gemini":
            template.update({"api_key": "your-google-api-key-here"})

        return template


# Global factory instance
_factory_instance: Optional[ProviderFactory] = None


def get_factory() -> ProviderFactory:
    """
    Get the global provider factory instance.

    Returns:
        Global ProviderFactory instance
    """
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = ProviderFactory()
    return _factory_instance


def create_model(config: Dict[str, Any]) -> BaseLanguageModel:
    """
    Convenience function to create a model using the global factory.

    Args:
        config: Configuration dictionary

    Returns:
        Configured language model instance
    """
    return get_factory().create_model(config)


def health_check(provider_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to perform health check using the global factory.

    Args:
        provider_name: Optional provider name to check

    Returns:
        Health check results
    """
    return get_factory().health_check(provider_name)
