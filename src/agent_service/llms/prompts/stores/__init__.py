"""
Prompt storage interface and implementations.

This module defines the PromptStore protocol and provides implementations
for different storage backends (local files, GCS, memory, etc.).
"""

from typing import Protocol, List, Optional
from ..models import PromptInfo
from ..exceptions import PromptNotFoundError, PromptValidationError


class PromptStore(Protocol):
    """
    Protocol for prompt storage backends.
    
    This protocol defines the interface that all prompt storage implementations
    must follow. It provides CRUD operations for prompt templates with
    versioning support.
    """
    
    def get_prompt(self, name: str, version: Optional[str] = None) -> PromptInfo:
        """
        Retrieve a prompt by name and optional version.
        
        Args:
            name: Name of the prompt to retrieve
            version: Optional version string. If None, returns the latest version
            
        Returns:
            PromptInfo object containing the prompt data
            
        Raises:
            PromptNotFoundError: If prompt is not found
            PromptValidationError: If name or version is invalid
        """
        ...
    
    def save_prompt(self, info: PromptInfo) -> None:
        """
        Save a prompt to storage.
        
        Args:
            info: PromptInfo object to save
            
        Raises:
            PromptValidationError: If prompt info is invalid
            PromptStorageError: If storage operation fails
        """
        ...
    
    def delete_prompt(self, name: str, version: Optional[str] = None) -> None:
        """
        Delete a prompt from storage.
        
        Args:
            name: Name of the prompt to delete
            version: Optional version string. If None, deletes the latest version
            
        Raises:
            PromptNotFoundError: If prompt is not found
            PromptValidationError: If name or version is invalid
        """
        ...
    
    def list_prompts(self) -> List[PromptInfo]:
        """
        List all available prompts.
        
        Returns:
            List of PromptInfo objects for all stored prompts
        """
        ...
    
    def get_latest_version(self, name: str) -> str:
        """
        Get the latest version of a prompt.
        
        Args:
            name: Name of the prompt
            
        Returns:
            Latest version string
            
        Raises:
            PromptNotFoundError: If no versions are found
            PromptValidationError: If name is invalid
        """
        ...
    
    def search_prompts(self, criteria: dict) -> List[PromptInfo]:
        """
        Search prompts based on criteria.
        
        Args:
            criteria: Search criteria dictionary
            
        Returns:
            List of matching PromptInfo objects
        """
        ...
    
    def get_prompt_versions(self, name: str) -> List[str]:
        """
        Get all versions of a prompt.
        
        Args:
            name: Name of the prompt
            
        Returns:
            List of version strings
            
        Raises:
            PromptNotFoundError: If prompt is not found
        """
        ...
    
    def exists(self, name: str, version: Optional[str] = None) -> bool:
        """
        Check if a prompt exists.
        
        Args:
            name: Name of the prompt
            version: Optional version string. If None, checks latest version
            
        Returns:
            True if prompt exists, False otherwise
        """
        ...
    
    def get_stats(self) -> dict:
        """
        Get storage statistics.
        
        Returns:
            Dictionary containing storage statistics
        """
        ...


# Import implementations
from .memory import InMemoryPromptStore
# from .local import LocalPromptStore
# from .gcs import GCSPromptStore

__all__ = [
    'PromptStore',
    'InMemoryPromptStore', 
    # 'LocalPromptStore',
    # 'GCSPromptStore'
] 