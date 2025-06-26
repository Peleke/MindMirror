"""
Prompt store protocol definition.

This module defines the PromptStore protocol that all storage
implementations must follow.
"""

from typing import Protocol, List
from ..models import PromptInfo, PromptStats
from ..exceptions import PromptStorageError, PromptNotFoundError


class PromptStore(Protocol):
    """
    Protocol for prompt storage backends.
    
    This protocol defines the interface that all prompt storage
    implementations must follow.
    """
    
    def save_prompt(self, prompt: PromptInfo) -> None:
        """
        Save a prompt to storage.
        
        Args:
            prompt: The prompt to save
            
        Raises:
            PromptStorageError: If the prompt cannot be saved
        """
        ...
    
    def get_prompt(self, name: str, version: str) -> PromptInfo:
        """
        Retrieve a prompt from storage.
        
        Args:
            name: The name of the prompt
            version: The version of the prompt
            
        Returns:
            The prompt information
            
        Raises:
            PromptNotFoundError: If the prompt is not found
            PromptStorageError: If the prompt cannot be loaded
        """
        ...
    
    def delete_prompt(self, name: str, version: str) -> None:
        """
        Delete a prompt from storage.
        
        Args:
            name: The name of the prompt
            version: The version of the prompt
            
        Raises:
            PromptNotFoundError: If the prompt is not found
            PromptStorageError: If the prompt cannot be deleted
        """
        ...
    
    def list_prompts(self) -> List[PromptInfo]:
        """
        List all prompts in storage.
        
        Returns:
            List of all prompts
            
        Raises:
            PromptStorageError: If prompts cannot be listed
        """
        ...
    
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
        ...
    
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
        ...
    
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
        ...
    
    def exists(self, name: str, version: str) -> bool:
        """
        Check if a prompt exists.
        
        Args:
            name: The name of the prompt
            version: The version of the prompt
            
        Returns:
            True if the prompt exists, False otherwise
        """
        ...
    
    def get_stats(self) -> PromptStats:
        """
        Get statistics about the store.
        
        Returns:
            Store statistics
            
        Raises:
            PromptStorageError: If statistics cannot be retrieved
        """
        ... 