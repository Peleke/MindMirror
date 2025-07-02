"""
LangGraph integration for MindMirror.

This package provides LangGraph-based workflows for journal analysis,
performance reviews, and other agent operations.
"""

from .graphs.base import BaseGraphBuilder
from .graphs.chat_graph import ChatGraphBuilder, ChatGraphFactory
from .graphs.journal_graph import JournalGraphBuilder
from .graphs.review_graph import ReviewGraphBuilder
from .nodes.base import BaseNode, LLMNode
from .nodes.rag_node import RAGNode
from .nodes.reviewer_node import ReviewerNode
from .nodes.summarizer_node import SummarizerNode
from .runner import GraphRunner, GraphRunnerFactory
from .service import LangGraphService, LangGraphServiceFactory
from .state import (
    AgentStateFactory,
    BaseAgentState,
    CoachingAgentState,
    JournalAgentState,
    MultiAgentState,
    RAGAgentState,
    StateManager,
)

__all__ = [
    # State management
    "BaseAgentState",
    "JournalAgentState",
    "RAGAgentState",
    "CoachingAgentState",
    "MultiAgentState",
    "StateManager",
    "AgentStateFactory",
    # Nodes
    "BaseNode",
    "LLMNode",
    "SummarizerNode",
    "ReviewerNode",
    "RAGNode",
    # Graph builders
    "BaseGraphBuilder",
    "JournalGraphBuilder",
    "ReviewGraphBuilder",
    "ChatGraphBuilder",
    "ChatGraphFactory",
    # Runners
    "GraphRunner",
    "GraphRunnerFactory",
    # Services
    "LangGraphService",
    "LangGraphServiceFactory",
]
