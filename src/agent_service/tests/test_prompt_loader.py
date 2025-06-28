"""
Tests for prompt template loading functionality.

These tests verify that the prompt loader correctly loads Jinja2 templates,
handles template rendering, and provides proper error handling.
"""

import os
from pathlib import Path
from typing import Any, Dict
from unittest.mock import Mock, mock_open, patch

import pytest

from agent_service.llms.prompts.loader import PromptLoader, TemplateError


@pytest.fixture(autouse=True)
def mock_langsmith_client():
    """Mock LangSmith client for all tests."""
    mock_client = Mock()
    mock_trace = Mock()
    mock_trace.__enter__ = Mock(return_value=mock_trace)
    mock_trace.__exit__ = Mock(return_value=None)
    mock_trace.add_metadata = Mock()
    mock_client.trace.return_value = mock_trace

    with patch("langsmith.Client", return_value=mock_client):
        yield mock_client


class TestPromptLoader:
    """Test prompt loader functionality."""

    def test_prompt_loader_initialization(self):
        """Test that prompt loader initializes correctly."""
        loader = PromptLoader()
        assert loader.template_dir is None
        assert loader.templates == {}

    def test_prompt_loader_with_template_dir(self):
        """Test that prompt loader works with template directory."""
        template_dir = Path("/tmp/prompts")
        loader = PromptLoader(template_dir=template_dir)
        assert loader.template_dir == template_dir

    def test_load_template_from_string(self):
        """Test loading template from string."""
        loader = PromptLoader()
        template_content = "Hello {{ name }}, how are you?"

        template = loader.load_template_from_string(template_content)

        assert template is not None
        result = template.render(name="World")
        assert result == "Hello World, how are you?"

    def test_load_template_from_string_with_variables(self):
        """Test loading template with multiple variables."""
        loader = PromptLoader()
        template_content = "{{ greeting }} {{ name }}! You have {{ count }} messages."

        template = loader.load_template_from_string(template_content)

        result = template.render(greeting="Hello", name="Alice", count=5)
        assert result == "Hello Alice! You have 5 messages."

    def test_load_template_from_string_with_conditionals(self):
        """Test loading template with Jinja2 conditionals."""
        loader = PromptLoader()
        template_content = """
        {% if user_type == "premium" %}
        Welcome back, {{ name }}! You have premium access.
        {% else %}
        Welcome, {{ name }}! Consider upgrading for premium features.
        {% endif %}
        """

        template = loader.load_template_from_string(template_content)

        # Test premium user
        result = template.render(name="Alice", user_type="premium")
        assert "premium access" in result
        assert "upgrading" not in result

        # Test regular user
        result = template.render(name="Bob", user_type="regular")
        assert "upgrading" in result
        assert "premium access" not in result

    def test_load_template_from_string_with_loops(self):
        """Test loading template with Jinja2 loops."""
        loader = PromptLoader()
        template_content = """
        Available items:
        {% for item in items %}
        - {{ item.name }}: {{ item.price }}
        {% endfor %}
        """

        template = loader.load_template_from_string(template_content)

        items = [{"name": "Apple", "price": "$1"}, {"name": "Banana", "price": "$0.50"}]

        result = template.render(items=items)
        assert "Apple: $1" in result
        assert "Banana: $0.50" in result

    def test_load_template_from_string_invalid_syntax(self):
        """Test that invalid template syntax raises error."""
        loader = PromptLoader()
        invalid_template = "Hello {{ name }}, how are you? {% if %} invalid syntax"

        with pytest.raises(TemplateError, match="Template syntax error"):
            loader.load_template_from_string(invalid_template)

    def test_load_template_from_file(self):
        """Test loading template from file."""
        template_content = "Hello {{ name }}!"

        with patch("builtins.open", mock_open(read_data=template_content)):
            loader = PromptLoader()
            template = loader.load_template_from_file("test.j2")

            assert template is not None
            result = template.render(name="World")
            assert result == "Hello World!"

    def test_load_template_from_file_not_found(self):
        """Test that missing file raises error."""
        with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
            loader = PromptLoader()

            with pytest.raises(TemplateError, match="Template file not found"):
                loader.load_template_from_file("missing.j2")

    def test_load_template_from_file_read_error(self):
        """Test that file read errors are handled."""
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            loader = PromptLoader()

            with pytest.raises(TemplateError, match="Error reading template file"):
                loader.load_template_from_file("test.j2")

    def test_load_templates_from_directory(self):
        """Test loading multiple templates from directory."""
        templates = {
            "greeting.j2": "Hello {{ name }}!",
            "farewell.j2": "Goodbye {{ name }}!",
            "welcome.j2": "Welcome {{ name }} to {{ service }}!",
        }

        # Create mock file paths
        mock_files = []
        for filename in templates.keys():
            mock_file = Mock()
            mock_file.name = filename
            mock_file.suffix = ".j2"
            mock_file.stem = filename.replace(".j2", "")
            mock_file.__str__ = lambda self, filename=filename: filename
            mock_files.append(mock_file)

        with patch("pathlib.Path.iterdir") as mock_iterdir:
            mock_iterdir.return_value = mock_files

            with patch("builtins.open") as mock_open:

                def mock_file_side_effect(filename, *args, **kwargs):
                    if filename in templates:
                        # Create a mock file object that supports context manager protocol
                        mock_file_obj = Mock()
                        mock_file_obj.read.return_value = templates[filename]
                        mock_file_obj.__enter__ = Mock(return_value=mock_file_obj)
                        mock_file_obj.__exit__ = Mock(return_value=None)
                        return mock_file_obj
                    else:
                        raise FileNotFoundError()

                mock_open.side_effect = mock_file_side_effect

                loader = PromptLoader()
                result = loader.load_templates_from_directory(Path("/tmp/prompts"))

                # Verify templates were loaded
                assert "greeting" in result
                assert "farewell" in result
                assert "welcome" in result
                assert "greeting" in loader.templates
                assert "farewell" in loader.templates
                assert "welcome" in loader.templates

    def test_get_template(self):
        """Test getting template by name."""
        loader = PromptLoader()
        template_content = "Hello {{ name }}!"
        loader.templates["greeting"] = loader.load_template_from_string(
            template_content
        )

        template = loader.get_template("greeting")

        assert template is not None
        result = template.render(name="World")
        assert result == "Hello World!"

    def test_get_template_not_found(self):
        """Test that getting non-existent template raises error."""
        loader = PromptLoader()

        with pytest.raises(TemplateError, match="Template 'missing' not found"):
            loader.get_template("missing")

    def test_render_template(self):
        """Test rendering template with variables."""
        loader = PromptLoader()
        template_content = "Hello {{ name }}! You have {{ count }} messages."
        loader.templates["greeting"] = loader.load_template_from_string(
            template_content
        )

        result = loader.render_template("greeting", name="Alice", count=3)

        assert result == "Hello Alice! You have 3 messages."

    def test_render_template_missing_variables(self):
        """Test that missing variables are handled gracefully."""
        loader = PromptLoader()
        template_content = "Hello {{ name }}! You have {{ count }} messages."
        loader.templates["greeting"] = loader.load_template_from_string(
            template_content
        )

        # Should handle missing variables gracefully
        result = loader.render_template("greeting", name="Alice")

        assert "Hello Alice!" in result
        assert "You have  messages." in result  # count is empty

    def test_render_template_with_defaults(self):
        """Test rendering template with default values."""
        loader = PromptLoader()
        template_content = "Hello {{ name | default('User') }}! You have {{ count | default(0) }} messages."
        loader.templates["greeting"] = loader.load_template_from_string(
            template_content
        )

        result = loader.render_template("greeting")

        assert result == "Hello User! You have 0 messages."

    def test_template_caching(self):
        """Test that templates are cached after loading."""
        loader = PromptLoader()
        template_content = "Hello {{ name }}!"

        # Load template first time
        template1 = loader.load_template_from_string(template_content)

        # Load same template second time
        template2 = loader.load_template_from_string(template_content)

        # Should be the same template object (cached)
        assert template1 is template2

    def test_template_validation(self):
        """Test template validation functionality."""
        loader = PromptLoader()

        # Valid template
        valid_template = "Hello {{ name }}!"
        assert loader.validate_template(valid_template) is True

        # Invalid template
        invalid_template = "Hello {{ name }}, {% if %} invalid"
        assert loader.validate_template(invalid_template) is False

    def test_template_variables_extraction(self):
        """Test extracting variables from template."""
        loader = PromptLoader()
        template_content = (
            "Hello {{ name }}! You have {{ count }} messages from {{ sender }}."
        )

        variables = loader.extract_template_variables(template_content)

        assert "name" in variables
        assert "count" in variables
        assert "sender" in variables
        assert len(variables) == 3


