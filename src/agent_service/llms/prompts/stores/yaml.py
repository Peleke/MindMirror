"""
YAML-based prompt storage implementation.

This module provides a prompt store that saves and loads prompts
as YAML files in a local directory structure.
"""

import os
import yaml
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from .protocol import PromptStore
from ..models import PromptInfo
from ..exceptions import PromptNotFoundError, PromptStorageError

logger = logging.getLogger(__name__)


class YAMLPromptStore(PromptStore):
    """
    YAML-based prompt storage implementation.
    
    This store saves prompts as YAML files in a local directory,
    with one file per prompt version.
    """
    
    def __init__(self, base_path: str):
        """
        Initialize the YAML prompt store.
        
        Args:
            base_path: Base directory path for storing YAML files
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized YAML prompt store at {self.base_path}")
    
    def _get_file_path(self, name: str, version: str) -> Path:
        """Get the file path for a prompt."""
        filename = f"{name}_{version}.yaml"
        return self.base_path / filename
    
    def save_prompt(self, prompt_info: PromptInfo) -> None:
        """
        Save a prompt to YAML file.
        
        Args:
            prompt_info: The prompt information to save
        """
        try:
            file_path = self._get_file_path(prompt_info.name, prompt_info.version)
            
            # Convert to dictionary and save as YAML
            prompt_dict = prompt_info.to_dict()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(prompt_dict, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"Saved prompt {prompt_info.name}:{prompt_info.version} to {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving prompt {prompt_info.name}:{prompt_info.version}: {e}")
            raise PromptStorageError(f"Failed to save prompt: {e}")
    
    def get_prompt(self, name: str, version: str = "1.0") -> PromptInfo:
        """
        Load a prompt from YAML file.
        
        Args:
            name: Prompt name
            version: Prompt version
            
        Returns:
            PromptInfo object
            
        Raises:
            PromptNotFoundError: If prompt file doesn't exist
        """
        try:
            file_path = self._get_file_path(name, version)
            
            if not file_path.exists():
                raise PromptNotFoundError(f"Prompt {name}:{version} not found at {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                prompt_dict = yaml.safe_load(f)
            
            prompt_info = PromptInfo.from_dict(prompt_dict)
            logger.debug(f"Loaded prompt {name}:{version} from {file_path}")
            return prompt_info
            
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML for prompt {name}:{version}: {e}")
            raise PromptStorageError(f"Invalid YAML format: {e}")
        except Exception as e:
            if isinstance(e, (PromptNotFoundError, PromptStorageError)):
                raise
            logger.error(f"Error loading prompt {name}:{version}: {e}")
            raise PromptStorageError(f"Failed to load prompt: {e}")
    
    def exists(self, name: str, version: str = "1.0") -> bool:
        """
        Check if a prompt exists.
        
        Args:
            name: Prompt name
            version: Prompt version
            
        Returns:
            True if prompt exists, False otherwise
        """
        file_path = self._get_file_path(name, version)
        return file_path.exists()
    
    def delete_prompt(self, name: str, version: str = "1.0") -> None:
        """
        Delete a prompt file.
        
        Args:
            name: Prompt name
            version: Prompt version
        """
        try:
            file_path = self._get_file_path(name, version)
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted prompt {name}:{version} at {file_path}")
            else:
                logger.warning(f"Prompt {name}:{version} not found for deletion")
                
        except Exception as e:
            logger.error(f"Error deleting prompt {name}:{version}: {e}")
            raise PromptStorageError(f"Failed to delete prompt: {e}")
    
    def list_prompts(self) -> List[PromptInfo]:
        """
        List all available prompts.
        
        Returns:
            List of PromptInfo objects
        """
        prompts = []
        
        try:
            for file_path in self.base_path.glob("*.yaml"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        prompt_dict = yaml.safe_load(f)
                    
                    prompt_info = PromptInfo.from_dict(prompt_dict)
                    prompts.append(prompt_info)
                    
                except yaml.YAMLError as e:
                    logger.warning(f"Skipping invalid YAML file {file_path}: {e}")
                except Exception as e:
                    logger.warning(f"Skipping file {file_path}: {e}")
            
            logger.info(f"Found {len(prompts)} prompts in {self.base_path}")
            return prompts
            
        except Exception as e:
            logger.error(f"Error listing prompts: {e}")
            raise PromptStorageError(f"Failed to list prompts: {e}")
    
    def list_versions(self, name: str) -> List[str]:
        """
        List all versions of a prompt.
        
        Args:
            name: Prompt name
            
        Returns:
            List of version strings
        """
        versions = []
        
        try:
            pattern = f"{name}_*.yaml"
            for file_path in self.base_path.glob(pattern):
                # Extract version from filename
                filename = file_path.stem  # Remove .yaml extension
                version = filename.replace(f"{name}_", "")
                versions.append(version)
            
            logger.debug(f"Found {len(versions)} versions for prompt {name}")
            return sorted(versions)
            
        except Exception as e:
            logger.error(f"Error listing versions for prompt {name}: {e}")
            raise PromptStorageError(f"Failed to list versions: {e}")
    
    def get_latest_version(self, name: str) -> str:
        """
        Get the latest version of a prompt.
        
        Args:
            name: Prompt name
            
        Returns:
            Latest version string
            
        Raises:
            PromptNotFoundError: If no versions found
        """
        try:
            versions = self.list_versions(name)
            if not versions:
                raise PromptNotFoundError(f"No versions found for prompt {name}")
            
            # Sort versions and return the latest
            # Simple version comparison - assumes semantic versioning
            latest = max(versions, key=lambda v: [int(x) for x in v.split('.')])
            logger.debug(f"Latest version for prompt {name}: {latest}")
            return latest
            
        except PromptNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting latest version for prompt {name}: {e}")
            raise PromptStorageError(f"Failed to get latest version: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the YAML store.
        
        Returns:
            Health status dictionary
        """
        try:
            # Check if base directory exists and is writable
            if not self.base_path.exists():
                return {
                    "status": "unhealthy",
                    "error": f"Base directory {self.base_path} does not exist"
                }
            
            # Check if directory is writable
            test_file = self.base_path / ".health_check"
            try:
                test_file.write_text("test")
                test_file.unlink()
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "error": f"Directory {self.base_path} is not writable: {e}"
                }
            
            # Count YAML files
            yaml_files = list(self.base_path.glob("*.yaml"))
            
            return {
                "status": "healthy",
                "storage_type": "yaml",
                "base_path": str(self.base_path),
                "file_count": len(yaml_files),
                "yaml_file_count": len(yaml_files),  # Alias for backward compatibility
                "writable": True
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def clear(self) -> None:
        """Clear all prompts from the store."""
        try:
            for file_path in self.base_path.glob("*.yaml"):
                file_path.unlink()
            logger.info(f"Cleared all prompts from {self.base_path}")
        except Exception as e:
            logger.error(f"Error clearing prompts: {e}")
            raise PromptStorageError(f"Failed to clear prompts: {e}") 