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

    def _validate_required_fields(
        self, config: Dict[str, Any], required_fields: List[str]
    ) -> bool:
        """
        Validate that required fields are present in configuration.

        Args:
            config: Configuration dictionary to validate
            required_fields: List of required field names

        Returns:
            True if all required fields are present, False otherwise
        """
        for field in required_fields:
            if field not in config or not config[field]:
                logger.warning(
                    f"Required field '{field}' missing from {self.provider_name} config"
                )
                return False
        return True

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
