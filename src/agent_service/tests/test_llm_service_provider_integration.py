"""
Tests for LLM service provider integration.

These tests verify that the LLM service correctly integrates with
different LLM providers and handles fallbacks gracefully.
"""

from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, Mock, patch

import pytest
from langchain_community.llms import Ollama
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from agent_service.app.graphql.types.suggestion_types import PerformanceReview
from agent_service.app.services.llm_service import LLMService
from agent_service.llms.prompts.service import PromptService
from agent_service.llms.provider_manager import ProviderManager


@pytest.fixture(scope="function")
def mock_prompt_service():
    """Create a mock prompt service."""
    mock_service = Mock(spec=PromptService)

    # Mock journal summary prompt
    mock_journal_prompt = Mock()
    mock_journal_prompt.metadata = {
        "model": "gpt-4o",
        "temperature": 0.7,
        "max_tokens": 250,
        "streaming": False,
    }
    mock_service.get_prompt.return_value = mock_journal_prompt
    mock_service.render_prompt.return_value = "Test prompt content"
    mock_service.health_check.return_value = {"status": "healthy"}

    return mock_service


@pytest.fixture(scope="function")
def mock_provider_manager():
    """Create a mock provider manager."""
    mock_manager = Mock(spec=ProviderManager)

    # Mock LLM instance
    mock_llm = Mock()
    mock_llm.ainvoke = AsyncMock(return_value=Mock(content="Test response"))
    mock_llm.invoke = Mock(return_value=Mock(content="Test response"))

    mock_manager.create_model_with_fallback.return_value = mock_llm
    mock_manager.create_model.return_value = mock_llm
    mock_manager.get_provider_status.return_value = {
        "openai": {"status": "healthy"},
        "ollama": {"status": "healthy"},
    }
    mock_manager.list_available_providers.return_value = ["openai", "ollama", "gemini"]
    mock_manager.get_working_providers.return_value = ["openai", "ollama"]

    return mock_manager


