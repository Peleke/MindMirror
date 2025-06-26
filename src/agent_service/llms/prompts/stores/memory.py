"""
In-memory prompt store implementation.

This module provides an in-memory implementation of the PromptStore interface
for development and testing purposes.
"""

import re
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..models import PromptInfo
from ..exceptions import PromptNotFoundError, PromptValidationError
from . import PromptStore


class InMemoryPromptStore(PromptStore):
    """
    In-memory implementation of PromptStore.
    
    This store keeps all prompts in memory and is suitable for development,
    testing, and small-scale deployments. Data is not persisted between
    application restarts.
    """
    
    def __init__(self):
        """Initialize the in-memory store."""
        # _prompts: Dict[name, Dict[version, PromptInfo]]
        self._prompts: Dict[str, Dict[str, PromptInfo]] = {}
        
        # _latest_versions: Dict[name, version]
        self._latest_versions: Dict[str, str] = {}
        
        # Statistics tracking
        self._stats = {
            'total_prompts': 0,
            'total_versions': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'render_count': 0,
            'storage_size_bytes': 0
        }
    
    def get_prompt(self, name: str, version: Optional[str] = None) -> PromptInfo:
        """Retrieve a prompt by name and optional version."""
        self._validate_name(name)
        
        if name not in self._prompts:
            raise PromptNotFoundError(f"Prompt '{name}' not found")
        
        if version is None:
            # Get latest version
            version = self._latest_versions[name]
        
        if version not in self._prompts[name]:
            raise PromptNotFoundError(f"Version '{version}' not found for prompt '{name}'")
        
        return self._prompts[name][version]
    
    def save_prompt(self, info: PromptInfo) -> None:
        """Save a prompt to storage."""
        if not isinstance(info, PromptInfo):
            raise PromptValidationError("info must be a PromptInfo object")
        
        # Initialize prompt entry if it doesn't exist
        if info.name not in self._prompts:
            self._prompts[info.name] = {}
            self._stats['total_prompts'] += 1
        
        # Check if this is a new version
        is_new_version = info.version not in self._prompts[info.name]
        
        # Save the prompt
        self._prompts[info.name][info.version] = info
        
        # Update latest version if this is newer
        if (info.name not in self._latest_versions or 
            self._compare_versions(info.version, self._latest_versions[info.name]) > 0):
            self._latest_versions[info.name] = info.version
        
        # Update statistics
        if is_new_version:
            self._stats['total_versions'] += 1
        
        # Update storage size (rough estimate)
        self._update_storage_size()
    
    def delete_prompt(self, name: str, version: Optional[str] = None) -> None:
        """Delete a prompt from storage."""
        self._validate_name(name)
        
        if name not in self._prompts:
            raise PromptNotFoundError(f"Prompt '{name}' not found")
        
        if version is None:
            # Delete latest version
            version = self._latest_versions[name]
        
        if version not in self._prompts[name]:
            raise PromptNotFoundError(f"Version '{version}' not found for prompt '{name}'")
        
        # Delete the version
        del self._prompts[name][version]
        self._stats['total_versions'] -= 1
        
        # Update latest version if we deleted the current latest
        if version == self._latest_versions[name]:
            if self._prompts[name]:
                # Find the new latest version
                latest_version = max(self._prompts[name].keys(), 
                                   key=lambda v: self._compare_versions(v, "0.0"))
                self._latest_versions[name] = latest_version
            else:
                # No more versions, remove the prompt entirely
                del self._prompts[name]
                del self._latest_versions[name]
                self._stats['total_prompts'] -= 1
        
        # Update storage size
        self._update_storage_size()
    
    def list_prompts(self) -> List[PromptInfo]:
        """List all available prompts (latest version only)."""
        result = []
        for name, latest_version in self._latest_versions.items():
            result.append(self._prompts[name][latest_version])
        return result
    
    def get_latest_version(self, name: str) -> str:
        """Get the latest version of a prompt."""
        self._validate_name(name)
        
        if name not in self._latest_versions:
            raise PromptNotFoundError(f"No versions found for prompt '{name}'")
        
        return self._latest_versions[name]
    
    def search_prompts(self, criteria: dict) -> List[PromptInfo]:
        """Search prompts based on criteria."""
        results = []
        
        for name, versions in self._prompts.items():
            # Get the latest version for each prompt
            latest_version = self._latest_versions[name]
            prompt = versions[latest_version]
            
            if self._matches_criteria(prompt, criteria):
                results.append(prompt)
        
        return results
    
    def get_prompt_versions(self, name: str) -> List[str]:
        """Get all versions of a prompt."""
        self._validate_name(name)
        
        if name not in self._prompts:
            raise PromptNotFoundError(f"Prompt '{name}' not found")
        
        return list(self._prompts[name].keys())
    
    def exists(self, name: str, version: Optional[str] = None) -> bool:
        """Check if a prompt exists."""
        if not name or name not in self._prompts:
            return False
        
        if version is None:
            return True
        
        return version in self._prompts[name]
    
    def get_stats(self) -> dict:
        """Get storage statistics."""
        return self._stats.copy()
    
    def _validate_name(self, name: str) -> None:
        """Validate prompt name."""
        if not name or not isinstance(name, str):
            raise PromptValidationError("Prompt name must be a non-empty string")
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare two version strings."""
        def version_to_tuple(v: str) -> tuple:
            parts = v.split('.')
            return tuple(int(part) for part in parts)
        
        try:
            v1_tuple = version_to_tuple(version1)
            v2_tuple = version_to_tuple(version2)
            
            if v1_tuple < v2_tuple:
                return -1
            elif v1_tuple > v2_tuple:
                return 1
            else:
                return 0
        except (ValueError, IndexError):
            # If version comparison fails, treat as equal
            return 0
    
    def _matches_criteria(self, prompt: PromptInfo, criteria: dict) -> bool:
        """Check if a prompt matches search criteria."""
        # Name pattern
        if 'name_pattern' in criteria and criteria['name_pattern']:
            pattern = criteria['name_pattern'].replace('*', '.*')
            if not re.search(pattern, prompt.name):
                return False
        
        # Version pattern
        if 'version_pattern' in criteria and criteria['version_pattern']:
            pattern = criteria['version_pattern'].replace('*', '.*')
            if not re.search(pattern, prompt.version):
                return False
        
        # Metadata filters
        if 'metadata_filters' in criteria and criteria['metadata_filters']:
            for key, value in criteria['metadata_filters'].items():
                if key not in prompt.metadata or prompt.metadata[key] != value:
                    return False
        
        # Content pattern
        if 'content_pattern' in criteria and criteria['content_pattern']:
            if criteria['content_pattern'].lower() not in prompt.content.lower():
                return False
        
        # Date filters
        if 'created_after' in criteria and criteria['created_after']:
            try:
                created_date = datetime.fromisoformat(prompt.created_at)
                if created_date <= criteria['created_after']:
                    return False
            except ValueError:
                pass
        
        if 'created_before' in criteria and criteria['created_before']:
            try:
                created_date = datetime.fromisoformat(prompt.created_at)
                if created_date >= criteria['created_before']:
                    return False
            except ValueError:
                pass
        
        if 'updated_after' in criteria and criteria['updated_after']:
            try:
                updated_date = datetime.fromisoformat(prompt.updated_at)
                if updated_date <= criteria['updated_after']:
                    return False
            except ValueError:
                pass
        
        if 'updated_before' in criteria and criteria['updated_before']:
            try:
                updated_date = datetime.fromisoformat(prompt.updated_at)
                if updated_date >= criteria['updated_before']:
                    return False
            except ValueError:
                pass
        
        return True
    
    def _update_storage_size(self) -> None:
        """Update storage size estimate."""
        total_size = 0
        for name, versions in self._prompts.items():
            for version, prompt in versions.items():
                # Rough estimate: sum of all string lengths
                total_size += len(name) + len(version) + len(prompt.content)
                total_size += len(str(prompt.metadata)) + len(str(prompt.variables))
                total_size += len(prompt.created_at) + len(prompt.updated_at)
        
        self._stats['storage_size_bytes'] = total_size
    
    def clear(self) -> None:
        """Clear all stored prompts (useful for testing)."""
        self._prompts.clear()
        self._latest_versions.clear()
        self._stats = {
            'total_prompts': 0,
            'total_versions': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'render_count': 0,
            'storage_size_bytes': 0
        } 