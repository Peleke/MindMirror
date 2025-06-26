"""
Local file system prompt store implementation.

This module provides the LocalPromptStore class that stores
prompts as YAML files in a local directory structure.
"""

import yaml
import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models import PromptInfo, PromptStats
from ..exceptions import PromptStorageError, PromptNotFoundError
from .protocol import PromptStore


class LocalPromptStore(PromptStore):
    """
    Local file system storage for prompts.
    
    This store saves prompts as YAML files in a directory structure:
    store_path/
    ├── prompt_name_1/
    │   ├── 1.0.yaml
    │   └── 1.1.yaml
    └── prompt_name_2/
        └── 1.0.yaml
    """
    
    def __init__(self, store_path: str):
        """
        Initialize the local prompt store.
        
        Args:
            store_path: Path to the directory where prompts will be stored
            
        Raises:
            PromptStorageError: If the store path cannot be created
        """
        if not store_path:
            raise PromptStorageError("store_path cannot be empty or None")
        
        self.store_path = Path(store_path)
        
        try:
            # Create the store directory if it doesn't exist
            self.store_path.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            raise PromptStorageError(f"Failed to create store directory: {e}")
    
    def save_prompt(self, prompt: PromptInfo) -> None:
        """
        Save a prompt to the local file system.
        
        Args:
            prompt: The prompt to save
            
        Raises:
            PromptStorageError: If the prompt cannot be saved
        """
        try:
            # Create the prompt directory
            prompt_dir = self.store_path / self._sanitize_filename(prompt.name)
            prompt_dir.mkdir(parents=True, exist_ok=True)
            
            # Create the prompt file
            prompt_file = prompt_dir / f"{prompt.version}.yaml"
            
            # Convert prompt to dictionary and save as YAML
            prompt_data = prompt.to_dict()
            
            with open(prompt_file, 'w', encoding='utf-8') as f:
                yaml.dump(prompt_data, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False)
                
        except (OSError, PermissionError, yaml.YAMLError) as e:
            raise PromptStorageError(f"Failed to save prompt: {e}")
    
    def get_prompt(self, name: str, version: str) -> PromptInfo:
        """
        Retrieve a prompt from the local file system.
        
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
            prompt_file = self.store_path / self._sanitize_filename(name) / f"{version}.yaml"
            
            if not prompt_file.exists():
                raise PromptNotFoundError(f"Prompt '{name}' version '{version}' not found")
            
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_data = yaml.safe_load(f)
            
            # Check if the loaded data is a dictionary
            if not isinstance(prompt_data, dict):
                raise PromptStorageError(f"Invalid prompt file format: expected dict, got {type(prompt_data)}")
            
            return PromptInfo.from_dict(prompt_data)
            
        except yaml.YAMLError as e:
            raise PromptStorageError(f"Failed to parse prompt file: {e}")
        except (OSError, PermissionError) as e:
            raise PromptStorageError(f"Failed to load prompt: {e}")
    
    def delete_prompt(self, name: str, version: str) -> None:
        """
        Delete a prompt from the local file system.
        
        Args:
            name: The name of the prompt
            version: The version of the prompt
            
        Raises:
            PromptNotFoundError: If the prompt is not found
            PromptStorageError: If the prompt cannot be deleted
        """
        try:
            prompt_file = self.store_path / self._sanitize_filename(name) / f"{version}.yaml"
            
            if not prompt_file.exists():
                raise PromptNotFoundError(f"Prompt '{name}' version '{version}' not found")
            
            # Delete the file
            prompt_file.unlink()
            
            # Remove the directory if it's empty
            prompt_dir = prompt_file.parent
            if not any(prompt_dir.iterdir()):
                prompt_dir.rmdir()
                
        except (OSError, PermissionError) as e:
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
            
            for prompt_dir in self.store_path.iterdir():
                if not prompt_dir.is_dir():
                    continue
                
                for version_file in prompt_dir.glob("*.yaml"):
                    try:
                        with open(version_file, 'r', encoding='utf-8') as f:
                            prompt_data = yaml.safe_load(f)
                        
                        prompts.append(PromptInfo.from_dict(prompt_data))
                    except (yaml.YAMLError, OSError):
                        # Skip corrupted files
                        continue
            
            return prompts
            
        except (OSError, PermissionError) as e:
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
            prompt_dir = self.store_path / self._sanitize_filename(name)
            
            if not prompt_dir.exists():
                raise PromptNotFoundError(f"Prompt '{name}' not found")
            
            versions = []
            for version_file in prompt_dir.glob("*.yaml"):
                version = version_file.stem  # Remove .yaml extension
                versions.append(version)
            
            if not versions:
                raise PromptNotFoundError(f"Prompt '{name}' not found")
            
            # Sort versions and return the latest
            return self._get_latest_version_from_list(versions)
            
        except (OSError, PermissionError) as e:
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
            prompt_dir = self.store_path / self._sanitize_filename(name)
            
            if not prompt_dir.exists():
                raise PromptNotFoundError(f"Prompt '{name}' not found")
            
            versions = []
            for version_file in prompt_dir.glob("*.yaml"):
                version = version_file.stem  # Remove .yaml extension
                versions.append(version)
            
            if not versions:
                raise PromptNotFoundError(f"Prompt '{name}' not found")
            
            return sorted(versions, key=self._version_key)
            
        except (OSError, PermissionError) as e:
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
            
        except (OSError, PermissionError) as e:
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
            prompt_file = self.store_path / self._sanitize_filename(name) / f"{version}.yaml"
            return prompt_file.exists()
        except (OSError, PermissionError):
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
            total_prompts = 0
            total_versions = 0
            storage_size_bytes = 0
            
            for prompt_dir in self.store_path.iterdir():
                if not prompt_dir.is_dir():
                    continue
                
                # Count this as one prompt (unique name)
                total_prompts += 1
                
                for version_file in prompt_dir.glob("*.yaml"):
                    total_versions += 1
                    storage_size_bytes += version_file.stat().st_size
            
            return PromptStats(
                total_prompts=total_prompts,
                total_versions=total_versions,
                storage_size_bytes=storage_size_bytes,
                last_updated=datetime.utcnow()
            )
            
        except (OSError, PermissionError) as e:
            raise PromptStorageError(f"Failed to get store statistics: {e}")
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a filename to be safe for the file system.
        
        Args:
            filename: The filename to sanitize
            
        Returns:
            A sanitized filename
        """
        # Replace problematic characters with underscores
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(' .')
        
        # Remove multiple consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        
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
            parts = version.split('.')
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