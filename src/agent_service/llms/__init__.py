"""
LLM Management package for MindMirror.

This package provides high-level management of LLM providers and models
for the MindMirror application. It includes the provider manager and
convenience functions for model creation and management.
"""

from .provider_manager import (
    ProviderManager,
    get_provider_manager,
    create_model,
    create_model_with_fallback,
    get_provider_status
)
from .providers import (
    BaseProvider,
    OpenAIProvider,
    OllamaProvider,
    GeminiProvider,
    ProviderFactory
)

__all__ = [
    "ProviderManager",
    "get_provider_manager",
    "create_model",
    "create_model_with_fallback", 
    "get_provider_status",
    "BaseProvider",
    "OpenAIProvider",
    "OllamaProvider",
    "GeminiProvider",
    "ProviderFactory"
] 