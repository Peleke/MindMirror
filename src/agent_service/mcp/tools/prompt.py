"""
Prompt Tool Implementations

Specialized tool implementations for prompt-based processing.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from .base import MCPTool, ToolMetadata, ToolBackend, EffectBoundary


@dataclass
class PromptTemplate:
    """Template for prompt-based tools."""
    name: str
    description: str
    template: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    tags: List[str] = field(default_factory=list)


class PromptTool(MCPTool):
    """Base class for prompt-based tools."""
    
    def __init__(self, template: PromptTemplate):
        self.template = template
        self._llm_service = None  # Would be injected
    
    @property
    def owner_domain(self) -> str:
        """Get the owner domain for this tool."""
        return "prompt"
    
    @property
    def version(self) -> str:
        """Get the tool version (semver)."""
        return "1.0.0"
    
    @property
    def output_schema(self) -> Dict[str, Any]:
        """Get the output schema for this tool."""
        return self.template.output_schema
    
    def get_metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        return ToolMetadata(
            name=self.template.name,
            description=self.template.description,
            input_schema=self.template.input_schema,
            output_schema=self.output_schema,
            backend=ToolBackend.PROMPT,
            owner_domain=self.owner_domain,
            version=self.version,
            tags=frozenset(self.template.tags),
            effect_boundary=EffectBoundary.LLM
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the prompt tool."""
        # Format the template with arguments
        formatted_prompt = self.template.template.format(**arguments)
        
        # Simulate LLM call
        response = f"Generated response for: {formatted_prompt}"
        
        return [{
            "type": "text",
            "text": response,
            "prompt": formatted_prompt,
            "arguments": arguments
        }]


class PromptChainTool(MCPTool):
    """Tool for executing chains of prompts."""
    
    def __init__(self, name: str, description: str, templates: List[PromptTemplate]):
        self.name = name
        self.description = description
        self.templates = templates
        self._llm_service = None  # Would be injected
    
    @property
    def owner_domain(self) -> str:
        """Get the owner domain for this tool."""
        return "prompt_chain"
    
    @property
    def version(self) -> str:
        """Get the tool version (semver)."""
        return "1.0.0"
    
    @property
    def output_schema(self) -> Dict[str, Any]:
        """Get the output schema for this tool."""
        return {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "step": {"type": "integer"},
                    "template": {"type": "string"},
                    "prompt": {"type": "string"},
                    "response": {"type": "string"}
                },
                "required": ["step", "template", "prompt", "response"]
            }
        }
    
    def get_metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        return ToolMetadata(
            name=self.name,
            description=self.description,
            input_schema=self._get_input_schema(),
            output_schema=self.output_schema,
            backend=ToolBackend.PROMPT,
            owner_domain=self.owner_domain,
            version=self.version,
            tags=frozenset(["chain", "prompt"]),
            effect_boundary=EffectBoundary.LLM
        )
    
    def _get_input_schema(self) -> Dict[str, Any]:
        """Get input schema for the chain."""
        properties = {}
        required = []
        
        for template in self.templates:
            for field_name, field_schema in template.input_schema.get("properties", {}).items():
                properties[field_name] = field_schema
                if field_name in template.input_schema.get("required", []):
                    required.append(field_name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required
        }
    
    def list_subtools(self) -> List[str]:
        """List available subtools (individual templates)."""
        return [template.name for template in self.templates]
    
    async def execute_subtool(self, name: str, args: Dict[str, Any]) -> Any:
        """Execute a subtool (individual template)."""
        for template in self.templates:
            if template.name == name:
                prompt_tool = PromptTool(template)
                return await prompt_tool.execute(args)
        raise ValueError(f"Subtool {name} not found")
    
    async def execute(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the prompt chain."""
        results = []
        current_args = arguments.copy()
        
        for i, template in enumerate(self.templates):
            # Format the template
            formatted_prompt = template.template.format(**current_args)
            
            # Simulate LLM call
            response = f"Step {i+1} response for: {formatted_prompt}"
            
            # Update arguments for next step
            current_args[f"step_{i+1}_response"] = response
            
            results.append({
                "step": i + 1,
                "template": template.name,
                "prompt": formatted_prompt,
                "response": response
            })
        
        return results


class PromptTemplateManager:
    """Manages prompt templates."""
    
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
    
    def register_template(self, template: PromptTemplate) -> None:
        """Register a template."""
        self.templates[template.name] = template
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a template by name."""
        return self.templates.get(name)
    
    def list_templates(self) -> List[str]:
        """List all template names."""
        return list(self.templates.keys())
    
    def create_tool_from_template(self, template_name: str) -> Optional[PromptTool]:
        """Create a tool from a template."""
        template = self.get_template(template_name)
        if template:
            return PromptTool(template)
        return None
    
    def export_templates(self) -> str:
        """Export templates to YAML."""
        import yaml
        
        export_data = {
            "templates": [
                {
                    "name": template.name,
                    "description": template.description,
                    "template": template.template,
                    "input_schema": template.input_schema,
                    "output_schema": template.output_schema,
                    "tags": template.tags
                }
                for template in self.templates.values()
            ]
        }
        
        return yaml.dump(export_data, default_flow_style=False, sort_keys=False) 