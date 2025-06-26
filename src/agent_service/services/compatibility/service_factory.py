"""
Service factory for managing service implementations.

This factory provides a way to switch between legacy and new service
implementations based on configuration or feature flags.
"""

import os
import logging
from typing import Optional

from agent_service.services.llm_service import LLMService
from agent_service.services.llm_service_refactored import LLMServiceRefactored
from agent_service.llms.prompts.service import PromptService
from agent_service.llms.prompts.models import PromptConfig, StoreType
from agent_service.llms.prompts.stores.memory import InMemoryPromptStore
from agent_service.llms.prompts.migrations import PromptMigrator

logger = logging.getLogger(__name__)


class ServiceFactory:
    """
    Factory for creating service instances.
    
    This factory provides methods to create either legacy or new service
    implementations based on configuration, with automatic migration support.
    """
    
    # Environment variable for service selection
    SERVICE_TYPE_ENV = "LLM_SERVICE_TYPE"
    
    # Service types
    SERVICE_TYPE_LEGACY = "legacy"
    SERVICE_TYPE_REFACTORED = "refactored"
    SERVICE_TYPE_AUTO = "auto"  # Automatically choose based on prompt availability
    
    def __init__(self):
        """Initialize the service factory."""
        self._service_type = os.getenv(self.SERVICE_TYPE_ENV, self.SERVICE_TYPE_AUTO)
        self._prompt_service: Optional[PromptService] = None
        self._migrator: Optional[PromptMigrator] = None
    
    def get_llm_service(self, force_type: Optional[str] = None) -> LLMService:
        """
        Get an LLM service instance.
        
        Args:
            force_type: Optional service type to force (overrides environment)
            
        Returns:
            LLM service instance (legacy or refactored)
        """
        service_type = force_type or self._service_type
        
        if service_type == self.SERVICE_TYPE_LEGACY:
            logger.info("Creating legacy LLM service")
            return LLMService()
        
        elif service_type == self.SERVICE_TYPE_REFACTORED:
            logger.info("Creating refactored LLM service")
            prompt_service = self._get_or_create_prompt_service()
            return LLMServiceRefactored(prompt_service)
        
        elif service_type == self.SERVICE_TYPE_AUTO:
            logger.info("Auto-selecting LLM service type")
            return self._get_auto_service()
        
        else:
            logger.warning(f"Unknown service type: {service_type}, falling back to legacy")
            return LLMService()
    
    def _get_auto_service(self) -> LLMService:
        """
        Automatically select the best service type.
        
        Returns:
            LLM service instance
        """
        try:
            # Try to create refactored service with prompts
            prompt_service = self._get_or_create_prompt_service()
            
            # Check if required prompts are available
            if self._are_required_prompts_available(prompt_service):
                logger.info("Required prompts available, using refactored service")
                return LLMServiceRefactored(prompt_service)
            else:
                logger.warning("Required prompts not available, using legacy service")
                return LLMService()
                
        except Exception as e:
            logger.error(f"Error creating refactored service: {e}, falling back to legacy")
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
            
            # Try to migrate prompts if they don't exist
            self._migrate_prompts_if_needed()
        
        return self._prompt_service
    
    def _migrate_prompts_if_needed(self) -> None:
        """Migrate prompts if they don't exist in the store."""
        try:
            if not self._are_required_prompts_available(self._prompt_service):
                logger.info("Required prompts not found, attempting migration...")
                
                migrator = PromptMigrator(self._prompt_service)
                result = migrator.migrate_llm_service_prompts(dry_run=False)
                
                if result["success"]:
                    logger.info(f"Successfully migrated {result['migrated_count']} prompts")
                else:
                    logger.error(f"Failed to migrate prompts: {result['errors']}")
                    
        except Exception as e:
            logger.error(f"Error during prompt migration: {e}")
    
    def _are_required_prompts_available(self, prompt_service: PromptService) -> bool:
        """
        Check if required prompts are available.
        
        Args:
            prompt_service: The prompt service to check
            
        Returns:
            True if all required prompts are available
        """
        required_prompts = [
            ("journal_summary", "1.0"),
            ("performance_review", "1.0")
        ]
        
        for prompt_name, version in required_prompts:
            if not prompt_service.exists(prompt_name, version):
                return False
        
        return True
    
    def get_prompt_service(self) -> Optional[PromptService]:
        """Get the prompt service instance if available."""
        return self._prompt_service
    
    def get_migrator(self) -> Optional[PromptMigrator]:
        """Get the prompt migrator instance if available."""
        if self._prompt_service and self._migrator is None:
            self._migrator = PromptMigrator(self._prompt_service)
        return self._migrator
    
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
            "prompt_service_available": self._prompt_service is not None,
            "migrator_available": self._migrator is not None
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