"""
Base node classes for LangGraph workflows.

This module provides base classes for creating nodes in LangGraph workflows,
including base nodes and LLM-specific nodes.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypeVar, Generic, List

from langchain_core.runnables import Runnable
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import HumanMessage, AIMessage

from agent_service.langgraph_.state import BaseAgentState, StateManager
from agent_service.tracing.decorators import trace_function
from agent_service.app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

# Type variable for state types
StateT = TypeVar('StateT', bound=BaseAgentState)


class BaseNode(ABC, Generic[StateT]):
    """
    Base class for all LangGraph nodes.
    
    Provides common functionality for tracing, error handling,
    and state management that all nodes need.
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize the base node.
        
        Args:
            name: Name of the node
            description: Description of what the node does
        """
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def execute(self, state: StateT) -> StateT:
        """
        Execute the node logic.
        
        This is the main method that subclasses must implement.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state
        """
        pass
    
    def __call__(self, state: StateT) -> StateT:
        """
        Call the node (LangGraph integration).
        
        This method wraps the execute method with tracing and error handling.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state
        """
        try:
            self.logger.info(f"Executing node {self.name} for user {state['user_id']}")
            
            # Execute the node logic
            result = self._execute_with_tracing(state)
            
            self.logger.info(f"Node {self.name} completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in node {self.name}: {e}")
            return self._handle_error(state, e)
    
    @trace_function(name="node_execution", tags=["node", "execution"])
    def _execute_with_tracing(self, state: StateT) -> StateT:
        """
        Execute the node with tracing.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state
        """
        return self.execute(state)
    
    def _handle_error(self, state: StateT, error: Exception) -> StateT:
        """
        Handle errors in node execution.
        
        Args:
            state: Current agent state
            error: The exception that occurred
            
        Returns:
            Updated state with error information
        """
        return StateManager.add_error(
            state,
            error=str(error),
            error_type=type(error).__name__,
        )
    
    def validate_state(self, state: StateT) -> bool:
        """
        Validate that the state has required fields for this node.
        
        Args:
            state: The state to validate
            
        Returns:
            True if state is valid, False otherwise
        """
        # Base implementation - subclasses can override
        required_fields = ["user_id", "tradition"]
        
        for field in required_fields:
            if field not in state or state[field] is None:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        return True
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this node.
        
        Returns:
            Dictionary containing node metadata
        """
        return {
            "name": self.name,
            "description": self.description,
            "type": self.__class__.__name__,
        }
    
    def __repr__(self) -> str:
        """String representation of the node."""
        return f"{self.__class__.__name__}(name='{self.name}')"


class LLMNode(BaseNode[StateT]):
    """
    Base class for nodes that use LLM services.
    
    Provides common functionality for LLM integration and provider management.
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        task: str = "",
        provider: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the LLM node.
        
        Args:
            name: Name of the node
            description: Description of what the node does
            task: LLM task name (e.g., "journal_summary", "performance_review")
            provider: Optional provider to use
            overrides: Optional configuration overrides
        """
        super().__init__(name, description)
        self.task = task
        self.provider = provider
        self.overrides = overrides or {}
        
        # Import here to avoid circular imports
        from agent_service.app.services.llm_service import LLMService
        self.llm_service = LLMService()
    
    def get_llm(self) -> Runnable:
        """
        Get the LLM instance for this node.
        
        Returns:
            Configured LLM instance
        """
        return self.llm_service.get_llm(
            task=self.task,
            provider=self.provider,
            overrides=self.overrides,
        )
    
    def validate_state(self, state: StateT) -> bool:
        """
        Validate state for LLM nodes.
        
        Args:
            state: The state to validate
            
        Returns:
            True if state is valid, False otherwise
        """
        # Call parent validation
        if not super().validate_state(state):
            return False
        
        # Additional validation for LLM nodes
        if not self.task:
            self.logger.error("No task specified for LLM node")
            return False
        
        return True 