class TestPromptLoaderIntegration:
    """Integration tests for prompt loader."""

    def test_load_and_render_complex_template(self):
        """Test loading and rendering a complex template."""
        loader = PromptLoader()
        template_content = """
        {% if user_type == "premium" %}
        Welcome back, {{ name }}! You have premium access.
        {% else %}
        Welcome, {{ name }}! Consider upgrading for premium features.
        {% endif %}
        
        Your recent activity:
        {% for activity in activities %}
        - {{ activity.type }}: {{ activity.description }}
        {% endfor %}
        
        {% if activities | length == 0 %}
        No recent activity.
        {% endif %}
        """

        template = loader.load_template_from_string(template_content)

        # Test with premium user and activities
        result = template.render(
            name="Alice",
            user_type="premium",
            activities=[
                {"type": "Login", "description": "Logged in at 9:00 AM"},
                {"type": "Search", "description": "Searched for 'coaching tips'"},
            ],
        )

        assert "premium access" in result
        assert "Logged in at 9:00 AM" in result
        assert "Searched for 'coaching tips'" in result

        # Test with regular user and no activities
        result = template.render(name="Bob", user_type="regular", activities=[])

        assert "upgrading" in result
        assert "No recent activity" in result

    def test_template_with_filters(self):
        """Test template with Jinja2 filters."""
        loader = PromptLoader()
        template_content = """
        User: {{ name | title }}
        Message: {{ message | truncate(50) }}
        Date: {{ date }}
        Count: {{ items | length }} items
        """

        template = loader.load_template_from_string(template_content)

        result = template.render(
            name="john doe",
            message="This is a very long message that should be truncated to fifty characters maximum",
            date="2024-01-15",
            items=["item1", "item2", "item3"],
        )

        assert "John Doe" in result
        # Check that the message was truncated (should end with "...")
        assert "..." in result
        assert "2024-01-15" in result
        assert "3 items" in result


class TestTemplateError:
    """Test template error handling."""

    def test_template_error_creation(self):
        """Test creating template errors."""
        error = TemplateError("Test error message")
        assert str(error) == "Test error message"

    def test_template_error_with_details(self):
        """Test template error with additional details."""
        error = TemplateError("Template error", details={"line": 5, "column": 10})
        assert "Template error" in str(error)
        assert error.details["line"] == 5
        assert error.details["column"] == 10
