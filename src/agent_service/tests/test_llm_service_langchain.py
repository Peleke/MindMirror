"""
Tests for LangChain-based LLM service.

This module tests the LLM service using LangChain instead of litellm
for better integration with LangGraph workflows.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any

from agent_service.services.llm_service import LLMService
from agent_service.api.types.suggestion_types import PerformanceReview


class TestLLMServiceLangChain:
    """Test LangChain-based LLM service functionality."""
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LangChain LLM."""
        mock = Mock()
        mock.ainvoke = AsyncMock()
        return mock
    
    @pytest.fixture
    def llm_service(self, mock_llm):
        """Create LLM service with mock LLM."""
        # Pass the mock LLM directly to the service constructor
        service = LLMService(llm=mock_llm)
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
    async def test_generate_performance_review_with_langchain(self, llm_service, mock_llm):
        """Test performance review generation using LangChain."""
        # Arrange
        journal_entries = [
            {"text": "I consistently exercised this week and felt great."},
            {"text": "I need to work on my time management skills."}
        ]
        
        mock_response = """SUCCESS: You maintained a consistent exercise routine and felt great about it.
IMPROVEMENT: Time management skills need attention and could be improved.
PROMPT: How can you better structure your day to make time management feel less overwhelming?"""
        
        mock_llm.ainvoke.return_value.content = mock_response
        
        # Act
        result = await llm_service.generate_performance_review(journal_entries)
        
        # Assert
        assert isinstance(result, PerformanceReview)
        assert "consistent exercise routine" in result.key_success.lower()
        assert "time management" in result.improvement_area.lower()
        assert "structure your day" in result.journal_prompt.lower()
        
        mock_llm.ainvoke.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_performance_review_empty_entries(self, llm_service):
        """Test performance review with empty entries."""
        # Arrange
        journal_entries = []
        
        # Act
        result = await llm_service.generate_performance_review(journal_entries)
        
        # Assert
        assert isinstance(result, PerformanceReview)
        assert "No recent journal entries found" in result.key_success
        assert "Try to journal more consistently" in result.improvement_area
        assert "small step you can take today" in result.journal_prompt
    
    @pytest.mark.asyncio
    async def test_llm_error_handling(self, llm_service, mock_llm):
        """Test error handling when LLM fails."""
        # Arrange
        journal_entries = [{"text": "Test entry"}]
        mock_llm.ainvoke.side_effect = Exception("LLM API error")
        
        # Act
        result = await llm_service.get_journal_summary(journal_entries)
        
        # Assert
        assert "I am having trouble summarizing" in result
    
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
        assert "journal_summary_prompt_available" in health
        assert "performance_review_prompt_available" in health
        assert "prompt_service_health" in health
    
    @pytest.mark.asyncio
    async def test_prompt_metadata_usage(self, llm_service, mock_llm):
        """Test that prompt metadata is used for LLM configuration."""
        # Arrange
        journal_entries = [{"text": "Test entry"}]
        mock_llm.ainvoke.return_value.content = "Test response"
        
        # Act
        await llm_service.get_journal_summary(journal_entries)
        
        # Assert
        # Verify that the LLM was configured with metadata from the prompt
        # This will be checked in the actual implementation
        mock_llm.ainvoke.assert_called_once()
    
    def test_configurable_storage(self):
        """Test that storage type is configurable via environment."""
        # Arrange
        with patch.dict('os.environ', {'PROMPT_STORE_TYPE': 'memory'}):
            # Act
            service = LLMService()
            
            # Assert
            assert service.prompt_service is not None
        
        # Test local storage
        with patch.dict('os.environ', {'PROMPT_STORE_TYPE': 'local', 'PROMPT_STORE_PATH': 'test_prompts'}):
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
        # into LangGraph agent workflows
        pass 