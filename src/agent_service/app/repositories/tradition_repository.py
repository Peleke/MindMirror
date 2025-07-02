"""
Tradition Repository

Manages access to tradition data (e.g., knowledge base directories).
"""

import os
from typing import List

from agent_service.app.repositories.tradition_loaders import (
    create_tradition_loader,
    TraditionLoader,
)


class TraditionRepository:
    """
    Manages access to tradition data using a loader (GCS-first, local fallback).
    """

    def __init__(self, loader: TraditionLoader = None):
        self._loader = loader or create_tradition_loader()

    def list_traditions(self) -> List[str]:
        """Lists all available traditions using the loader."""
        return self._loader.list_traditions()
