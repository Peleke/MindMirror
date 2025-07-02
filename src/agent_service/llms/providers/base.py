"""
Base provider interface for LLM backends.

This module defines the LLMProvider Protocol and BaseProvider abstract class
that all LLM providers must implement for the MindMirror system.
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol

from langchain_core.language_models import BaseChatModel

logger = logging.getLogger(__name__)


class LLMProvider(Protocol):
    """
    Protocol defining the interface for LLM providers.

    All LLM providers must implement these methods to be compatible
    with the MindMirror LLM service layer.
    """

    def create_model(self, config: Dict[str, Any]) -> BaseChatModel:
        """
        Create a LangChain model instance from configuration.

        Args:
            config: Configuration dictionary containing model parameters

        Returns:
            Configured LangChain model instance

        Raises:
            ValueError: If required configuration is missing or invalid
            RuntimeError: If model creation fails
        """
        ...

    def get_supported_models(self) -> List[str]:
        """
        Get list of supported model names for this provider.

        Returns:
            List of supported model identifiers
        """
        ...

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration for this provider.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if configuration is valid, False otherwise
        """
        ...

    def get_provider_name(self) -> str:
        """
        Get the name of this provider.

        Returns:
            Provider name (e.g., "openai", "ollama", "gemini")
        """
        ...


class BaseProvider(ABC):
    """
    Abstract base class for LLM providers.

    Provides common functionality and enforces the LLMProvider protocol.
    All concrete providers should inherit from this class.
    """

    def __init__(self, provider_name: str):
        """
        Initialize the base provider.

        Args:
            provider_name: Name of the provider (e.g., "openai", "ollama")
        """
        self.provider_name = provider_name
        self._supported_models: List[str] = []

    @abstractmethod
    def create_model(self, config: Dict[str, Any]) -> BaseChatModel:
        """
        Create a LangChain model instance from configuration.

        Args:
            config: Configuration dictionary containing model parameters

        Returns:
            Configured LangChain model instance

        Raises:
            ValueError: If required configuration is missing or invalid
            RuntimeError: If model creation fails
        """
        pass

    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """
        Get list of supported model names for this provider.

        Returns:
            List of supported model identifiers
        """
        return self._supported_models

    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration for this provider.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if configuration is valid, False otherwise
        """
        pass

    def get_provider_name(self) -> str:
        """
        Get the name of this provider.

        Returns:
            Provider name
        """
        return self.provider_name

    def test_connection(self) -> bool:
        """
        Test if the provider can connect and create models.

        Returns:
            True if provider is healthy, False otherwise
        """
        try:
            # Try to create a model with minimal config to test connectivity
            test_config = {"provider": self.provider_name}

            # Add required fields based on provider type
            if self.provider_name == "openai":
                import os

                if not os.getenv("OPENAI_API_KEY"):
                    return False
                test_config.update(
                    {
                        "model": "gpt-3.5-turbo",
                        "api_key": os.getenv("OPENAI_API_KEY"),
                        "temperature": 0,
                        "max_tokens": 1,
                    }
                )
            elif self.provider_name == "ollama":
                test_config.update(
                    {
                        "model": "llama3.2",
                        "base_url": "http://localhost:11434",
                        "temperature": 0,
                    }
                )
            elif self.provider_name == "gemini":
                import os

                if not os.getenv("GOOGLE_API_KEY"):
                    return False
                test_config.update(
                    {
                        "model": "gemini-pro",
                        "api_key": os.getenv("GOOGLE_API_KEY"),
                        "temperature": 0,
                    }
                )

            # Try to validate config (lightweight test)
            return self.validate_config(test_config)

        except Exception:
            return False

    def supports_streaming(self) -> bool:
        """
        Check if this provider supports streaming.

        Returns:
            True if streaming is supported, False otherwise
        """
        return True  # Most providers support streaming

    def supports_function_calling(self) -> bool:
        """
        Check if this provider supports function calling.

        Returns:
            True if function calling is supported, False otherwise
        """
        return False  # Override in specific providers as needed

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get information about a specific model.

        Args:
            model_name: Name of the model

        Returns:
            Model information dictionary
        """
        if model_name not in self.get_supported_models():
            raise ValueError(
                f"Model '{model_name}' not supported by {self.provider_name}"
            )

        return {"name": model_name, "provider": self.provider_name, "supported": True}

    def _validate_required_fields(
        self, config: Dict[str, Any], required_fields: List[str]
    ) -> bool:
        """
        Helper method to validate required fields in configuration.

        Args:
            config: Configuration dictionary to validate
            required_fields: List of required field names

        Returns:
            True if all required fields are present, False otherwise
        """
        for field in required_fields:
            if field not in config or config[field] is None:
                logger.error(
                    f"Missing required field '{field}' for {self.provider_name} provider"
                )
                return False
        return True

    def _get_api_key(self, config: Dict[str, Any], env_var: str) -> str:
        """
        Get API key from config or environment variable.

        Args:
            config: Configuration dictionary
            env_var: Environment variable name to fall back to

        Returns:
            API key string

        Raises:
            ValueError: If API key is not found in config or environment
        """
        # Check config first
        if "api_key" in config and config["api_key"]:
            return config["api_key"]

        # Fall back to environment variable
        api_key = os.getenv(env_var)
        if not api_key:
            raise ValueError(
                f"API key not found in config or environment variable {env_var}"
            )

        return api_key

    def _log_model_creation(self, model_name: str, config: Dict[str, Any]) -> None:
        """
        Log model creation for observability.

        Args:
            model_name: Name of the model being created
            config: Configuration used to create the model
        """
        logger.info(f"Creating {self.provider_name} model: {model_name}")
        logger.debug(f"Model config: {config}")

    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on this provider.

        Returns:
            Health status dictionary
        """
        try:
            # Basic health check - can we create a minimal config?
            test_config = self._get_test_config()
            if test_config:
                # Try to create a model (this might fail if API keys are missing)
                try:
                    model = self.create_model(test_config)
                    return {
                        "status": "healthy",
                        "provider": self.provider_name,
                        "supported_models": self.get_supported_models(),
                        "model_creation": "success",
                    }
                except (ValueError, RuntimeError) as e:
                    return {
                        "status": "degraded",
                        "provider": self.provider_name,
                        "supported_models": self.get_supported_models(),
                        "model_creation": "failed",
                        "error": str(e),
                    }
            else:
                return {
                    "status": "unhealthy",
                    "provider": self.provider_name,
                    "error": "No test configuration available",
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": self.provider_name,
                "error": str(e),
            }

    def _get_test_config(self) -> Optional[Dict[str, Any]]:
        """
        Get a minimal test configuration for health checks.

        Returns:
            Minimal configuration dictionary or None if not available
        """
        # Default implementation - override in subclasses
        return None
