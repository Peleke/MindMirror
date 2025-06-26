"""
Service compatibility layer.

This package provides compatibility between old and new service implementations
to ensure smooth migration and backward compatibility.
"""

from .service_factory import ServiceFactory
from .legacy_llm_service import LegacyLLMService

__all__ = [
    'ServiceFactory',
    'LegacyLLMService'
] 