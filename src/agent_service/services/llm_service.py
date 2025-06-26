"""
LLM service using the new prompt system with LangChain.

This service provides LLM functionality using the new prompt storage
and rendering system with LangChain for better integration with LangGraph workflows.
"""

import logging
import os
from typing import List, Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from agent_service.api.types.suggestion_types import PerformanceReview
from agent_service.llms.prompts.service import PromptService
from agent_service.llms.prompts.models import PromptConfig, StoreType
from agent_service.llms.prompts.stores.local import LocalPromptStore
from agent_service.llms.prompts.stores.memory import InMemoryPromptStore
from agent_service.llms.prompts.init_prompts import create_default_prompts

logger = logging.getLogger(__name__)


class LLMService:
    """
    LLM service using the new prompt system with LangChain.
    
    This service provides LLM functionality using the new prompt storage
    and rendering system with LangChain for better integration with LangGraph workflows.
    """

    def __init__(self, prompt_service: PromptService = None, store_path: str = None, llm=None):
        """
        Initialize the LLM service.
        
        Args:
            prompt_service: Optional prompt service instance. If not provided,
                          creates a default service based on configuration.
            store_path: Path to store prompts (used if prompt_service is None)
            llm: Optional LangChain LLM instance. If not provided, will be created per request.
        """
        if prompt_service is None:
            # Get storage configuration from environment
            store_type = os.getenv("PROMPT_STORE_TYPE", "memory")
            store_path = store_path or os.getenv("PROMPT_STORE_PATH", "prompts")
            
            # Create prompt service based on configuration
            if store_type == "local":
                config = PromptConfig(
                    store_type=StoreType.LOCAL,
                    store_path=store_path,
                    enable_caching=True,
                    cache_size=100,
                    cache_ttl=3600
                )
                store = LocalPromptStore(store_path)
            else:  # Default to memory
                config = PromptConfig(
                    store_type=StoreType.MEMORY,
                    enable_caching=True,
                    cache_size=100,
                    cache_ttl=3600
                )
                store = InMemoryPromptStore()
            
            self.prompt_service = PromptService(store=store, config=config)
            
            # Initialize prompts if they don't exist
            self._ensure_prompts_exist()
        else:
            self.prompt_service = prompt_service
        
        # Store the LLM instance (will be configured per request if not provided)
        self.llm = llm
    
    def _ensure_prompts_exist(self) -> None:
        """Ensure required prompts exist in the store."""
        try:
            required_prompts = [
                ("journal_summary", "1.0"),
                ("performance_review", "1.0")
            ]
            
            missing_prompts = []
            for name, version in required_prompts:
                if not self.prompt_service.exists(name, version):
                    missing_prompts.append((name, version))
            
            if missing_prompts:
                logger.info(f"Missing prompts: {missing_prompts}, creating defaults...")
                # Create default prompts in the store
                self._create_default_prompts()
                
        except Exception as e:
            logger.error(f"Error ensuring prompts exist: {e}")
    
    def _create_default_prompts(self) -> None:
        """Create default prompts in the store."""
        # Create journal summary prompt
        journal_summary = {
            "name": "journal_summary",
            "version": "1.0",
            "content": """As an AI companion, your task is to provide a brief, insightful summary based on the user's recent journal entries.
Analyze the following entries and identify the main themes, recurring thoughts, or significant events.
The summary should be gentle, encouraging, and forward-looking, like a friendly observer.
Do not be overly conversational or ask questions. Focus on synthesizing the information into a cohesive insight.

Journal Entries:
{{ content_block }}

Synthesize these entries into a single, concise paragraph of 2-4 sentences.""",
            "variables": ["content_block"],
            "metadata": {
                "category": "journal",
                "type": "summary",
                "model": "gpt-4o",
                "temperature": 0.7,
                "max_tokens": 250,
                "description": "Generate a concise summary of journal entries"
            }
        }
        
        # Create performance review prompt
        performance_review = {
            "name": "performance_review",
            "version": "1.0",
            "content": """Analyze the following journal entries from the past two weeks to generate a performance review.
The user is focused on self-improvement. Your task is to identify one key success and one primary area for improvement.
Based on this analysis, create a new, targeted journaling prompt to help them reflect further.

Journal Entries:
{{ content_block }}

Based on these entries, provide the following in a structured format:
1.  **Key Success**: A specific, positive achievement or consistent behavior.
2.  **Improvement Area**: A constructive, actionable area where the user can focus their efforts.
3.  **Journal Prompt**: A new, open-ended question that encourages reflection on the improvement area.

Please format your response as follows:
SUCCESS: [Your identified key success here]
IMPROVEMENT: [Your identified improvement area here]
PROMPT: [Your generated journal prompt here]""",
            "variables": ["content_block"],
            "metadata": {
                "category": "journal",
                "type": "review",
                "model": "gpt-4o",
                "temperature": 0.5,
                "max_tokens": 500,
                "description": "Generate a structured performance review from journal entries",
                "output_format": "structured"
            }
        }
        
        # Save prompts to store
        from agent_service.llms.prompts.models import PromptInfo
        
        for prompt_data in [journal_summary, performance_review]:
            if not self.prompt_service.exists(prompt_data["name"], prompt_data["version"]):
                prompt_info = PromptInfo(**prompt_data)
                self.prompt_service.save_prompt(prompt_info)
                logger.info(f"Created prompt: {prompt_info.name}:{prompt_info.version}")
    
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
            
            # Use stored LLM or create new one with prompt metadata
            if self.llm is None:
                self.llm = ChatOpenAI(
                    model=metadata.get("model", "gpt-4o"),
                    temperature=metadata.get("temperature", 0.7),
                    max_tokens=metadata.get("max_tokens", 250),
                )
            
            # Create message and invoke LLM
            message = HumanMessage(content=rendered_prompt)
            response = await self.llm.ainvoke([message])
            summary = response.content.strip()
            
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
            
            # Use stored LLM or create new one with prompt metadata
            if self.llm is None:
                self.llm = ChatOpenAI(
                    model=metadata.get("model", "gpt-4o"),
                    temperature=metadata.get("temperature", 0.5),
                    max_tokens=metadata.get("max_tokens", 500),
                )
            
            # Create message and invoke LLM
            message = HumanMessage(content=rendered_prompt)
            response = await self.llm.ainvoke([message])
            raw_text = response.content.strip()

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