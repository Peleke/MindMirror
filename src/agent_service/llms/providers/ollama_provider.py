"""
Ollama provider implementation for LangChain integration.

This module provides the OllamaProvider class that handles Ollama model
creation with Docker-aware base URL detection and local model support.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from langchain_ollama import ChatOllama

from .base import BaseProvider

logger = logging.getLogger(__name__)


class OllamaProvider(BaseProvider):
    """
    Ollama provider for LangChain integration.
    
    Handles Ollama model creation with Docker-aware base URL detection,
    local model support, and configuration validation.
    """
    
    def __init__(self):
        """Initialize the Ollama provider."""
        super().__init__("ollama")
        self._supported_models = [
            "llama2",
            "llama2:7b",
            "llama2:13b",
            "llama2:70b",
            "llama3.2",
            "llama3.2:3b",
            "llama3.2:8b",
            "llama3.2:70b",
            "mistral",
            "mistral:7b",
            "mistral:7b-instruct",
            "codellama",
            "codellama:7b",
            "codellama:13b",
            "codellama:34b",
            "nomic-embed-text",
            "phi3",
            "phi3:mini",
            "phi3:medium",
            "phi3:large"
        ]
    
    def create_model(self, config: Dict[str, Any]) -> ChatOllama:
        """
        Create an Ollama ChatOllama model instance.
        
        Args:
            config: Configuration dictionary containing model parameters
            
        Returns:
            Configured ChatOllama instance
            
        Raises:
            ValueError: If required configuration is missing or invalid
            RuntimeError: If model creation fails
        """
        try:
            # Validate configuration
            if not self.validate_config(config):
                raise ValueError(f"Invalid configuration for {self.provider_name} provider")
            
            # Extract model parameters
            model_name = config.get("model", "llama3.2")
            temperature = config.get("temperature", 0.7)
            streaming = config.get("streaming", False)
            
            # Get base URL with Docker detection
            base_url = self._get_base_url(config)
            
            # Create model configuration
            model_config = {
                "model": model_name,
                "base_url": base_url,
                "temperature": temperature,
                "streaming": streaming
            }
            
            # Add optional parameters if provided
            if "timeout" in config:
                model_config["timeout"] = config["timeout"]
            
            if "num_ctx" in config:
                model_config["num_ctx"] = config["num_ctx"]
            
            if "num_gpu" in config:
                model_config["num_gpu"] = config["num_gpu"]
            
            if "num_thread" in config:
                model_config["num_thread"] = config["num_thread"]
            
            # Log model creation
            self._log_model_creation(model_name, model_config)
            
            # Create and return the model
            return ChatOllama(**model_config)
            
        except Exception as e:
            logger.error(f"Failed to create Ollama model: {e}")
            raise RuntimeError(f"Ollama model creation failed: {str(e)}")
    
    def get_supported_models(self) -> List[str]:
        """
        Get list of supported Ollama models.
        
        Returns:
            List of supported model identifiers
        """
        return self._supported_models.copy()
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate Ollama configuration.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if configuration is valid, False otherwise
        """
        # Check for required model field
        if not self._validate_required_fields(config, ["model"]):
            return False
        
        # Validate model name (allow custom models not in our list)
        model_name = config.get("model")
        if not model_name:
            logger.warning("No model specified for Ollama provider")
            return False
        
        # Validate temperature range
        temperature = config.get("temperature", 0.7)
        if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
            logger.warning(f"Invalid temperature value: {temperature}. Must be between 0 and 2.")
            return False
        
        # Validate optional numeric parameters
        for param in ["num_ctx", "num_gpu", "num_thread"]:
            if param in config:
                value = config[param]
                if not isinstance(value, int) or value <= 0:
                    logger.warning(f"Invalid {param} value: {value}. Must be positive integer.")
                    return False
        
        return True
    
    def _get_base_url(self, config: Dict[str, Any]) -> str:
        """
        Get Ollama base URL with Docker detection.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Base URL for Ollama API
        """
        # Check config first
        if "base_url" in config and config["base_url"]:
            return config["base_url"]
        
        # Check environment variable
        env_base_url = os.getenv("OLLAMA_BASE_URL")
        if env_base_url:
            return env_base_url
        
        # Check if we're in Docker
        if os.getenv("I_AM_IN_A_DOCKER_CONTAINER"):
            # In Docker, use host.docker.internal to access host Ollama
            return "http://host.docker.internal:11434"
        
        # Default to localhost
        return "http://localhost:11434"
    
    def _get_test_config(self) -> Optional[Dict[str, Any]]:
        """
        Get a minimal test configuration for health checks.
        
        Returns:
            Minimal configuration dictionary
        """
        return {
            "model": "llama3.2:3b",  # Use small model for health checks
            "temperature": 0.0,
            "streaming": False
        }
    
    def get_available_models(self) -> List[str]:
        """
        Get list of models available on the local Ollama instance.
        
        Returns:
            List of available model names
        """
        try:
            import requests
            
            base_url = self._get_base_url({})
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            else:
                logger.warning(f"Failed to get Ollama models: {response.status_code}")
                return []
                
        except Exception as e:
            logger.warning(f"Failed to get available Ollama models: {e}")
            return []
    
    def is_model_available(self, model_name: str) -> bool:
        """
        Check if a specific model is available on the local Ollama instance.
        
        Args:
            model_name: Name of the model to check
            
        Returns:
            True if model is available, False otherwise
        """
        available_models = self.get_available_models()
        return model_name in available_models
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get information about a specific Ollama model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary containing model information
        """
        model_info = {
            "llama2": {
                "max_tokens": 4096,
                "supports_streaming": True,
                "size_gb": 3.8
            },
            "llama2:7b": {
                "max_tokens": 4096,
                "supports_streaming": True,
                "size_gb": 3.8
            },
            "llama2:13b": {
                "max_tokens": 4096,
                "supports_streaming": True,
                "size_gb": 7.3
            },
            "llama2:70b": {
                "max_tokens": 4096,
                "supports_streaming": True,
                "size_gb": 39.0
            },
            "llama3.2": {
                "max_tokens": 8192,
                "supports_streaming": True,
                "size_gb": 4.7
            },
            "llama3.2:3b": {
                "max_tokens": 8192,
                "supports_streaming": True,
                "size_gb": 1.8
            },
            "llama3.2:8b": {
                "max_tokens": 8192,
                "supports_streaming": True,
                "size_gb": 4.7
            },
            "llama3.2:70b": {
                "max_tokens": 8192,
                "supports_streaming": True,
                "size_gb": 40.0
            },
            "mistral": {
                "max_tokens": 8192,
                "supports_streaming": True,
                "size_gb": 4.1
            },
            "mistral:7b": {
                "max_tokens": 8192,
                "supports_streaming": True,
                "size_gb": 4.1
            },
            "mistral:7b-instruct": {
                "max_tokens": 8192,
                "supports_streaming": True,
                "size_gb": 4.1
            },
            "nomic-embed-text": {
                "max_tokens": 8192,
                "supports_streaming": False,
                "size_gb": 0.5,
                "embedding_model": True
            }
        }
        
        return model_info.get(model_name, {}) 