"""
Tests for YAML prompt templates.

This module tests the loading and usage of YAML prompt templates
from the templates directory.
"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest

from agent_service.llms.prompts.models import PromptConfig, StoreType
from agent_service.llms.prompts.service import PromptService
from agent_service.llms.prompts.stores.yaml import YAMLPromptStore


class TestYAMLTemplates:
    """Test YAML prompt templates loading and usage."""

    @pytest.fixture
    def templates_dir(self):
        """Get the templates directory path."""
        return Path(__file__).parent.parent / "llms" / "prompts" / "templates"

    @pytest.fixture
    def temp_templates_dir(self):
        """Create a temporary directory with copied templates."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy templates to temp directory
            source_dir = Path(__file__).parent.parent / "llms" / "prompts" / "templates"
            if source_dir.exists():
                for template_file in source_dir.glob("*.yaml"):
                    shutil.copy2(template_file, temp_dir)
            yield temp_dir

    def test_templates_directory_exists(self, templates_dir):
        """Test that the templates directory exists."""
        assert templates_dir.exists(), f"Templates directory not found: {templates_dir}"
        assert (
            templates_dir.is_dir()
        ), f"Templates path is not a directory: {templates_dir}"

    def test_required_templates_exist(self, templates_dir):
        """Test that required template files exist."""
        required_templates = ["journal_summary_1.0.yaml", "performance_review_1.0.yaml"]

        for template in required_templates:
            template_path = templates_dir / template
            assert template_path.exists(), f"Required template not found: {template}"

    def test_journal_summary_template_structure(self, templates_dir):
        """Test journal summary template structure."""
        template_path = templates_dir / "journal_summary_1.0.yaml"

        # Load the template
        store = YAMLPromptStore(str(templates_dir))
        prompt_info = store.get_prompt("journal_summary", "1.0")

        # Verify structure
        assert prompt_info.name == "journal_summary"
        assert prompt_info.version == "1.0"
        assert "content_block" in prompt_info.variables
        assert (
            prompt_info.metadata.get("description")
            == "Generate a concise summary from journal entries"
        )
        assert prompt_info.metadata.get("temperature") == 0.7

    def test_performance_review_template_structure(self, templates_dir):
        """Test performance review template structure."""
        template_path = templates_dir / "performance_review_1.0.yaml"

        # Load the template
        store = YAMLPromptStore(str(templates_dir))
        prompt_info = store.get_prompt("performance_review", "1.0")

        # Verify structure
        assert prompt_info.name == "performance_review"
        assert prompt_info.version == "1.0"
        assert "content_block" in prompt_info.variables
        assert (
            prompt_info.metadata.get("description")
            == "Generate a performance review from journal entries"
        )
        assert prompt_info.metadata.get("temperature") == 0.7

    def test_template_rendering(self, temp_templates_dir):
        """Test that templates can be rendered correctly."""
        # Create prompt service with templates
        config = PromptConfig(
            store_type=StoreType.YAML,
            store_path=temp_templates_dir,
            enable_caching=True,
            cache_size=100,
            cache_ttl=3600,
        )

        store = YAMLPromptStore(temp_templates_dir)
        service = PromptService(store=store, config=config)

        # Test journal summary rendering
        journal_entries = [
            {"text": "Today I felt productive and accomplished my goals."},
            {
                "text": "I struggled with focus but managed to complete the important tasks."
            },
        ]

        content_block = "\n\n---\n\n".join([entry["text"] for entry in journal_entries])

        rendered = service.render_prompt(
            "journal_summary", {"content_block": content_block, "style": "concise"}
        )

        assert "Today I felt productive" in rendered
        assert "I struggled with focus" in rendered
        assert "You are an AI assistant that helps create concise summaries" in rendered

    def test_template_metadata_usage(self, temp_templates_dir):
        """Test that template metadata is accessible."""
        store = YAMLPromptStore(temp_templates_dir)

        # Get journal summary prompt
        prompt_info = store.get_prompt("journal_summary", "1.0")

        # Verify metadata (updated to match actual template structure)
        metadata = prompt_info.metadata
        assert metadata["temperature"] == 0.7
        assert metadata["max_tokens"] == 500
        assert metadata["streaming"] is False
        assert (
            metadata["description"] == "Generate a concise summary from journal entries"
        )

    def test_template_versioning(self, temp_templates_dir):
        """Test template versioning support."""
        store = YAMLPromptStore(temp_templates_dir)

        # List available versions
        versions = store.list_versions("journal_summary")
        assert "1.0" in versions

        # Get latest version
        latest = store.get_latest_version("journal_summary")
        assert latest == "1.0"

    def test_template_health_check(self, temp_templates_dir):
        """Test template store health check."""
        store = YAMLPromptStore(temp_templates_dir)

        health = store.health_check()
        assert health["status"] == "healthy"
        assert health["writable"] is True
        assert health["yaml_file_count"] >= 2  # At least our two templates


class TestTemplateIntegration:
    """Test integration of templates with the prompt system."""

    @pytest.fixture
    def temp_templates_dir(self):
        """Create a temporary directory with copied templates."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy templates to temp directory
            source_dir = Path(__file__).parent.parent / "llms" / "prompts" / "templates"
            if source_dir.exists():
                for template_file in source_dir.glob("*.yaml"):
                    shutil.copy2(template_file, temp_dir)
            yield temp_dir

    def test_service_with_templates(self, temp_templates_dir):
        """Test prompt service with YAML templates."""
        config = PromptConfig(
            store_type=StoreType.YAML,
            store_path=temp_templates_dir,
            enable_caching=True,
            cache_size=100,
            cache_ttl=3600,
        )

        store = YAMLPromptStore(temp_templates_dir)
        service = PromptService(store=store, config=config)

        # Verify templates are loaded
        prompts = service.list_prompts()
        assert len(prompts) >= 2

        prompt_names = [p.name for p in prompts]
        assert "journal_summary" in prompt_names
        assert "performance_review" in prompt_names

    def test_template_variable_extraction(self, temp_templates_dir):
        """Test that template variables are correctly extracted."""
        store = YAMLPromptStore(temp_templates_dir)

        # Get journal summary prompt
        prompt_info = store.get_prompt("journal_summary", "1.0")

        # Verify variables (updated to match actual template)
        assert "content_block" in prompt_info.variables
        assert "style" in prompt_info.variables
        assert len(prompt_info.variables) == 2

    def test_template_content_validation(self, temp_templates_dir):
        """Test that template content contains expected patterns."""
        store = YAMLPromptStore(temp_templates_dir)

        # Get journal summary prompt
        prompt_info = store.get_prompt("journal_summary", "1.0")

        # Verify content contains template variables and expected text
        content = prompt_info.content
        assert "{{content_block}}" in content
        assert "{{style}}" in content
        assert (
            "You are an AI assistant that helps create concise summaries of journal entries"
            in content
        )
