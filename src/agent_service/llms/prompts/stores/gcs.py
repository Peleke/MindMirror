"""
GCS prompt store implementation.

This module provides the GCSPromptStore class that stores
prompts in Google Cloud Storage using the storage abstraction layer.
"""

import re
from datetime import datetime
from typing import Any, Dict, List

import yaml

from ..exceptions import (PromptNotFoundError, PromptStorageError,
                          PromptValidationError)
from ..models import PromptInfo, PromptStats
from .loaders.protocol import StorageLoader
from .protocol import PromptStore


class GCSPromptStore(PromptStore):
    """
    Google Cloud Storage prompt store.

    This store saves prompts as YAML files in GCS using the
    storage abstraction layer for easy switching between backends.
    """

    def __init__(self, loader: StorageLoader):
        """
        Initialize the GCS prompt store.

        Args:
            loader: Storage loader instance (GCSStorageLoader or LocalStorageLoader)
        """
        self.loader = loader

    def save_prompt(self, prompt: PromptInfo) -> None:
        """
        Save a prompt to GCS.

        Args:
            prompt: The prompt to save

        Raises:
            PromptStorageError: If the prompt cannot be saved
        """
        try:
            # Create the prompt path
            prompt_path = (
                f"prompts/{self._sanitize_filename(prompt.name)}/{prompt.version}.yaml"
            )

            # Convert prompt to YAML and save
            prompt_data = prompt.to_dict()
            yaml_content = yaml.dump(
                prompt_data,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )

            # Retry logic for transient failures
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.loader.write_file(prompt_path, yaml_content)
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise PromptStorageError(f"Failed to save prompt: {e}")
                    # Continue to retry for transient errors
                    continue

        except Exception as e:
            raise PromptStorageError(f"Failed to save prompt: {e}")

    def get_prompt(self, name: str, version: str) -> PromptInfo:
        """
        Retrieve a prompt from GCS.

        Args:
            name: The name of the prompt
            version: The version of the prompt

        Returns:
            The prompt information

        Raises:
            PromptNotFoundError: If the prompt is not found
            PromptStorageError: If the prompt cannot be loaded
        """
        try:
            prompt_path = f"prompts/{self._sanitize_filename(name)}/{version}.yaml"

            # Read the YAML content
            try:
                yaml_content = self.loader.read_file(prompt_path)
            except PromptStorageError:
                raise PromptNotFoundError(
                    f"Prompt '{name}' version '{version}' not found"
                )
            except Exception as e:
                raise PromptStorageError(f"Failed to read prompt file: {e}")

            # Parse YAML and validate
            try:
                prompt_data = yaml.safe_load(yaml_content)
            except yaml.YAMLError as e:
                raise PromptStorageError(f"Failed to parse prompt file: {e}")

            if not isinstance(prompt_data, dict):
                raise PromptStorageError(
                    f"Invalid prompt file format: expected dict, got {type(prompt_data)}"
                )

            return PromptInfo.from_dict(prompt_data)

        except (PromptNotFoundError, PromptStorageError):
            raise
        except Exception as e:
            raise PromptStorageError(f"Failed to load prompt: {e}")

    def delete_prompt(self, name: str, version: str) -> None:
        """
        Delete a prompt from GCS.

        Args:
            name: The name of the prompt
            version: The version of the prompt

        Raises:
            PromptNotFoundError: If the prompt is not found
            PromptStorageError: If the prompt cannot be deleted
        """
        try:
            prompt_path = f"prompts/{self._sanitize_filename(name)}/{version}.yaml"
            self.loader.delete_file(prompt_path)

        except PromptStorageError:
            raise PromptNotFoundError(f"Prompt '{name}' version '{version}' not found")
        except Exception as e:
            raise PromptStorageError(f"Failed to delete prompt: {e}")

    def list_prompts(self) -> List[PromptInfo]:
        """
        List all prompts in the store.

        Returns:
            List of all prompts

        Raises:
            PromptStorageError: If prompts cannot be listed
        """
        try:
            prompts = []

            # List all prompt files
            files = self.loader.list_files("prompts/")

            for file_path in files:
                if file_path.endswith(".yaml"):
                    try:
                        yaml_content = self.loader.read_file(file_path)
                        prompt_data = yaml.safe_load(yaml_content)

                        if isinstance(prompt_data, dict):
                            prompts.append(PromptInfo.from_dict(prompt_data))
                    except (yaml.YAMLError, Exception):
                        # Skip corrupted files
                        continue

            return prompts

        except Exception as e:
            raise PromptStorageError(f"Failed to list prompts: {e}")

    def get_latest_version(self, name: str) -> str:
        """
        Get the latest version of a prompt.

        Args:
            name: The name of the prompt

        Returns:
            The latest version string

        Raises:
            PromptNotFoundError: If the prompt is not found
            PromptStorageError: If versions cannot be retrieved
        """
        try:
            # List all files for this prompt
            prefix = f"prompts/{self._sanitize_filename(name)}/"
            files = self.loader.list_files(prefix)

            if not files:
                raise PromptNotFoundError(f"Prompt '{name}' not found")

            # Extract versions from file paths
            versions = []
            for file_path in files:
                if file_path.endswith(".yaml"):
                    version = file_path.split("/")[-1].replace(".yaml", "")
                    versions.append(version)

            if not versions:
                raise PromptNotFoundError(f"Prompt '{name}' not found")

            # Sort versions and return the latest
            return self._get_latest_version_from_list(versions)

        except PromptNotFoundError:
            raise
        except Exception as e:
            raise PromptStorageError(f"Failed to get latest version: {e}")

    def get_prompt_versions(self, name: str) -> List[str]:
        """
        Get all versions of a prompt.

        Args:
            name: The name of the prompt

        Returns:
            List of version strings

        Raises:
            PromptNotFoundError: If the prompt is not found
            PromptStorageError: If versions cannot be retrieved
        """
        try:
            # List all files for this prompt
            prefix = f"prompts/{self._sanitize_filename(name)}/"
            files = self.loader.list_files(prefix)

            if not files:
                raise PromptNotFoundError(f"Prompt '{name}' not found")

            # Extract versions from file paths
            versions = []
            for file_path in files:
                if file_path.endswith(".yaml"):
                    version = file_path.split("/")[-1].replace(".yaml", "")
                    versions.append(version)

            if not versions:
                raise PromptNotFoundError(f"Prompt '{name}' not found")

            return sorted(versions, key=self._version_key)

        except PromptNotFoundError:
            raise
        except Exception as e:
            raise PromptStorageError(f"Failed to get prompt versions: {e}")

    def search_prompts(self, query: str) -> List[PromptInfo]:
        """
        Search prompts by content or name.

        Args:
            query: The search query

        Returns:
            List of matching prompts

        Raises:
            PromptStorageError: If search cannot be performed
        """
        try:
            query_lower = query.lower()
            matching_prompts = []

            for prompt in self.list_prompts():
                # Search in name
                if query_lower in prompt.name.lower():
                    matching_prompts.append(prompt)
                    continue

                # Search in content
                if query_lower in prompt.content.lower():
                    matching_prompts.append(prompt)
                    continue

                # Search in metadata
                for value in prompt.metadata.values():
                    if isinstance(value, str) and query_lower in value.lower():
                        matching_prompts.append(prompt)
                        break

            return matching_prompts

        except Exception as e:
            raise PromptStorageError(f"Failed to search prompts: {e}")

    def exists(self, name: str, version: str) -> bool:
        """
        Check if a prompt exists.

        Args:
            name: The name of the prompt
            version: The version of the prompt

        Returns:
            True if the prompt exists, False otherwise
        """
        try:
            prompt_path = f"prompts/{self._sanitize_filename(name)}/{version}.yaml"
            return self.loader.exists(prompt_path)
        except Exception:
            return False

    def get_stats(self) -> PromptStats:
        """
        Get statistics about the store.

        Returns:
            Store statistics

        Raises:
            PromptStorageError: If statistics cannot be retrieved
        """
        try:
            # Get loader stats
            loader_stats = {}
            try:
                if hasattr(self.loader, "get_stats"):
                    stats_result = self.loader.get_stats()
                    if isinstance(stats_result, dict):
                        loader_stats = stats_result
            except Exception:
                pass  # Ignore errors from get_stats

            # Count unique prompts
            files = self.loader.list_files("prompts/")
            prompt_names = set()

            for file_path in files:
                if file_path.endswith(".yaml"):
                    parts = file_path.split("/")
                    if len(parts) >= 3:
                        prompt_names.add(parts[1])  # Second part is prompt name

            return PromptStats(
                total_prompts=len(prompt_names),
                total_versions=loader_stats.get("total_files", 0),
                storage_size_bytes=loader_stats.get("total_size_bytes", 0),
                last_updated=datetime.utcnow(),
            )

        except Exception as e:
            raise PromptStorageError(f"Failed to get store statistics: {e}")

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a filename to be safe for storage.

        Args:
            filename: The filename to sanitize

        Returns:
            A sanitized filename
        """
        # Replace problematic characters with underscores
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)

        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(" .")

        # Remove multiple consecutive underscores
        sanitized = re.sub(r"_+", "_", sanitized)

        # Remove leading/trailing underscores
        sanitized = sanitized.strip("_")

        # Ensure the filename is not empty
        if not sanitized:
            sanitized = "unnamed"

        return sanitized

    def _version_key(self, version: str) -> tuple:
        """
        Convert version string to tuple for proper sorting.

        Args:
            version: Version string (e.g., "1.0", "1.1", "2.0")

        Returns:
            Tuple for sorting
        """
        try:
            parts = version.split(".")
            return tuple(int(part) for part in parts)
        except (ValueError, AttributeError):
            # Fallback to string comparison for invalid versions
            return (0, 0, 0)

    def _get_latest_version_from_list(self, versions: List[str]) -> str:
        """
        Get the latest version from a list of version strings.

        Args:
            versions: List of version strings

        Returns:
            The latest version string
        """
        if not versions:
            raise ValueError("No versions provided")

        # Sort versions and return the latest
        sorted_versions = sorted(versions, key=self._version_key)
        return sorted_versions[-1]

    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the GCS store.

        Returns:
            Health status dictionary
        """
        try:
            # Test connectivity by listing files
            files = self.loader.list_files("prompts/")

            # Get bucket info
            bucket_name = self.loader.bucket_name

            return {
                "status": "healthy",
                "storage_type": "gcs",
                "bucket_name": bucket_name,
                "file_count": len(files),
                "connected": True,
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "storage_type": "gcs",
                "error": str(e),
                "connected": False,
            }
