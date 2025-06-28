"""
Journal graph builder for journal processing workflows.

This module provides the JournalGraphBuilder class that creates
a graph for journal summary generation.
"""

import logging
from typing import Any, Dict, Optional

from langchain_core.runnables import Runnable
from langgraph.graph import StateGraph, END

from agent_service.langgraph_.graphs.base import BaseGraphBuilder
from agent_service.langgraph_.nodes.summarizer_node import SummarizerNode
from agent_service.langgraph_.state import JournalAgentState

logger = logging.getLogger(__name__)


class JournalGraphBuilder(BaseGraphBuilder[JournalAgentState]):
    """
    Graph builder for journal processing workflows.
    
    Creates a graph that can generate summaries from journal entries
    using the SummarizerNode.
    """
    
    def __init__(
        self,
        name: str = "journal_graph",
        description: str = "Graph for journal summary generation",
        provider: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the journal graph builder.
        
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
        Build the journal processing graph.
        
        Returns:
            Configured StateGraph for journal processing
        """
        # Create the summarizer node
        summarizer_node = SummarizerNode(
            provider=self.provider,
            overrides=self.overrides,
        )
        
        # Add node to graph
        self.add_node("summarizer", summarizer_node)
        
        # Create the state graph
        self.graph = StateGraph(JournalAgentState)
        
        # Add nodes to the graph
        self.graph.add_node("summarizer", summarizer_node)
        
        # Define the workflow: summarizer -> END
        self.graph.set_entry_point("summarizer")
        self.graph.add_edge("summarizer", END)
        
        # Compile the graph
        compiled_graph = self.graph.compile()
        
        self.logger.info(f"Built journal graph with {len(self.nodes)} nodes")
        return compiled_graph
    
    def get_summary_graph(self) -> Runnable:
        """
        Get a compiled graph for summary generation.
        
        Returns:
            Compiled graph runnable
        """
        if not self.graph:
            self.build()
        
        if not self.validate_graph():
            raise ValueError("Graph validation failed")
        
        return self.graph.compile() 