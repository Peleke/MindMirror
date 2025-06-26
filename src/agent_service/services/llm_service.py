"""
LLM service using the new prompt system with LangChain.

This service provides LLM functionality using the new prompt storage
and rendering system with LangChain for better integration with LangGraph workflows.
"""

import logging
import os
from typing import List, Dict, Any, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.language_models import BaseLanguageModel

from agent_service.api.types.suggestion_types import PerformanceReview
from agent_service.llms.prompts.service import PromptService
from agent_service.llms.prompts.factory import PromptServiceFactory, get_prompt_service
from agent_service.llms.provider_manager import ProviderManager, get_provider_manager

logger = logging.getLogger(__name__)


class LLMService:
    """
    LLM service using the new prompt system with LangChain.
    
    This service provides LLM functionality using the new prompt storage
    and rendering system with LangChain for better integration with LangGraph workflows.
    
    Now integrates with the new provider system for enhanced LLM management and fallbacks.
    """

    def __init__(
        self, 
        prompt_service: Optional[PromptService] = None, 
        llm: Optional[BaseLanguageModel] = None,
        provider_manager: Optional[ProviderManager] = None
    ):
        """
        Initialize the LLM service.
        
        Args:
            prompt_service: Optional prompt service instance. If not provided,
                          creates a default service based on environment configuration.
            llm: DEPRECATED - Optional LangChain LLM instance. If not provided, will be created per request.
                 Use provider_manager for better LLM management.
            provider_manager: Optional provider manager instance. If not provided,
                            uses the global provider manager.
        """
        if prompt_service is None:
            # Use the configurable factory to create prompt service
            self.prompt_service = PromptServiceFactory.create_from_environment()
            logger.info("Created LLM service with environment-configured prompt service")
        else:
            self.prompt_service = prompt_service
            logger.info("Created LLM service with provided prompt service")
        
        # DEPRECATED: Store the LLM instance (will be configured per request if not provided)
        # This is kept for backward compatibility but should be replaced with provider_manager
        self.llm = llm
        
        # NEW: Provider manager for enhanced LLM management
        if provider_manager is None:
            self.provider_manager = get_provider_manager()
            logger.info("Created LLM service with global provider manager")
        else:
            self.provider_manager = provider_manager
            logger.info("Created LLM service with provided provider manager")
    
    def _get_llm_for_task(self, task_name: str, metadata: Dict[str, Any]) -> BaseLanguageModel:
        """
        Get an LLM instance configured for a specific task.
        
        Args:
            task_name: Name of the task (e.g., "journal_summary", "performance_review")
            metadata: Prompt metadata containing LLM configuration
            
        Returns:
            Configured LLM instance
        """
        try:
            # Try to create LLM using provider manager with fallback
            config = {
                "model": metadata.get("model", "gpt-4o"),
                "temperature": metadata.get("temperature", 0.7),
                "max_tokens": metadata.get("max_tokens", 1000),
                "streaming": metadata.get("streaming", False)
            }
            
            # Use provider manager to create LLM with fallback
            return self.provider_manager.create_model_with_fallback(config)
            
        except Exception as e:
            logger.warning(f"Failed to create LLM with provider manager: {e}")
            
            # DEPRECATED: Fallback to direct ChatOpenAI creation
            logger.warning("Falling back to direct ChatOpenAI creation (DEPRECATED)")
            return ChatOpenAI(
                model=metadata.get("model", "gpt-4o"),
                temperature=metadata.get("temperature", 0.7),
                max_tokens=metadata.get("max_tokens", 1000),
            )

    async def get_journal_summary(self, journal_entries: List[Dict[str, Any]]) -> str:
        """
        Generates a concise summary from a list of journal entries.

        Args:
            journal_entries: A list of journal entries, each represented as a dict.

        Returns:
            A string containing the AI-generated summary.
        """
        if not journal_entries:
            return "No recent journal entries to summarize."

        # Consolidate journal content into a single block for the prompt
        content_block = "\n\n---\n\n".join(
            [entry.get("text", "") for entry in journal_entries]
        )

        try:
            # Render the prompt using the prompt service
            rendered_prompt = self.prompt_service.render_prompt(
                "journal_summary",
                {"content_block": content_block}
            )
            
            # Get prompt metadata for LLM configuration
            prompt_info = self.prompt_service.get_prompt("journal_summary")
            metadata = prompt_info.metadata
            
            # Get LLM using new provider system
            llm = self._get_llm_for_task("journal_summary", metadata)
            
            # Create the message and invoke the LLM
            message = HumanMessage(content=rendered_prompt)
            response = await llm.ainvoke([message])
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating journal summary: {e}")
            return f"Error generating summary: {str(e)}"

    async def get_performance_review(
        self, journal_entries: List[Dict[str, Any]]
    ) -> PerformanceReview:
        """
        Generates a performance review from a list of journal entries.

        Args:
            journal_entries: A list of journal entries, each represented as a dict.

        Returns:
            A PerformanceReview object containing the AI-generated review.
        """
        if not journal_entries:
            return PerformanceReview(
                key_success="No recent journal entries to review.",
                improvement_area="Consider adding more journal entries for better insights.",
                journal_prompt="What would you like to focus on in your next journal entry?"
            )

        # Consolidate journal content into a single block for the prompt
        content_block = "\n\n---\n\n".join(
            [entry.get("text", "") for entry in journal_entries]
        )

        try:
            # Render the prompt using the prompt service
            rendered_prompt = self.prompt_service.render_prompt(
                "performance_review",
                {"content_block": content_block}
            )
            
            # Get prompt metadata for LLM configuration
            prompt_info = self.prompt_service.get_prompt("performance_review")
            metadata = prompt_info.metadata
            
            # Get LLM using new provider system
            llm = self._get_llm_for_task("performance_review", metadata)
            
            # Create the message and invoke the LLM
            message = HumanMessage(content=rendered_prompt)
            response = llm.invoke([message])

            # Parse the structured response
            return self._parse_performance_review_response(response.content)
            
        except Exception as e:
            logger.error(f"Error generating performance review: {e}")
            return PerformanceReview(
                key_success="Unable to generate performance review.",
                improvement_area="Consider adding more detailed journal entries.",
                journal_prompt="What would you like to focus on in your next journal entry?"
            )
    
    def _parse_performance_review_response(self, response: str) -> PerformanceReview:
        """
        Parse the structured response from the LLM into a PerformanceReview object.
        
        Args:
            response: The raw response from the LLM
            
        Returns:
            Parsed PerformanceReview object
        """
        try:
            # Extract sections from the structured response
            lines = response.strip().split('\n')
            key_success = ""
            improvement_area = ""
            journal_prompt = ""
            
            current_section = None
            for line in lines:
                line = line.strip()
                if line.startswith("SUCCESS:"):
                    current_section = "success"
                    key_success = line.replace("SUCCESS:", "").strip()
                elif line.startswith("IMPROVEMENT:"):
                    current_section = "improvement"
                    improvement_area = line.replace("IMPROVEMENT:", "").strip()
                elif line.startswith("PROMPT:"):
                    current_section = "prompt"
                    journal_prompt = line.replace("PROMPT:", "").strip()
                elif current_section and line:
                    # Continue building the current section
                    if current_section == "success":
                        key_success += " " + line
                    elif current_section == "improvement":
                        improvement_area += " " + line
                    elif current_section == "prompt":
                        journal_prompt += " " + line
            
            # Clean up the extracted text
            key_success = key_success.strip()
            improvement_area = improvement_area.strip()
            journal_prompt = journal_prompt.strip()
            
            # Provide defaults if sections are missing
            if not key_success:
                key_success = "No specific success identified in the review period."
            if not improvement_area:
                improvement_area = "Consider adding more detailed journal entries for better insights."
            if not journal_prompt:
                journal_prompt = "What would you like to focus on in your next journal entry?"
            
            return PerformanceReview(
                key_success=key_success,
                improvement_area=improvement_area,
                journal_prompt=journal_prompt
            )
            
        except Exception as e:
            logger.error(f"Error parsing performance review response: {e}")
            return PerformanceReview(
                key_success="Unable to parse performance review response.",
                improvement_area="Consider adding more detailed journal entries.",
                journal_prompt="What would you like to focus on in your next journal entry?"
            )
    
    # NEW: Provider-aware methods
    
    def get_llm(self, task: str, provider: Optional[str] = None, overrides: Optional[Dict[str, Any]] = None) -> BaseLanguageModel:
        """
        Get an LLM instance for a specific task with optional provider and overrides.
        
        Args:
            task: Name of the task (e.g., "journal_summary", "performance_review")
            provider: Optional provider name to use (e.g., "openai", "ollama", "gemini")
            overrides: Optional configuration overrides
            
        Returns:
            Configured LLM instance
        """
        try:
            # Get prompt metadata for the task
            prompt_info = self.prompt_service.get_prompt(task)
            metadata = prompt_info.metadata
            
            # Start with metadata configuration
            config = {
                "model": metadata.get("model", "gpt-4o"),
                "temperature": metadata.get("temperature", 0.7),
                "max_tokens": metadata.get("max_tokens", 1000),
                "streaming": metadata.get("streaming", False)
            }
            
            # Apply overrides if provided
            if overrides:
                config.update(overrides)
            
            # Use specific provider if requested
            if provider:
                config["provider"] = provider
                return self.provider_manager.create_model(config)
            else:
                # Use provider manager with fallback
                return self.provider_manager.create_model_with_fallback(config)
                
        except Exception as e:
            logger.error(f"Error getting LLM for task '{task}': {e}")
            raise
    
    def get_provider_status(self, provider_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get status of LLM providers.
        
        Args:
            provider_name: Optional provider name to check
            
        Returns:
            Provider status information
        """
        return self.provider_manager.get_provider_status(provider_name)
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available LLM providers.
        
        Returns:
            List of available provider names
        """
        return self.provider_manager.list_available_providers()
    
    def get_working_providers(self) -> List[str]:
        """
        Get list of working LLM providers.
        
        Returns:
            List of working provider names
        """
        return self.provider_manager.get_working_providers()
    
    # DEPRECATED: Legacy methods for backward compatibility
    
    def get_prompt_service(self) -> PromptService:
        """Get the underlying prompt service."""
        return self.prompt_service
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the LLM service.
        
        Returns:
            Health status dictionary
        """
        try:
            # Check prompt service health
            prompt_health = self.prompt_service.health_check()
            
            # Check if required prompts exist
            required_prompts = ["journal_summary", "performance_review"]
            missing_prompts = []
            
            for prompt_name in required_prompts:
                try:
                    self.prompt_service.get_prompt(prompt_name)
                except Exception:
                    missing_prompts.append(prompt_name)
            
            # Check provider status
            provider_status = self.get_provider_status()
            working_providers = self.get_working_providers()
            
            return {
                "status": "healthy" if not missing_prompts and working_providers else "degraded",
                "prompt_service": prompt_health,
                "missing_prompts": missing_prompts,
                "provider_status": provider_status,
                "working_providers": working_providers,
                "llm_configured": self.llm is not None  # DEPRECATED
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            } 