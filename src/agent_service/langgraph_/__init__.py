"""
LangGraph integration for MindMirror.

This package provides LangGraph-based workflows for journal analysis,
performance reviews, and other agent operations.
"""

from .state import (
    BaseAgentState,
    JournalAgentState,
    RAGAgentState,
    CoachingAgentState,
    MultiAgentState,
    StateManager,
    AgentStateFactory,
)

from .nodes.base import BaseNode, LLMNode
from .nodes.summarizer_node import SummarizerNode
from .nodes.reviewer_node import ReviewerNode

from .graphs.base import BaseGraphBuilder
from .graphs.journal_graph import JournalGraphBuilder
from .graphs.review_graph import ReviewGraphBuilder

from .runner import GraphRunner, GraphRunnerFactory
from .service import LangGraphService, LangGraphServiceFactory

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
    
    # Graph builders
    "BaseGraphBuilder",
    "JournalGraphBuilder",
    "ReviewGraphBuilder",
    
    # Runners
    "GraphRunner",
    "GraphRunnerFactory",
    
    # Services
    "LangGraphService",
    "LangGraphServiceFactory",
] 