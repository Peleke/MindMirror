"""
Tradition Repository

Manages access to tradition data (e.g., knowledge base directories).
"""

import os
from typing import List

from app.config import get_settings


class TraditionRepository:
    """
    Manages access to tradition data (e.g., knowledge base directories).
    """

    def __init__(self, data_dir: str = None):
        settings = get_settings()
        self._data_dir = data_dir or settings.data_dir or "/app/local_gcs_bucket"

    def list_traditions(self) -> List[str]:
        """
        Lists all available traditions by scanning the data directory.
        A "tradition" is defined as any subdirectory within the main data directory.
        """
        if not os.path.isdir(self._data_dir):
            return []

        return [
            d
            for d in os.listdir(self._data_dir)
            if os.path.isdir(os.path.join(self._data_dir, d))
        ] 