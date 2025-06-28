"""
Graph runner utilities for LangGraph workflows.

This module provides utilities for executing LangGraph workflows
with proper error handling, tracing, and state management.
"""

import logging
from typing import Any, Dict, List, Optional, TypeVar, Generic

from langchain_core.runnables import Runnable

from agent_service.langgraph_.state import BaseAgentState, StateManager
from agent_service.tracing.decorators import trace_function

logger = logging.getLogger(__name__)

# Type variable for state types
StateT = TypeVar('StateT', bound=BaseAgentState)


class GraphRunner(Generic[StateT]):
    """
    Utility class for running LangGraph workflows.
    
    Provides methods for executing graphs with proper error handling,
    tracing, and state management.
    """
    
    def __init__(self, graph: Runnable):
        """
        Initialize the graph runner.
        
        Args:
            graph: Compiled LangGraph to run
        """
        self.graph = graph
        self.logger = logging.getLogger(f"{__name__}.GraphRunner")
    
    @trace_function(name="graph_execution", tags=["graph", "execution"])
    async def run_async(self, state: StateT) -> StateT:
        """
        Run the graph asynchronously.
        
        Args:
            state: Initial state for the graph
            
        Returns:
            Final state after graph execution
        """
        try:
            self.logger.info(f"Starting graph execution for user {state['user_id']}")
            
            # Execute the graph
            result = await self.graph.ainvoke(state)
            
            self.logger.info(f"Graph execution completed for user {state['user_id']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in graph execution: {e}")
            return StateManager.add_error(
                state,
                error=f"Graph execution error: {str(e)}",
                error_type=type(e).__name__,
            )
    
    @trace_function(name="graph_execution", tags=["graph", "execution"])
    def run_sync(self, state: StateT) -> StateT:
        """
        Run the graph synchronously.
        
        Args:
            state: Initial state for the graph
            
        Returns:
            Final state after graph execution
        """
        try:
            self.logger.info(f"Starting graph execution for user {state['user_id']}")
            
            # Execute the graph
            result = self.graph.invoke(state)
            
            self.logger.info(f"Graph execution completed for user {state['user_id']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in graph execution: {e}")
            return StateManager.add_error(
                state,
                error=f"Graph execution error: {str(e)}",
                error_type=type(e).__name__,
            )
    
    def run_stream(self, state: StateT):
        """
        Run the graph with streaming output.
        
        Args:
            state: Initial state for the graph
            
        Yields:
            State updates as the graph executes
        """
        try:
            self.logger.info(f"Starting streaming graph execution for user {state['user_id']}")
            
            # Execute the graph with streaming
            for chunk in self.graph.stream(state):
                yield chunk
            
            self.logger.info(f"Streaming graph execution completed for user {state['user_id']}")
            
        except Exception as e:
            self.logger.error(f"Error in streaming graph execution: {e}")
            error_state = StateManager.add_error(
                state,
                error=f"Graph execution error: {str(e)}",
                error_type=type(e).__name__,
            )
            yield error_state
    
    def validate_state(self, state: StateT) -> bool:
        """
        Validate that the state is suitable for graph execution.
        
        Args:
            state: The state to validate
            
        Returns:
            True if state is valid, False otherwise
        """
        required_fields = ["user_id", "tradition"]
        
        for field in required_fields:
            if field not in state or state[field] is None:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        return True
    
    def get_execution_info(self) -> Dict[str, Any]:
        """
        Get information about the graph execution.
        
        Returns:
            Dictionary containing execution information
        """
        return {
            "graph_type": type(self.graph).__name__,
            "has_async": hasattr(self.graph, 'ainvoke'),
            "has_stream": hasattr(self.graph, 'stream'),
        }


class GraphRunnerFactory:
    """
    Factory for creating graph runners with different configurations.
    """
    
    @staticmethod
    def create_journal_summary_runner(
        provider: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> GraphRunner:
        """
        Create a graph runner for journal summary generation.
        
        Args:
            provider: Optional LLM provider to use
            overrides: Optional configuration overrides
            
        Returns:
            Configured graph runner
        """
        from agent_service.langgraph_.graphs.journal_graph import JournalGraphBuilder
        
        builder = JournalGraphBuilder(provider=provider, overrides=overrides)
        graph = builder.get_summary_graph()
        
        return GraphRunner(graph)
    
    @staticmethod
    def create_performance_review_runner(
        provider: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> GraphRunner:
        """
        Create a graph runner for performance review generation.
        
        Args:
            provider: Optional LLM provider to use
            overrides: Optional configuration overrides
            
        Returns:
            Configured graph runner
        """
        from agent_service.langgraph_.graphs.review_graph import ReviewGraphBuilder
        
        builder = ReviewGraphBuilder(provider=provider, overrides=overrides)
        graph = builder.get_review_graph()
        
        return GraphRunner(graph) 