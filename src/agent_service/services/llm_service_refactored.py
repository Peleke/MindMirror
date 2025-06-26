"""
Refactored LLM service using the new prompt system.

This service provides the same functionality as the original LLMService
but uses the new prompt storage and rendering system.
"""

import logging
from typing import List, Dict, Any

from litellm import acompletion

from agent_service.api.types.suggestion_types import PerformanceReview
from agent_service.llms.prompts.service import PromptService
from agent_service.llms.prompts.models import PromptConfig, StoreType
from agent_service.llms.prompts.stores.memory import InMemoryPromptStore

logger = logging.getLogger(__name__)


class LLMServiceRefactored:
    """
    Refactored LLM service using the new prompt system.
    
    This service provides the same interface as the original LLMService
    but uses the new prompt storage and rendering system for better
    maintainability and flexibility.
    """

    def __init__(self, prompt_service: PromptService = None):
        """
        Initialize the refactored LLM service.
        
        Args:
            prompt_service: Optional prompt service instance. If not provided,
                          creates a default in-memory service.
        """
        if prompt_service is None:
            # Create default prompt service with in-memory store
            config = PromptConfig(
                store_type=StoreType.MEMORY,
                enable_caching=True,
                cache_size=100,
                cache_ttl=3600
            )
            store = InMemoryPromptStore()
            self.prompt_service = PromptService(store=store, config=config)
        else:
            self.prompt_service = prompt_service
    
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
            
            response = await acompletion(
                model=metadata.get("model", "gpt-4o"),
                messages=[{"role": "user", "content": rendered_prompt}],
                temperature=metadata.get("temperature", 0.7),
                max_tokens=metadata.get("max_tokens", 250),
            )
            summary = response.choices[0].message.content.strip()
            logger.info("Successfully generated journal summary.")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating journal summary from LLM: {e}")
            return "I am having trouble summarizing your recent thoughts at the moment. Please try again later."

    async def generate_performance_review(
        self, journal_entries: List[Dict[str, Any]]
    ) -> PerformanceReview:
        """
        Generates a structured performance review from a list of journal entries.

        Args:
            journal_entries: A list of relevant journal entries from semantic search.

        Returns:
            A PerformanceReview object with success, improvement area, and a prompt.
        """
        if not journal_entries:
            return PerformanceReview(
                key_success="No recent journal entries found to generate a review.",
                improvement_area="Try to journal more consistently to get a review.",
                journal_prompt="What is one small step you can take today to get back on track?",
            )

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
            
            response = await acompletion(
                model=metadata.get("model", "gpt-4o"),
                messages=[{"role": "user", "content": rendered_prompt}],
                temperature=metadata.get("temperature", 0.5),
                max_tokens=metadata.get("max_tokens", 500),
            )
            raw_text = response.choices[0].message.content.strip()

            # Parse the structured response
            key_success = raw_text.split("SUCCESS:")[1].split("IMPROVEMENT:")[0].strip()
            improvement_area = raw_text.split("IMPROVEMENT:")[1].split("PROMPT:")[0].strip()
            journal_prompt = raw_text.split("PROMPT:")[1].strip()

            logger.info("Successfully generated performance review.")
            return PerformanceReview(
                key_success=key_success,
                improvement_area=improvement_area,
                journal_prompt=journal_prompt,
            )
            
        except Exception as e:
            logger.error(f"Error generating performance review from LLM: {e}")
            # Return a default error state
            return PerformanceReview(
                key_success="Could not generate a review at this time.",
                improvement_area="There was an error processing your journal entries.",
                journal_prompt="How do you feel about your progress over the last two weeks?",
            )
    
    def get_prompt_service(self) -> PromptService:
        """Get the underlying prompt service."""
        return self.prompt_service
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the service."""
        try:
            # Check if required prompts exist
            journal_summary_exists = self.prompt_service.exists("journal_summary", "1.0")
            performance_review_exists = self.prompt_service.exists("performance_review", "1.0")
            
            # Check prompt service health
            prompt_service_health = self.prompt_service.health_check()
            
            return {
                "status": "healthy" if journal_summary_exists and performance_review_exists else "degraded",
                "journal_summary_prompt_available": journal_summary_exists,
                "performance_review_prompt_available": performance_review_exists,
                "prompt_service_health": prompt_service_health
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "journal_summary_prompt_available": False,
                "performance_review_prompt_available": False
            } 