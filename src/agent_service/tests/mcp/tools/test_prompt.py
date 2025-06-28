"""
Test Suite for Prompt-Based Tool Implementations

Comprehensive tests for prompt-based tool functionality.
"""

import json
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock

import pytest

# If PromptType does not exist, comment out or fix the import
try:
    from agent_service.mcp.tools.prompt import (PromptChainTool, PromptConfig,
                                                PromptTemplateManager,
                                                PromptTool, PromptType)
except ImportError:
    PromptType = None


class TestPromptType:
    """Test PromptType enum."""

    def test_prompt_type_values(self):
        """Test prompt type enum values."""
        assert PromptType.TEXT.value == "text"
        assert PromptType.STRUCTURED.value == "structured"
        assert PromptType.TEMPLATE.value == "template"
        assert PromptType.CHAIN.value == "chain"
        assert PromptType.CONDITIONAL.value == "conditional"


class TestPromptConfig:
    """Test PromptConfig dataclass."""

    def test_prompt_config_creation(self):
        """Test prompt config creation."""
        config = PromptConfig(
            prompt_type=PromptType.TEXT,
            content="Hello {name}!",
            variables={
                "name": {
                    "type": "string",
                    "description": "User's name",
                    "required": True,
                    "validation": {"min_length": 1},
                }
            },
            validation_rules={"max_length": 100},
            output_format={"type": "text"},
            tags=["greeting", "personal"],
        )

        assert config.prompt_type == PromptType.TEXT
        assert config.content == "Hello {name}!"
        assert config.variables["name"]["type"] == "string"
        assert config.variables["name"]["required"] is True
        assert config.tags == ["greeting", "personal"]

    def test_prompt_config_defaults(self):
        """Test prompt config with defaults."""
        config = PromptConfig(prompt_type=PromptType.TEXT, content="Simple prompt")

        assert config.variables == {}
        assert config.validation_rules == {}
        assert config.output_format == {}
        assert config.tags == []