class TestLLMServiceProviderIntegration:
    """Test cases for LLMService provider integration."""

    def test_llm_service_initialization_with_provider_manager(
        self, mock_prompt_service, mock_provider_manager
    ):
        """Test LLMService initialization with provider manager."""
        service = LLMService(
            prompt_service=mock_prompt_service, provider_manager=mock_provider_manager
        )

        assert service.prompt_service == mock_prompt_service
        assert service.provider_manager == mock_provider_manager
        assert service.llm is None  # Should be None when using provider manager

    def test_llm_service_initialization_without_provider_manager(
        self, mock_prompt_service
    ):
        """Test LLMService initialization without provider manager (uses global)."""
        with patch(
            "agent_service.app.services.llm_service.get_provider_manager"
        ) as mock_get:
            mock_manager = Mock(spec=ProviderManager)
            mock_get.return_value = mock_manager

            service = LLMService(prompt_service=mock_prompt_service)

            assert service.prompt_service == mock_prompt_service
            assert service.provider_manager == mock_manager
            mock_get.assert_called_once()

    def test_llm_service_backward_compatibility(self, mock_prompt_service):
        """Test LLMService backward compatibility with old constructor."""
        mock_llm = Mock()

        service = LLMService(
            prompt_service=mock_prompt_service,
            llm=mock_llm,  # DEPRECATED but should still work
        )

        assert service.prompt_service == mock_prompt_service
        assert service.llm == mock_llm  # DEPRECATED field should still be set
        assert (
            service.provider_manager is not None
        )  # Should get global provider manager

    @pytest.mark.asyncio
    async def test_get_journal_summary_with_provider_manager(
        self, mock_prompt_service, mock_provider_manager
    ):
        """Test journal summary generation using provider manager."""
        service = LLMService(
            prompt_service=mock_prompt_service, provider_manager=mock_provider_manager
        )

        journal_entries = [{"text": "Test journal entry"}]

        result = await service.get_journal_summary(journal_entries)

        assert result == "Test response"
        mock_prompt_service.render_prompt.assert_called_once()
        mock_provider_manager.create_model_with_fallback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_performance_review_with_provider_manager(
        self, mock_prompt_service, mock_provider_manager
    ):
        """Test performance review generation using provider manager."""
        service = LLMService(
            prompt_service=mock_prompt_service, provider_manager=mock_provider_manager
        )

        journal_entries = [{"text": "Test journal entry"}]

        result = await service.get_performance_review(journal_entries)

        assert isinstance(result, PerformanceReview)
        mock_prompt_service.render_prompt.assert_called_once()
        mock_provider_manager.create_model_with_fallback.assert_called_once()

    def test_get_llm_with_specific_provider(
        self, mock_prompt_service, mock_provider_manager
    ):
        """Test getting LLM with specific provider."""
        service = LLMService(
            prompt_service=mock_prompt_service, provider_manager=mock_provider_manager
        )

        llm = service.get_llm("journal_summary", provider="openai")

        assert llm is not None
        mock_provider_manager.create_model.assert_called_once()

        # Check that provider was set in config
        call_args = mock_provider_manager.create_model.call_args[0][0]
        assert call_args["provider"] == "openai"

    def test_get_llm_with_overrides(self, mock_prompt_service, mock_provider_manager):
        """Test getting LLM with configuration overrides."""
        service = LLMService(
            prompt_service=mock_prompt_service, provider_manager=mock_provider_manager
        )

        overrides = {"temperature": 0.9, "max_tokens": 500}
        llm = service.get_llm("journal_summary", overrides=overrides)

        assert llm is not None
        mock_provider_manager.create_model_with_fallback.assert_called_once()

        # Check that overrides were applied
        call_args = mock_provider_manager.create_model_with_fallback.call_args[0][0]
        assert call_args["temperature"] == 0.9
        assert call_args["max_tokens"] == 500

    def test_get_llm_with_fallback(self, mock_prompt_service, mock_provider_manager):
        """Test getting LLM with fallback when specific provider fails."""
        service = LLMService(
            prompt_service=mock_prompt_service, provider_manager=mock_provider_manager
        )

        # Make create_model fail, but create_model_with_fallback succeed
        mock_provider_manager.create_model.side_effect = Exception("Provider failed")

        # This should raise an exception since we're not using fallback logic in get_llm
        with pytest.raises(Exception, match="Provider failed"):
            service.get_llm("journal_summary", provider="openai")

    def test_get_provider_status(self, mock_prompt_service, mock_provider_manager):
        """Test getting provider status."""
        service = LLMService(
            prompt_service=mock_prompt_service, provider_manager=mock_provider_manager
        )

        status = service.get_provider_status()

        assert status == {
            "openai": {"status": "healthy"},
            "ollama": {"status": "healthy"},
        }
        mock_provider_manager.get_provider_status.assert_called_once()

    def test_get_provider_status_specific(
        self, mock_prompt_service, mock_provider_manager
    ):
        """Test getting status for specific provider."""
        service = LLMService(
            prompt_service=mock_prompt_service, provider_manager=mock_provider_manager
        )

        status = service.get_provider_status("openai")

        mock_provider_manager.get_provider_status.assert_called_once_with("openai")

    def test_get_available_providers(self, mock_prompt_service, mock_provider_manager):
        """Test getting available providers."""
        service = LLMService(
            prompt_service=mock_prompt_service, provider_manager=mock_provider_manager
        )

        providers = service.get_available_providers()

        assert providers == ["openai", "ollama", "gemini"]
        mock_provider_manager.list_available_providers.assert_called_once()

    def test_get_working_providers(self, mock_prompt_service, mock_provider_manager):
        """Test getting working providers."""
        service = LLMService(
            prompt_service=mock_prompt_service, provider_manager=mock_provider_manager
        )

        providers = service.get_working_providers()

        assert providers == ["openai", "ollama"]
        mock_provider_manager.get_working_providers.assert_called_once()

    def test_health_check_with_provider_integration(
        self, mock_prompt_service, mock_provider_manager
    ):
        """Test health check with provider integration."""
        service = LLMService(
            prompt_service=mock_prompt_service, provider_manager=mock_provider_manager
        )

        health = service.health_check()

        assert health["status"] == "healthy"
        assert "provider_status" in health
        assert "working_providers" in health
        assert health["working_providers"] == ["openai", "ollama"]
        assert health["llm_configured"] is False  # DEPRECATED field

    def test_health_check_degraded_without_working_providers(
        self, mock_prompt_service, mock_provider_manager
    ):
        """Test health check when no providers are working."""
        mock_provider_manager.get_working_providers.return_value = []

        service = LLMService(
            prompt_service=mock_prompt_service, provider_manager=mock_provider_manager
        )

        health = service.health_check()

        assert health["status"] == "degraded"
        assert health["working_providers"] == []

    @pytest.mark.asyncio
    async def test_fallback_to_deprecated_llm_creation(
        self, mock_prompt_service, mock_provider_manager
    ):
        """Test fallback to deprecated direct ChatOpenAI creation."""
        # Make provider manager fail
        mock_provider_manager.create_model_with_fallback.side_effect = Exception(
            "Provider failed"
        )

        service = LLMService(
            prompt_service=mock_prompt_service, provider_manager=mock_provider_manager
        )

        journal_entries = [{"text": "Test journal entry"}]

        # Should return error message instead of raising
        result = await service.get_journal_summary(journal_entries)

        assert "Error generating summary" in result
        mock_provider_manager.create_model_with_fallback.assert_called_once()

    def test_get_prompt_service_backward_compatibility(self, mock_prompt_service):
        """Test backward compatibility of get_prompt_service method."""
        service = LLMService(prompt_service=mock_prompt_service)

        result = service.get_prompt_service()

        assert result == mock_prompt_service


