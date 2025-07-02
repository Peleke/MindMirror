"""
LLM Management package for MindMirror.

This package provides high-level management of LLM providers and models
for the MindMirror application. It includes the provider manager and
convenience functions for model creation and management.
"""

from .provider_manager import (ProviderManager,
                               create_model_with_fallback,
                               get_provider_manager)
from .providers import (BaseProvider, GeminiProvider, OllamaProvider,
                        OpenAIProvider, ProviderFactory)

__all__ = [
    "ProviderManager",
    "get_provider_manager",
    "create_model_with_fallback",
    "BaseProvider",
    "OpenAIProvider",
    "OllamaProvider",
    "GeminiProvider",
    "ProviderFactory",
]