class TestPromptTool:
    """Test PromptTool base class."""

    def test_tool_creation(self):
        """Test tool creation."""
        prompt_config = PromptConfig(
            prompt_type=PromptType.TEXT,
            content="Hello {name}!",
            variables={"name": {"type": "string", "required": True}},
        )

        tool = PromptTool(prompt_config)
        assert tool.prompt_config == prompt_config
        assert tool._compiled_template is None

    def test_tool_metadata(self):
        """Test tool metadata retrieval."""
        prompt_config = PromptConfig(
            prompt_type=PromptType.TEXT,
            content="Hello {name}!",
            tags=["greeting", "test"],
        )

        tool = PromptTool(prompt_config)
        metadata = tool.get_metadata()

        assert metadata.name == "prompt_text"
        assert metadata.description == "A text prompt tool"
        assert "greeting" in metadata.tags
        assert "test" in metadata.tags
        assert "prompt" in metadata.tags

    def test_input_schema_with_variables(self):
        """Test input schema generation with variables."""
        prompt_config = PromptConfig(
            prompt_type=PromptType.TEXT,
            content="Hello {name}!",
            variables={
                "name": {
                    "type": "string",
                    "description": "User's name",
                    "required": True,
                },
                "age": {
                    "type": "number",
                    "description": "User's age",
                    "required": False,
                },
            },
        )

        tool = PromptTool(prompt_config)
        schema = tool._get_input_schema()

        assert "variables" in schema["properties"]
        assert "name" in schema["properties"]["variables"]["properties"]
        assert "age" in schema["properties"]["variables"]["properties"]
        assert "name" in schema["properties"]["variables"]["required"]
        assert "age" not in schema["properties"]["variables"]["required"]

    def test_input_schema_without_variables(self):
        """Test input schema generation without variables."""
        prompt_config = PromptConfig(
            prompt_type=PromptType.TEXT, content="Hello world!"
        )

        tool = PromptTool(prompt_config)
        schema = tool._get_input_schema()

        assert "variables" in schema["properties"]
        assert schema["properties"]["variables"]["type"] == "object"

    def test_variable_validation_missing_required(self):
        """Test variable validation with missing required variable."""
        prompt_config = PromptConfig(
            prompt_type=PromptType.TEXT,
            content="Hello {name}!",
            variables={"name": {"type": "string", "required": True}},
        )

        tool = PromptTool(prompt_config)

        with pytest.raises(ValueError, match="Required variable 'name' is missing"):
            tool._validate_variables({})

    def test_variable_validation_wrong_type(self):
        """Test variable validation with wrong type."""
        prompt_config = PromptConfig(
            prompt_type=PromptType.TEXT,
            content="Hello {name}!",
            variables={"name": {"type": "string", "required": True}},
        )

        tool = PromptTool(prompt_config)

        with pytest.raises(ValueError, match="Variable 'name' must be a string"):
            tool._validate_variables({"name": 123})

    def test_variable_validation_length_rules(self):
        """Test variable validation with length rules."""
        prompt_config = PromptConfig(
            prompt_type=PromptType.TEXT,
            content="Hello {name}!",
            variables={
                "name": {
                    "type": "string",
                    "required": True,
                    "validation": {"min_length": 3, "max_length": 10},
                }
            },
        )

        tool = PromptTool(prompt_config)

        # Test too short
        with pytest.raises(ValueError, match="Variable 'name' is too short"):
            tool._validate_variables({"name": "ab"})

        # Test too long
        with pytest.raises(ValueError, match="Variable 'name' is too long"):
            tool._validate_variables({"name": "very_long_name_that_exceeds_limit"})

        # Test valid length
        tool._validate_variables({"name": "John"})  # Should not raise

    @pytest.mark.asyncio
    async def test_execute_text_prompt(self):
        """Test executing a text prompt."""
        prompt_config = PromptConfig(
            prompt_type=PromptType.TEXT,
            content="Hello {name}! You are {age} years old.",
        )

        tool = PromptTool(prompt_config)
        result = await tool.execute({"variables": {"name": "John", "age": "25"}})

        assert len(result) == 1
        assert result[0]["type"] == "prompt_result"
        assert result[0]["prompt_type"] == "text"
        assert result[0]["processed_prompt"] == "Hello John! You are 25 years old."
        assert "name" in result[0]["variables_used"]
        assert "age" in result[0]["variables_used"]

    @pytest.mark.asyncio
    async def test_execute_structured_prompt(self):
        """Test executing a structured prompt."""
        structured_content = {
            "system": "You are a helpful assistant.",
            "user": "Hello {name}!",
            "context": {"user_info": {"name": "{name}", "age": "{age}"}},
        }

        prompt_config = PromptConfig(
            prompt_type=PromptType.STRUCTURED, content=json.dumps(structured_content)
        )

        tool = PromptTool(prompt_config)
        result = await tool.execute({"variables": {"name": "John", "age": "25"}})

        assert len(result) == 1
        assert result[0]["type"] == "prompt_result"
        assert result[0]["prompt_type"] == "structured"

        processed_content = result[0]["processed_content"]
        assert processed_content["user"] == "Hello John!"
        assert processed_content["context"]["user_info"]["name"] == "John"
        assert processed_content["context"]["user_info"]["age"] == "25"

    @pytest.mark.asyncio
    async def test_execute_structured_prompt_invalid_json(self):
        """Test executing structured prompt with invalid JSON."""
        prompt_config = PromptConfig(
            prompt_type=PromptType.STRUCTURED, content="invalid json content"
        )

        tool = PromptTool(prompt_config)

        with pytest.raises(ValueError, match="Invalid JSON"):
            await tool.execute({"variables": {}})

    @pytest.mark.asyncio
    async def test_execute_template_prompt(self):
        """Test executing a template prompt."""
        template = """
        Hello {name}!
        {% if has_account %}
        Welcome back to your account.
        {% endif %}
        {% for item in items %}
        - {item}
        {% endfor %}
        """

        prompt_config = PromptConfig(prompt_type=PromptType.TEMPLATE, content=template)

        tool = PromptTool(prompt_config)
        result = await tool.execute(
            {
                "variables": {
                    "name": "John",
                    "has_account": True,
                    "items": ["item1", "item2", "item3"],
                }
            }
        )

        assert len(result) == 1
        assert result[0]["type"] == "prompt_result"
        assert result[0]["prompt_type"] == "template"

        processed_template = result[0]["processed_template"]
        assert "Hello John!" in processed_template
        assert "Welcome back to your account." in processed_template
        assert "- item1" in processed_template
        assert "- item2" in processed_template
        assert "- item3" in processed_template

    @pytest.mark.asyncio
    async def test_execute_chain_prompt(self):
        """Test executing a chain prompt."""
        chain_config = {
            "steps": [
                {
                    "name": "step1",
                    "prompt": "Process: {input}",
                    "output_variable": "step1_result",
                },
                {
                    "name": "step2",
                    "prompt": "Continue: {step1_result}",
                    "output_variable": "final_result",
                },
            ]
        }

        prompt_config = PromptConfig(
            prompt_type=PromptType.CHAIN, content=json.dumps(chain_config)
        )

        tool = PromptTool(prompt_config)
        result = await tool.execute({"variables": {"input": "test input"}})

        assert len(result) == 1
        assert result[0]["type"] == "prompt_result"
        assert result[0]["prompt_type"] == "chain"
        assert len(result[0]["steps"]) == 2
        assert result[0]["steps"][0]["step"] == "step1"
        assert result[0]["steps"][1]["step"] == "step2"

    @pytest.mark.asyncio
    async def test_execute_conditional_prompt(self):
        """Test executing a conditional prompt."""
        conditional_config = {
            "conditions": [
                {
                    "condition": "user_type == 'premium'",
                    "prompt": "Welcome premium user {name}!",
                },
                {
                    "condition": "user_type == 'basic'",
                    "prompt": "Welcome basic user {name}!",
                },
            ],
            "default": "Welcome {name}!",
        }

        prompt_config = PromptConfig(
            prompt_type=PromptType.CONDITIONAL, content=json.dumps(conditional_config)
        )

        tool = PromptTool(prompt_config)

        # Test premium user
        result_premium = await tool.execute(
            {"variables": {"name": "John", "user_type": "premium"}}
        )

        assert result_premium[0]["matched_condition"] == "user_type == 'premium'"
        assert "Welcome premium user John!" in result_premium[0]["processed_prompt"]

        # Test basic user
        result_basic = await tool.execute(
            {"variables": {"name": "Jane", "user_type": "basic"}}
        )

        assert result_basic[0]["matched_condition"] == "user_type == 'basic'"
        assert "Welcome basic user Jane!" in result_basic[0]["processed_prompt"]

        # Test unknown user type (should use default)
        result_default = await tool.execute(
            {"variables": {"name": "Bob", "user_type": "unknown"}}
        )

        assert result_default[0]["matched_condition"] == "default"
        assert "Welcome Bob!" in result_default[0]["processed_prompt"]

    def test_evaluate_condition(self):
        """Test condition evaluation."""
        prompt_config = PromptConfig(prompt_type=PromptType.CONDITIONAL, content="{}")

        tool = PromptTool(prompt_config)

        # Test always condition
        assert tool._evaluate_condition("always", {}) is True

        # Test never condition
        assert tool._evaluate_condition("never", {}) is False

        # Test equality conditions
        assert tool._evaluate_condition("name == 'John'", {"name": "John"}) is True
        assert tool._evaluate_condition("name == 'John'", {"name": "Jane"}) is False
        assert tool._evaluate_condition("age != 25", {"age": 30}) is True
        assert tool._evaluate_condition("age != 25", {"age": 25}) is False

        # Test in condition
        assert (
            tool._evaluate_condition(
                "item in items", {"item": "apple", "items": ["apple", "banana"]}
            )
            is True
        )
        assert (
            tool._evaluate_condition(
                "item in items", {"item": "orange", "items": ["apple", "banana"]}
            )
            is False
        )

        # Test truthy condition
        assert tool._evaluate_condition("has_data", {"has_data": True}) is True
        assert tool._evaluate_condition("has_data", {"has_data": False}) is False
        assert tool._evaluate_condition("has_data", {}) is False


