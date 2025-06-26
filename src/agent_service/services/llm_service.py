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
from agent_service.llms.prompts.factory import PromptServiceFactory, get_prompt_service

logger = logging.getLogger(__name__)


class LLMService:
    """
    LLM service using the new prompt system with LangChain.
    
    This service provides LLM functionality using the new prompt storage
    and rendering system with LangChain for better integration with LangGraph workflows.
    """

    def __init__(self, prompt_service: PromptService = None, llm=None):
        """
        Initialize the LLM service.
        
        Args:
            prompt_service: Optional prompt service instance. If not provided,
                          creates a default service based on environment configuration.
            llm: Optional LangChain LLM instance. If not provided, will be created per request.
        """
        if prompt_service is None:
            # Use the configurable factory to create prompt service
            self.prompt_service = PromptServiceFactory.create_from_environment()
            logger.info("Created LLM service with environment-configured prompt service")
        else:
            self.prompt_service = prompt_service
            logger.info("Created LLM service with provided prompt service")
        
        # Store the LLM instance (will be configured per request if not provided)
        self.llm = llm
    
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
            
            # Create the message and invoke the LLM
            message = HumanMessage(content=rendered_prompt)
            response = await self.llm.ainvoke([message])
            
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
            
            # Use stored LLM or create new one with prompt metadata
            if self.llm is None:
                self.llm = ChatOpenAI(
                    model=metadata.get("model", "gpt-4o"),
                    temperature=metadata.get("temperature", 0.5),
                    max_tokens=metadata.get("max_tokens", 500),
                )
            
            # Create the message and invoke the LLM
            message = HumanMessage(content=rendered_prompt)
            response = self.llm.invoke([message])
            
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
            
            return {
                "status": "healthy" if not missing_prompts else "degraded",
                "prompt_service": prompt_health,
                "missing_prompts": missing_prompts,
                "llm_configured": self.llm is not None
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            } 