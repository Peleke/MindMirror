"""
Prompt-Based Tool Implementations

Specialized tool implementations for prompt-based backend integration.
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import re

from .base import MCPTool, ToolMetadata, ToolBackend, EffectBoundary


class PromptType(Enum):
    """Types of prompts."""
    TEXT = "text"
    STRUCTURED = "structured"
    TEMPLATE = "template"
    CHAIN = "chain"
    CONDITIONAL = "conditional"


@dataclass
class PromptConfig:
    """Configuration for a prompt-based tool."""
    prompt_type: PromptType
    content: str
    variables: Dict[str, Any] = field(default_factory=dict)
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    output_format: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


class PromptTool(MCPTool):
    """Base class for prompt-based tools."""
    
    def __init__(self, prompt_config: PromptConfig):
        self.prompt_config = prompt_config
        self._compiled_template = None
    
    def get_metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        return ToolMetadata(
            name=f"prompt_{self.prompt_config.prompt_type.value}",
            description=f"A {self.prompt_config.prompt_type.value} prompt tool",
            input_schema=self._get_input_schema(),
            backend=ToolBackend.PROMPT,
            tags=frozenset(self.prompt_config.tags + ["prompt"]),
            effect_boundary=EffectBoundary.LLM
        )
    
    def _get_input_schema(self) -> Dict[str, Any]:
        """Get input schema for the prompt tool."""
        properties = {
            "variables": {
                "type": "object",
                "description": "Variables to substitute in the prompt"
            }
        }
        
        # Add required variables based on prompt config
        if self.prompt_config.variables:
            properties["variables"]["properties"] = {}
            required = []
            for var_name, var_config in self.prompt_config.variables.items():
                properties["variables"]["properties"][var_name] = {
                    "type": var_config.get("type", "string"),
                    "description": var_config.get("description", f"Variable: {var_name}")
                }
                if var_config.get("required", False):
                    required.append(var_name)
            
            if required:
                properties["variables"]["required"] = required
        
        return {
            "type": "object",
            "properties": properties,
            "required": ["variables"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the prompt tool."""
        variables = arguments.get("variables", {})
        
        # Validate variables
        self._validate_variables(variables)
        
        # Process prompt based on type
        if self.prompt_config.prompt_type == PromptType.TEXT:
            return await self._execute_text_prompt(variables)
        elif self.prompt_config.prompt_type == PromptType.STRUCTURED:
            return await self._execute_structured_prompt(variables)
        elif self.prompt_config.prompt_type == PromptType.TEMPLATE:
            return await self._execute_template_prompt(variables)
        elif self.prompt_config.prompt_type == PromptType.CHAIN:
            return await self._execute_chain_prompt(variables)
        elif self.prompt_config.prompt_type == PromptType.CONDITIONAL:
            return await self._execute_conditional_prompt(variables)
        else:
            raise ValueError(f"Unsupported prompt type: {self.prompt_config.prompt_type}")
    
    def _validate_variables(self, variables: Dict[str, Any]) -> None:
        """Validate input variables."""
        for var_name, var_config in self.prompt_config.variables.items():
            if var_config.get("required", False) and var_name not in variables:
                raise ValueError(f"Required variable '{var_name}' is missing")
            
            if var_name in variables:
                value = variables[var_name]
                expected_type = var_config.get("type", "string")
                
                if expected_type == "string" and not isinstance(value, str):
                    raise ValueError(f"Variable '{var_name}' must be a string")
                elif expected_type == "number" and not isinstance(value, (int, float)):
                    raise ValueError(f"Variable '{var_name}' must be a number")
                elif expected_type == "boolean" and not isinstance(value, bool):
                    raise ValueError(f"Variable '{var_name}' must be a boolean")
                
                # Check validation rules
                validation_rules = var_config.get("validation", {})
                if "min_length" in validation_rules and isinstance(value, str):
                    if len(value) < validation_rules["min_length"]:
                        raise ValueError(f"Variable '{var_name}' is too short")
                if "max_length" in validation_rules and isinstance(value, str):
                    if len(value) > validation_rules["max_length"]:
                        raise ValueError(f"Variable '{var_name}' is too long")
    
    async def _execute_text_prompt(self, variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute a simple text prompt."""
        prompt = self.prompt_config.content
        
        # Simple variable substitution
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            prompt = prompt.replace(placeholder, str(var_value))
        
        return [{
            "type": "prompt_result",
            "prompt_type": "text",
            "processed_prompt": prompt,
            "variables_used": list(variables.keys())
        }]
    
    async def _execute_structured_prompt(self, variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute a structured prompt."""
        try:
            # Parse structured content
            structured_content = json.loads(self.prompt_config.content)
            
            # Apply variable substitution to structured content
            processed_content = self._substitute_variables_in_structure(
                structured_content, variables
            )
            
            return [{
                "type": "prompt_result",
                "prompt_type": "structured",
                "processed_content": processed_content,
                "variables_used": list(variables.keys())
            }]
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in structured prompt content")
    
    def _substitute_variables_in_structure(self, structure: Any, variables: Dict[str, Any]) -> Any:
        """Recursively substitute variables in a structured object."""
        if isinstance(structure, dict):
            return {
                key: self._substitute_variables_in_structure(value, variables)
                for key, value in structure.items()
            }
        elif isinstance(structure, list):
            return [
                self._substitute_variables_in_structure(item, variables)
                for item in structure
            ]
        elif isinstance(structure, str):
            # Substitute variables in strings
            for var_name, var_value in variables.items():
                placeholder = f"{{{var_name}}}"
                structure = structure.replace(placeholder, str(var_value))
            return structure
        else:
            return structure
    
    async def _execute_template_prompt(self, variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute a template prompt."""
        template = self.prompt_config.content
        
        # Advanced template processing with regex
        processed_template = template
        
        # Handle different placeholder formats: {var}, {{var}}, ${var}
        for var_name, var_value in variables.items():
            patterns = [
                f"{{{var_name}}}",
                f"{{{{{var_name}}}}}",
                f"${{{var_name}}}"
            ]
            
            for pattern in patterns:
                processed_template = processed_template.replace(pattern, str(var_value))
        
        # Handle conditional blocks: {% if var %}...{% endif %}
        processed_template = self._process_conditional_blocks(processed_template, variables)
        
        # Handle loops: {% for item in items %}...{% endfor %}
        processed_template = self._process_loop_blocks(processed_template, variables)
        
        return [{
            "type": "prompt_result",
            "prompt_type": "template",
            "processed_template": processed_template,
            "variables_used": list(variables.keys())
        }]
    
    def _process_conditional_blocks(self, template: str, variables: Dict[str, Any]) -> str:
        """Process conditional blocks in template."""
        # Simple conditional processing
        pattern = r'{%\s*if\s+(\w+)\s*%}(.*?){%\s*endif\s*%}'
        
        def replace_conditional(match):
            condition_var = match.group(1)
            content = match.group(2)
            
            if condition_var in variables and variables[condition_var]:
                return content
            else:
                return ""
        
        return re.sub(pattern, replace_conditional, template, flags=re.DOTALL)
    
    def _process_loop_blocks(self, template: str, variables: Dict[str, Any]) -> str:
        """Process loop blocks in template."""
        # Simple loop processing
        pattern = r'{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%}(.*?){%\s*endfor\s*%}'
        
        def replace_loop(match):
            item_var = match.group(1)
            list_var = match.group(2)
            content = match.group(3)
            
            if list_var in variables and isinstance(variables[list_var], list):
                result = ""
                for item in variables[list_var]:
                    # Replace item placeholder in content
                    item_content = content.replace(f"{{{item_var}}}", str(item))
                    result += item_content
                return result
            else:
                return ""
        
        return re.sub(pattern, replace_loop, template, flags=re.DOTALL)
    
    async def _execute_chain_prompt(self, variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute a chain of prompts."""
        chain_config = json.loads(self.prompt_config.content)
        steps = chain_config.get("steps", [])
        
        results = []
        current_variables = variables.copy()
        
        for step in steps:
            step_prompt = step.get("prompt", "")
            step_type = step.get("type", "text")
            
            # Process step prompt
            processed_prompt = step_prompt
            for var_name, var_value in current_variables.items():
                placeholder = f"{{{var_name}}}"
                processed_prompt = processed_prompt.replace(placeholder, str(var_value))
            
            # Simulate step execution
            step_result = f"Step result: {processed_prompt}"
            
            # Update variables for next step
            output_var = step.get("output_variable")
            if output_var:
                current_variables[output_var] = step_result
            
            results.append({
                "step": step.get("name", "unnamed"),
                "prompt": processed_prompt,
                "result": step_result
            })
        
        return [{
            "type": "prompt_result",
            "prompt_type": "chain",
            "steps": results,
            "final_variables": current_variables
        }]
    
    async def _execute_conditional_prompt(self, variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute a conditional prompt."""
        conditional_config = json.loads(self.prompt_config.content)
        conditions = conditional_config.get("conditions", [])
        
        # Find matching condition
        matching_prompt = None
        matched_condition = None
        
        for condition in conditions:
            condition_expr = condition.get("condition", "")
            if self._evaluate_condition(condition_expr, variables):
                matching_prompt = condition.get("prompt", "")
                matched_condition = condition_expr
                break
        
        if not matching_prompt:
            # Use default prompt
            matching_prompt = conditional_config.get("default", "")
            matched_condition = "default"
        
        # Process the selected prompt
        processed_prompt = matching_prompt
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            processed_prompt = processed_prompt.replace(placeholder, str(var_value))
        
        return [{
            "type": "prompt_result",
            "prompt_type": "conditional",
            "matched_condition": matched_condition,
            "processed_prompt": processed_prompt,
            "variables_used": list(variables.keys())
        }]
    
    def _evaluate_condition(self, condition: str, variables: Dict[str, Any]) -> bool:
        """Evaluate a condition expression."""
        # Simple condition evaluation
        if condition == "always":
            return True
        elif condition == "never":
            return False
        elif "==" in condition:
            var_name, value = condition.split("==", 1)
            var_name = var_name.strip()
            value = value.strip().strip('"\'')
            return variables.get(var_name) == value
        elif "!=" in condition:
            var_name, value = condition.split("!=", 1)
            var_name = var_name.strip()
            value = value.strip().strip('"\'')
            # Handle numeric comparison
            try:
                if isinstance(variables.get(var_name), (int, float)):
                    return variables.get(var_name) != float(value)
                else:
                    return variables.get(var_name) != value
            except (ValueError, TypeError):
                return variables.get(var_name) != value
        elif "in" in condition:
            var_name, list_name = condition.split(" in ", 1)
            var_name = var_name.strip()
            list_name = list_name.strip()
            return variables.get(var_name) in variables.get(list_name, [])
        else:
            # Check if variable exists and is truthy
            var_name = condition.strip()
            return var_name in variables and bool(variables[var_name])


class PromptChainTool(MCPTool):
    """Tool for executing chains of prompts."""
    
    def __init__(self, chain_config: Dict[str, Any]):
        self.chain_config = chain_config
        self.prompts = chain_config.get("prompts", [])
        self.flow_control = chain_config.get("flow_control", {})
    
    def get_metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        return ToolMetadata(
            name=self.chain_config.get("name", "prompt_chain"),
            description=self.chain_config.get("description", "A chain of prompts"),
            input_schema=self._get_input_schema(),
            backend=ToolBackend.PROMPT,
            tags=frozenset(["prompt", "chain"]),
            effect_boundary=EffectBoundary.LLM
        )
    
    def _get_input_schema(self) -> Dict[str, Any]:
        """Get input schema for the prompt chain."""
        return {
            "type": "object",
            "properties": {
                "initial_variables": {
                    "type": "object",
                    "description": "Initial variables for the chain"
                },
                "chain_config": {
                    "type": "object",
                    "description": "Configuration for chain execution"
                }
            },
            "required": ["initial_variables"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the prompt chain."""
        initial_variables = arguments.get("initial_variables", {})
        chain_config = arguments.get("chain_config", {})
        
        current_variables = initial_variables.copy()
        results = []
        
        for i, prompt_config in enumerate(self.prompts):
            # Create prompt tool for this step
            prompt_tool = PromptTool(PromptConfig(
                prompt_type=PromptType(prompt_config.get("type", "text")),
                content=prompt_config.get("content", ""),
                variables=prompt_config.get("variables", {}),
                tags=prompt_config.get("tags", [])
            ))
            
            # Execute prompt
            prompt_result = await prompt_tool.execute({
                "variables": current_variables
            })
            
            # Extract result and update variables
            if prompt_result:
                result = prompt_result[0]
                results.append({
                    "step": i,
                    "prompt_name": prompt_config.get("name", f"step_{i}"),
                    "result": result
                })
                
                # Update variables for next step
                output_mapping = prompt_config.get("output_mapping", {})
                for output_key, var_name in output_mapping.items():
                    if output_key in result:
                        current_variables[var_name] = result[output_key]
        
        return [{
            "type": "chain_result",
            "steps": results,
            "final_variables": current_variables,
            "total_steps": len(results)
        }]


class PromptTemplateManager:
    """Manages prompt templates."""
    
    def __init__(self):
        self.templates = {}
    
    def register_template(self, name: str, template: PromptConfig) -> None:
        """Register a prompt template."""
        self.templates[name] = template
    
    def get_template(self, name: str) -> Optional[PromptConfig]:
        """Get a prompt template by name."""
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
    
    def export_templates(self) -> Dict[str, Any]:
        """Export all templates."""
        return {
            name: {
                "prompt_type": template.prompt_type.value,
                "content": template.content,
                "variables": template.variables,
                "tags": template.tags
            }
            for name, template in self.templates.items()
        } 