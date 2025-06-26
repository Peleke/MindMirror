"""
Provider manager for MindMirror LLM integration.

This module provides the ProviderManager class that integrates the provider
factory with the existing MindMirror system and provides high-level management
functions for LLM providers.
"""

import logging
import os
from typing import Dict, List, Any, Optional
from langchain_core.language_models import BaseLanguageModel

from .providers.factory import get_factory, ProviderFactory
from .providers.base import BaseProvider

logger = logging.getLogger(__name__)


class ProviderManager:
    """
    High-level manager for LLM providers in MindMirror.
    
    Integrates the provider factory with the existing system and provides
    convenient methods for model management and configuration.
    """
    
    def __init__(self):
        """Initialize the provider manager."""
        self._factory: ProviderFactory = get_factory()
        self._default_provider: Optional[str] = None
        self._default_model: Optional[str] = None
        self._load_defaults()
    
    def _load_defaults(self):
        """Load default provider and model from environment variables."""
        self._default_provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
        self._default_model = os.getenv("DEFAULT_LLM_MODEL", "gpt-3.5-turbo")
        
        # Validate defaults
        if not self._factory.get_provider(self._default_provider):
            logger.warning(f"Default provider '{self._default_provider}' not found, using first available")
            available_providers = self._factory.list_providers()
            if available_providers:
                self._default_provider = available_providers[0]
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration for the default provider and model.
        
        Returns:
            Default configuration dictionary
        """
        if not self._default_provider:
            raise ValueError("No default provider configured")
        
        return self._factory.create_config_template(
            self._default_provider,
            self._default_model or "gpt-3.5-turbo"
        )
    
    def create_model(self, config: Optional[Dict[str, Any]] = None) -> BaseLanguageModel:
        """
        Create a model using provided config or defaults.
        
        Args:
            config: Optional configuration dictionary. If None, uses defaults.
            
        Returns:
            Configured language model instance
        """
        if config is None:
            config = self.get_default_config()
        
        return self._factory.create_model(config)
    
    def create_model_for_provider(self, provider_name: str, model_name: str, **kwargs) -> BaseLanguageModel:
        """
        Create a model for a specific provider and model.
        
        Args:
            provider_name: Name of the provider
            model_name: Name of the model
            **kwargs: Additional configuration parameters
            
        Returns:
            Configured language model instance
        """
        config = self._factory.create_config_template(provider_name, model_name)
        config.update(kwargs)
        return self._factory.create_model(config)
    
    def list_available_providers(self) -> List[str]:
        """
        Get list of all available providers.
        
        Returns:
            List of provider names
        """
        return self._factory.list_providers()
    
    def get_provider_status(self, provider_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get status of all providers or a specific provider.
        
        Args:
            provider_name: Optional provider name to check
            
        Returns:
            Status information dictionary
        """
        return self._factory.health_check(provider_name)
    
    def get_supported_models(self, provider_name: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Get supported models for all providers or a specific provider.
        
        Args:
            provider_name: Optional provider name to filter results
            
        Returns:
            Dictionary mapping provider names to lists of supported models
        """
        return self._factory.get_supported_models(provider_name)
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate a configuration dictionary.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if configuration is valid, False otherwise
        """
        return self._factory.validate_config(config)
    
    def get_provider_info(self, provider_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Dictionary containing provider information
        """
        return self._factory.get_provider_info(provider_name)
    
    def get_model_info(self, provider_name: str, model_name: str) -> Dict[str, Any]:
        """
        Get information about a specific model.
        
        Args:
            provider_name: Name of the provider
            model_name: Name of the model
            
        Returns:
            Dictionary containing model information
        """
        return self._factory.get_model_info(provider_name, model_name)
    
    def register_custom_provider(self, provider: BaseProvider):
        """
        Register a custom provider.
        
        Args:
            provider: Provider instance to register
        """
        self._factory.register_provider(provider)
        logger.info(f"Registered custom provider: {provider.provider_name}")
    
    def set_default_provider(self, provider_name: str):
        """
        Set the default provider.
        
        Args:
            provider_name: Name of the provider to set as default
        """
        if not self._factory.get_provider(provider_name):
            raise ValueError(f"Provider '{provider_name}' not found")
        
        self._default_provider = provider_name
        logger.info(f"Set default provider to: {provider_name}")
    
    def set_default_model(self, model_name: str):
        """
        Set the default model.
        
        Args:
            model_name: Name of the model to set as default
        """
        self._default_model = model_name
        logger.info(f"Set default model to: {model_name}")
    
    def get_default_provider(self) -> Optional[str]:
        """
        Get the current default provider.
        
        Returns:
            Name of the default provider or None
        """
        return self._default_provider
    
    def get_default_model(self) -> Optional[str]:
        """
        Get the current default model.
        
        Returns:
            Name of the default model or None
        """
        return self._default_model
    
    def create_config_from_env(self) -> Dict[str, Any]:
        """
        Create configuration from environment variables.
        
        Returns:
            Configuration dictionary based on environment variables
        """
        config = {}
        
        # Get provider from environment
        provider = os.getenv("LLM_PROVIDER", self._default_provider)
        if provider:
            config["provider"] = provider
        
        # Get model from environment
        model = os.getenv("LLM_MODEL", self._default_model)
        if model:
            config["model"] = model
        
        # Get common parameters from environment
        temperature = os.getenv("LLM_TEMPERATURE")
        if temperature:
            try:
                config["temperature"] = float(temperature)
            except ValueError:
                logger.warning(f"Invalid temperature value: {temperature}")
        
        max_tokens = os.getenv("LLM_MAX_TOKENS")
        if max_tokens:
            try:
                config["max_tokens"] = int(max_tokens)
            except ValueError:
                logger.warning(f"Invalid max_tokens value: {max_tokens}")
        
        streaming = os.getenv("LLM_STREAMING", "false").lower()
        config["streaming"] = streaming in ("true", "1", "yes")
        
        # Get provider-specific parameters
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                config["api_key"] = api_key
        
        elif provider == "ollama":
            base_url = os.getenv("OLLAMA_BASE_URL")
            if base_url:
                config["base_url"] = base_url
        
        elif provider == "gemini":
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                config["api_key"] = api_key
        
        return config
    
    def get_working_providers(self) -> List[str]:
        """
        Get list of providers that are currently working (pass health check).
        
        Returns:
            List of working provider names
        """
        working_providers = []
        status = self.get_provider_status()
        
        for provider_name, provider_status in status.items():
            if provider_status.get("status") == "healthy":
                working_providers.append(provider_name)
        
        return working_providers
    
    def get_best_available_provider(self) -> Optional[str]:
        """
        Get the best available provider based on health status and preferences.
        
        Returns:
            Name of the best available provider or None
        """
        # First check if default provider is working
        if self._default_provider:
            status = self.get_provider_status(self._default_provider)
            if status.get("status") == "healthy":
                return self._default_provider
        
        # Check all working providers
        working_providers = self.get_working_providers()
        if working_providers:
            # Prefer local providers (ollama) over cloud providers
            if "ollama" in working_providers:
                return "ollama"
            return working_providers[0]
        
        return None
    
    def create_model_with_fallback(self, config: Optional[Dict[str, Any]] = None) -> BaseLanguageModel:
        """
        Create a model with fallback to working providers.
        
        Args:
            config: Optional configuration dictionary
            
        Returns:
            Configured language model instance
            
        Raises:
            RuntimeError: If no working providers are available
        """
        if config is None:
            config = self.get_default_config()
        
        # Try to create model with provided config
        try:
            return self._factory.create_model(config)
        except Exception as e:
            logger.warning(f"Failed to create model with config: {e}")
        
        # Try to find a working provider and create model
        best_provider = self.get_best_available_provider()
        if not best_provider:
            raise RuntimeError("No working LLM providers available")
        
        # Create minimal config for the working provider
        fallback_config = {
            "provider": best_provider,
            "model": self._get_default_model_for_provider(best_provider),
            "temperature": 0.7,
            "max_tokens": 1000,
            "streaming": False
        }
        
        logger.info(f"Using fallback provider: {best_provider}")
        return self._factory.create_model(fallback_config)
    
    def _get_default_model_for_provider(self, provider_name: str) -> str:
        """
        Get default model for a specific provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Default model name for the provider
        """
        provider_defaults = {
            "openai": "gpt-3.5-turbo",
            "ollama": "llama3.2",
            "gemini": "models/gemini-1.5-flash"
        }
        
        return provider_defaults.get(provider_name, "gpt-3.5-turbo")


# Global provider manager instance
_provider_manager_instance: Optional[ProviderManager] = None


def get_provider_manager() -> ProviderManager:
    """
    Get the global provider manager instance.
    
    Returns:
        Global ProviderManager instance
    """
    global _provider_manager_instance
    if _provider_manager_instance is None:
        _provider_manager_instance = ProviderManager()
    return _provider_manager_instance


def create_model(config: Optional[Dict[str, Any]] = None) -> BaseLanguageModel:
    """
    Convenience function to create a model using the global provider manager.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured language model instance
    """
    return get_provider_manager().create_model(config)


def create_model_with_fallback(config: Optional[Dict[str, Any]] = None) -> BaseLanguageModel:
    """
    Convenience function to create a model with fallback using the global provider manager.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured language model instance
    """
    return get_provider_manager().create_model_with_fallback(config)


def get_provider_status(provider_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to get provider status using the global provider manager.
    
    Args:
        provider_name: Optional provider name to check
        
    Returns:
        Status information dictionary
    """
    return get_provider_manager().get_provider_status(provider_name) 