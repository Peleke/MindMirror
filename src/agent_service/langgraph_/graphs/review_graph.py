"""
Review graph builder for performance review workflows.

This module provides the ReviewGraphBuilder class that creates
a graph for performance review generation.
"""

import logging
from typing import Any, Dict, Optional

from langchain_core.runnables import Runnable
from langgraph.graph import StateGraph, END

from agent_service.langgraph_.graphs.base import BaseGraphBuilder
from agent_service.langgraph_.nodes.reviewer_node import ReviewerNode
from agent_service.langgraph_.state import JournalAgentState

logger = logging.getLogger(__name__)


class ReviewGraphBuilder(BaseGraphBuilder[JournalAgentState]):
    """
    Graph builder for performance review workflows.
    
    Creates a graph that can generate performance reviews from journal entries
    using the ReviewerNode.
    """
    
    def __init__(
        self,
        name: str = "review_graph",
        description: str = "Graph for performance review generation",
        provider: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the review graph builder.
        
        Args:
            name: Graph name
            description: Graph description
            provider: Optional LLM provider to use
            overrides: Optional configuration overrides
        """
        super().__init__(name, description)
        self.provider = provider
        self.overrides = overrides or {}
    
    def build(self) -> StateGraph:
        """
        Build the performance review graph.
        
        Returns:
            Configured StateGraph for performance review processing
        """
        # Create the reviewer node
        reviewer_node = ReviewerNode(
            provider=self.provider,
            overrides=self.overrides,
        )
        
        # Add node to graph
        self.add_node("reviewer", reviewer_node)
        
        # Create the state graph
        self.graph = StateGraph(JournalAgentState)
        
        # Add nodes to the graph
        self.graph.add_node("reviewer", reviewer_node)
        
        # Define the workflow: reviewer -> END
        self.graph.set_entry_point("reviewer")
        self.graph.add_edge("reviewer", END)
        
        # Compile the graph
        compiled_graph = self.graph.compile()
        
        self.logger.info(f"Built review graph with {len(self.nodes)} nodes")
        return compiled_graph
    
    def get_review_graph(self) -> Runnable:
        """
        Get a compiled graph for review generation.
        
        Returns:
            Compiled graph runnable
        """
        if not self.graph:
            self.build()
        
        if not self.validate_graph():
            raise ValueError("Graph validation failed")
        
        return self.graph.compile() 