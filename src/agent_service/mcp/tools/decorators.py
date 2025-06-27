"""
MCP Tool Decorators

Enhanced decorator-based registration for MCP tools with multi-domain ownership,
versioning, hierarchical tools, observability, and schema introspection.
"""

import functools
from typing import Dict, List, Any, Optional, Type, TypeVar
from .base import MCPTool, ToolMetadata, ToolBackend, EffectBoundary

T = TypeVar('T', bound=Type[MCPTool])


def register_tool(
    name: str,
    description: str,
    input_schema: Dict[str, Any],
    output_schema: Optional[Dict[str, Any]] = None,
    backend: str = "prompt",
    owner_domain: str = "default",
    version: str = "1.0.0",
    tags: Optional[List[str]] = None,
    effect_boundary: str = "llm",
    subtools: Optional[List[str]] = None
):
    """
    Enhanced decorator for registering MCP tools.
    
    Args:
        name: Tool name
        description: Tool description
        input_schema: JSON schema for input validation
        output_schema: JSON schema for output documentation (optional)
        backend: Tool backend (langgraph, prompt, retriever, hybrid, external)
        owner_domain: Domain ownership for feature grouping
        version: Semver version string
        tags: List of tags for categorization
        effect_boundary: Effect boundary (pure, retriever, llm, external)
        subtools: List of available subtools (optional)
    """
    def decorator(cls: T) -> T:
        # Validate backend
        try:
            backend_enum = ToolBackend(backend)
        except ValueError:
            raise ValueError(f"Invalid backend: {backend}. Must be one of {[b.value for b in ToolBackend]}")
        
        # Validate effect boundary
        try:
            effect_boundary_enum = EffectBoundary(effect_boundary)
        except ValueError:
            raise ValueError(f"Invalid effect_boundary: {effect_boundary}. Must be one of {[e.value for e in EffectBoundary]}")
        
        # Set default output schema if not provided
        default_output_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "content": {"type": "object"}
                }
            }
        }
        
        # Use the provided output_schema or the default
        final_output_schema = output_schema if output_schema is not None else default_output_schema
        
        # Convert lists to frozensets for immutability
        tags_set = frozenset(tags or [])
        subtools_set = frozenset(subtools or [])
        
        # Create metadata getter
        @functools.wraps(cls.get_metadata)
        def get_metadata(self) -> ToolMetadata:
            return ToolMetadata(
                name=name,
                description=description,
                input_schema=input_schema,
                output_schema=final_output_schema,
                backend=backend_enum,
                owner_domain=owner_domain,
                version=version,
                tags=tags_set,
                effect_boundary=effect_boundary_enum,
                subtools=subtools_set
            )
        
        # Override the get_metadata method
        cls.get_metadata = get_metadata
        
        # Add properties for schema introspection
        @property
        def input_schema_property(self) -> Dict[str, Any]:
            return input_schema
        
        @property
        def output_schema_property(self) -> Dict[str, Any]:
            return final_output_schema
        
        @property
        def owner_domain_property(self) -> str:
            return owner_domain
        
        @property
        def version_property(self) -> str:
            return version
        
        # Override properties if they don't exist or are the default ones
        if not hasattr(cls, 'input_schema') or cls.input_schema.__get__(None, cls) == MCPTool.input_schema.__get__(None, MCPTool):
            cls.input_schema = input_schema_property
        
        if not hasattr(cls, 'output_schema') or cls.output_schema.__get__(None, cls) == MCPTool.output_schema.__get__(None, MCPTool):
            cls.output_schema = output_schema_property
        
        if not hasattr(cls, 'owner_domain') or cls.owner_domain.__get__(None, cls) == MCPTool.owner_domain.__get__(None, MCPTool):
            cls.owner_domain = owner_domain_property
        
        if not hasattr(cls, 'version') or cls.version.__get__(None, cls) == MCPTool.version.__get__(None, MCPTool):
            cls.version = version_property
        
        # Add subtools support if not already implemented
        if not hasattr(cls, 'list_subtools') or cls.list_subtools.__get__(None, cls) == MCPTool.list_subtools.__get__(None, MCPTool):
            def list_subtools_method(self) -> List[str]:
                return list(subtools_set)
            cls.list_subtools = list_subtools_method
        
        # Add auto-registration support
        def register_with_global_registry(self):
            """Register this tool with the global registry."""
            from .base import ToolRegistry
            # This would need a global registry instance
            # For now, we'll just mark the tool as decorated
            pass
        
        cls._decorated = True
        cls._decorator_args = {
            'name': name,
            'description': description,
            'input_schema': input_schema,
            'output_schema': final_output_schema,
            'backend': backend,
            'owner_domain': owner_domain,
            'version': version,
            'tags': tags,
            'effect_boundary': effect_boundary,
            'subtools': subtools
        }
        
        return cls
    
    return decorator


def auto_register(cls: T) -> T:
    """
    Decorator for automatic registration with a global registry.
    This is a simpler alternative to the full register_tool decorator.
    """
    # Mark the class for auto-registration
    cls._auto_register = True
    return cls


def validate_schema(schema: Dict[str, Any]) -> bool:
    """
    Validate that a schema is a valid JSON schema.
    Basic validation - can be enhanced with full JSON Schema validation.
    """
    if not isinstance(schema, dict):
        return False
    
    if "type" not in schema:
        return False
    
    valid_types = ["object", "array", "string", "number", "integer", "boolean", "null"]
    if schema["type"] not in valid_types:
        return False
    
    return True


def create_tool_metadata(
    name: str,
    description: str,
    input_schema: Dict[str, Any],
    output_schema: Optional[Dict[str, Any]] = None,
    backend: str = "prompt",
    owner_domain: str = "default",
    version: str = "1.0.0",
    tags: Optional[List[str]] = None,
    effect_boundary: str = "llm",
    subtools: Optional[List[str]] = None
) -> ToolMetadata:
    """
    Create ToolMetadata with validation.
    
    This is a helper function for creating metadata outside of the decorator.
    """
    # Validate schemas
    if not validate_schema(input_schema):
        raise ValueError(f"Invalid input schema for tool {name}")
    
    if output_schema and not validate_schema(output_schema):
        raise ValueError(f"Invalid output schema for tool {name}")
    
    # Validate backend
    try:
        backend_enum = ToolBackend(backend)
    except ValueError:
        raise ValueError(f"Invalid backend: {backend}")
    
    # Validate effect boundary
    try:
        effect_boundary_enum = EffectBoundary(effect_boundary)
    except ValueError:
        raise ValueError(f"Invalid effect_boundary: {effect_boundary}")
    
    # Set default output schema
    if output_schema is None:
        output_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "content": {"type": "object"}
                }
            }
        }
    
    return ToolMetadata(
        name=name,
        description=description,
        input_schema=input_schema,
        output_schema=output_schema,
        backend=backend_enum,
        owner_domain=owner_domain,
        version=version,
        tags=frozenset(tags or []),
        effect_boundary=effect_boundary_enum,
        subtools=frozenset(subtools or [])
    ) 