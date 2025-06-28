"""
LLM Providers package for MindMirror.

This package provides a modular system for integrating different LLM providers
with the MindMirror application. It includes base classes, specific provider
implementations, and a factory for managing providers.
"""

from .base import BaseProvider
from .factory import ProviderFactory, create_model, get_factory, health_check
from .gemini_provider import GeminiProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider

__all__ = [
    "BaseProvider",
    "OpenAIProvider",
    "OllamaProvider",
    "GeminiProvider",
    "ProviderFactory",
    "get_factory",
    "create_model",
    "health_check",
]
