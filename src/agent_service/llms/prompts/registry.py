"""
Prompt registry for managing prompt templates.

This module provides a centralized registry for managing prompt templates
with versioning, validation, and retrieval functionality.
"""

import re
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path

from .loader import PromptLoader, TemplateError


class PromptNotFoundError(Exception):
    """Raised when a prompt is not found in the registry."""
    pass


class PromptValidationError(Exception):
    """Raised when a prompt fails validation."""
    pass


@dataclass
class PromptInfo:
    """Information about a registered prompt."""
    name: str
    content: str
    version: str
    metadata: Dict[str, Any]
    variables: List[str]
    created_at: str
    updated_at: str


class PromptRegistry:
    """
    Registry for managing prompt templates.
    
    This class provides functionality for registering, retrieving, and managing
    prompt templates with versioning and validation support.
    """
    
    def __init__(self, loader: Optional[PromptLoader] = None):
        """
        Initialize the prompt registry.
        
        Args:
            loader: Optional prompt loader instance. If not provided, a new one will be created.
        """
        self.prompts: Dict[str, Dict[str, Any]] = {}
        self.loader = loader or PromptLoader()
    
    def register_prompt(
        self,
        name: str,
        content: str,
        version: str = "1.0",
        metadata: Optional[Dict[str, Any]] = None,
        validate: bool = True,
        override: bool = False
    ) -> None:
        """
        Register a new prompt template.
        
        Args:
            name: Unique name for the prompt
            content: Template content (Jinja2 format)
            version: Version string for the prompt
            metadata: Optional metadata dictionary
            validate: Whether to validate the template syntax
            override: Whether to override existing prompt with same name
            
        Raises:
            ValueError: If prompt already exists and override is False
            PromptValidationError: If template validation fails
        """
        if name in self.prompts and not override:
            raise ValueError(f"Prompt '{name}' already registered")
        
        if validate and not self.validate_prompt(content):
            raise PromptValidationError("Invalid template syntax")
        
        # Extract variables from template
        variables = self._extract_variables(content)
        
        # Store prompt information
        self.prompts[name] = {
            "content": content,
            "version": version,
            "metadata": metadata or {},
            "variables": variables,
            "created_at": self._get_timestamp(),
            "updated_at": self._get_timestamp()
        }
    
    def get_prompt(self, name: str) -> Dict[str, Any]:
        """
        Get a registered prompt by name.
        
        Args:
            name: Name of the prompt to retrieve
            
        Returns:
            Dictionary containing prompt information
            
        Raises:
            PromptNotFoundError: If prompt is not found
        """
        if name not in self.prompts:
            raise PromptNotFoundError(f"Prompt '{name}' not found")
        
        return self.prompts[name].copy()
    
    def render_prompt(self, name: str, **kwargs) -> str:
        """
        Render a prompt template with provided variables.
        
        Args:
            name: Name of the prompt to render
            **kwargs: Variables to substitute in the template
            
        Returns:
            Rendered prompt string
            
        Raises:
            PromptNotFoundError: If prompt is not found
            PromptValidationError: If template rendering fails
        """
        if name not in self.prompts:
            raise PromptNotFoundError(f"Prompt '{name}' not found")
        
        try:
            return self.loader.render_template(
                self.loader.load_template_from_string(self.prompts[name]["content"]),
                **kwargs
            )
        except TemplateError as e:
            raise PromptValidationError(f"Template rendering failed: {e}")
    
    def list_prompts(self) -> List[str]:
        """
        List all registered prompt names.
        
        Returns:
            List of prompt names
        """
        return list(self.prompts.keys())
    
    def get_prompt_info(self, name: str) -> PromptInfo:
        """
        Get detailed information about a prompt.
        
        Args:
            name: Name of the prompt
            
        Returns:
            PromptInfo object with detailed information
            
        Raises:
            PromptNotFoundError: If prompt is not found
        """
        if name not in self.prompts:
            raise PromptNotFoundError(f"Prompt '{name}' not found")
        
        prompt_data = self.prompts[name]
        return PromptInfo(
            name=name,
            content=prompt_data["content"],
            version=prompt_data["version"],
            metadata=prompt_data["metadata"],
            variables=prompt_data["variables"],
            created_at=prompt_data["created_at"],
            updated_at=prompt_data["updated_at"]
        )
    
    def validate_prompt(self, content: str) -> bool:
        """
        Validate template syntax.
        
        Args:
            content: Template content to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            self.loader.validate_template(content)
            return True
        except TemplateError:
            return False
    
    def update_prompt(
        self,
        name: str,
        content: str,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        validate: bool = True
    ) -> None:
        """
        Update an existing prompt.
        
        Args:
            name: Name of the prompt to update
            content: New template content
            version: New version string (auto-incremented if not provided)
            metadata: New metadata dictionary
            validate: Whether to validate the template syntax
            
        Raises:
            PromptNotFoundError: If prompt is not found
            PromptValidationError: If template validation fails
        """
        if name not in self.prompts:
            raise PromptNotFoundError(f"Prompt '{name}' not found")
        
        if validate and not self.validate_prompt(content):
            raise PromptValidationError("Invalid template syntax")
        
        # Auto-increment version if not provided
        if version is None:
            current_version = self.prompts[name]["version"]
            try:
                major, minor = current_version.split(".")
                new_minor = str(int(minor) + 1)
                version = f"{major}.{new_minor}"
            except (ValueError, AttributeError):
                version = "1.1"
        
        # Extract variables from new template
        variables = self._extract_variables(content)
        
        # Update prompt information
        self.prompts[name].update({
            "content": content,
            "version": version,
            "variables": variables,
            "updated_at": self._get_timestamp()
        })
        
        # Update metadata if provided
        if metadata is not None:
            self.prompts[name]["metadata"] = metadata
    
    def delete_prompt(self, name: str) -> None:
        """
        Delete a prompt from the registry.
        
        Args:
            name: Name of the prompt to delete
            
        Raises:
            PromptNotFoundError: If prompt is not found
        """
        if name not in self.prompts:
            raise PromptNotFoundError(f"Prompt '{name}' not found")
        
        del self.prompts[name]
    
    def search_prompts(
        self,
        query: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Search prompts by content or metadata.
        
        Args:
            query: Text to search for in prompt content
            metadata: Metadata filters to apply
            
        Returns:
            List of matching prompt names
        """
        results = []
        
        for name, prompt_data in self.prompts.items():
            # Search by content
            if query and query.lower() in prompt_data["content"].lower():
                results.append(name)
                continue
            
            # Search by metadata
            if metadata:
                prompt_metadata = prompt_data.get("metadata", {})
                if all(
                    prompt_metadata.get(key) == value
                    for key, value in metadata.items()
                ):
                    results.append(name)
        
        return results
    
    def get_prompts_by_category(self, category: str) -> List[str]:
        """
        Get prompts by category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of prompt names in the specified category
        """
        return self.search_prompts(metadata={"category": category})
    
    def load_prompts_from_directory(self, directory_path: Union[str, Path]) -> None:
        """
        Load prompts from a directory containing .j2 template files.
        
        Args:
            directory_path: Path to directory containing templates
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory {directory_path} does not exist")
        
        # Load templates from directory
        templates = self.loader.load_templates_from_directory(directory_path)
        
        # Register each template as a prompt
        for template_name, template in templates.items():
            try:
                content = template.source
                self.register_prompt(template_name, content)
            except Exception as e:
                # Log warning but continue loading other templates
                print(f"Warning: Failed to load template {template_name}: {e}")
    
    def export_prompts(self) -> Dict[str, Any]:
        """
        Export all prompts to a dictionary format.
        
        Returns:
            Dictionary containing all prompt data
        """
        return {
            "prompts": self.prompts.copy(),
            "exported_at": self._get_timestamp()
        }
    
    def import_prompts(self, data: Dict[str, Any]) -> None:
        """
        Import prompts from exported data.
        
        Args:
            data: Dictionary containing prompt data from export
        """
        if "prompts" not in data:
            raise ValueError("Invalid export data format")
        
        for name, prompt_data in data["prompts"].items():
            self.register_prompt(
                name=name,
                content=prompt_data["content"],
                version=prompt_data.get("version", "1.0"),
                metadata=prompt_data.get("metadata", {}),
                override=True
            )
    
    def _extract_variables(self, content: str) -> List[str]:
        """
        Extract variable names from template content.
        
        Args:
            content: Template content
            
        Returns:
            List of variable names
        """
        try:
            return self.loader.extract_template_variables(content)
        except TemplateError:
            # Fallback to regex extraction
            pattern = r'\{\{\s*(\w+)\s*\}\}'
            variables = re.findall(pattern, content)
            return list(set(variables))
    
    def _get_timestamp(self) -> str:
        """
        Get current timestamp string.
        
        Returns:
            ISO format timestamp string
        """
        from datetime import datetime
        return datetime.now().isoformat()