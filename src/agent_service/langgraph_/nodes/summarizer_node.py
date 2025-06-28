"""
Summarizer node for journal processing.

This node generates summaries from journal entries using the LLMService.
"""

import logging
from typing import Any, Dict, List

from agent_service.langgraph_.nodes.base import LLMNode
from agent_service.langgraph_.state import JournalAgentState, StateManager

logger = logging.getLogger(__name__)


class SummarizerNode(LLMNode[JournalAgentState]):
    """
    Node for generating journal summaries.
    
    Uses the existing LLMService.get_journal_summary() method to maintain
    compatibility while providing graph orchestration capabilities.
    """
    
    def __init__(
        self,
        name: str = "summarizer",
        description: str = "Generates summaries from journal entries",
        provider: str = None,
        overrides: Dict[str, Any] = None,
    ):
        """
        Initialize the summarizer node.
        
        Args:
            name: Node name
            description: Node description
            provider: Optional LLM provider to use
            overrides: Optional configuration overrides
        """
        super().__init__(
            name=name,
            description=description,
            task="journal_summary",
            provider=provider,
            overrides=overrides,
        )
    
    def execute(self, state: JournalAgentState) -> JournalAgentState:
        """
        Execute the summarizer node.
        
        Args:
            state: Current journal agent state
            
        Returns:
            Updated state with generated summary
        """
        # Validate state
        if not self.validate_state(state):
            return StateManager.add_error(
                state,
                error="Invalid state for summarizer node",
                error_type="ValidationError",
            )
        
        # Check if we have journal entries
        if not state["journal_entries"]:
            self.logger.warning("No journal entries to summarize")
            return StateManager.set_journal_summary(
                state,
                "No recent journal entries to summarize.",
            )
        
        try:
            # Generate summary using LLMService
            summary = self.llm_service.get_journal_summary(state["journal_entries"])
            
            # Update state with summary
            updated_state = StateManager.set_journal_summary(
                state,
                summary,
            )
            
            self.logger.info(f"Generated summary for {state['entry_count']} entries")
            return updated_state
            
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return StateManager.add_error(
                state,
                error=f"Error generating summary: {str(e)}",
                error_type=type(e).__name__,
            )
    
    def validate_state(self, state: JournalAgentState) -> bool:
        """
        Validate state for summarizer node.
        
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