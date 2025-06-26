"""
Service compatibility layer.

This package provides compatibility between old and new service implementations
to ensure smooth migration and backward compatibility.
"""

from .service_factory import ServiceFactory

__all__ = [
    'ServiceFactory'
] 