"""
Service factory for managing service implementations.

This factory provides a way to switch between different service
implementations based on configuration or feature flags.
"""

import os
import logging
from typing import Optional

from agent_service.services.llm_service import LLMService
from agent_service.llms.prompts.service import PromptService
from agent_service.llms.prompts.models import PromptConfig, StoreType
from agent_service.llms.prompts.stores.memory import InMemoryPromptStore

logger = logging.getLogger(__name__)


class ServiceFactory:
    """
    Factory for creating service instances.
    
    This factory provides methods to create service implementations
    based on configuration, with automatic prompt setup support.
    """
    
    # Environment variable for service selection
    SERVICE_TYPE_ENV = "LLM_SERVICE_TYPE"
    
    # Service types
    SERVICE_TYPE_DEFAULT = "default"
    SERVICE_TYPE_CUSTOM = "custom"
    
    def __init__(self):
        """Initialize the service factory."""
        self._service_type = os.getenv(self.SERVICE_TYPE_ENV, self.SERVICE_TYPE_DEFAULT)
        self._prompt_service: Optional[PromptService] = None
    
    def get_llm_service(self, force_type: Optional[str] = None) -> LLMService:
        """
        Get an LLM service instance.
        
        Args:
            force_type: Optional service type to force (overrides environment)
            
        Returns:
            LLM service instance
        """
        service_type = force_type or self._service_type
        
        if service_type == self.SERVICE_TYPE_DEFAULT:
            logger.info("Creating default LLM service")
            return LLMService()
        
        elif service_type == self.SERVICE_TYPE_CUSTOM:
            logger.info("Creating custom LLM service")
            prompt_service = self._get_or_create_prompt_service()
            return LLMService(prompt_service)
        
        else:
            logger.warning(f"Unknown service type: {service_type}, falling back to default")
            return LLMService()
    
    def _get_or_create_prompt_service(self) -> PromptService:
        """Get or create a prompt service instance."""
        if self._prompt_service is None:
            # Create default prompt service with in-memory store
            config = PromptConfig(
                store_type=StoreType.MEMORY,
                enable_caching=True,
                cache_size=100,
                cache_ttl=3600
            )
            store = InMemoryPromptStore()
            self._prompt_service = PromptService(store=store, config=config)
        
        return self._prompt_service
    
    def get_prompt_service(self) -> Optional[PromptService]:
        """Get the prompt service instance if available."""
        return self._prompt_service
    
    def set_service_type(self, service_type: str) -> None:
        """Set the service type for future service creation."""
        self._service_type = service_type
    
    def get_service_type(self) -> str:
        """Get the current service type."""
        return self._service_type
    
    def health_check(self) -> dict:
        """Perform a health check on the factory and services."""
        health_info = {
            "service_type": self._service_type,
            "prompt_service_available": self._prompt_service is not None
        }
        
        if self._prompt_service:
            try:
                health_info["prompt_service_health"] = self._prompt_service.health_check()
            except Exception as e:
                health_info["prompt_service_health"] = {"error": str(e)}
        
        return health_info


# Global service factory instance
_service_factory = ServiceFactory()


def get_llm_service(force_type: Optional[str] = None) -> LLMService:
    """
    Get an LLM service instance using the global factory.
    
    Args:
        force_type: Optional service type to force
        
    Returns:
        LLM service instance
    """
    return _service_factory.get_llm_service(force_type)


def get_service_factory() -> ServiceFactory:
    """Get the global service factory instance."""
    return _service_factory 