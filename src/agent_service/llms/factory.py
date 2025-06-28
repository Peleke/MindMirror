"""
LLM factory for centralized language model management.

This module provides a clean interface for creating and configuring
language models with proper tracing and error handling.
"""

import logging
from typing import Any, Dict, Optional

from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from agent_service.tracing.decorators import trace_function

logger = logging.getLogger(__name__)


class LLMFactory:
    """
    Factory for creating and configuring language models.

    Provides centralized management of LLM configurations,
    error handling, and tracing integration.
    """

    # Default configurations for different use cases
    DEFAULT_CONFIGS = {
        "rag": {
            "temperature": 0,
            "streaming": False,
            "max_tokens": 1000,
        },
        "coaching": {
            "temperature": 0.3,
            "streaming": False,
            "max_tokens": 1500,
        },
        "creative": {
            "temperature": 0.7,
            "streaming": False,
            "max_tokens": 2000,
        },
        "analysis": {
            "temperature": 0.1,
            "streaming": False,
            "max_tokens": 2000,
        },
    }

    @staticmethod
    @trace_function(name="llm_factory.create_llm", tags=["llm", "factory"])
    def create_llm(
        provider: str = "openai",
        model_name: Optional[str] = None,
        config_name: Optional[str] = None,
        **kwargs: Any,
    ) -> BaseChatModel:
        """
        Create a language model with the specified configuration.

        Args:
            provider: LLM provider ("openai" or "ollama")
            model_name: Specific model name (optional)
            config_name: Predefined configuration name (optional)
            **kwargs: Additional configuration parameters

        Returns:
            Configured language model
        """
        try:
            # Get base configuration
            base_config = LLMFactory._get_base_config(provider, model_name)

            # Apply predefined config if specified
            if config_name:
                base_config.update(LLMFactory.DEFAULT_CONFIGS.get(config_name, {}))

            # Apply custom kwargs (override defaults)
            base_config.update(kwargs)

            # Create the model
            if provider == "openai":
                return LLMFactory._create_openai_llm(base_config)
            elif provider == "ollama":
                return LLMFactory._create_ollama_llm(base_config)
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")

        except Exception as e:
            logger.error(f"Error creating LLM: {e}")
            raise

    @staticmethod
    def _get_base_config(provider: str, model_name: Optional[str]) -> Dict[str, Any]:
        """Get base configuration for the provider."""
        if provider == "openai":
            return {
                "model_name": model_name or "gpt-4o",
                "temperature": 0,
                "streaming": False,
            }
        elif provider == "ollama":
            return {
                "model": model_name or "llama3",
                "base_url": "http://localhost:11434",
                "temperature": 0,
                "streaming": False,
            }
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    @staticmethod
    def _create_openai_llm(config: Dict[str, Any]) -> ChatOpenAI:
        """Create an OpenAI language model."""
        # Ensure required fields are present
        if "openai_api_key" not in config:
            import os

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            config["openai_api_key"] = api_key

        return ChatOpenAI(**config)

    @staticmethod
    def _create_ollama_llm(config: Dict[str, Any]) -> ChatOllama:
        """Create an Ollama language model."""
        # Handle Docker environment
        if LLMFactory._is_docker_environment():
            config["base_url"] = "http://host.docker.internal:11434"

        return ChatOllama(**config)

    @staticmethod
    def _is_docker_environment() -> bool:
        """Check if running in Docker environment."""
        import os

        return (
            os.path.exists("/.dockerenv")
            or os.getenv("DOCKER_CONTAINER") == "true"
            or os.getenv("IN_DOCKER") == "true"
        )

    @staticmethod
    def get_rag_llm(**kwargs: Any) -> BaseChatModel:
        """
        Get a language model optimized for RAG tasks.

        Args:
            **kwargs: Additional configuration parameters

        Returns:
            Configured LLM for RAG
        """
        return LLMFactory.create_llm(config_name="rag", **kwargs)

    @staticmethod
    def get_coaching_llm(**kwargs: Any) -> BaseChatModel:
        """
        Get a language model optimized for coaching tasks.

        Args:
            **kwargs: Additional configuration parameters

        Returns:
            Configured LLM for coaching
        """
        return LLMFactory.create_llm(config_name="coaching", **kwargs)

    @staticmethod
    def get_creative_llm(**kwargs: Any) -> BaseChatModel:
        """
        Get a language model optimized for creative tasks.

        Args:
            **kwargs: Additional configuration parameters

        Returns:
            Configured LLM for creative tasks
        """
        return LLMFactory.create_llm(config_name="creative", **kwargs)

    @staticmethod
    def get_analysis_llm(**kwargs: Any) -> BaseChatModel:
        """
        Get a language model optimized for analysis tasks.

        Args:
            **kwargs: Additional configuration parameters

        Returns:
            Configured LLM for analysis
        """
        return LLMFactory.create_llm(config_name="analysis", **kwargs)


# Convenience function for backward compatibility
def get_llm(
    provider: str = "openai",
    model_name: Optional[str] = None,
    **kwargs: Any,
) -> BaseChatModel:
    """
    Get a language model (backward compatibility function).

    Args:
        provider: LLM provider
        model_name: Specific model name
        **kwargs: Additional configuration

    Returns:
        Configured language model
    """
    return LLMFactory.create_llm(
        provider=provider,
        model_name=model_name,
        **kwargs,
    )
