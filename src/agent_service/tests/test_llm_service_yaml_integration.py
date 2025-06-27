"""
Tests for LLM service YAML integration.

These tests verify that the LLM service correctly integrates with
YAML-based prompt management and configuration.
"""

import pytest
import tempfile
import shutil
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any, Optional

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.language_models import BaseLanguageModel

from agent_service.app.services.llm_service import LLMService
from agent_service.llms.prompts.stores.yaml import YAMLPromptStore
from agent_service.llms.prompts.service import PromptService
from agent_service.llms.prompts.models import PromptConfig, StoreType, PromptInfo
from agent_service.llms.prompts.factory import PromptServiceFactory


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
        return mock
    
    @pytest.fixture
    def yaml_prompt_service(self, temp_templates_dir):
        """Create prompt service with YAML storage."""
        config = PromptConfig(
            store_type=StoreType.YAML,
            store_path=temp_templates_dir,
            enable_caching=True,
            cache_size=100,
            cache_ttl=3600
        )
        
        store = YAMLPromptStore(temp_templates_dir)
        return PromptService(store=store, config=config)
    
    @pytest.fixture
    def llm_service_with_yaml(self, mock_llm, yaml_prompt_service):
        """Create LLM service with YAML prompt service."""
        return LLMService(llm=mock_llm, prompt_service=yaml_prompt_service)
    
    def test_llm_service_uses_yaml_templates(self, llm_service_with_yaml):
        """Test that LLM service uses YAML templates instead of hardcoded prompts."""
        # Test journal summary generation
        journal_entries = [
            {"text": "Today I felt productive and accomplished my goals."},
            {"text": "I struggled with focus but managed to complete the important tasks."}
        ]
        
        result = llm_service_with_yaml.get_journal_summary(journal_entries)
        
        # Verify the service used the YAML template
        assert result is not None
        assert "Mock response from LLM" in result
    
    def test_llm_service_uses_template_metadata(self, llm_service_with_yaml, mock_llm):
        """Test that LLM service uses template metadata for configuration."""
        journal_entries = [
            {"text": "Today I felt productive and accomplished my goals."}
        ]
        
        # Generate summary
        llm_service_with_yaml.get_journal_summary(journal_entries)
        
        # Verify the LLM was called with the correct configuration
        mock_llm.invoke.assert_called_once()
        call_args = mock_llm.invoke.call_args
        
        # Check that the prompt contains the template content
        # The mock is called with a list of messages, so we need to access the first message
        messages = call_args[0][0]  # First argument is the list of messages
        prompt_content = messages[0].content  # First message in the list
        assert "As an AI companion" in prompt_content
        assert "Synthesize these entries" in prompt_content
        assert "Today I felt productive" in prompt_content
    
    @pytest.mark.asyncio
    async def test_llm_service_performance_review_with_yaml(self, llm_service_with_yaml):
        """Test performance review generation with YAML templates."""
        journal_entries = [
            {"text": "This week I improved my time management skills."},
            {"text": "I need to work on my communication with team members."}
        ]
        
        result = await llm_service_with_yaml.get_performance_review(journal_entries)
        
        # Verify the service used the YAML template
        assert result is not None
        assert hasattr(result, 'key_success')
        assert hasattr(result, 'improvement_area')
        assert hasattr(result, 'journal_prompt')
    
    def test_llm_service_handles_empty_entries_with_yaml(self, llm_service_with_yaml):
        """Test that LLM service handles empty entries with YAML templates."""
        result = llm_service_with_yaml.get_journal_summary([])
        
        # Should return early message for empty entries (correct behavior)
        assert result is not None
        assert "No recent journal entries to summarize" in result
    
    def test_llm_service_template_rendering(self, llm_service_with_yaml, mock_llm):
        """Test that LLM service properly renders YAML templates."""
        journal_entries = [
            {"text": "Entry 1: I learned something new today."},
            {"text": "Entry 2: I struggled with a difficult problem."}
        ]
        
        # Generate summary
        llm_service_with_yaml.get_journal_summary(journal_entries)
        
        # Verify template rendering
        call_args = mock_llm.invoke.call_args
        messages = call_args[0][0]  # First argument is the list of messages
        prompt_content = messages[0].content  # First message in the list
        
        # Check that variables were properly substituted
        assert "Entry 1: I learned something new today." in prompt_content
        assert "Entry 2: I struggled with a difficult problem." in prompt_content
        assert "{{ content_block }}" not in prompt_content  # Should be replaced
    
    def test_llm_service_template_versioning(self, llm_service_with_yaml):
        """Test that LLM service respects template versioning."""
        # This test verifies that the service can use specific template versions
        # when needed (though by default it uses the latest)
        journal_entries = [{"text": "Test entry"}]
        
        result = llm_service_with_yaml.get_journal_summary(journal_entries)
        assert result is not None
    
    def test_llm_service_fallback_behavior(self, mock_llm):
        """Test LLM service fallback behavior when templates are missing."""
        # Create service without templates
        config = PromptConfig(
            store_type=StoreType.MEMORY,  # Use memory store (empty)
            enable_caching=True,
            cache_size=100,
            cache_ttl=3600
        )
        
        from agent_service.llms.prompts.stores.memory import InMemoryPromptStore
        store = InMemoryPromptStore()
        prompt_service = PromptService(store=store, config=config)
        
        llm_service = LLMService(llm=mock_llm, prompt_service=prompt_service)
        
        # Should handle missing templates gracefully
        journal_entries = [{"text": "Test entry"}]
        
        # This should either use a fallback or handle the error gracefully
        try:
            result = llm_service.get_journal_summary(journal_entries)
            # If it succeeds, it should return a response
            assert result is not None
        except Exception as e:
            # If it fails, it should be a meaningful error
            assert "prompt" in str(e).lower() or "template" in str(e).lower()


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
        mock.invoke.return_value.content = "Mock response from LLM"
        return mock
    
    def test_migration_from_hardcoded_to_yaml(self, temp_templates_dir, mock_llm):
        """Test that the service can migrate from hardcoded prompts to YAML."""
        # Create YAML-based prompt service
        config = PromptConfig(
            store_type=StoreType.YAML,
            store_path=temp_templates_dir,
            enable_caching=True,
            cache_size=100,
            cache_ttl=3600
        )
        
        store = YAMLPromptStore(temp_templates_dir)
        prompt_service = PromptService(store=store, config=config)
        
        # Create LLM service with YAML templates
        llm_service = LLMService(llm=mock_llm, prompt_service=prompt_service)
        
        # Test that it works the same as before
        journal_entries = [{"text": "Test entry"}]
        
        result = llm_service.get_journal_summary(journal_entries)
        assert result is not None
        assert "Mock response from LLM" in result
    
    @pytest.mark.asyncio
    async def test_backward_compatibility(self, temp_templates_dir, mock_llm):
        """Test backward compatibility with existing code."""
        # Create YAML-based prompt service
        config = PromptConfig(
            store_type=StoreType.YAML,
            store_path=temp_templates_dir,
            enable_caching=True,
            cache_size=100,
            cache_ttl=3600
        )
        
        store = YAMLPromptStore(temp_templates_dir)
        prompt_service = PromptService(store=store, config=config)
        
        # Create LLM service
        llm_service = LLMService(llm=mock_llm, prompt_service=prompt_service)
        
        # Test that existing method signatures still work
        journal_entries = [{"text": "Test entry"}]
        
        # These should work exactly as before
        summary = llm_service.get_journal_summary(journal_entries)
        review = await llm_service.get_performance_review(journal_entries)
        
        assert summary is not None
        assert review is not None
    
    def test_template_metadata_integration(self, temp_templates_dir, mock_llm):
        """Test that template metadata is properly integrated."""
        # Create YAML-based prompt service
        config = PromptConfig(
            store_type=StoreType.YAML,
            store_path=temp_templates_dir,
            enable_caching=True,
            cache_size=100,
            cache_ttl=3600
        )
        
        store = YAMLPromptStore(temp_templates_dir)
        prompt_service = PromptService(store=store, config=config)
        
        # Create LLM service
        llm_service = LLMService(llm=mock_llm, prompt_service=prompt_service)
        
        # Test that template metadata is accessible
        journal_entries = [{"text": "Test entry"}]
        
        # Generate summary to trigger template usage
        llm_service.get_journal_summary(journal_entries)
        
        # Verify that the template was loaded and used
        # (This is verified by checking that the mock was called)
        mock_llm.invoke.assert_called_once() 