"""
Storage loader protocol definition.

This module defines the StorageLoader protocol that all storage
backends must follow for the abstraction layer.
"""

from typing import Protocol, List, Dict, Any


class StorageLoader(Protocol):
    """
    Protocol for storage backends.
    
    This protocol defines the interface that all storage loaders
    must follow to provide a unified storage abstraction.
    """
    
    def write_file(self, path: str, content: str) -> None:
        """
        Write content to a file at the specified path.
        
        Args:
            path: The file path (relative to storage root)
            content: The content to write
            
        Raises:
            PromptStorageError: If the file cannot be written
        """
        ...
    
    def read_file(self, path: str) -> str:
        """
        Read content from a file at the specified path.
        
        Args:
            path: The file path (relative to storage root)
            
        Returns:
            The file content as a string
            
        Raises:
            PromptStorageError: If the file cannot be read
        """
        ...
    
    def delete_file(self, path: str) -> None:
        """
        Delete a file at the specified path.
        
        Args:
            path: The file path (relative to storage root)
            
        Raises:
            PromptStorageError: If the file cannot be deleted
        """
        ...
    
    def list_files(self, prefix: str = "") -> List[str]:
        """
        List all files with the given prefix.
        
        Args:
            prefix: The prefix to filter files (optional)
            
        Returns:
            List of file paths (relative to storage root)
            
        Raises:
            PromptStorageError: If files cannot be listed
        """
        ...
    
    def exists(self, path: str) -> bool:
        """
        Check if a file exists at the specified path.
        
        Args:
            path: The file path (relative to storage root)
            
        Returns:
            True if the file exists, False otherwise
        """
        ...
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the storage.
        
        Returns:
            Dictionary containing storage statistics
            
        Raises:
            PromptStorageError: If statistics cannot be retrieved
        """
        ... 