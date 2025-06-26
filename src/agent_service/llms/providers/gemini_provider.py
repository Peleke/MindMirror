"""
Gemini provider implementation for LangChain integration.

This module provides the GeminiProvider class that handles Google Gemini model
creation with API key fallback and streaming support.
"""

import logging
from typing import Dict, List, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI

from .base import BaseProvider

logger = logging.getLogger(__name__)


class GeminiProvider(BaseProvider):
    """
    Gemini provider for LangChain integration.
    
    Handles Google Gemini model creation with proper API key management,
    configuration validation, and streaming support.
    """
    
    def __init__(self):
        """Initialize the Gemini provider."""
        super().__init__("gemini")
        self._supported_models = [
            "models/gemini-pro",
            "models/gemini-1.5-pro",
            "models/gemini-1.5-pro-latest",
            "models/gemini-1.5-flash",
            "models/gemini-1.5-flash-latest",
            "models/gemini-pro-vision",
            "models/gemini-1.5-pro-vision-latest"
        ]
    
    def create_model(self, config: Dict[str, Any]) -> ChatGoogleGenerativeAI:
        """
        Create a Gemini ChatGoogleGenerativeAI model instance.
        
        Args:
            config: Configuration dictionary containing model parameters
            
        Returns:
            Configured ChatGoogleGenerativeAI instance
            
        Raises:
            ValueError: If required configuration is missing or invalid
            RuntimeError: If model creation fails
        """
        try:
            # Validate configuration
            if not self.validate_config(config):
                raise ValueError(f"Invalid configuration for {self.provider_name} provider")
            
            # Get API key from config or environment
            api_key = self._get_api_key(config, "GOOGLE_API_KEY")
            
            # Extract model parameters
            model_name = config.get("model", "models/gemini-1.5-pro-latest")
            temperature = config.get("temperature", 0.7)
            max_tokens = config.get("max_tokens", 1000)
            streaming = config.get("streaming", False)
            
            # Create model configuration
            model_config = {
                "google_api_key": api_key,
                "model": model_name,
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                "streaming": streaming
            }
            
            # Add optional parameters if provided
            if "top_p" in config:
                model_config["top_p"] = config["top_p"]
            
            if "top_k" in config:
                model_config["top_k"] = config["top_k"]
            
            if "safety_settings" in config:
                model_config["safety_settings"] = config["safety_settings"]
            
            if "generation_config" in config:
                model_config["generation_config"] = config["generation_config"]
            
            # Log model creation
            self._log_model_creation(model_name, model_config)
            
            # Create and return the model
            return ChatGoogleGenerativeAI(**model_config)
            
        except Exception as e:
            logger.error(f"Failed to create Gemini model: {e}")
            raise RuntimeError(f"Gemini model creation failed: {str(e)}")
    
    def get_supported_models(self) -> List[str]:
        """
        Get list of supported Gemini models.
        
        Returns:
            List of supported model identifiers
        """
        return self._supported_models.copy()
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate Gemini configuration.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if configuration is valid, False otherwise
        """
        # Check for required model field
        if not self._validate_required_fields(config, ["model"]):
            return False
        
        # Validate model name
        model_name = config.get("model")
        if model_name not in self._supported_models:
            logger.warning(f"Unsupported Gemini model: {model_name}")
            # Don't fail validation for unsupported models - they might still work
            # Just log a warning
        
        # Validate temperature range
        temperature = config.get("temperature", 0.7)
        if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
            logger.warning(f"Invalid temperature value: {temperature}. Must be between 0 and 2.")
            return False
        
        # Validate max_tokens
        max_tokens = config.get("max_tokens", 1000)
        if not isinstance(max_tokens, int) or max_tokens <= 0:
            logger.warning(f"Invalid max_tokens value: {max_tokens}. Must be positive integer.")
            return False
        
        # Validate top_p if provided
        if "top_p" in config:
            top_p = config["top_p"]
            if not isinstance(top_p, (int, float)) or top_p < 0 or top_p > 1:
                logger.warning(f"Invalid top_p value: {top_p}. Must be between 0 and 1.")
                return False
        
        # Validate top_k if provided
        if "top_k" in config:
            top_k = config["top_k"]
            if not isinstance(top_k, int) or top_k <= 0:
                logger.warning(f"Invalid top_k value: {top_k}. Must be positive integer.")
                return False
        
        return True
    
    def _get_test_config(self) -> Optional[Dict[str, Any]]:
        """
        Get a minimal test configuration for health checks.
        
        Returns:
            Minimal configuration dictionary or None if API key not available
        """
        # Check if API key is available
        api_key = self._get_api_key({}, "GOOGLE_API_KEY")
        if api_key:
            return {
                "model": "models/gemini-1.5-flash",  # Use fast model for health checks
                "temperature": 0.0,
                "max_tokens": 10,
                "streaming": False
            }
        return None
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get information about a specific Gemini model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary containing model information
        """
        model_info = {
            "models/gemini-pro": {
                "max_tokens": 30720,
                "supports_streaming": True,
                "supports_vision": False,
                "cost_per_1k_tokens": 0.0005
            },
            "models/gemini-1.5-pro": {
                "max_tokens": 1048576,  # 1M tokens
                "supports_streaming": True,
                "supports_vision": True,
                "cost_per_1k_tokens": 0.0035
            },
            "models/gemini-1.5-pro-latest": {
                "max_tokens": 1048576,  # 1M tokens
                "supports_streaming": True,
                "supports_vision": True,
                "cost_per_1k_tokens": 0.0035
            },
            "models/gemini-1.5-flash": {
                "max_tokens": 1048576,  # 1M tokens
                "supports_streaming": True,
                "supports_vision": True,
                "cost_per_1k_tokens": 0.000075
            },
            "models/gemini-1.5-flash-latest": {
                "max_tokens": 1048576,  # 1M tokens
                "supports_streaming": True,
                "supports_vision": True,
                "cost_per_1k_tokens": 0.000075
            },
            "models/gemini-pro-vision": {
                "max_tokens": 30720,
                "supports_streaming": True,
                "supports_vision": True,
                "cost_per_1k_tokens": 0.0005
            },
            "models/gemini-1.5-pro-vision-latest": {
                "max_tokens": 1048576,  # 1M tokens
                "supports_streaming": True,
                "supports_vision": True,
                "cost_per_1k_tokens": 0.0035
            }
        }
        
        return model_info.get(model_name, {})
    
    def get_safety_settings(self, level: str = "default") -> List[Dict[str, Any]]:
        """
        Get predefined safety settings for Gemini models.
        
        Args:
            level: Safety level ("default", "low", "high")
            
        Returns:
            List of safety settings dictionaries
        """
        safety_settings = {
            "default": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ],
            "low": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                }
            ],
            "high": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_LOW_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_LOW_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_LOW_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_LOW_AND_ABOVE"
                }
            ]
        }
        
        return safety_settings.get(level, safety_settings["default"]) 