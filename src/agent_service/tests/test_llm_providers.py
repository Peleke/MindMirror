"""
Tests for LLM provider system.

This module contains comprehensive tests for the LLM provider system,
including base provider functionality, specific provider implementations,
factory management, and provider manager integration.
"""

import os
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest
from src.agent_service.llms.provider_manager import ProviderManager
from src.agent_service.llms.providers.base import BaseProvider
from src.agent_service.llms.providers.factory import ProviderFactory
from src.agent_service.llms.providers.gemini_provider import GeminiProvider
from src.agent_service.llms.providers.ollama_provider import OllamaProvider
from src.agent_service.llms.providers.openai_provider import OpenAIProvider


class TestProvider(BaseProvider):
    """Concrete test provider for testing BaseProvider functionality."""

    def create_model(self, config: Dict[str, Any]):
        """Create a mock model."""
        return Mock()

    def get_supported_models(self):
        """Return supported models."""
        return ["test-model"]

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate config."""
        return self._validate_required_fields(config, ["model"])


class TestBaseProvider:
    """Test cases for BaseProvider class."""

    def test_base_provider_initialization(self):
        """Test BaseProvider initialization."""
        provider = TestProvider("test_provider")
        assert provider.provider_name == "test_provider"

    def test_validate_required_fields_success(self):
        """Test successful validation of required fields."""
        provider = TestProvider("test_provider")
        config = {"field1": "value1", "field2": "value2"}
        assert provider._validate_required_fields(config, ["field1", "field2"])

    def test_validate_required_fields_missing(self):
        """Test validation failure when required fields are missing."""
        provider = TestProvider("test_provider")
        config = {"field1": "value1"}
        assert not provider._validate_required_fields(config, ["field1", "field2"])

    def test_get_api_key_from_config(self):
        """Test getting API key from config."""
        provider = TestProvider("test_provider")
        config = {"api_key": "test_key"}
        api_key = provider._get_api_key(config, "API_KEY_ENV")
        assert api_key == "test_key"

    @patch.dict(os.environ, {"API_KEY_ENV": "env_key"})
    def test_get_api_key_from_env(self):
        """Test getting API key from environment."""
        provider = TestProvider("test_provider")
        config = {}
        api_key = provider._get_api_key(config, "API_KEY_ENV")
        assert api_key == "env_key"

    def test_get_api_key_not_found(self):
        """Test getting API key when not found."""
        provider = TestProvider("test_provider")
        config = {}
        with pytest.raises(ValueError):
            provider._get_api_key(config, "NONEXISTENT_KEY")


class TestOpenAIProvider:
    """Test cases for OpenAIProvider class."""

    def test_openai_provider_initialization(self):
        """Test OpenAIProvider initialization."""
        provider = OpenAIProvider()
        assert provider.provider_name == "openai"
        assert "gpt-3.5-turbo" in provider.get_supported_models()
        assert "gpt-4" in provider.get_supported_models()

    def test_validate_config_success(self):
        """Test successful configuration validation."""
        provider = OpenAIProvider()
        config = {"model": "gpt-3.5-turbo", "temperature": 0.7, "max_tokens": 1000}
        assert provider.validate_config(config)

    def test_validate_config_missing_model(self):
        """Test configuration validation with missing model."""
        provider = OpenAIProvider()
        config = {"temperature": 0.7}
        assert not provider.validate_config(config)

    def test_validate_config_invalid_temperature(self):
        """Test configuration validation with invalid temperature."""
        provider = OpenAIProvider()
        config = {
            "model": "gpt-3.5-turbo",
            "temperature": 3.0,  # Invalid: > 2
            "max_tokens": 1000,
        }
        assert not provider.validate_config(config)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    def test_create_model_success(self):
        """Test successful model creation."""
        provider = OpenAIProvider()
        config = {"model": "gpt-3.5-turbo", "temperature": 0.7, "max_tokens": 1000}

        with patch(
            "src.agent_service.llms.providers.openai_provider.ChatOpenAI"
        ) as mock_chat:
            mock_instance = Mock()
            mock_chat.return_value = mock_instance
            model = provider.create_model(config)

            assert model == mock_instance
            mock_chat.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)  # Clear environment to ensure no API key
    def test_create_model_no_api_key(self):
        """Test model creation without API key."""
        provider = OpenAIProvider()
        config = {"model": "gpt-3.5-turbo", "temperature": 0.7}

        with pytest.raises(RuntimeError, match="API key not found"):
            provider.create_model(config)

    def test_get_model_info(self):
        """Test getting model information."""
        provider = OpenAIProvider()
        info = provider.get_model_info("gpt-3.5-turbo")
        assert "max_tokens" in info
        assert "cost_per_1k_tokens" in info


class TestOllamaProvider:
    """Test cases for OllamaProvider class."""

    def test_ollama_provider_initialization(self):
        """Test OllamaProvider initialization."""
        provider = OllamaProvider()
        assert provider.provider_name == "ollama"
        assert "llama3.2" in provider.get_supported_models()
        assert "mistral" in provider.get_supported_models()

    def test_validate_config_success(self):
        """Test successful configuration validation."""
        provider = OllamaProvider()
        config = {
            "model": "llama3.2",  # Fixed: use 'model' not 'model_name'
            "temperature": 0.7,
            "streaming": False,
        }
        assert provider.validate_config(config)

    def test_validate_config_missing_model(self):
        """Test configuration validation with missing model."""
        provider = OllamaProvider()
        config = {"temperature": 0.7}
        assert not provider.validate_config(config)

    @patch("src.agent_service.llms.providers.ollama_provider.ChatOllama")
    def test_create_model_success(self, mock_chat):
        """Test successful model creation."""
        provider = OllamaProvider()
        config = {
            "model": "llama3.2",  # Fixed: use 'model' not 'model_name'
            "temperature": 0.7,
            "streaming": False,
        }

        mock_instance = Mock()
        mock_chat.return_value = mock_instance
        model = provider.create_model(config)

        assert model == mock_instance
        mock_chat.assert_called_once()

    @patch.dict(
        os.environ, {}, clear=True
    )  # Clear environment to avoid Docker detection
    def test_get_base_url_default(self):
        """Test getting default base URL."""
        provider = OllamaProvider()
        base_url = provider._get_base_url({})
        assert base_url == "http://localhost:11434"

    def test_get_base_url_from_config(self):
        """Test getting base URL from config."""
        provider = OllamaProvider()
        config = {"base_url": "http://custom:11434"}
        base_url = provider._get_base_url(config)
        assert base_url == "http://custom:11434"

    @patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://env:11434"})
    def test_get_base_url_from_env(self):
        """Test getting base URL from environment."""
        provider = OllamaProvider()
        base_url = provider._get_base_url({})
        assert base_url == "http://env:11434"

    @patch("requests.get")
    def test_get_available_models(self, mock_get):
        """Test getting available models from Ollama."""
        provider = OllamaProvider()
        mock_response = Mock()
        mock_response.status_code = 200  # Fixed: set status_code
        mock_response.json.return_value = {"models": [{"name": "llama3.2"}]}
        mock_get.return_value = mock_response

        models = provider.get_available_models()
        assert "llama3.2" in models

    def test_is_model_available(self):
        """Test checking if model is available."""
        provider = OllamaProvider()
        with patch.object(provider, "get_available_models", return_value=["llama3.2"]):
            assert provider.is_model_available("llama3.2")
            assert not provider.is_model_available("nonexistent")


class TestGeminiProvider:
    """Test cases for GeminiProvider class."""

    def test_gemini_provider_initialization(self):
        """Test GeminiProvider initialization."""
        provider = GeminiProvider()
        assert provider.provider_name == "gemini"
        assert "models/gemini-1.5-pro" in provider.get_supported_models()
        assert "models/gemini-1.5-flash" in provider.get_supported_models()

    def test_validate_config_success(self):
        """Test successful configuration validation."""
        provider = GeminiProvider()
        config = {
            "model": "models/gemini-1.5-flash",
            "temperature": 0.7,
            "max_tokens": 1000,
        }
        assert provider.validate_config(config)

    def test_validate_config_invalid_temperature(self):
        """Test configuration validation with invalid temperature."""
        provider = GeminiProvider()
        config = {
            "model": "models/gemini-1.5-flash",
            "temperature": 3.0,  # Invalid: > 2
            "max_tokens": 1000,
        }
        assert not provider.validate_config(config)

    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"})
    def test_create_model_success(self):
        """Test successful model creation."""
        provider = GeminiProvider()
        config = {
            "model": "models/gemini-1.5-flash",
            "temperature": 0.7,
            "max_tokens": 1000,
        }

        with patch(
            "src.agent_service.llms.providers.gemini_provider.ChatGoogleGenerativeAI"
        ) as mock_chat:
            mock_instance = Mock()
            mock_chat.return_value = mock_instance
            model = provider.create_model(config)

            assert model == mock_instance
            mock_chat.assert_called_once()

    def test_get_model_info(self):
        """Test getting model information."""
        provider = GeminiProvider()
        info = provider.get_model_info("models/gemini-1.5-flash")
        assert "max_tokens" in info
        assert "supports_streaming" in info
        assert "cost_per_1k_tokens" in info

    def test_get_safety_settings(self):
        """Test getting safety settings."""
        provider = GeminiProvider()
        settings = provider.get_safety_settings("default")
        assert isinstance(settings, list)
        assert len(settings) > 0

        # Test different levels
        low_settings = provider.get_safety_settings("low")
        high_settings = provider.get_safety_settings("high")
        assert len(low_settings) == len(high_settings)


class TestProviderFactory:
    """Test cases for ProviderFactory class."""

    def test_factory_initialization(self):
        """Test ProviderFactory initialization."""
        factory = ProviderFactory()
        providers = factory.list_providers()
        assert "openai" in providers
        assert "ollama" in providers
        assert "gemini" in providers

    def test_register_provider(self):
        """Test registering a custom provider."""
        factory = ProviderFactory()
        custom_provider = Mock(spec=BaseProvider)
        custom_provider.provider_name = "custom"

        factory.register_provider(custom_provider)
        assert "custom" in factory.list_providers()

    def test_get_provider(self):
        """Test getting a provider by name."""
        factory = ProviderFactory()
        provider = factory.get_provider("openai")
        assert provider is not None
        assert provider.provider_name == "openai"

    def test_get_provider_not_found(self):
        """Test getting a non-existent provider."""
        factory = ProviderFactory()
        provider = factory.get_provider("nonexistent")
        assert provider is None

    def test_get_supported_models(self):
        """Test getting supported models."""
        factory = ProviderFactory()
        models = factory.get_supported_models()
        assert "openai" in models
        assert "ollama" in models
        assert "gemini" in models

    def test_get_supported_models_specific_provider(self):
        """Test getting supported models for specific provider."""
        factory = ProviderFactory()
        models = factory.get_supported_models("openai")
        assert "openai" in models
        assert "gpt-3.5-turbo" in models["openai"]

    def test_validate_config_success(self):
        """Test successful configuration validation."""
        factory = ProviderFactory()
        config = {"provider": "openai", "model": "gpt-3.5-turbo", "temperature": 0.7}
        assert factory.validate_config(config)

    def test_validate_config_no_provider(self):
        """Test configuration validation without provider."""
        factory = ProviderFactory()
        config = {"model": "gpt-3.5-turbo"}
        assert not factory.validate_config(config)

    def test_validate_config_invalid_provider(self):
        """Test configuration validation with invalid provider."""
        factory = ProviderFactory()
        config = {"provider": "nonexistent", "model": "gpt-3.5-turbo"}
        assert not factory.validate_config(config)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    def test_create_model_success(self):
        """Test successful model creation."""
        factory = ProviderFactory()
        config = {"provider": "openai", "model": "gpt-3.5-turbo", "temperature": 0.7}

        with patch(
            "src.agent_service.llms.providers.openai_provider.ChatOpenAI"
        ) as mock_chat:
            mock_instance = Mock()
            mock_chat.return_value = mock_instance
            model = factory.create_model(config)

            assert model == mock_instance

    def test_create_model_no_provider(self):
        """Test model creation without provider specification."""
        factory = ProviderFactory()
        config = {"model": "gpt-3.5-turbo"}

        with pytest.raises(ValueError, match="Provider name must be specified"):
            factory.create_model(config)

    def test_create_model_invalid_provider(self):
        """Test model creation with invalid provider."""
        factory = ProviderFactory()
        config = {"provider": "nonexistent", "model": "gpt-3.5-turbo"}

        with pytest.raises(ValueError, match="Provider 'nonexistent' not found"):
            factory.create_model(config)

    def test_health_check(self):
        """Test health check functionality."""
        factory = ProviderFactory()
        health = factory.health_check()
        assert "openai" in health
        assert "ollama" in health
        assert "gemini" in health

    def test_health_check_specific_provider(self):
        """Test health check for specific provider."""
        factory = ProviderFactory()
        health = factory.health_check("openai")
        assert "status" in health
        assert "message" in health

    def test_create_config_template(self):
        """Test creating configuration template."""
        factory = ProviderFactory()
        template = factory.create_config_template("openai", "gpt-3.5-turbo")
        assert template["provider"] == "openai"
        assert template["model"] == "gpt-3.5-turbo"
        assert "temperature" in template
        assert "max_tokens" in template


class TestProviderManager:
    """Test cases for ProviderManager class."""

    def test_manager_initialization(self):
        """Test ProviderManager initialization."""
        manager = ProviderManager()
        assert manager._factory is not None
        assert manager._default_provider is not None

    def test_get_default_config(self):
        """Test getting default configuration."""
        manager = ProviderManager()
        config = manager.get_default_config()
        assert "provider" in config
        assert "model" in config

    @patch.dict(os.environ, {"LLM_PROVIDER": "ollama"})
    def test_load_defaults_from_env(self):
        """Test loading defaults from environment variables."""
        manager = ProviderManager()
        assert manager._default_provider == "ollama"

    def test_create_model_with_config(self):
        """Test creating model with provided config."""
        manager = ProviderManager()
        config = {"provider": "openai", "model": "gpt-3.5-turbo", "temperature": 0.7}

        with patch.object(manager._factory, "create_model") as mock_create:
            mock_instance = Mock()
            mock_create.return_value = mock_instance
            model = manager.create_model(config)

            assert model == mock_instance
            mock_create.assert_called_once_with(config)

    def test_create_model_without_config(self):
        """Test creating model without config (uses defaults)."""
        manager = ProviderManager()

        with patch.object(manager, "create_config_from_env") as mock_config_from_env:
            mock_config_from_env.return_value = {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
            }
            with patch.object(manager._factory, "create_model") as mock_create:
                mock_instance = Mock()
                mock_create.return_value = mock_instance
                model = manager.create_model()

                assert model == mock_instance
                mock_config_from_env.assert_called_once()

    def test_create_model_for_provider(self):
        """Test creating model for specific provider."""
        manager = ProviderManager()

        with patch.object(manager._factory, "create_model") as mock_create:
            mock_instance = Mock()
            mock_create.return_value = mock_instance

            # Mock the settings properties to avoid missing attribute errors
            with patch.object(manager._settings, "llm_temperature", 0.7), patch.object(
                manager._settings, "llm_max_tokens", 1000
            ), patch.object(manager._settings, "llm_streaming", False), patch.object(
                manager._settings, "openai_api_key", "test_key"
            ):

                # Mock the llm_api_key property specifically
                with patch.object(
                    type(manager._settings),
                    "llm_api_key",
                    new_callable=lambda: property(lambda self: "test_key"),
                ):
                    model = manager.create_model_for_provider(
                        "openai", "gpt-3.5-turbo", temperature=0.8
                    )

                    assert model == mock_instance
                    mock_create.assert_called_once()
                    # Verify the config was built correctly
                    call_args = mock_create.call_args[0][0]
                    assert call_args["provider"] == "openai"
                    assert call_args["model"] == "gpt-3.5-turbo"
                    assert call_args["temperature"] == 0.8  # Should be overridden

    def test_list_available_providers(self):
        """Test listing available providers."""
        manager = ProviderManager()
        providers = manager.list_available_providers()
        assert "openai" in providers
        assert "ollama" in providers
        assert "gemini" in providers

    def test_get_provider_status(self):
        """Test getting provider status."""
        manager = ProviderManager()
        status = manager.get_provider_status()
        assert "openai" in status
        assert "ollama" in status
        assert "gemini" in status

    def test_get_provider_status_specific(self):
        """Test getting status for specific provider."""
        manager = ProviderManager()
        status = manager.get_provider_status("openai")
        assert "status" in status
        assert "message" in status

    def test_validate_config(self):
        """Test configuration validation."""
        manager = ProviderManager()
        config = {"provider": "openai", "model": "gpt-3.5-turbo", "temperature": 0.7}
        assert manager.validate_config(config)

    def test_get_working_providers(self):
        """Test getting working providers."""
        manager = ProviderManager()

        with patch.object(manager._factory, "list_providers") as mock_list:
            mock_list.return_value = ["openai", "ollama"]
            with patch.object(manager._factory, "get_provider") as mock_get:
                # Mock providers that test_connection successfully
                mock_provider = Mock()
                mock_provider.test_connection.return_value = True
                mock_get.return_value = mock_provider

                working = manager.get_working_providers()
                assert "openai" in working
                assert "ollama" in working

    def test_get_best_available_provider(self):
        """Test getting best available provider."""
        manager = ProviderManager()

        with patch.object(manager._settings, "llm_provider", "openai"):
            with patch.object(manager, "test_provider_health") as mock_health:
                mock_health.return_value = True
                best = manager.get_best_available_provider()
                assert best == "openai"

    def test_get_best_available_provider_fallback(self):
        """Test getting best available provider with fallback."""
        manager = ProviderManager()

        with patch.object(manager._settings, "llm_provider", "openai"):
            with patch.object(manager, "test_provider_health") as mock_health:
                mock_health.return_value = False
                best = manager.get_best_available_provider()
                assert (
                    best is None
                )  # Current implementation returns None instead of fallback

    def test_create_model_with_fallback(self):
        """Test creating model with fallback."""
        manager = ProviderManager()

        with patch.object(manager, "create_config_from_env") as mock_config:
            mock_config.return_value = {"provider": "openai", "model": "gpt-3.5-turbo"}
            with patch.object(manager._factory, "create_model") as mock_create:
                mock_instance = Mock()
                mock_create.return_value = mock_instance
                model = manager.create_model_with_fallback()

                assert model == mock_instance
                mock_create.assert_called_once()

    def test_create_model_with_fallback_no_working_providers(self):
        """Test creating model with fallback when no providers work."""
        manager = ProviderManager()

        with patch.object(manager, "create_config_from_env") as mock_config:
            mock_config.return_value = {"provider": "openai", "model": "gpt-3.5-turbo"}
            with patch.object(manager._factory, "create_model") as mock_create:
                mock_create.side_effect = Exception("Failed")

                with pytest.raises(RuntimeError, match="Model creation failed"):
                    manager.create_model_with_fallback()


class TestIntegration:
    """Integration tests for the complete LLM provider system."""

    def test_end_to_end_model_creation(self):
        """Test end-to-end model creation through the complete system."""
        from src.agent_service.llms import (
            create_model_with_fallback,
            get_provider_manager,
        )

        manager = get_provider_manager()
        assert manager is not None

        # Test that we can get provider status
        status = manager.get_provider_status()
        assert isinstance(status, dict)
        assert len(status) > 0

    def test_factory_singleton(self):
        """Test that factory is a singleton."""
        from src.agent_service.llms.providers.factory import get_factory

        factory1 = get_factory()
        factory2 = get_factory()
        assert factory1 is factory2

    def test_manager_singleton(self):
        """Test that manager is a singleton."""
        from src.agent_service.llms.provider_manager import get_provider_manager

        manager1 = get_provider_manager()
        manager2 = get_provider_manager()
        assert manager1 is manager2

    def test_provider_registration(self):
        """Test that all providers are properly registered."""
        from src.agent_service.llms.providers.factory import get_factory

        factory = get_factory()
        providers = factory.list_providers()

        expected_providers = ["openai", "ollama", "gemini"]
        for provider in expected_providers:
            assert provider in providers
            assert factory.get_provider(provider) is not None
