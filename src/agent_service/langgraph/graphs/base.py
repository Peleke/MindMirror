"""
Base graph builder for LangGraph workflows.

This module provides the BaseGraphBuilder class that all graph builders inherit from,
with common functionality for graph construction and validation.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic

from langchain_core.runnables import Runnable
from langgraph.graph import StateGraph, END

from agent_service.langgraph.state import BaseAgentState
from agent_service.tracing.decorators import trace_function

logger = logging.getLogger(__name__)

# Type variable for state types
StateT = TypeVar('StateT', bound=BaseAgentState)


class BaseGraphBuilder(ABC, Generic[StateT]):
    """
    Base class for building LangGraph workflows.
    
    Provides common functionality for graph construction, validation,
    and execution that all graph builders need.
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize the base graph builder.
        
        Args:
            name: Name of the graph
            description: Description of what the graph does
        """
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.nodes: Dict[str, Runnable] = {}
        self.graph: Optional[StateGraph] = None
    
    @abstractmethod
    def build(self) -> StateGraph:
        """
        Build the graph workflow.
        
        This is the main method that subclasses must implement.
        
        Returns:
            Configured StateGraph instance
        """
        pass
    
    def add_node(self, name: str, node: Runnable) -> None:
        """
        Add a node to the graph.
        
        Args:
            name: Name of the node
            node: Node instance (must be callable)
        """
        self.nodes[name] = node
        self.logger.info(f"Added node '{name}' to graph '{self.name}'")
    
    def validate_graph(self) -> bool:
        """
        Validate that the graph is properly configured.
        
        Returns:
            True if graph is valid, False otherwise
        """
        if not self.nodes:
            self.logger.error("No nodes added to graph")
            return False
        
        if not self.graph:
            self.logger.error("Graph not built yet")
            return False
        
        return True
    
    def get_node(self, name: str) -> Optional[Runnable]:
        """
        Get a node by name.
        
        Args:
            name: Name of the node
            
        Returns:
            Node instance or None if not found
        """
        return self.nodes.get(name)
    
    def list_nodes(self) -> List[str]:
        """
        Get list of node names in the graph.
        
        Returns:
            List of node names
        """
        return list(self.nodes.keys())
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this graph.
        
        Returns:
            Dictionary containing graph metadata
        """
        return {
            "name": self.name,
            "description": self.description,
            "type": self.__class__.__name__,
            "nodes": self.list_nodes(),
            "node_count": len(self.nodes),
        }
    
    def __repr__(self) -> str:
        """String representation of the graph builder."""
        return f"{self.__class__.__name__}(name='{self.name}', nodes={len(self.nodes)})" 