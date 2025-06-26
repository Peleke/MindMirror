"""
Local file system prompt store.

This store provides local file system storage for prompts,
suitable for development and small-scale deployments.
"""

import os
import yaml
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models import PromptInfo, PromptStats
from ..exceptions import PromptStorageError, PromptNotFoundError
from .protocol import PromptStore


class LocalPromptStore(PromptStore):
    """
    Local file system implementation of prompt storage.
    
    This store saves prompts as YAML files in a directory structure:
    prompts/
    ├── journal_summary/
    │   ├── 1.0.yaml
    │   └── 2.0.yaml
    └── performance_review/
        └── 1.0.yaml
    """
    
    def __init__(self, base_path: str = "prompts"):
        """
        Initialize the local prompt store.
        
        Args:
            base_path: Base directory for storing prompts
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save_prompt(self, prompt_info: PromptInfo) -> None:
        """
        Save a prompt to local storage.
        
        Args:
            prompt_info: The prompt to save
            
        Raises:
            PromptStorageError: If saving fails
        """
        try:
            # Create prompt directory
            prompt_dir = self.base_path / prompt_info.name
            prompt_dir.mkdir(parents=True, exist_ok=True)
            
            # Create file path
            file_path = prompt_dir / f"{prompt_info.version}.yaml"
            
            # Convert to dictionary
            prompt_data = {
                "name": prompt_info.name,
                "version": prompt_info.version,
                "content": prompt_info.content,
                "variables": prompt_info.variables,
                "metadata": prompt_info.metadata,
                "created_at": prompt_info.created_at,
                "updated_at": prompt_info.updated_at
            }
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(prompt_data, f, default_flow_style=False, allow_unicode=True)
                
        except Exception as e:
            raise PromptStorageError(f"Failed to save prompt {prompt_info.name}:{prompt_info.version}: {str(e)}")
    
    def get_prompt(self, name: str, version: str = "1.0") -> PromptInfo:
        """
        Retrieve a prompt from local storage.
        
        Args:
            name: Prompt name
            version: Prompt version
            
        Returns:
            PromptInfo object
            
        Raises:
            PromptNotFoundError: If prompt doesn't exist
            PromptStorageError: If retrieval fails
        """
        try:
            file_path = self.base_path / name / f"{version}.yaml"
            
            if not file_path.exists():
                raise PromptNotFoundError(f"Prompt {name}:{version} not found")
            
            # Read from file
            with open(file_path, 'r', encoding='utf-8') as f:
                prompt_data = yaml.safe_load(f)
            
            # Create PromptInfo object
            return PromptInfo(**prompt_data)
            
        except PromptNotFoundError:
            raise
        except Exception as e:
            raise PromptStorageError(f"Failed to retrieve prompt {name}:{version}: {str(e)}")
    
    def exists(self, name: str, version: str = "1.0") -> bool:
        """
        Check if a prompt exists.
        
        Args:
            name: Prompt name
            version: Prompt version
            
        Returns:
            True if prompt exists
        """
        file_path = self.base_path / name / f"{version}.yaml"
        return file_path.exists()
    
    def delete_prompt(self, name: str, version: str = "1.0") -> None:
        """
        Delete a prompt from local storage.
        
        Args:
            name: Prompt name
            version: Prompt version
            
        Raises:
            PromptNotFoundError: If prompt doesn't exist
            PromptStorageError: If deletion fails
        """
        try:
            file_path = self.base_path / name / f"{version}.yaml"
            
            if not file_path.exists():
                raise PromptNotFoundError(f"Prompt {name}:{version} not found")
            
            # Delete file
            file_path.unlink()
            
            # Remove directory if empty
            prompt_dir = self.base_path / name
            if prompt_dir.exists() and not any(prompt_dir.iterdir()):
                prompt_dir.rmdir()
                
        except PromptNotFoundError:
            raise
        except Exception as e:
            raise PromptStorageError(f"Failed to delete prompt {name}:{version}: {str(e)}")
    
    def list_prompts(self, name_pattern: Optional[str] = None) -> List[PromptInfo]:
        """
        List all prompts in storage.
        
        Args:
            name_pattern: Optional pattern to filter prompt names
            
        Returns:
            List of PromptInfo objects
            
        Raises:
            PromptStorageError: If listing fails
        """
        try:
            prompts = []
            
            if not self.base_path.exists():
                return prompts
            
            # Iterate through prompt directories
            for prompt_dir in self.base_path.iterdir():
                if not prompt_dir.is_dir():
                    continue
                
                prompt_name = prompt_dir.name
                
                # Apply name pattern filter
                if name_pattern and name_pattern not in prompt_name:
                    continue
                
                # Iterate through version files
                for version_file in prompt_dir.glob("*.yaml"):
                    try:
                        version = version_file.stem  # Remove .yaml extension
                        
                        # Read prompt data
                        with open(version_file, 'r', encoding='utf-8') as f:
                            prompt_data = yaml.safe_load(f)
                        
                        prompts.append(PromptInfo(**prompt_data))
                        
                    except Exception as e:
                        # Log error but continue with other prompts
                        print(f"Error reading {version_file}: {e}")
                        continue
            
            return prompts
            
        except Exception as e:
            raise PromptStorageError(f"Failed to list prompts: {str(e)}")
    
    def list_versions(self, name: str) -> List[str]:
        """
        List all versions of a prompt.
        
        Args:
            name: Prompt name
            
        Returns:
            List of version strings
            
        Raises:
            PromptStorageError: If listing fails
        """
        try:
            prompt_dir = self.base_path / name
            
            if not prompt_dir.exists():
                return []
            
            versions = []
            for version_file in prompt_dir.glob("*.yaml"):
                version = version_file.stem  # Remove .yaml extension
                versions.append(version)
            
            return sorted(versions)
            
        except Exception as e:
            raise PromptStorageError(f"Failed to list versions for {name}: {str(e)}")
    
    def get_stats(self) -> PromptStats:
        """
        Get statistics about the prompt store.
        
        Returns:
            PromptStats object
            
        Raises:
            PromptStorageError: If stats calculation fails
        """
        try:
            total_prompts = 0
            total_versions = 0
            storage_size_bytes = 0
            last_updated = None
            
            if self.base_path.exists():
                # Count prompts and versions
                for prompt_dir in self.base_path.iterdir():
                    if not prompt_dir.is_dir():
                        continue
                    
                    total_prompts += 1
                    
                    for version_file in prompt_dir.glob("*.yaml"):
                        total_versions += 1
                        storage_size_bytes += version_file.stat().st_size
                        
                        # Track last updated
                        mtime = datetime.fromtimestamp(version_file.stat().st_mtime)
                        if last_updated is None or mtime > last_updated:
                            last_updated = mtime
            
            return PromptStats(
                total_prompts=total_prompts,
                total_versions=total_versions,
                storage_size_bytes=storage_size_bytes,
                last_updated=last_updated
            )
            
        except Exception as e:
            raise PromptStorageError(f"Failed to calculate stats: {str(e)}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the store.
        
        Returns:
            Health check information
        """
        try:
            # Check if base directory is accessible
            if not self.base_path.exists():
                self.base_path.mkdir(parents=True, exist_ok=True)
            
            # Try to write and read a test file
            test_file = self.base_path / ".health_check"
            test_file.write_text("test")
            test_file.unlink()
            
            return {
                "status": "healthy",
                "base_path": str(self.base_path),
                "writable": True,
                "readable": True
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "base_path": str(self.base_path),
                "error": str(e),
                "writable": False,
                "readable": False
            } 