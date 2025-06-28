"""
Storage loaders for prompt stores.

This module provides storage abstraction layer that allows
switching between local and GCS storage backends.
"""

from .gcs import GCSStorageLoader
from .local import LocalStorageLoader
from .protocol import StorageLoader

__all__ = ["StorageLoader", "LocalStorageLoader", "GCSStorageLoader"]
