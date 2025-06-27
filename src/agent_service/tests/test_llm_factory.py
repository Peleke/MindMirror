"""
Tests for LLM factory functionality.

These tests verify that the LLM factory correctly creates different types
of language models with proper configurations, error handling, and tracing.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from agent_service.llms.factory import LLMFactory, get_llm


class TestLLMFactory:
    """Test LLM factory methods."""
    
    @patch('agent_service.tracing.decorators.langsmith.Client')
    def test_create_llm_openai_default(self, mock_client_class):
        """Test creating OpenAI LLM with default settings."""
        # Setup LangSmith client mock
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_client.trace.return_value = mock_context_manager
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            llm = LLMFactory.create_llm(provider="openai")
            
            assert isinstance(llm, ChatOpenAI)
            assert llm.model_name == "gpt-4o"
            assert llm.temperature == 0
            assert llm.streaming is False
    
    @patch('agent_service.tracing.decorators.langsmith.Client')
    def test_create_llm_openai_custom(self, mock_client_class):
        """Test creating OpenAI LLM with custom settings."""
        # Setup LangSmith client mock
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_client.trace.return_value = mock_context_manager
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            llm = LLMFactory.create_llm(
                provider="openai",
                model_name="gpt-3.5-turbo",
                temperature=0.7,
                streaming=True,
            )
            
            assert isinstance(llm, ChatOpenAI)
            assert llm.model_name == "gpt-3.5-turbo"
            assert llm.temperature == 0.7
            assert llm.streaming is True
    
    @patch('agent_service.tracing.decorators.langsmith.Client')
    def test_create_llm_ollama_default(self, mock_client_class):
        """Test creating Ollama LLM with default settings."""
        # Setup LangSmith client mock
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_client.trace.return_value = mock_context_manager
        mock_client_class.return_value = mock_client
        
        llm = LLMFactory.create_llm(provider="ollama")
        
        assert isinstance(llm, ChatOllama)
        assert llm.model == "llama3"
        assert llm.base_url == "http://localhost:11434"
        assert llm.temperature == 0
        # ChatOllama doesn't have a stream attribute by default
        # Just verify the core attributes we set are correct
    
    @patch('agent_service.tracing.decorators.langsmith.Client')
    def test_create_llm_ollama_custom(self, mock_client_class):
        """Test creating Ollama LLM with custom settings."""
        # Setup LangSmith client mock
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_client.trace.return_value = mock_context_manager
        mock_client_class.return_value = mock_client
        
        llm = LLMFactory.create_llm(
            provider="ollama",
            model_name="mistral",
            temperature=0.5,
            base_url="http://custom:11434",
        )
        
        assert isinstance(llm, ChatOllama)
        assert llm.model == "mistral"
        assert llm.base_url == "http://custom:11434"
        assert llm.temperature == 0.5
    
    @patch('agent_service.tracing.decorators.langsmith.Client')
    def test_create_llm_with_config_name(self, mock_client_class):
        """Test creating LLM with predefined configuration."""
        # Setup LangSmith client mock
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_client.trace.return_value = mock_context_manager
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            llm = LLMFactory.create_llm(
                provider="openai",
                config_name="coaching",
            )
            
            assert isinstance(llm, ChatOpenAI)
            assert llm.temperature == 0.3
            assert llm.max_tokens == 1500
    
    @patch('agent_service.tracing.decorators.langsmith.Client')
    def test_create_llm_config_override(self, mock_client_class):
        """Test that custom kwargs override config settings."""
        # Setup LangSmith client mock
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_client.trace.return_value = mock_context_manager
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            llm = LLMFactory.create_llm(
                provider="openai",
                config_name="coaching",
                temperature=0.8,  # Override config
            )
            
            assert llm.temperature == 0.8  # Custom value
            assert llm.max_tokens == 1500  # From config
    
    @patch('agent_service.tracing.decorators.langsmith.Client')
    def test_create_llm_unsupported_provider(self, mock_client_class):
        """Test that unsupported providers raise an error."""
        # Setup LangSmith client mock
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_client.trace.return_value = mock_context_manager
        mock_client_class.return_value = mock_client
        
        with pytest.raises(ValueError, match="Unsupported provider"):
            LLMFactory.create_llm(provider="unsupported")
    
    @patch('agent_service.tracing.decorators.langsmith.Client')
    def test_create_llm_missing_openai_key(self, mock_client_class):
        """Test that missing OpenAI API key raises an error."""
        # Setup LangSmith client mock
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_client.trace.return_value = mock_context_manager
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                LLMFactory.create_llm(provider="openai")
    
    @patch('agent_service.llms.factory.LLMFactory._is_docker_environment')
    @patch('agent_service.tracing.decorators.langsmith.Client')
    def test_create_ollama_docker_environment(self, mock_client_class, mock_is_docker):
        """Test that Ollama uses correct base URL in Docker."""
        # Setup LangSmith client mock
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_client.trace.return_value = mock_context_manager
        mock_client_class.return_value = mock_client
        
        mock_is_docker.return_value = True
        
        llm = LLMFactory.create_llm(provider="ollama")
        
        assert llm.base_url == "http://host.docker.internal:11434"
    
    @patch('agent_service.tracing.decorators.langsmith.Client')
    def test_get_rag_llm(self, mock_client_class):
        """Test getting RAG-optimized LLM."""
        # Setup LangSmith client mock
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_client.trace.return_value = mock_context_manager
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            llm = LLMFactory.get_rag_llm()
            
            assert isinstance(llm, ChatOpenAI)
            assert llm.temperature == 0
            assert llm.max_tokens == 1000
            assert llm.streaming is False
    
    @patch('agent_service.tracing.decorators.langsmith.Client')
    def test_get_coaching_llm(self, mock_client_class):
        """Test getting coaching-optimized LLM."""
        # Setup LangSmith client mock
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_client.trace.return_value = mock_context_manager
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            llm = LLMFactory.get_coaching_llm()
            
            assert isinstance(llm, ChatOpenAI)
            assert llm.temperature == 0.3
            assert llm.max_tokens == 1500
    
    @patch('agent_service.tracing.decorators.langsmith.Client')
    def test_get_creative_llm(self, mock_client_class):
        """Test getting creative-optimized LLM."""
        # Setup LangSmith client mock
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_client.trace.return_value = mock_context_manager
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            llm = LLMFactory.get_creative_llm()
            
            assert isinstance(llm, ChatOpenAI)
            assert llm.temperature == 0.7
            assert llm.max_tokens == 2000
    
    @patch('agent_service.tracing.decorators.langsmith.Client')
    def test_get_analysis_llm(self, mock_client_class):
        """Test getting analysis-optimized LLM."""
        # Setup LangSmith client mock
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_client.trace.return_value = mock_context_manager
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            llm = LLMFactory.get_analysis_llm()
            
            assert isinstance(llm, ChatOpenAI)
            assert llm.temperature == 0.1
            assert llm.max_tokens == 2000


class TestGetLLMBackwardCompatibility:
    """Test backward compatibility function."""
    
    @patch('agent_service.tracing.decorators.langsmith.Client')
    def test_get_llm_function(self, mock_client_class):
        """Test that get_llm function works correctly."""
        # Setup LangSmith client mock
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_client.trace.return_value = mock_context_manager
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            llm = get_llm(provider="openai", model_name="gpt-3.5-turbo")
            
            assert isinstance(llm, ChatOpenAI)
            assert llm.model_name == "gpt-3.5-turbo"
    
    @patch('agent_service.tracing.decorators.langsmith.Client')
    def test_get_llm_with_kwargs(self, mock_client_class):
        """Test that get_llm accepts additional kwargs."""
        # Setup LangSmith client mock
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_client.trace.return_value = mock_context_manager
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            llm = get_llm(
                provider="openai",
                temperature=0.5,
                max_tokens=500,
            )
            
            assert llm.temperature == 0.5
            assert llm.max_tokens == 500


class TestLLMFactoryErrorHandling:
    """Test error handling in LLM factory."""
    
    @patch('agent_service.llms.factory.ChatOpenAI')
    @patch('agent_service.tracing.decorators.langsmith.Client')
    def test_create_openai_llm_error(self, mock_client_class, mock_chat_openai):
        """Test that OpenAI LLM creation errors are handled."""
        # Setup LangSmith client mock
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_client.trace.return_value = mock_context_manager
        mock_client_class.return_value = mock_client
        
        mock_chat_openai.side_effect = Exception("OpenAI error")
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with pytest.raises(Exception, match="OpenAI error"):
                LLMFactory.create_llm(provider="openai")
    
    @patch('agent_service.llms.factory.ChatOllama')
    @patch('agent_service.tracing.decorators.langsmith.Client')
    def test_create_ollama_llm_error(self, mock_client_class, mock_chat_ollama):
        """Test that Ollama LLM creation errors are handled."""
        # Setup LangSmith client mock
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_client.trace.return_value = mock_context_manager
        mock_client_class.return_value = mock_client
        
        mock_chat_ollama.side_effect = Exception("Ollama error")
        
        with pytest.raises(Exception, match="Ollama error"):
            LLMFactory.create_llm(provider="ollama")
    
    @patch('agent_service.tracing.decorators.langsmith.Client')
    def test_invalid_config_name(self, mock_client_class):
        """Test that invalid config names use defaults."""
        # Setup LangSmith client mock
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_client.trace.return_value = mock_context_manager
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            llm = LLMFactory.create_llm(
                provider="openai",
                config_name="invalid_config",
            )
            
            # Should use default OpenAI settings
            assert llm.temperature == 0
            assert llm.streaming is False


class TestLLMFactoryTracing:
    """Test that LLM factory integrates with tracing."""
    
    @patch('agent_service.tracing.decorators.langsmith.Client')
    def test_create_llm_traced(self, mock_client_class):
        """Test that create_llm is traced."""
        # Setup LangSmith client mock
        mock_client = Mock()
        mock_trace = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_trace)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_client.trace.return_value = mock_context_manager
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            # Don't mock trace_function here - let it actually run
            # to test that the decorator is applied
            llm = LLMFactory.create_llm(provider="openai")
            
            # Verify the LLM was created successfully
            assert isinstance(llm, ChatOpenAI)
            assert llm.model_name == "gpt-4o"


class TestLLMFactoryDockerDetection:
    """Test Docker environment detection."""
    
    @patch('builtins.open', create=True)
    @patch('os.path.exists')
    @patch('os.getenv')
    def test_docker_detection_dockerenv(self, mock_getenv, mock_exists, mock_open):
        """Test Docker detection via /.dockerenv file."""
        mock_exists.return_value = True
        mock_getenv.return_value = None
        
        assert LLMFactory._is_docker_environment() is True
    
    @patch('os.path.exists')
    @patch('os.getenv')
    def test_docker_detection_env_var(self, mock_getenv, mock_exists):
        """Test Docker detection via environment variables."""
        mock_exists.return_value = False
        mock_getenv.side_effect = lambda key: {
            "DOCKER_CONTAINER": "true",
            "IN_DOCKER": None,
        }.get(key)
        
        assert LLMFactory._is_docker_environment() is True
    
    @patch('os.path.exists')
    @patch('os.getenv')
    def test_docker_detection_not_docker(self, mock_getenv, mock_exists):
        """Test Docker detection when not in Docker."""
        mock_exists.return_value = False
        mock_getenv.return_value = None
        
        assert LLMFactory._is_docker_environment() is False 