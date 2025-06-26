"""
Prompt template loader for Jinja2 templates.

This module provides functionality to load, cache, and render Jinja2 templates
for use in LLM prompts throughout the agent service.
"""

import re
from pathlib import Path
from typing import Dict, Any, Optional, Set
from jinja2 import Environment, Template, TemplateError as Jinja2TemplateError

from agent_service.tracing.decorators import trace_function


class TemplateError(Exception):
    """Custom exception for template-related errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class PromptLoader:
    """
    Loader for Jinja2 prompt templates.
    
    Provides functionality to load templates from strings, files, or directories,
    with caching and error handling.
    """
    
    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialize the prompt loader.
        
        Args:
            template_dir: Optional directory to load templates from
        """
        self.template_dir = template_dir
        self.templates: Dict[str, Template] = {}
        self._template_cache: Dict[str, Template] = {}
        
        # Create Jinja2 environment with safe defaults
        self.env = Environment(
            autoescape=False,  # Don't escape HTML for prompts
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )
    
    @trace_function(name="prompt_loader.load_template_from_string", tags=["prompt", "loader"])
    def load_template_from_string(self, template_content: str) -> Template:
        """
        Load a template from a string.
        
        Args:
            template_content: The template content as a string
            
        Returns:
            Jinja2 Template object
            
        Raises:
            TemplateError: If template syntax is invalid
        """
        try:
            # Check cache first
            cache_key = f"string:{hash(template_content)}"
            if cache_key in self._template_cache:
                return self._template_cache[cache_key]
            
            # Create template
            template = self.env.from_string(template_content)
            
            # Cache the template
            self._template_cache[cache_key] = template
            
            return template
            
        except Jinja2TemplateError as e:
            raise TemplateError(f"Template syntax error: {str(e)}", {"error": str(e)})
        except Exception as e:
            raise TemplateError(f"Error loading template: {str(e)}", {"error": str(e)})
    
    @trace_function(name="prompt_loader.load_template_from_file", tags=["prompt", "loader"])
    def load_template_from_file(self, file_path: str) -> Template:
        """
        Load a template from a file.
        
        Args:
            file_path: Path to the template file
            
        Returns:
            Jinja2 Template object
            
        Raises:
            TemplateError: If file cannot be read or template is invalid
        """
        try:
            # Check cache first
            cache_key = f"file:{file_path}"
            if cache_key in self._template_cache:
                return self._template_cache[cache_key]
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Load template from string
            template = self.load_template_from_string(template_content)
            
            # Cache the template
            self._template_cache[cache_key] = template
            
            return template
            
        except FileNotFoundError:
            raise TemplateError(f"Template file not found: {file_path}")
        except PermissionError:
            raise TemplateError(f"Error reading template file: {file_path}")
        except Exception as e:
            raise TemplateError(f"Error loading template from file: {str(e)}")
    
    @trace_function(name="prompt_loader.load_templates_from_directory", tags=["prompt", "loader"])
    def load_templates_from_directory(self, directory: Path) -> Dict[str, Template]:
        """
        Load all .j2 templates from a directory.
        
        Args:
            directory: Directory containing template files
            
        Returns:
            Dictionary mapping template names to Template objects
            
        Raises:
            TemplateError: If directory cannot be read
        """
        try:
            loaded_templates = {}
            
            for file_path in directory.iterdir():
                if file_path.suffix == '.j2':
                    template_name = file_path.stem
                    template = self.load_template_from_file(str(file_path))
                    loaded_templates[template_name] = template
                    self.templates[template_name] = template
            
            return loaded_templates
            
        except Exception as e:
            raise TemplateError(f"Error loading templates from directory: {str(e)}")
    
    def get_template(self, template_name: str) -> Template:
        """
        Get a template by name.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template object
            
        Raises:
            TemplateError: If template is not found
        """
        if template_name not in self.templates:
            raise TemplateError(f"Template '{template_name}' not found")
        
        return self.templates[template_name]
    
    @trace_function(name="prompt_loader.render_template", tags=["prompt", "loader"])
    def render_template(self, template_name: str, **kwargs: Any) -> str:
        """
        Render a template with the given variables.
        
        Args:
            template_name: Name of the template to render
            **kwargs: Variables to pass to the template
            
        Returns:
            Rendered template string
            
        Raises:
            TemplateError: If template is not found or rendering fails
        """
        try:
            template = self.get_template(template_name)
            return template.render(**kwargs)
            
        except Jinja2TemplateError as e:
            raise TemplateError(f"Error rendering template '{template_name}': {str(e)}")
        except Exception as e:
            raise TemplateError(f"Unexpected error rendering template: {str(e)}")
    
    def validate_template(self, template_content: str) -> bool:
        """
        Validate template syntax without rendering.
        
        Args:
            template_content: Template content to validate
            
        Returns:
            True if template is valid, False otherwise
        """
        try:
            self.env.from_string(template_content)
            return True
        except Jinja2TemplateError:
            return False
    
    def extract_template_variables(self, template_content: str) -> Set[str]:
        """
        Extract variable names from a template.
        
        Args:
            template_content: Template content to analyze
            
        Returns:
            Set of variable names found in the template
        """
        # Simple regex to find Jinja2 variables
        variable_pattern = r'\{\{\s*(\w+)\s*\}\}'
        matches = re.findall(variable_pattern, template_content)
        return set(matches)
    
    def list_templates(self) -> Set[str]:
        """
        Get list of available template names.
        
        Returns:
            Set of template names
        """
        return set(self.templates.keys())
    
    def clear_cache(self) -> None:
        """Clear the template cache."""
        self._template_cache.clear()
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """
        Get information about a template.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Dictionary with template information
            
        Raises:
            TemplateError: If template is not found
        """
        template = self.get_template(template_name)
        
        # Get template source
        source = template.source
        
        # Extract variables
        variables = self.extract_template_variables(source)
        
        return {
            "name": template_name,
            "source": source,
            "variables": list(variables),
            "is_valid": self.validate_template(source),
        } 