class TestLLMServiceMigration:
    """Test cases for migration scenarios."""

    def test_migration_from_old_to_new_constructor(self):
        """Test migration from old constructor to new constructor."""
        # Old way (still works)
        old_service = LLMService()

        # New way (recommended)
        with patch(
            "agent_service.app.services.llm_service.get_provider_manager"
        ) as mock_get:
            mock_manager = Mock(spec=ProviderManager)
            mock_get.return_value = mock_manager

            new_service = LLMService(provider_manager=mock_manager)

            # Both should work the same way
            assert old_service.provider_manager is not None
            assert new_service.provider_manager == mock_manager

    def test_migration_from_llm_parameter_to_provider_manager(self):
        """Test migration from llm parameter to provider_manager."""
        mock_llm = Mock()

        # Old way (DEPRECATED)
        old_service = LLMService(llm=mock_llm)

        # New way (recommended)
        with patch(
            "agent_service.app.services.llm_service.get_provider_manager"
        ) as mock_get:
            mock_manager = Mock(spec=ProviderManager)
            mock_get.return_value = mock_manager

            new_service = LLMService(provider_manager=mock_manager)

            # Old way should still work but log deprecation
            assert old_service.llm == mock_llm  # DEPRECATED
            assert old_service.provider_manager is not None  # Should get global

            # New way should use provider manager
            assert new_service.provider_manager == mock_manager
            assert new_service.llm is None  # Should be None when using provider manager


class TestLLMServiceErrorHandling:
    """Test cases for error handling scenarios."""

    def test_error_handling_in_get_llm(
        self, mock_prompt_service, mock_provider_manager
    ):
        """Test error handling in get_llm method."""
        mock_provider_manager.create_model_with_fallback.side_effect = Exception(
            "Provider error"
        )

        service = LLMService(
            prompt_service=mock_prompt_service, provider_manager=mock_provider_manager
        )

        with pytest.raises(Exception, match="Provider error"):
            service.get_llm("journal_summary")

    @pytest.mark.asyncio
    async def test_error_handling_in_journal_summary(
        self, mock_prompt_service, mock_provider_manager
    ):
        """Test error handling in journal summary generation."""
        mock_provider_manager.create_model_with_fallback.side_effect = Exception(
            "Provider error"
        )

        service = LLMService(
            prompt_service=mock_prompt_service, provider_manager=mock_provider_manager
        )

        journal_entries = [{"text": "Test journal entry"}]

        # Should return error message instead of raising
        result = await service.get_journal_summary(journal_entries)

        assert "Error generating summary" in result

    @pytest.mark.asyncio
    async def test_error_handling_in_performance_review(
        self, mock_prompt_service, mock_provider_manager
    ):
        """Test error handling in performance review generation."""
        mock_provider_manager.create_model_with_fallback.side_effect = Exception(
            "Provider error"
        )

        service = LLMService(
            prompt_service=mock_prompt_service, provider_manager=mock_provider_manager
        )

        journal_entries = [{"text": "Test journal entry"}]

        # Should return default PerformanceReview instead of raising
        result = await service.get_performance_review(journal_entries)

        assert isinstance(result, PerformanceReview)
        assert "Unable to generate performance review" in result.key_success
