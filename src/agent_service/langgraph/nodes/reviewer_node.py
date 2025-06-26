"""
Reviewer node for performance review generation.

This node generates performance reviews from journal entries using the LLMService.
"""

import logging
from typing import Any, Dict, List

from agent_service.langgraph.nodes.base import LLMNode
from agent_service.langgraph.state import JournalAgentState, StateManager

logger = logging.getLogger(__name__)


class ReviewerNode(LLMNode[JournalAgentState]):
    """
    Node for generating performance reviews.
    
    Uses the existing LLMService.get_performance_review() method to maintain
    compatibility while providing graph orchestration capabilities.
    """
    
    def __init__(
        self,
        name: str = "reviewer",
        description: str = "Generates performance reviews from journal entries",
        provider: str = None,
        overrides: Dict[str, Any] = None,
    ):
        """
        Initialize the reviewer node.
        
        Args:
            name: Node name
            description: Node description
            provider: Optional LLM provider to use
            overrides: Optional configuration overrides
        """
        super().__init__(
            name=name,
            description=description,
            task="performance_review",
            provider=provider,
            overrides=overrides,
        )
    
    def execute(self, state: JournalAgentState) -> JournalAgentState:
        """
        Execute the reviewer node.
        
        Args:
            state: Current journal agent state
            
        Returns:
            Updated state with generated review
        """
        # Validate state
        if not self.validate_state(state):
            return StateManager.add_error(
                state,
                error="Invalid state for reviewer node",
                error_type="ValidationError",
            )
        
        # Check if we have journal entries
        if not state["journal_entries"]:
            self.logger.warning("No journal entries to review")
            return StateManager.set_performance_review(
                state,
                {
                    "key_success": "No recent journal entries to review.",
                    "improvement_area": "Consider adding more journal entries for better insights.",
                    "journal_prompt": "What would you like to focus on in your next journal entry?"
                },
            )
        
        try:
            # Generate review using LLMService
            review = self.llm_service.get_performance_review(state["journal_entries"])
            
            # Convert PerformanceReview object to dict for state
            review_dict = {
                "key_success": review.key_success,
                "improvement_area": review.improvement_area,
                "journal_prompt": review.journal_prompt,
            }
            
            # Update state with review
            updated_state = StateManager.set_performance_review(
                state,
                review_dict,
            )
            
            self.logger.info(f"Generated review for {state['entry_count']} entries")
            return updated_state
            
        except Exception as e:
            self.logger.error(f"Error generating review: {e}")
            return StateManager.add_error(
                state,
                error=f"Error generating review: {str(e)}",
                error_type=type(e).__name__,
            )
    
    def validate_state(self, state: JournalAgentState) -> bool:
        """
        Validate state for reviewer node.
        
        Args:
            state: The state to validate
            
        Returns:
            True if state is valid, False otherwise
        """
        # Call parent validation
        if not super().validate_state(state):
            return False
        
        # Check for required journal fields
        required_fields = ["journal_entries", "entry_count"]
        for field in required_fields:
            if field not in state:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        return True 