class TestPromptChainTool:
    """Test PromptChainTool."""

    def test_chain_tool_creation(self):
        """Test chain tool creation."""
        chain_config = {
            "name": "test_chain",
            "description": "A test prompt chain",
            "prompts": [
                {
                    "name": "step1",
                    "type": "text",
                    "content": "Step 1: {input}",
                    "variables": {"input": {"type": "string", "required": True}},
                },
                {
                    "name": "step2",
                    "type": "text",
                    "content": "Step 2: {step1_output}",
                    "variables": {"step1_output": {"type": "string", "required": True}},
                },
            ],
            "flow_control": {"max_steps": 5},
        }

        tool = PromptChainTool(chain_config)
        assert tool.chain_config == chain_config
        assert len(tool.prompts) == 2
        assert tool.flow_control == {"max_steps": 5}

    def test_chain_tool_metadata(self):
        """Test chain tool metadata."""
        chain_config = {
            "name": "test_chain",
            "description": "A test prompt chain",
            "prompts": [],
        }

        tool = PromptChainTool(chain_config)
        metadata = tool.get_metadata()

        assert metadata.name == "test_chain"
        assert metadata.description == "A test prompt chain"
        assert "prompt" in metadata.tags
        assert "chain" in metadata.tags

    @pytest.mark.asyncio
    async def test_chain_execution(self):
        """Test chain execution."""
        chain_config = {
            "name": "test_chain",
            "description": "A test prompt chain",
            "prompts": [
                {
                    "name": "step1",
                    "type": "text",
                    "content": "Step 1: {input}",
                    "output_mapping": {"processed_prompt": "step1_output"},
                },
                {
                    "name": "step2",
                    "type": "text",
                    "content": "Step 2: {step1_output}",
                    "output_mapping": {"processed_prompt": "final_output"},
                },
            ],
        }

        tool = PromptChainTool(chain_config)
        result = await tool.execute(
            {
                "initial_variables": {"input": "test input"},
                "chain_config": {"max_steps": 5},
            }
        )

        assert len(result) == 1
        assert result[0]["type"] == "chain_result"
        assert len(result[0]["steps"]) == 2
        assert result[0]["total_steps"] == 2
        assert "step1_output" in result[0]["final_variables"]
        assert "final_output" in result[0]["final_variables"]


