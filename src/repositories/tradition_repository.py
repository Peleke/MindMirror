import os
from typing import List

from config import DATA_DIR


class TraditionRepository:
    """
    A repository for managing knowledge base traditions.
    For now, it interacts directly with the filesystem.
    """

    def __init__(self, data_dir: str = DATA_DIR):
        self._data_dir = data_dir

    def list_traditions(self) -> List[str]:
        """
        Scans the data directory and returns a list of available tradition names.
        A tradition is identified by a subdirectory within the data directory.
        """
        if not os.path.exists(self._data_dir):
            return []

        tradition_dirs = [
            d
            for d in os.listdir(self._data_dir)
            if os.path.isdir(os.path.join(self._data_dir, d))
        ]
        return tradition_dirs
