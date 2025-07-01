"""
Base graph builder classes for LangGraph workflows.

This module provides foundational graph builder classes that specific graph
builders can inherit from, promoting code reuse and consistent patterns.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

from langgraph.graph import StateGraph

from ..state import BaseAgentState

logger = logging.getLogger(__name__)

StateT = TypeVar("StateT")


class BaseGraphBuilder(ABC, Generic[StateT]):
    """
    Base class for building LangGraph workflows.

    Provides common functionality for graph construction,
    validation, and management.
    """

    def __init__(self, name: str, description: str):
        """
        Initialize the base graph builder.

        Args:
            name: Graph name
            description: Graph description
        """
        self.name = name
        self.description = description
        self.graph: StateGraph = None
        self.nodes: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def add_node(self, name: str, node: Any) -> None:
        """
        Add a node to the graph.

        Args:
            name: Node name
            node: Node instance
        """
        if name in self.nodes:
            self.logger.warning(f"Node '{name}' already exists, overwriting")

        self.nodes[name] = node
        self.logger.debug(f"Added node '{name}' to graph")

    def remove_node(self, name: str) -> bool:
        """
        Remove a node from the graph.

        Args:
            name: Node name to remove

        Returns:
            True if node was removed, False if not found
        """
        if name in self.nodes:
            del self.nodes[name]
            self.logger.debug(f"Removed node '{name}' from graph")
            return True
        return False

    def get_node(self, name: str) -> Any:
        """
        Get a node by name.

        Args:
            name: Node name

        Returns:
            Node instance or None if not found
        """
        return self.nodes.get(name)

    def list_nodes(self) -> Dict[str, Any]:
        """
        Get all nodes in the graph.

        Returns:
            Dictionary of node names to node instances
        """
        return self.nodes.copy()

    def validate_graph(self) -> bool:
        """
        Validate the graph structure.

        Returns:
            True if graph is valid, False otherwise
        """
        if not self.graph:
            self.logger.error("Graph has not been built yet")
            return False

        if not self.nodes:
            self.logger.error("Graph has no nodes")
            return False

        # Check for required nodes (subclasses can override)
        required_nodes = self.get_required_nodes()
        for node_name in required_nodes:
            if node_name not in self.nodes:
                self.logger.error(f"Required node '{node_name}' is missing")
                return False

        self.logger.info(f"Graph validation passed with {len(self.nodes)} nodes")
        return True

    def get_required_nodes(self) -> list:
        """
        Get list of required nodes for this graph type.

        Returns:
            List of required node names
        """
        return []

    def get_graph_info(self) -> Dict[str, Any]:
        """
        Get information about the graph.

        Returns:
            Dictionary with graph information
        """
        return {
            "name": self.name,
            "description": self.description,
            "node_count": len(self.nodes),
            "nodes": list(self.nodes.keys()),
            "built": self.graph is not None,
            "valid": self.validate_graph() if self.graph else False,
        }

    @abstractmethod
    def build(self) -> StateGraph:
        """
        Build the graph.

        Returns:
            Configured StateGraph
        """
        pass

    def reset(self) -> None:
        """
        Reset the graph builder state.
        """
        self.graph = None
        self.nodes.clear()
        self.logger.info("Graph builder reset")

    def __str__(self) -> str:
        """String representation of the graph builder."""
        info = self.get_graph_info()
        return f"{self.__class__.__name__}({info['name']}, nodes={info['node_count']})"

    def __repr__(self) -> str:
        """Detailed string representation of the graph builder."""
        info = self.get_graph_info()
        return (
            f"{self.__class__.__name__}("
            f"name='{info['name']}', "
            f"description='{info['description']}', "
            f"nodes={info['nodes']}, "
            f"built={info['built']}, "
            f"valid={info['valid']}"
            f")"
        )
