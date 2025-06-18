"""
This service encapsulates all interactions with Large Language Models (LLMs).

It provides a centralized place for prompt engineering and processing,
making the GraphQL resolvers cleaner and more focused on business logic.
"""
import logging
from typing import List, Dict, Any

from litellm import acompletion
from pydantic import BaseModel

from agent_service.api.types.suggestion_types import PerformanceReview

logger = logging.getLogger(__name__)


class LLMService:
    """
    A service for handling all LLM-related tasks like summarization
    and structured data extraction.
    """

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

        prompt = f"""
        As an AI companion, your task is to provide a brief, insightful summary based on the user's recent journal entries.
        Analyze the following entries and identify the main themes, recurring thoughts, or significant events.
        The summary should be gentle, encouraging, and forward-looking, like a friendly observer.
        Do not be overly conversational or ask questions. Focus on synthesizing the information into a cohesive insight.

        Journal Entries:
        {content_block}

        Synthesize these entries into a single, concise paragraph of 2-4 sentences.
        """

        try:
            response = await acompletion(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=250,
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

        prompt = f"""
        Analyze the following journal entries from the past two weeks to generate a performance review.
        The user is focused on self-improvement. Your task is to identify one key success and one primary area for improvement.
        Based on this analysis, create a new, targeted journaling prompt to help them reflect further.

        Journal Entries:
        {content_block}

        Based on these entries, provide the following in a structured format:
        1.  **Key Success**: A specific, positive achievement or consistent behavior.
        2.  **Improvement Area**: A constructive, actionable area where the user can focus their efforts.
        3.  **Journal Prompt**: A new, open-ended question that encourages reflection on the improvement area.

        Please format your response as follows:
        SUCCESS: [Your identified key success here]
        IMPROVEMENT: [Your identified improvement area here]
        PROMPT: [Your generated journal prompt here]
        """

        try:
            response = await acompletion(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=500,
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