"""
Prompt Tool Implementations

Specialized tool implementations for prompt-based processing.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .base import EffectBoundary, MCPTool, ToolBackend, ToolMetadata


class PromptType(Enum):
    """Types of prompts supported."""

    TEXT = "text"
    STRUCTURED = "structured"
    TEMPLATE = "template"
    CHAIN = "chain"
    CONDITIONAL = "conditional"


@dataclass
class PromptConfig:
    """Configuration for prompt-based tools."""

    prompt_type: PromptType
    content: str
    variables: Dict[str, Any] = field(default_factory=dict)
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    output_format: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


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

    def __init__(self, prompt_config: PromptConfig):
        self.prompt_config = prompt_config
        self._compiled_template = None
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
        return self.prompt_config.output_format

    def get_metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        return ToolMetadata(
            name=f"prompt_{self.prompt_config.prompt_type.value}",
            description=f"A {self.prompt_config.prompt_type.value} prompt tool",
            input_schema=self._get_input_schema(),
            output_schema=self.output_schema,
            backend=ToolBackend.PROMPT,
            owner_domain=self.owner_domain,
            version=self.version,
            tags=frozenset(self.prompt_config.tags + ["prompt"]),
            effect_boundary=EffectBoundary.LLM,
        )

    def _get_input_schema(self) -> Dict[str, Any]:
        """Get input schema for the prompt."""
        return {
            "type": "object",
            "properties": {
                "variables": {
                    "type": "object",
                    "properties": self.prompt_config.variables,
                    "required": [
                        k
                        for k, v in self.prompt_config.variables.items()
                        if v.get("required", False)
                    ],
                }
            },
            "required": ["variables"],
        }

    def _validate_variables(self, variables: Dict[str, Any]) -> None:
        """Validate input variables."""
        for var_name, var_config in self.prompt_config.variables.items():
            if var_config.get("required", False) and var_name not in variables:
                raise ValueError(f"Required variable '{var_name}' is missing")

            if var_name in variables:
                value = variables[var_name]
                expected_type = var_config.get("type", "string")

                # Type validation
                if expected_type == "string" and not isinstance(value, str):
                    raise ValueError(f"Variable '{var_name}' must be a string")
                elif expected_type == "number" and not isinstance(value, (int, float)):
                    raise ValueError(f"Variable '{var_name}' must be a number")

                # Length validation
                if isinstance(value, str):
                    validation = var_config.get("validation", {})
                    if (
                        "min_length" in validation
                        and len(value) < validation["min_length"]
                    ):
                        raise ValueError(f"Variable '{var_name}' is too short")
                    if (
                        "max_length" in validation
                        and len(value) > validation["max_length"]
                    ):
                        raise ValueError(f"Variable '{var_name}' is too long")

    async def execute(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the prompt tool."""
        variables = arguments.get("variables", {})
        self._validate_variables(variables)

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
            raise ValueError(
                f"Unsupported prompt type: {self.prompt_config.prompt_type}"
            )

    async def _execute_text_prompt(
        self, variables: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute a text prompt."""
        try:
            formatted_prompt = self.prompt_config.content.format(**variables)
        except KeyError as e:
            raise ValueError(f"Missing variable in prompt: {e}")

        # Simulate LLM call
        response = f"Generated response for: {formatted_prompt}"

        return [
            {
                "type": "prompt_result",
                "prompt_type": "text",
                "text": response,
                "prompt": formatted_prompt,
                "processed_prompt": formatted_prompt,
                "variables": variables,
                "variables_used": list(variables.keys()),
            }
        ]

    async def _execute_structured_prompt(
        self, variables: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute a structured prompt."""
        try:
            import json

            # Parse JSON content
            structured_content = json.loads(self.prompt_config.content)

            # Format the user prompt with variables
            user_prompt = structured_content.get("user", "")
            formatted_prompt = user_prompt.format(**variables)

            # Create processed content with formatted values
            processed_content = structured_content.copy()
            processed_content["user"] = formatted_prompt

            # Format nested variables in context
            def format_nested_dict(obj, vars_dict):
                if isinstance(obj, dict):
                    return {k: format_nested_dict(v, vars_dict) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [format_nested_dict(item, vars_dict) for item in obj]
                elif isinstance(obj, str):
                    try:
                        return obj.format(**vars_dict)
                    except (KeyError, ValueError):
                        return obj
                else:
                    return obj

            # Format nested variables in context
            if "context" in processed_content:
                processed_content["context"] = format_nested_dict(
                    processed_content["context"], variables
                )

            # Simulate structured response
            response = {
                "summary": f"Structured response for: {formatted_prompt}",
                "confidence": 0.95,
                "entities": ["entity1", "entity2"],
            }
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in structured prompt")
        except KeyError as e:
            raise ValueError(f"Missing variable in prompt: {e}")
        except Exception:
            raise ValueError("Failed to generate structured response")

        return [
            {
                "type": "prompt_result",
                "prompt_type": "structured",
                "data": response,
                "prompt": formatted_prompt,
                "processed_content": processed_content,
                "variables": variables,
            }
        ]

    async def _execute_template_prompt(
        self, variables: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute a template prompt."""
        try:
            # Simple template processing - handle Jinja2-like conditions
            content = self.prompt_config.content

            # Handle if conditions
            import re

            if_pattern = r"{%\s*if\s+(\w+)\s*%}(.*?){%\s*endif\s*%}"

            def replace_if(match):
                condition_var = match.group(1)
                content_block = match.group(2)
                if variables.get(condition_var):
                    return content_block
                return ""

            content = re.sub(if_pattern, replace_if, content, flags=re.DOTALL)

            # Handle for loops (simplified)
            for_pattern = r"{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%}(.*?){%\s*endfor\s*%}"

            def replace_for(match):
                item_var = match.group(1)
                list_var = match.group(2)
                content_block = match.group(3)
                items = variables.get(list_var, [])
                result = ""
                for item in items:
                    temp_vars = variables.copy()
                    temp_vars[item_var] = item
                    result += content_block.format(**temp_vars)
                return result

            content = re.sub(for_pattern, replace_for, content, flags=re.DOTALL)

            # Format remaining content
            formatted_prompt = content.format(**variables)

            # Simulate template processing
            response = f"Template response for: {formatted_prompt}"
        except KeyError as e:
            raise ValueError(f"Missing variable in prompt: {e}")

        return [
            {
                "type": "prompt_result",
                "prompt_type": "template",
                "text": response,
                "prompt": formatted_prompt,
                "processed_template": formatted_prompt,
                "variables": variables,
                "template_used": self.prompt_config.content,
            }
        ]

    async def _execute_chain_prompt(
        self, variables: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute a chain prompt."""
        try:
            import json

            # Parse JSON content
            chain_config = json.loads(self.prompt_config.content)

            # Process all steps
            steps = chain_config.get("steps", [])
            processed_steps = []

            current_vars = variables.copy()
            for i, step in enumerate(steps):
                prompt = step.get("prompt", "")
                formatted_prompt = prompt.format(**current_vars)

                # Simulate step execution
                step_response = f"Step {i+1} response: {formatted_prompt}"

                # Update variables for next step
                output_var = step.get("output_variable")
                if output_var:
                    current_vars[output_var] = step_response

                processed_steps.append(
                    {
                        "step": step.get("name", f"step{i+1}"),
                        "prompt": formatted_prompt,
                        "response": step_response,
                    }
                )

            # Return the final result
            final_response = f"Chain completed with {len(steps)} steps"

        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in chain prompt")
        except KeyError as e:
            raise ValueError(f"Missing variable in prompt: {e}")

        return [
            {
                "type": "prompt_result",
                "prompt_type": "chain",
                "text": final_response,
                "prompt": formatted_prompt if "formatted_prompt" in locals() else "",
                "variables": variables,
                "steps": processed_steps,
            }
        ]

    async def _execute_conditional_prompt(
        self, variables: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute a conditional prompt."""
        try:
            import json

            # Parse JSON content
            conditional_config = json.loads(self.prompt_config.content)

            # Evaluate conditions
            conditions = conditional_config.get("conditions", [])
            matched_prompt = conditional_config.get("default", "")
            matched_condition = (
                "default"  # Default to "default" if no condition matches
            )

            for condition_item in conditions:
                condition = condition_item.get("condition", "")
                if self._evaluate_condition(condition, variables):
                    matched_prompt = condition_item.get("prompt", "")
                    matched_condition = condition
                    break

            # Format the matched prompt
            formatted_prompt = matched_prompt.format(**variables)

            # Simulate conditional processing
            response = f"Conditional response for: {formatted_prompt}"
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in conditional prompt")
        except KeyError as e:
            raise ValueError(f"Missing variable in prompt: {e}")

        return [
            {
                "type": "prompt_result",
                "prompt_type": "conditional",
                "text": response,
                "prompt": formatted_prompt,
                "processed_prompt": formatted_prompt,
                "variables": variables,
                "condition": True,
                "matched_condition": matched_condition,
            }
        ]

    def _evaluate_condition(self, condition: str, variables: Dict[str, Any]) -> bool:
        """Evaluate condition for conditional prompts."""
        # Simple condition evaluation
        if condition == "always":
            return True
        elif condition == "never":
            return False
        elif "==" in condition:
            # Parse simple equality conditions like "user_type == 'premium'"
            try:
                left, right = condition.split("==")
                left = left.strip()
                right = right.strip().strip("'\"")
                return variables.get(left) == right
            except:
                return False
        elif "!=" in condition:
            # Parse simple inequality conditions like "age != 25"
            try:
                left, right = condition.split("!=")
                left = left.strip()
                right = right.strip().strip("'\"")
                # Try to convert to int if possible
                try:
                    right = int(right)
                except ValueError:
                    pass
                return variables.get(left) != right
            except:
                return False
        elif " in " in condition:
            # Parse "in" conditions like "item in items"
            try:
                left, right = condition.split(" in ")
                left = left.strip()
                right = right.strip()
                return variables.get(left) in variables.get(right, [])
            except:
                return False
        else:
            # Check if the condition is a variable name and evaluate its truthiness
            if condition in variables:
                return bool(variables[condition])
            # Default: return True if variables exist
            return len(variables) > 0


class PromptChainTool(MCPTool):
    """Tool for executing chains of prompts."""

    def __init__(self, config: Dict[str, Any]):
        self.name = config.get("name", "chain_tool")
        self.description = config.get("description", "A prompt chain tool")
        self.prompts = config.get("prompts", [])
        self.flow_control = config.get("flow_control", {})
        self.chain_config = config  # Store the full config for tests
        self._llm_service = None  # Would be injected

        # Convert prompts to templates
        self.templates = []
        for prompt in self.prompts:
            template = PromptTemplate(
                name=prompt.get("name", "unnamed"),
                description=prompt.get("description", ""),
                template=prompt.get("content", ""),
                input_schema=prompt.get("variables", {}),
                output_schema=prompt.get("output_schema", {}),
                tags=prompt.get("tags", []),
            )
            self.templates.append(template)

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
                    "response": {"type": "string"},
                },
                "required": ["step", "template", "prompt", "response"],
            },
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
            effect_boundary=EffectBoundary.LLM,
        )

    def _get_input_schema(self) -> Dict[str, Any]:
        """Get input schema for the chain."""
        properties = {}
        required = []

        for template in self.templates:
            for field_name, field_schema in template.input_schema.get(
                "properties", {}
            ).items():
                properties[field_name] = field_schema
                if field_name in template.input_schema.get("required", []):
                    required.append(field_name)

        return {"type": "object", "properties": properties, "required": required}

    def list_subtools(self) -> List[str]:
        """List available subtools (individual templates)."""
        return [template.name for template in self.templates]

    async def execute_subtool(self, name: str, args: Dict[str, Any]) -> Any:
        """Execute a subtool (individual template)."""
        for template in self.templates:
            if template.name == name:
                # Create a PromptConfig from the template
                prompt_config = PromptConfig(
                    prompt_type=PromptType.TEMPLATE,
                    content=template.template,
                    variables=template.input_schema.get("properties", {}),
                    tags=template.tags,
                )
                prompt_tool = PromptTool(prompt_config)
                return await prompt_tool.execute({"variables": args})
        raise ValueError(f"Subtool {name} not found")

    async def execute(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the prompt chain."""
        results = []

        # Handle different argument structures
        if "initial_variables" in arguments:
            current_args = arguments["initial_variables"].copy()
        else:
            current_args = arguments.copy()

        for i, template in enumerate(self.templates):
            # Format the template
            try:
                formatted_prompt = template.template.format(**current_args)
            except KeyError as e:
                raise ValueError(f"Missing variable in template {template.name}: {e}")

            # Simulate LLM call
            response = f"Step {i+1} response for: {formatted_prompt}"

            # Update arguments for next step based on output mapping
            # Check if this prompt has output mapping
            prompt_config = self.prompts[i] if i < len(self.prompts) else {}
            output_mapping = prompt_config.get("output_mapping", {})

            # Apply output mappings
            for output_key, variable_name in output_mapping.items():
                if output_key == "processed_prompt":
                    current_args[variable_name] = formatted_prompt
                elif output_key == "text":
                    current_args[variable_name] = response
                else:
                    # Default mapping
                    current_args[variable_name] = response

            # Also add step response for backward compatibility
            current_args[f"step_{i+1}_response"] = response

            results.append(
                {
                    "step": i + 1,
                    "template": template.name,
                    "prompt": formatted_prompt,
                    "response": response,
                }
            )

        # Return a single result with all steps
        return [
            {
                "type": "chain_result",
                "steps": results,
                "total_steps": len(results),
                "final_variables": current_args,
            }
        ]


class PromptTemplateManager:
    """Manages prompt templates."""

    def __init__(self):
        self.templates: Dict[str, Any] = {}
        self.original_configs: Dict[str, PromptConfig] = (
            {}
        )  # Store original PromptConfig objects

    def register_template(self, name: str, template: Any) -> None:
        """Register a template with a name."""
        if isinstance(template, PromptConfig):
            # Store the original config
            self.original_configs[name] = template
            # Also store in templates for direct access
            self.templates[name] = template
            # Convert PromptConfig to PromptTemplate for internal use
            prompt_template = PromptTemplate(
                name=name,
                description=f"Template for {name}",
                template=template.content,
                input_schema={"properties": template.variables},
                output_schema=template.output_format,
                tags=template.tags,
            )
            # Store template version separately
            self._template_objects = getattr(self, "_template_objects", {})
            self._template_objects[name] = prompt_template
        elif isinstance(template, PromptTemplate):
            self.templates[name] = template
        else:
            raise ValueError(f"Unsupported template type: {type(template)}")

    def get_template(self, name: str) -> Optional[Any]:
        """Get a template by name."""
        # Return original config if available, otherwise template
        if name in self.original_configs:
            return self.original_configs[name]
        return self.templates.get(name)

    def list_templates(self) -> List[str]:
        """List all template names."""
        return list(self.templates.keys())

    def create_tool_from_template(self, template_name: str) -> Optional[PromptTool]:
        """Create a tool from a template."""
        template = self.get_template(template_name)
        if template:
            if isinstance(template, PromptConfig):
                return PromptTool(template)
            else:
                # Create a PromptConfig from the template
                prompt_config = PromptConfig(
                    prompt_type=PromptType.TEMPLATE,
                    content=template.template,
                    variables=template.input_schema.get("properties", {}),
                    tags=template.tags,
                )
                return PromptTool(prompt_config)
        return None

    def export_templates(self) -> Dict[str, Any]:
        """Export templates to dictionary format."""
        data = {}
        for name, template in self.templates.items():
            if name in self.original_configs:
                # Use original config for export
                config = self.original_configs[name]
                data[name] = {
                    "prompt_type": config.prompt_type.value,
                    "content": config.content,
                    "variables": config.variables,
                    "validation_rules": config.validation_rules,
                    "output_format": config.output_format,
                    "tags": config.tags,
                }
            else:
                data[name] = {
                    "description": template.description,
                    "template": template.template,
                    "input_schema": template.input_schema,
                    "output_schema": template.output_schema,
                    "tags": template.tags,
                }

        return data

    def __getitem__(self, name: str) -> Any:
        """Allow dictionary-style access to templates."""
        return self.get_template(name)

    def __contains__(self, name: str) -> bool:
        """Check if template exists."""
        return name in self.templates or name in self.original_configs
