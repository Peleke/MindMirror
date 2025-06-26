"""
Storage loaders for prompt stores.

This module provides storage abstraction layer that allows
switching between local and GCS storage backends.
"""

from .protocol import StorageLoader
from .local import LocalStorageLoader
from .gcs import GCSStorageLoader

__all__ = [
    'StorageLoader',
    'LocalStorageLoader',
    'GCSStorageLoader'
] 