class TestPromptTemplateManager:
    """Test PromptTemplateManager."""

    def test_template_manager_creation(self):
        """Test template manager creation."""
        manager = PromptTemplateManager()
        assert manager.templates == {}

    def test_register_template(self):
        """Test template registration."""
        manager = PromptTemplateManager()
        template = PromptConfig(
            prompt_type=PromptType.TEXT,
            content="Hello {name}!",
            variables={"name": {"type": "string", "required": True}},
            tags=["greeting"],
        )

        manager.register_template("greeting", template)

        assert "greeting" in manager.templates
        assert manager.templates["greeting"] == template

    def test_get_template(self):
        """Test getting a template."""
        manager = PromptTemplateManager()
        template = PromptConfig(prompt_type=PromptType.TEXT, content="Hello {name}!")

        manager.register_template("greeting", template)
        retrieved_template = manager.get_template("greeting")

        assert retrieved_template == template

    def test_get_nonexistent_template(self):
        """Test getting a non-existent template."""
        manager = PromptTemplateManager()

        template = manager.get_template("nonexistent")

        assert template is None

    def test_list_templates(self):
        """Test listing templates."""
        manager = PromptTemplateManager()
        template1 = PromptConfig(prompt_type=PromptType.TEXT, content="Template 1")
        template2 = PromptConfig(prompt_type=PromptType.TEXT, content="Template 2")

        manager.register_template("template1", template1)
        manager.register_template("template2", template2)

        templates = manager.list_templates()

        assert len(templates) == 2
        assert "template1" in templates
        assert "template2" in templates

    def test_create_tool_from_template(self):
        """Test creating a tool from a template."""
        manager = PromptTemplateManager()
        template = PromptConfig(
            prompt_type=PromptType.TEXT,
            content="Hello {name}!",
            variables={"name": {"type": "string", "required": True}},
        )

        manager.register_template("greeting", template)
        tool = manager.create_tool_from_template("greeting")

        assert tool is not None
        assert isinstance(tool, PromptTool)
        assert tool.prompt_config == template

    def test_create_tool_from_nonexistent_template(self):
        """Test creating a tool from a non-existent template."""
        manager = PromptTemplateManager()

        tool = manager.create_tool_from_template("nonexistent")

        assert tool is None

    def test_export_templates(self):
        """Test exporting templates."""
        manager = PromptTemplateManager()
        template = PromptConfig(
            prompt_type=PromptType.TEXT,
            content="Hello {name}!",
            variables={"name": {"type": "string", "required": True}},
            tags=["greeting"],
        )

        manager.register_template("greeting", template)
        exported = manager.export_templates()

        assert "greeting" in exported
        assert exported["greeting"]["prompt_type"] == "text"
        assert exported["greeting"]["content"] == "Hello {name}!"
        assert exported["greeting"]["variables"] == {
            "name": {"type": "string", "required": True}
        }
        assert exported["greeting"]["tags"] == ["greeting"]
