"""
GCS storage loader implementation.

This module provides the GCSStorageLoader class that implements
Google Cloud Storage for production deployments.
"""

import os
from typing import List, Dict, Any

from ...exceptions import PromptStorageError
from .protocol import StorageLoader
from ...models import StorageConfig


class GCSStorageLoader(StorageLoader):
    """
    Google Cloud Storage loader.
    
    This loader provides GCS storage backend with retry logic
    for transient failures and comprehensive error handling.
    """
    
    def __init__(self, config: StorageConfig):
        """
        Initialize the GCS storage loader.
        
        Args:
            config: Storage configuration
            
        Raises:
            PromptStorageError: If the GCS configuration is invalid
        """
        if not config.gcs_bucket:
            raise PromptStorageError("gcs_bucket is required for GCSStorageLoader")
        
        if not config.gcs_credentials:
            raise PromptStorageError("gcs_credentials is required for GCSStorageLoader")
        
        self.bucket_name = config.gcs_bucket
        self.credentials_path = config.gcs_credentials
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
        
        try:
            from google.cloud import storage
            self.client = storage.Client.from_service_account_json(self.credentials_path)
        except ImportError:
            raise PromptStorageError("google-cloud-storage package is required for GCSStorageLoader")
        except Exception as e:
            raise PromptStorageError(f"Failed to initialize GCS client: {e}")
    
    def write_file(self, path: str, content: str) -> None:
        """
        Write content to a GCS blob.
        
        Args:
            path: The blob path
            content: The content to write
            
        Raises:
            PromptStorageError: If the blob cannot be written
        """
        for attempt in range(self.max_retries):
            try:
                bucket = self.client.bucket(self.bucket_name)
                blob = bucket.blob(path)
                blob.upload_from_string(content)
                return
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise PromptStorageError(f"Failed to write blob {path} after {self.max_retries} attempts: {e}")
                
                time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
    
    def read_file(self, path: str) -> str:
        """
        Read content from a GCS blob.
        
        Args:
            path: The blob path
            
        Returns:
            The blob content as a string
            
        Raises:
            PromptStorageError: If the blob cannot be read
        """
        for attempt in range(self.max_retries):
            try:
                bucket = self.client.bucket(self.bucket_name)
                blob = bucket.blob(path)
                return blob.download_as_text()
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise PromptStorageError(f"Failed to read blob {path} after {self.max_retries} attempts: {e}")
                
                time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
    
    def delete_file(self, path: str) -> None:
        """
        Delete a GCS blob.
        
        Args:
            path: The blob path
            
        Raises:
            PromptStorageError: If the blob cannot be deleted
        """
        for attempt in range(self.max_retries):
            try:
                bucket = self.client.bucket(self.bucket_name)
                blob = bucket.blob(path)
                blob.delete()
                return
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise PromptStorageError(f"Failed to delete blob {path} after {self.max_retries} attempts: {e}")
                
                time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
    
    def list_files(self, prefix: str = "") -> List[str]:
        """
        List all blobs with the given prefix.
        
        Args:
            prefix: The prefix to filter blobs (optional)
            
        Returns:
            List of blob paths
            
        Raises:
            PromptStorageError: If blobs cannot be listed
        """
        for attempt in range(self.max_retries):
            try:
                bucket = self.client.bucket(self.bucket_name)
                blobs = bucket.list_blobs(prefix=prefix)
                return [blob.name for blob in blobs]
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise PromptStorageError(f"Failed to list blobs after {self.max_retries} attempts: {e}")
                
                time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
    
    def exists(self, path: str) -> bool:
        """
        Check if a blob exists.
        
        Args:
            path: The blob path
            
        Returns:
            True if the blob exists, False otherwise
        """
        for attempt in range(self.max_retries):
            try:
                bucket = self.client.bucket(self.bucket_name)
                blob = bucket.blob(path)
                return blob.exists()
                
            except Exception:
                if attempt == self.max_retries - 1:
                    return False
                
                time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the GCS bucket.
        
        Returns:
            Dictionary containing storage statistics
            
        Raises:
            PromptStorageError: If statistics cannot be retrieved
        """
        for attempt in range(self.max_retries):
            try:
                bucket = self.client.bucket(self.bucket_name)
                blobs = list(bucket.list_blobs())
                
                total_files = len(blobs)
                total_size_bytes = sum(blob.size for blob in blobs)
                
                return {
                    "total_files": total_files,
                    "total_size_bytes": total_size_bytes,
                    "storage_type": "gcs",
                    "bucket_name": self.bucket_name
                }
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise PromptStorageError(f"Failed to get GCS statistics after {self.max_retries} attempts: {e}")
                
                time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff 