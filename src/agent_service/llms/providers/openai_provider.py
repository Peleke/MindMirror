"""
OpenAI provider implementation for LangChain integration.

This module provides the OpenAIProvider class that handles OpenAI model
creation, configuration validation, and API key management.
"""

import logging
from typing import Any, Dict, List, Optional

from langchain_openai import ChatOpenAI

from .base import BaseProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseProvider):
    """
    OpenAI provider for LangChain integration.

    Handles OpenAI model creation with proper API key management,
    configuration validation, and model selection.
    """

    def __init__(self):
        """Initialize the OpenAI provider."""
        super().__init__("openai")
        self._supported_models = [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-4",
            "gpt-4-32k",
            "gpt-4o",
            "gpt-4o-mini",
        ]

    def create_model(self, config: Dict[str, Any]) -> ChatOpenAI:
        """
        Create an OpenAI ChatOpenAI model instance.

        Args:
            config: Configuration dictionary containing model parameters

        Returns:
            Configured ChatOpenAI instance

        Raises:
            ValueError: If required configuration is missing or invalid
            RuntimeError: If model creation fails
        """
        try:
            # Validate configuration
            if not self.validate_config(config):
                raise ValueError(
                    f"Invalid configuration for {self.provider_name} provider"
                )

            # Get API key from config or environment
            api_key = self._get_api_key(config, "OPENAI_API_KEY")

            # Extract model parameters
            model_name = config.get("model", config.get("model_name"))
            if not model_name:
                raise ValueError("Model name must be specified in configuration")
            temperature = config.get("temperature", 0.7)
            max_tokens = config.get("max_tokens", 1000)
            streaming = config.get("streaming", False)

            # Create model configuration
            model_config = {
                "openai_api_key": api_key,
                "model": model_name,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "streaming": streaming,
            }

            # Add optional parameters if provided
            if "base_url" in config:
                model_config["base_url"] = config["base_url"]

            if "timeout" in config:
                model_config["timeout"] = config["timeout"]

            if "max_retries" in config:
                model_config["max_retries"] = config["max_retries"]

            # Log model creation
            self._log_model_creation(model_name, model_config)

            # Create and return the model
            return ChatOpenAI(**model_config)

        except Exception as e:
            logger.error(f"Failed to create OpenAI model: {e}")
            raise RuntimeError(f"OpenAI model creation failed: {str(e)}")

    def get_supported_models(self) -> List[str]:
        """
        Get list of supported OpenAI models.

        Returns:
            List of supported model identifiers
        """
        return self._supported_models.copy()

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate OpenAI configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if configuration is valid, False otherwise
        """
        # Check for required model field
        if not self._validate_required_fields(config, ["model"]):
            return False

        # Validate model name
        model_name = config.get("model", config.get("model_name"))
        if model_name not in self._supported_models:
            logger.warning(f"Unsupported OpenAI model: {model_name}")
            # Don't fail validation for unsupported models - they might still work
            # Just log a warning

        # Validate temperature range
        temperature = config.get("temperature", 0.7)
        if (
            not isinstance(temperature, (int, float))
            or temperature < 0
            or temperature > 2
        ):
            logger.warning(
                f"Invalid temperature value: {temperature}. Must be between 0 and 2."
            )
            return False

        # Validate max_tokens
        max_tokens = config.get("max_tokens", 1000)
        if not isinstance(max_tokens, int) or max_tokens <= 0:
            logger.warning(
                f"Invalid max_tokens value: {max_tokens}. Must be positive integer."
            )
            return False

        return True

    def _get_test_config(self) -> Optional[Dict[str, Any]]:
        """
        Get a minimal test configuration for health checks.

        Returns:
            Minimal configuration dictionary or None if API key not available
        """
        # Check if API key is available
        api_key = self._get_api_key({}, "OPENAI_API_KEY")
        if api_key:
            return {
                "model": "gpt-4o-mini",  # Use cheapest model for health checks
                "temperature": 0.0,
                "max_tokens": 10,
                "streaming": False,
            }
        return None

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get information about a specific OpenAI model.

        Args:
            model_name: Name of the model

        Returns:
            Dictionary containing model information
        """
        model_info = {
            "gpt-3.5-turbo": {
                "max_tokens": 4096,
                "supports_streaming": True,
                "cost_per_1k_tokens": 0.0015,
            },
            "gpt-3.5-turbo-16k": {
                "max_tokens": 16384,
                "supports_streaming": True,
                "cost_per_1k_tokens": 0.003,
            },
            "gpt-4": {
                "max_tokens": 8192,
                "supports_streaming": True,
                "cost_per_1k_tokens": 0.03,
            },
            "gpt-4-32k": {
                "max_tokens": 32768,
                "supports_streaming": True,
                "cost_per_1k_tokens": 0.06,
            },
            "gpt-4o": {
                "max_tokens": 128000,
                "supports_streaming": True,
                "cost_per_1k_tokens": 0.005,
            },
            "gpt-4o-mini": {
                "max_tokens": 128000,
                "supports_streaming": True,
                "cost_per_1k_tokens": 0.00015,
            },
        }

        return model_info.get(model_name, {})
