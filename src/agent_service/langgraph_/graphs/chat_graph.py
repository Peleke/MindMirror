"""
Chat graph for ask/chat operations.

This module provides a LangGraph workflow for chat operations
that use RAG with Qdrant for document retrieval.
"""

import logging
from typing import Any, Dict, Optional

from langchain_core.runnables import Runnable
from langgraph.graph import StateGraph, END

from agent_service.langgraph_.graphs.base import BaseGraphBuilder
from agent_service.langgraph_.nodes.rag_node import RAGNode
from agent_service.langgraph_.state import RAGAgentState

logger = logging.getLogger(__name__)


class ChatGraphBuilder(BaseGraphBuilder[RAGAgentState]):
    """
    Graph builder for chat/ask operations.
    
    Creates a graph that can answer questions using RAG with
    Qdrant for document retrieval.
    """
    
    def __init__(
        self,
        name: str = "chat_graph",
        description: str = "Graph for chat/ask operations with RAG",
        provider: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the chat graph builder.
        
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
        Build the chat graph.
        
        Returns:
            Configured StateGraph for chat operations
        """
        # Create the RAG node
        rag_node = RAGNode(
            retriever=None,  # Will be set dynamically based on user context
            provider=self.provider,
            overrides=self.overrides,
        )
        
        # Add node to graph
        self.add_node("rag", rag_node)
        
        # Create the state graph
        self.graph = StateGraph(RAGAgentState)
        
        # Add nodes to the graph
        self.graph.add_node("rag", rag_node)
        
        # Define the workflow: rag -> END
        self.graph.set_entry_point("rag")
        self.graph.add_edge("rag", END)
        
        # Compile the graph
        compiled_graph = self.graph.compile()
        
        self.logger.info(f"Built chat graph with {len(self.nodes)} nodes")
        return compiled_graph
    
    def get_chat_graph(self) -> Runnable:
        """
        Get a compiled graph for chat operations.
        
        Returns:
            Compiled graph runnable
        """
        if not self.graph:
            self.build()
        
        if not self.validate_graph():
            raise ValueError("Graph validation failed")
        
        return self.graph.compile()


class ChatGraphFactory:
    """
    Factory for creating chat graphs with different configurations.
    """
    
    @staticmethod
    def create_default_chat_graph(
        provider: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> ChatGraphBuilder:
        """
        Create a default chat graph.
        
        Args:
            provider: Optional LLM provider to use
            overrides: Optional configuration overrides
            
        Returns:
            Configured ChatGraphBuilder
        """
        return ChatGraphBuilder(
            name="default_chat",
            description="Default chat graph for ask operations",
            provider=provider,
            overrides=overrides,
        )
    
    @staticmethod
    def create_knowledge_chat_graph(
        provider: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> ChatGraphBuilder:
        """
        Create a knowledge-focused chat graph.
        
        Args:
            provider: Optional LLM provider to use
            overrides: Optional configuration overrides
            
        Returns:
            Configured ChatGraphBuilder
        """
        return ChatGraphBuilder(
            name="knowledge_chat",
            description="Knowledge-focused chat graph",
            provider=provider,
            overrides=overrides,
        )
    
    @staticmethod
    def create_personal_chat_graph(
        provider: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> ChatGraphBuilder:
        """
        Create a personal-focused chat graph.
        
        Args:
            provider: Optional LLM provider to use
            overrides: Optional configuration overrides
            
        Returns:
            Configured ChatGraphBuilder
        """
        return ChatGraphBuilder(
            name="personal_chat",
            description="Personal-focused chat graph",
            provider=provider,
            overrides=overrides,
        ) 