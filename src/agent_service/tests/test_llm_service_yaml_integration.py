"""
Tests for LLM service YAML integration.

These tests verify that the LLM service correctly integrates with
YAML-based prompt management and configuration.
"""

import asyncio
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, Mock, patch

import pytest
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import AIMessage, HumanMessage

from agent_service.app.services.llm_service import LLMService
from agent_service.llms.prompts.factory import PromptServiceFactory
from agent_service.llms.prompts.models import PromptConfig, PromptInfo, StoreType
from agent_service.llms.prompts.service import PromptService
from agent_service.llms.prompts.stores.yaml import YAMLPromptStore


class TestLLMServiceYAMLIntegration:
    """Test LLM service integration with YAML templates."""

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

    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM for testing."""
        mock = Mock()
        mock.invoke.return_value.content = "Mock response from LLM"
        mock.ainvoke = AsyncMock()
        mock.ainvoke.return_value.content = "Mock response from LLM"
        return mock

    @pytest.fixture
    def mock_provider_manager(self, mock_llm):
        """Create a mock provider manager."""
        mock_manager = Mock()
        mock_manager.create_model_with_fallback.return_value = mock_llm
        mock_manager.get_working_providers.return_value = ["openai"]
        mock_manager.get_provider_status.return_value = {"openai": "healthy"}
        return mock_manager

    @pytest.fixture
    def mock_tool_registry(self):
        """Create a mock tool registry."""
        mock_registry = Mock()
        mock_registry.list_tool_names.return_value = []
        mock_registry.get_tool_registry_health.return_value = {"status": "healthy"}
        return mock_registry

    @pytest.fixture
    def yaml_prompt_service(self, temp_templates_dir):
        """Create prompt service with YAML storage."""
        config = PromptConfig(
            store_type=StoreType.YAML,
            store_path=temp_templates_dir,
            enable_caching=True,
            cache_size=100,
            cache_ttl=3600,
        )

        store = YAMLPromptStore(temp_templates_dir)
        return PromptService(store=store, config=config)

    @pytest.fixture
    def llm_service_with_yaml(
        self, mock_llm, yaml_prompt_service, mock_provider_manager, mock_tool_registry
    ):
        """Create LLM service with YAML prompt service."""
        return LLMService(
            llm=mock_llm,
            prompt_service=yaml_prompt_service,
            provider_manager=mock_provider_manager,
            tool_registry=mock_tool_registry,
        )

    @pytest.mark.asyncio
    async def test_llm_service_uses_yaml_templates(self, llm_service_with_yaml):
        """Test that LLM service uses YAML templates instead of hardcoded prompts."""
        # Test journal summary generation
        journal_entries = [
            {"text": "Today I felt productive and accomplished my goals."},
            {
                "text": "I struggled with focus but managed to complete the important tasks."
            },
        ]

        result = await llm_service_with_yaml.get_journal_summary(journal_entries)

        # Verify the service used the YAML template
        assert result is not None
        assert "Mock response from LLM" in result

    @pytest.mark.asyncio
    async def test_llm_service_uses_template_metadata(
        self, llm_service_with_yaml, mock_llm
    ):
        """Test that LLM service uses template metadata for configuration."""
        journal_entries = [
            {"text": "Today I felt productive and accomplished my goals."}
        ]

        # Generate summary
        await llm_service_with_yaml.get_journal_summary(journal_entries)

        # Verify the LLM was called with the correct configuration
        mock_llm.ainvoke.assert_called_once()
        call_args = mock_llm.ainvoke.call_args

        # Check that the prompt contains the template content
        # The mock is called with a list of messages, so we need to access the first message
        messages = call_args[0][0]  # First argument is the list of messages
        prompt_content = messages[0].content  # First message in the list
        assert (
            "You are an AI assistant that helps create concise summaries"
            in prompt_content
        )
        assert "Today I felt productive" in prompt_content

    @pytest.mark.asyncio
    async def test_llm_service_performance_review_with_yaml(
        self, llm_service_with_yaml
    ):
        """Test performance review generation with YAML templates."""
        journal_entries = [
            {"text": "This week I improved my time management skills."},
            {"text": "I need to work on my communication with team members."},
        ]

        result = await llm_service_with_yaml.get_performance_review(journal_entries)

        # Verify the service used the YAML template
        assert result is not None
        assert hasattr(result, "key_success")
        assert hasattr(result, "improvement_area")
        assert hasattr(result, "journal_prompt")

    @pytest.mark.asyncio
    async def test_llm_service_handles_empty_entries_with_yaml(
        self, llm_service_with_yaml
    ):
        """Test that LLM service handles empty entries with YAML templates."""
        result = await llm_service_with_yaml.get_journal_summary([])

        # Should return early message for empty entries (correct behavior)
        assert result is not None
        assert "No recent journal entries to summarize" in result

    @pytest.mark.asyncio
    async def test_llm_service_template_rendering(
        self, llm_service_with_yaml, mock_llm
    ):
        """Test that LLM service properly renders YAML templates."""
        journal_entries = [
            {"text": "Entry 1: I learned something new today."},
            {"text": "Entry 2: I struggled with a difficult problem."},
        ]

        # Generate summary
        await llm_service_with_yaml.get_journal_summary(journal_entries)

        # Verify template rendering
        call_args = mock_llm.ainvoke.call_args
        messages = call_args[0][0]  # First argument is the list of messages
        prompt_content = messages[0].content  # First message in the list

        # Check that variables were properly substituted
        assert "Entry 1: I learned something new today." in prompt_content
        assert "Entry 2: I struggled with a difficult problem." in prompt_content
        assert "{{ content_block }}" not in prompt_content  # Should be replaced

    @pytest.mark.asyncio
    async def test_llm_service_template_versioning(self, llm_service_with_yaml):
        """Test that LLM service respects template versioning."""
        # This test verifies that the service can use specific template versions
        # when needed (though by default it uses the latest)
        journal_entries = [{"text": "Test entry"}]

        result = await llm_service_with_yaml.get_journal_summary(journal_entries)
        assert result is not None

    @pytest.mark.asyncio
    async def test_llm_service_fallback_behavior(
        self, mock_llm, mock_provider_manager, mock_tool_registry
    ):
        """Test LLM service fallback behavior when templates are missing."""
        # Create service without templates
        config = PromptConfig(
            store_type=StoreType.MEMORY,
            enable_caching=True,
            cache_size=100,
            cache_ttl=3600,
        )

        from agent_service.llms.prompts.stores.memory import InMemoryPromptStore

        store = InMemoryPromptStore()
        prompt_service = PromptService(store=store, config=config)

        service = LLMService(
            llm=mock_llm,
            prompt_service=prompt_service,
            provider_manager=mock_provider_manager,
            tool_registry=mock_tool_registry,
        )

        # This should handle missing template gracefully by falling back to direct method
        journal_entries = [{"text": "Test entry"}]

        # The service should not raise an exception but should fall back to direct method
        result = await service.get_journal_summary(journal_entries)

        # Should get some result (mock response)
        assert result is not None

    def test_llm_service_health_check_with_yaml(self, llm_service_with_yaml):
        """Test LLM service health check with YAML templates."""
        health = llm_service_with_yaml.health_check()

        assert health["status"] in ["healthy", "degraded"]
        assert "prompt_service" in health
        assert "missing_prompts" in health
        assert "provider_status" in health
        assert "working_providers" in health
        assert "tool_registry" in health


class TestLLMServiceMigration:
    """Test migration from hardcoded prompts to YAML templates."""

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

    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM for testing."""
        mock = Mock()
        mock.invoke.return_value.content = "YAML template response"
        mock.ainvoke = AsyncMock()
        mock.ainvoke.return_value.content = "YAML template response"
        return mock

    @pytest.fixture
    def mock_provider_manager(self, mock_llm):
        """Create a mock provider manager."""
        mock_manager = Mock()
        mock_manager.create_model_with_fallback.return_value = mock_llm
        mock_manager.get_working_providers.return_value = ["openai"]
        mock_manager.get_provider_status.return_value = {"openai": "healthy"}
        return mock_manager

    @pytest.fixture
    def mock_tool_registry(self):
        """Create a mock tool registry."""
        mock_registry = Mock()
        mock_registry.list_tool_names.return_value = []
        mock_registry.get_tool_registry_health.return_value = {"status": "healthy"}
        return mock_registry

    @pytest.mark.asyncio
    async def test_migration_from_hardcoded_to_yaml(
        self, temp_templates_dir, mock_llm, mock_provider_manager, mock_tool_registry
    ):
        """Test migration from hardcoded prompts to YAML templates."""
        # Create YAML-based service
        yaml_config = PromptConfig(
            store_type=StoreType.YAML,
            store_path=temp_templates_dir,
            enable_caching=True,
            cache_size=100,
            cache_ttl=3600,
        )

        yaml_store = YAMLPromptStore(temp_templates_dir)
        yaml_service = PromptService(store=yaml_store, config=yaml_config)

        llm_service = LLMService(
            llm=mock_llm,
            prompt_service=yaml_service,
            provider_manager=mock_provider_manager,
            tool_registry=mock_tool_registry,
        )

        # Test with sample data
        journal_entries = [{"text": "Migration test entry"}]

        result = await llm_service.get_journal_summary(journal_entries)

        # Verify YAML template was used
        assert result == "YAML template response"

    @pytest.mark.asyncio
    async def test_backward_compatibility(
        self, temp_templates_dir, mock_llm, mock_provider_manager, mock_tool_registry
    ):
        """Test that migration maintains backward compatibility."""
        # Test both old and new services produce results
        yaml_config = PromptConfig(
            store_type=StoreType.YAML,
            store_path=temp_templates_dir,
            enable_caching=True,
            cache_size=100,
            cache_ttl=3600,
        )

        yaml_store = YAMLPromptStore(temp_templates_dir)
        yaml_service = PromptService(store=yaml_store, config=yaml_config)

        llm_service = LLMService(
            llm=mock_llm,
            prompt_service=yaml_service,
            provider_manager=mock_provider_manager,
            tool_registry=mock_tool_registry,
        )

        journal_entries = [{"text": "Backward compatibility test"}]

        result = await llm_service.get_journal_summary(journal_entries)
        assert result is not None

    @pytest.mark.asyncio
    async def test_template_metadata_integration(
        self, temp_templates_dir, mock_llm, mock_provider_manager, mock_tool_registry
    ):
        """Test that template metadata is properly integrated."""
        yaml_config = PromptConfig(
            store_type=StoreType.YAML,
            store_path=temp_templates_dir,
            enable_caching=True,
            cache_size=100,
            cache_ttl=3600,
        )

        yaml_store = YAMLPromptStore(temp_templates_dir)
        yaml_service = PromptService(store=yaml_store, config=yaml_config)

        llm_service = LLMService(
            llm=mock_llm,
            prompt_service=yaml_service,
            provider_manager=mock_provider_manager,
            tool_registry=mock_tool_registry,
        )

        # Get the template directly to verify metadata
        prompt_info = yaml_service.get_prompt("journal_summary")

        # Verify metadata structure (adjusted for actual template format)
        assert prompt_info.metadata["temperature"] == 0.7
        assert prompt_info.metadata["max_tokens"] == 500
        assert prompt_info.metadata["streaming"] is False

        # Test that service uses metadata
        journal_entries = [{"text": "Metadata test"}]
        result = await llm_service.get_journal_summary(journal_entries)
        assert result is not None
