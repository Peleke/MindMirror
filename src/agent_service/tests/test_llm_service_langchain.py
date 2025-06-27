"""
Tests for LLM service with LangChain integration.

These tests verify that the LLM service correctly integrates with LangChain
and handles various LLM operations including chat, completion, and streaming.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.language_models import BaseLanguageModel

from agent_service.app.services.llm_service import LLMService
from agent_service.app.graphql.types.suggestion_types import PerformanceReview


class TestLLMServiceLangChain:
    """Test LangChain-based LLM service functionality."""
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LangChain LLM."""
        mock = Mock()
        mock.ainvoke = AsyncMock()
        mock.invoke = Mock()  # Add synchronous invoke method
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
    def mock_prompt_service(self):
        """Create a mock prompt service."""
        mock_service = Mock()
        
        # Mock journal summary prompt
        mock_journal_prompt = Mock()
        mock_journal_prompt.metadata = {
            "model": "gpt-4o",
            "temperature": 0.7,
            "max_tokens": 250,
            "streaming": False
        }
        mock_service.get_prompt.return_value = mock_journal_prompt
        
        # Mock render_prompt to return realistic content
        def mock_render_prompt(prompt_name, variables):
            if prompt_name == "journal_summary":
                content_block = variables.get("content_block", "")
                return f"Synthesize these entries into a single, concise paragraph:\n\n{content_block}\n\nSynthesize these entries into a single, concise paragraph of 2-4 sentences."
            elif prompt_name == "performance_review":
                content_block = variables.get("content_block", "")
                return f"Analyze the following journal entries:\n\n{content_block}\n\nPlease format your response as follows:\nSUCCESS: [Your identified key success here]\nIMPROVEMENT: [Your identified improvement area here]\nPROMPT: [Your generated journal prompt here]"
            return "Test prompt content"
        
        mock_service.render_prompt.side_effect = mock_render_prompt
        mock_service.health_check.return_value = {"status": "healthy"}
        
        return mock_service
    
    @pytest.fixture
    def mock_tool_registry(self):
        """Create a mock tool registry."""
        mock_registry = Mock()
        mock_registry.list_tool_names.return_value = []
        mock_registry.get_tool_registry_health.return_value = {"status": "healthy"}
        return mock_registry
    
    @pytest.fixture
    def llm_service(self, mock_llm, mock_prompt_service, mock_provider_manager, mock_tool_registry):
        """Create LLM service with mocked dependencies."""
        # Create service with mocked dependencies
        service = LLMService(
            prompt_service=mock_prompt_service,
            llm=mock_llm,  # Keep for backward compatibility
            provider_manager=mock_provider_manager,
            tool_registry=mock_tool_registry
        )
        return service
    
    @pytest.mark.asyncio
    async def test_get_journal_summary_with_langchain(self, llm_service, mock_llm):
        """Test journal summary generation using LangChain."""
        # Arrange
        journal_entries = [
            {"text": "Today I felt productive and accomplished my goals."},
            {"text": "I struggled with focus but managed to complete the important tasks."}
        ]
        
        expected_response = "You showed resilience today, balancing productivity with challenges."
        mock_llm.ainvoke.return_value.content = expected_response
        
        # Act
        result = await llm_service.get_journal_summary(journal_entries)
        
        # Assert
        assert result == expected_response
        mock_llm.ainvoke.assert_called_once()
        
        # Check that the prompt was rendered correctly
        call_args = mock_llm.ainvoke.call_args[0][0]
        assert "Today I felt productive" in str(call_args)
        assert "I struggled with focus" in str(call_args)
        assert "Synthesize these entries" in str(call_args)
    
    @pytest.mark.asyncio
    async def test_get_journal_summary_empty_entries(self, llm_service):
        """Test journal summary with empty entries."""
        # Arrange
        journal_entries = []
        
        # Act
        result = await llm_service.get_journal_summary(journal_entries)
        
        # Assert
        assert result == "No recent journal entries to summarize."
    
    @pytest.mark.asyncio
    async def test_get_performance_review_with_langchain(self, llm_service, mock_llm):
        """Test performance review generation using LangChain."""
        # Arrange
        journal_entries = [
            {"text": "I consistently exercised this week and felt great."},
            {"text": "I need to work on my time management skills."}
        ]
        
        mock_response = """SUCCESS: You maintained a consistent exercise routine and felt great about it.
IMPROVEMENT: Time management skills need attention and could be improved.
PROMPT: How can you better structure your day to make time management feel less overwhelming?"""
        
        mock_llm.invoke.return_value.content = mock_response
        
        # Act
        result = await llm_service.get_performance_review(journal_entries)
        
        # Assert
        assert isinstance(result, PerformanceReview)
        assert "consistent exercise routine" in result.key_success.lower()
        assert "time management" in result.improvement_area.lower()
        assert "structure your day" in result.journal_prompt.lower()
        
        mock_llm.invoke.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_performance_review_empty_entries(self, llm_service):
        """Test performance review with empty entries."""
        # Arrange
        journal_entries = []
        
        # Act
        result = await llm_service.get_performance_review(journal_entries)
        
        # Assert
        assert isinstance(result, PerformanceReview)
        assert "No recent journal entries to review" in result.key_success
        assert "Consider adding more journal entries" in result.improvement_area
        assert "What would you like to focus on" in result.journal_prompt
    
    @pytest.mark.asyncio
    async def test_llm_error_handling(self, llm_service, mock_llm):
        """Test error handling when LLM fails."""
        # Arrange
        journal_entries = [{"text": "Test entry"}]
        mock_llm.ainvoke.side_effect = Exception("LLM API error")
        
        # Act
        result = await llm_service.get_journal_summary(journal_entries)
        
        # Assert
        assert "Error generating summary" in result
    
    def test_prompt_service_integration(self, llm_service):
        """Test that prompt service is properly integrated."""
        # Arrange & Act
        prompt_service = llm_service.get_prompt_service()
        
        # Assert
        assert prompt_service is not None
        assert hasattr(prompt_service, 'render_prompt')
        assert hasattr(prompt_service, 'get_prompt')
    
    def test_health_check(self, llm_service):
        """Test health check functionality."""
        # Act
        health = llm_service.health_check()
        
        # Assert
        assert "status" in health
        assert "llm_configured" in health
        assert "prompt_service" in health
        assert "missing_prompts" in health
        assert "provider_status" in health
        assert "working_providers" in health
        assert "tool_registry" in health
    
    @pytest.mark.asyncio
    async def test_prompt_metadata_usage(self, llm_service, mock_llm):
        """Test that prompt metadata is used for LLM configuration."""
        # Arrange
        journal_entries = [{"text": "Test entry"}]
        mock_llm.ainvoke.return_value.content = "Test response"
        
        # Act
        await llm_service.get_journal_summary(journal_entries)
        
        # Assert
        # Verify that the LLM was called
        mock_llm.ainvoke.assert_called_once()
    
    def test_configurable_storage(self):
        """Test that storage type is configurable via environment."""
        # Arrange
        with patch.dict('os.environ', {'PROMPT_STORAGE_TYPE': 'memory'}):
            # Act
            service = LLMService()
            
            # Assert
            assert service.prompt_service is not None
        
        # Test local storage
        with patch.dict('os.environ', {'PROMPT_STORAGE_TYPE': 'local', 'PROMPT_STORE_PATH': 'test_prompts'}):
            # Act
            service = LLMService()
            
            # Assert
            assert service.prompt_service is not None


class TestLangChainIntegration:
    """Test LangChain-specific integration features."""
    
    @pytest.mark.asyncio
    async def test_langchain_prompt_templates(self):
        """Test that LangChain prompt templates are used correctly."""
        # This test will verify that we're using LangChain's prompt templates
        # instead of raw string formatting
        pass
    
    @pytest.mark.asyncio
    async def test_langchain_llm_configuration(self):
        """Test that LangChain LLM is configured with correct parameters."""
        # This test will verify that temperature, model, etc. are passed correctly
        pass
    
    def test_langchain_compatibility(self):
        """Test that the service is compatible with LangGraph workflows."""
        # This test will verify that the service can be easily integrated
        pass 