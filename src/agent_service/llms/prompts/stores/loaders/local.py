"""
Local storage loader implementation.

This module provides the LocalStorageLoader class that implements
local file system storage for Docker volume mounting.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List

from ...exceptions import PromptStorageError
from ...models import StorageConfig
from .protocol import StorageLoader


class LocalStorageLoader(StorageLoader):
    """
    Local file system storage loader.

    This loader provides local file system storage that can be
    used with Docker volume mounting for local development.
    """

    def __init__(self, config: StorageConfig):
        """
        Initialize the local storage loader.

        Args:
            config: Storage configuration

        Raises:
            PromptStorageError: If the storage path cannot be created
        """
        if not config.local_path:
            raise PromptStorageError("local_path is required for LocalStorageLoader")

        self.base_path = Path(config.local_path)

        try:
            # Create the base directory if it doesn't exist
            self.base_path.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            raise PromptStorageError(f"Failed to create storage directory: {e}")

    def write_file(self, path: str, content: str) -> None:
        """
        Write content to a local file.

        Args:
            path: The file path (relative to base_path)
            content: The content to write

        Raises:
            PromptStorageError: If the file cannot be written
        """
        try:
            file_path = self.base_path / path

            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

        except (OSError, PermissionError) as e:
            raise PromptStorageError(f"Failed to write file {path}: {e}")

    def read_file(self, path: str) -> str:
        """
        Read content from a local file.

        Args:
            path: The file path (relative to base_path)

        Returns:
            The file content as a string

        Raises:
            PromptStorageError: If the file cannot be read
        """
        try:
            file_path = self.base_path / path

            if not file_path.exists():
                raise PromptStorageError(f"File not found: {path}")

            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        except (OSError, PermissionError) as e:
            raise PromptStorageError(f"Failed to read file {path}: {e}")

    def delete_file(self, path: str) -> None:
        """
        Delete a local file.

        Args:
            path: The file path (relative to base_path)

        Raises:
            PromptStorageError: If the file cannot be deleted
        """
        try:
            file_path = self.base_path / path

            if not file_path.exists():
                raise PromptStorageError(f"File not found: {path}")

            file_path.unlink()

        except (OSError, PermissionError) as e:
            raise PromptStorageError(f"Failed to delete file {path}: {e}")

    def list_files(self, prefix: str = "") -> List[str]:
        """
        List all files with the given prefix.

        Args:
            prefix: The prefix to filter files (optional)

        Returns:
            List of file paths (relative to base_path)

        Raises:
            PromptStorageError: If files cannot be listed
        """
        try:
            files = []
            search_path = self.base_path / prefix if prefix else self.base_path

            if not search_path.exists():
                return []

            for file_path in search_path.rglob("*"):
                if file_path.is_file():
                    # Convert to relative path
                    relative_path = file_path.relative_to(self.base_path)
                    files.append(str(relative_path))

            return files

        except (OSError, PermissionError) as e:
            raise PromptStorageError(f"Failed to list files: {e}")

    def exists(self, path: str) -> bool:
        """
        Check if a file exists.

        Args:
            path: The file path (relative to base_path)

        Returns:
            True if the file exists, False otherwise
        """
        try:
            file_path = self.base_path / path
            return file_path.exists() and file_path.is_file()
        except (OSError, PermissionError):
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the local storage.

        Returns:
            Dictionary containing storage statistics

        Raises:
            PromptStorageError: If statistics cannot be retrieved
        """
        try:
            total_files = 0
            total_size_bytes = 0

            for file_path in self.base_path.rglob("*"):
                if file_path.is_file():
                    total_files += 1
                    total_size_bytes += file_path.stat().st_size

            return {
                "total_files": total_files,
                "total_size_bytes": total_size_bytes,
                "storage_type": "local",
                "base_path": str(self.base_path),
            }

        except (OSError, PermissionError) as e:
            raise PromptStorageError(f"Failed to get storage statistics: {e}")

    def _sanitize_path(self, path: str) -> str:
        """
        Sanitize a file path to be safe for the file system.

        Args:
            path: The path to sanitize

        Returns:
            A sanitized path
        """
        # Replace problematic characters with underscores
        sanitized = re.sub(r'[<>:"|?*]', "_", path)

        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(" .")

        # Remove multiple consecutive underscores
        sanitized = re.sub(r"_+", "_", sanitized)

        # Remove leading/trailing underscores
        sanitized = sanitized.strip("_")

        # Ensure the path is not empty
        if not sanitized:
            sanitized = "unnamed"

        return sanitized
