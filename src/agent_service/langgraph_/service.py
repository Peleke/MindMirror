"""
LangGraph service integration layer.

This module provides a high-level service interface for using
LangGraph workflows while maintaining compatibility with existing code.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from agent_service.langgraph_.runner import GraphRunner, GraphRunnerFactory
from agent_service.langgraph_.state import (
    BaseAgentState,
    JournalAgentState,
    StateManager,
    AgentStateFactory,
)
from agent_service.llms.provider_manager import ProviderManager

logger = logging.getLogger(__name__)


class LangGraphService:
    """
    High-level service for LangGraph workflows.
    
    Provides a clean API for executing LangGraph workflows
    while handling state management and provider configuration.
    """
    
    def __init__(self, provider_manager: Optional[ProviderManager] = None):
        """
        Initialize the LangGraph service.
        
        Args:
            provider_manager: Optional provider manager for LLM configuration
        """
        self.provider_manager = provider_manager
        self.logger = logging.getLogger(f"{__name__}.LangGraphService")
        
        # Cache for graph runners
        self._runners: Dict[str, GraphRunner] = {}
    
    def _get_runner(self, graph_type: str, provider: Optional[str] = None, overrides: Optional[Dict[str, Any]] = None) -> GraphRunner:
        """
        Get or create a graph runner for the specified type.
        
        Args:
            graph_type: Type of graph ('journal_summary' or 'performance_review')
            provider: Optional LLM provider to use
            overrides: Optional configuration overrides
            
        Returns:
            Configured graph runner
        """
        cache_key = f"{graph_type}:{provider}:{hash(str(overrides))}"
        
        if cache_key not in self._runners:
            if graph_type == "journal_summary":
                runner = GraphRunnerFactory.create_journal_summary_runner(provider, overrides)
            elif graph_type == "performance_review":
                runner = GraphRunnerFactory.create_performance_review_runner(provider, overrides)
            else:
                raise ValueError(f"Unknown graph type: {graph_type}")
            
            self._runners[cache_key] = runner
        
        return self._runners[cache_key]
    
    async def generate_journal_summary(
        self,
        user_id: str,
        journal_entries: List[Dict[str, Any]],
        tradition: str = "default",
        provider: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
        stream: bool = False,
    ) -> Union[JournalAgentState, Any]:
        """
        Generate a summary from journal entries using LangGraph.
        
        Args:
            user_id: User identifier
            journal_entries: List of journal entries to summarize
            tradition: Tradition/context for the summary
            provider: Optional LLM provider to use
            overrides: Optional configuration overrides
            stream: Whether to stream the results
            
        Returns:
            Summary state or stream of updates
        """
        try:
            # Create initial state
            state = AgentStateFactory.create_journal_state(
                user_id=user_id,
                tradition=tradition,
                journal_entries=journal_entries,
            )
            
            # Get the runner
            runner = self._get_runner("journal_summary", provider, overrides)
            
            # Validate state
            if not runner.validate_state(state):
                raise ValueError("Invalid state for journal summary generation")
            
            # Execute the graph
            if stream:
                return runner.run_stream(state)
            else:
                return await runner.run_async(state)
                
        except Exception as e:
            self.logger.error(f"Error generating journal summary: {e}")
            
            # Return error state
            error_state = AgentStateFactory.create_journal_state(
                user_id=user_id,
                tradition=tradition,
                journal_entries=journal_entries,
            )
            return StateManager.add_error(
                error_state,
                error=f"Journal summary generation failed: {str(e)}",
                error_type=type(e).__name__,
            )
    
    async def generate_performance_review(
        self,
        user_id: str,
        performance_data: Dict[str, Any],
        tradition: str = "default",
        provider: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
        stream: bool = False,
    ) -> Union[JournalAgentState, Any]:
        """
        Generate a performance review using LangGraph.
        
        Args:
            user_id: User identifier
            performance_data: Performance data to analyze
            tradition: Tradition/context for the review
            provider: Optional LLM provider to use
            overrides: Optional configuration overrides
            stream: Whether to stream the results
            
        Returns:
            Review state or stream of updates
        """
        try:
            # Create initial state with performance data as journal entries
            # This is a workaround since we're using JournalAgentState for both
            journal_entries = [{"content": str(performance_data), "type": "performance_data"}]
            
            state = AgentStateFactory.create_journal_state(
                user_id=user_id,
                tradition=tradition,
                journal_entries=journal_entries,
            )
            
            # Get the runner
            runner = self._get_runner("performance_review", provider, overrides)
            
            # Validate state
            if not runner.validate_state(state):
                raise ValueError("Invalid state for performance review generation")
            
            # Execute the graph
            if stream:
                return runner.run_stream(state)
            else:
                return await runner.run_async(state)
                
        except Exception as e:
            self.logger.error(f"Error generating performance review: {e}")
            
            # Return error state
            error_state = AgentStateFactory.create_journal_state(
                user_id=user_id,
                tradition=tradition,
                journal_entries=[],
            )
            return StateManager.add_error(
                error_state,
                error=f"Performance review generation failed: {str(e)}",
                error_type=type(e).__name__,
            )
    
    def get_available_graphs(self) -> List[Dict[str, Any]]:
        """
        Get information about available graph types.
        
        Returns:
            List of available graph configurations
        """
        return [
            {
                "type": "journal_summary",
                "name": "Journal Summary Generation",
                "description": "Generate summaries from journal entries",
                "state_type": "JournalAgentState",
            },
            {
                "type": "performance_review", 
                "name": "Performance Review Generation",
                "description": "Generate performance reviews from data",
                "state_type": "JournalAgentState",
            },
        ]
    
    def get_graph_info(self, graph_type: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific graph type.
        
        Args:
            graph_type: Type of graph to get info for
            
        Returns:
            Graph information or None if not found
        """
        try:
            runner = self._get_runner(graph_type)
            return runner.get_execution_info()
        except Exception as e:
            self.logger.error(f"Error getting graph info for {graph_type}: {e}")
            return None
    
    def clear_cache(self):
        """Clear the graph runner cache."""
        self._runners.clear()
        self.logger.info("Graph runner cache cleared")


class LangGraphServiceFactory:
    """
    Factory for creating LangGraph services with different configurations.
    """
    
    @staticmethod
    def create_default_service() -> LangGraphService:
        """
        Create a default LangGraph service.
        
        Returns:
            Configured LangGraph service
        """
        return LangGraphService()
    
    @staticmethod
    def create_service_with_provider(provider_name: str) -> LangGraphService:
        """
        Create a LangGraph service with a specific provider.
        
        Args:
            provider_name: Name of the provider to use
            
        Returns:
            Configured LangGraph service
        """
        provider_manager = ProviderManager()
        provider_manager.set_default_provider(provider_name)
        
        return LangGraphService(provider_manager)
    
    @staticmethod
    def create_service_with_overrides(overrides: Dict[str, Any]) -> LangGraphService:
        """
        Create a LangGraph service with configuration overrides.
        
        Args:
            overrides: Configuration overrides to apply
            
        Returns:
            Configured LangGraph service
        """
        service = LangGraphService()
        
        # Apply overrides to all runners
        for graph_type in ["journal_summary", "performance_review"]:
            service._get_runner(graph_type, overrides=overrides)
        
        return service 