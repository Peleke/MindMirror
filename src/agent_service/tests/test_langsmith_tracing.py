"""
Tests for LangSmith tracing infrastructure.

These tests verify that tracing works correctly for all LLM operations,
agent workflows, and LangChain components.
"""

import os
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest

from agent_service.tracing import get_langsmith_client, setup_langsmith_tracing

try:
    from agent_service.tracing.decorators import (trace_agent_workflow,
                                                  trace_function,
                                                  trace_langchain_operation,
                                                  trace_runnable)
except ImportError:

    def trace_langchain_operation(*args, **kwargs):
        pass


class TestLangSmithTracingSetup:
    """Test LangSmith tracing configuration and setup."""

    def test_setup_langsmith_tracing_with_env_vars(self):
        """Test that tracing setup works with environment variables."""
        with patch.dict(
            os.environ,
            {
                "LANGCHAIN_API_KEY": "test-api-key",
                "LANGCHAIN_PROJECT": "test-project",
            },
        ):
            client = setup_langsmith_tracing()
            assert client is not None
            assert os.getenv("LANGCHAIN_TRACING_V2") == "true"

    def test_setup_langsmith_tracing_with_parameters(self):
        """Test that tracing setup works with explicit parameters."""
        with patch.dict(os.environ, {}, clear=True):
            client = setup_langsmith_tracing(
                api_key="test-key",
                project_name="test-project",
                endpoint="https://api.smith.langchain.com",
            )
            assert client is not None
            assert os.getenv("LANGCHAIN_API_KEY") == "test-key"
            assert os.getenv("LANGCHAIN_PROJECT") == "test-project"
            assert os.getenv("LANGCHAIN_ENDPOINT") == "https://api.smith.langchain.com"

    def test_setup_langsmith_tracing_missing_api_key(self):
        """Test that setup fails gracefully when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="LANGCHAIN_API_KEY"):
                setup_langsmith_tracing()

    def test_get_langsmith_client(self):
        """Test that get_langsmith_client returns a client instance."""
        with patch.dict(os.environ, {"LANGCHAIN_API_KEY": "test-key"}):
            client = get_langsmith_client()
            assert client is not None


class TestTracingDecorators:
    """Test tracing decorators for functions and operations."""

    @patch("agent_service.tracing.decorators.langsmith.Client")
    def test_trace_function_success(self, mock_client_class):
        """Test that trace_function decorator works for successful operations."""
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)

        mock_client_class.return_value = mock_client
        mock_client.trace.return_value = mock_context_manager

        @trace_function(name="test_function", tags=["test"])
        def test_func(x: int) -> int:
            return x * 2

        result = test_func(5)

        assert result == 10
        mock_client.trace.assert_called_once()
        mock_trace.add_metadata.assert_called_with(
            {
                "result_type": "int",
                "success": True,
            }
        )

    @patch("agent_service.tracing.decorators.langsmith.Client")
    def test_trace_function_error(self, mock_client_class):
        """Test that trace_function decorator handles errors correctly."""
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)

        mock_client_class.return_value = mock_client
        mock_client.trace.return_value = mock_context_manager

        @trace_function(name="test_function", tags=["test"])
        def test_func(x: int) -> int:
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            test_func(5)

        # Should have called trace once (one trace span that captures the error)
        assert mock_client.trace.call_count == 1
        # Should have added error metadata
        mock_trace.add_metadata.assert_called_with(
            {
                "error": "Test error",
                "error_type": "ValueError",
                "success": False,
            }
        )

    @patch("agent_service.tracing.decorators.langsmith.Client")
    def test_trace_langchain_operation(self, mock_client_class):
        """Test that trace_langchain_operation adds LangChain-specific tags."""
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)

        mock_client_class.return_value = mock_client
        mock_client.trace.return_value = mock_context_manager

        @trace_langchain_operation("test_operation", tags=["custom"])
        def test_func(x: int) -> int:
            return x * 2

        result = test_func(5)

        assert result == 10
        mock_client.trace.assert_called_once()
        call_args = mock_client.trace.call_args
        assert "langchain" in call_args[1]["tags"]
        assert "test_operation" in call_args[1]["tags"]
        assert "custom" in call_args[1]["tags"]

    @patch("agent_service.tracing.decorators.langsmith.Client")
    def test_trace_agent_workflow(self, mock_client_class):
        """Test that trace_agent_workflow adds agent-specific tags."""
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)

        mock_client_class.return_value = mock_client
        mock_client.trace.return_value = mock_context_manager

        @trace_agent_workflow("test_workflow", tags=["custom"])
        def test_func(x: int) -> int:
            return x * 2

        result = test_func(5)

        assert result == 10
        mock_client.trace.assert_called_once()
        call_args = mock_client.trace.call_args
        assert "agent" in call_args[1]["tags"]
        assert "workflow" in call_args[1]["tags"]
        assert "test_workflow" in call_args[1]["tags"]
        assert "custom" in call_args[1]["tags"]


class TestTraceRunnable:
    """Test tracing wrapper for LangChain Runnables."""

    @patch("agent_service.tracing.decorators.langsmith.Client")
    def test_trace_runnable_sync(self, mock_client_class):
        """Test that trace_runnable works for synchronous Runnables."""
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)

        mock_client_class.return_value = mock_client
        mock_client.trace.return_value = mock_context_manager

        # Create a simple mock runnable
        mock_runnable = Mock()
        mock_runnable.invoke.return_value = "test_result"

        traced_runnable = trace_runnable(mock_runnable, name="test_runnable")
        result = traced_runnable.invoke("test_input")

        assert result == "test_result"
        mock_runnable.invoke.assert_called_once_with("test_input", None)
        mock_client.trace.assert_called_once()
        mock_trace.add_metadata.assert_called_with(
            {
                "result_type": "str",
                "success": True,
            }
        )

    @patch("agent_service.tracing.decorators.langsmith.Client")
    @pytest.mark.asyncio
    async def test_trace_runnable_async(self, mock_client_class):
        """Test that trace_runnable works for asynchronous Runnables."""
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)

        mock_client_class.return_value = mock_client
        mock_client.trace.return_value = mock_context_manager

        # Create a simple mock async runnable
        mock_runnable = Mock()

        # Make ainvoke return an awaitable
        async def mock_ainvoke(input_data, config=None):
            return "test_result"

        mock_runnable.ainvoke = mock_ainvoke

        traced_runnable = trace_runnable(mock_runnable, name="test_runnable")
        result = await traced_runnable.ainvoke("test_input")

        assert result == "test_result"
        mock_client.trace.assert_called_once()
        mock_trace.add_metadata.assert_called_with(
            {
                "result_type": "str",
                "success": True,
            }
        )

    @patch("agent_service.tracing.decorators.langsmith.Client")
    def test_trace_runnable_error(self, mock_client_class):
        """Test that trace_runnable handles errors correctly."""
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)

        mock_client_class.return_value = mock_client
        mock_client.trace.return_value = mock_context_manager

        # Create a mock runnable that raises an error
        mock_runnable = Mock()
        mock_runnable.invoke.side_effect = ValueError("Test error")

        traced_runnable = trace_runnable(mock_runnable, name="test_runnable")

        with pytest.raises(ValueError, match="Test error"):
            traced_runnable.invoke("test_input")


class TestTracingIntegration:
    """Integration tests for tracing with real LangChain components."""

    @patch("agent_service.tracing.decorators.langsmith.Client")
    def test_tracing_with_langchain_chain(self, mock_client_class):
        """Test tracing integration with a LangChain chain."""
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)

        mock_client_class.return_value = mock_client
        mock_client.trace.return_value = mock_context_manager

        # Create a simple chain-like object that matches LangChain interface
        class MockChain:
            def invoke(
                self,
                input_data: Dict[str, Any],
                config: Optional[Dict[str, Any]] = None,
            ) -> str:
                return f"Processed: {input_data.get('input', '')}"

        chain = MockChain()
        traced_chain = trace_runnable(chain, name="test_chain")

        result = traced_chain.invoke({"input": "test"})

        assert result == "Processed: test"
        mock_client.trace.assert_called_once()

    @patch("agent_service.tracing.decorators.langsmith.Client")
    def test_tracing_with_multiple_operations(self, mock_client_class):
        """Test that multiple traced operations work together."""
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)

        mock_client_class.return_value = mock_client
        mock_client.trace.return_value = mock_context_manager

        @trace_function(name="step1")
        def step1(x: int) -> int:
            return x + 1

        @trace_function(name="step2")
        def step2(x: int) -> int:
            return x * 2

        result1 = step1(5)
        result2 = step2(result1)

        assert result1 == 6
        assert result2 == 12
        assert mock_client.trace.call_count == 2
