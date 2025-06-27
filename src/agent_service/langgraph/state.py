"""
State management for LangGraph agents.

This module defines the state classes and state management utilities
for different types of agent workflows in the system.
"""

from typing import Any, Dict, List, Optional, TypedDict, Union
from datetime import datetime
from uuid import UUID

from langchain_core.documents import Document


class BaseAgentState(TypedDict):
    """
    Base state class for all agent workflows.
    
    Contains common fields that all agents need.
    """
    # User and session context
    user_id: str
    tradition: str
    session_id: Optional[str]
    
    # Input and output
    input: Optional[str]
    output: Optional[str]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    # Error handling
    error: Optional[str]
    error_type: Optional[str]


class RAGAgentState(BaseAgentState):
    """
    State for RAG-based agent workflows.
    
    Used for question-answering and knowledge retrieval tasks.
    """
    # Query and context
    query: str
    context: List[Document]
    
    # Retrieval results
    retrieved_documents: List[Document]
    retrieval_scores: List[float]
    
    # Generation
    generated_response: Optional[str]
    response_metadata: Optional[Dict[str, Any]]


class JournalAgentState(BaseAgentState):
    """
    State for journal processing agent workflows.
    
    Used for journal summarization, analysis, and review generation.
    """
    # Journal entries
    journal_entries: List[Dict[str, Any]]
    entry_count: int
    
    # Processing results
    summary: Optional[str]
    analysis: Optional[Dict[str, Any]]
    review: Optional[Dict[str, Any]]
    
    # Metadata
    date_range: Optional[Dict[str, datetime]]
    entry_types: List[str]


class CoachingAgentState(BaseAgentState):
    """
    State for coaching agent workflows.
    
    Used for personalized coaching, goal tracking, and recommendations.
    """
    # User context
    user_goals: Optional[Dict[str, Any]]
    user_preferences: Optional[Dict[str, Any]]
    user_history: Optional[Dict[str, Any]]
    
    # Coaching session
    session_type: str  # "meal_suggestion", "workout_plan", "review", etc.
    session_data: Optional[Dict[str, Any]]
    
    # Recommendations
    recommendations: List[Dict[str, Any]]
    next_actions: List[str]
    
    # Progress tracking
    progress_metrics: Optional[Dict[str, Any]]


class MultiAgentState(BaseAgentState):
    """
    State for multi-agent orchestration workflows.
    
    Used when multiple agents need to collaborate on a task.
    """
    # Agent coordination
    active_agents: List[str]
    agent_results: Dict[str, Any]
    coordination_data: Dict[str, Any]
    
    # Workflow management
    workflow_steps: List[str]
    current_step: str
    completed_steps: List[str]
    
    # Integration
    external_data: Dict[str, Any]
    integration_results: Dict[str, Any]


class AgentStateFactory:
    """
    Factory for creating and managing agent state instances.
    """
    
    @staticmethod
    def create_rag_state(
        user_id: str,
        tradition: str,
        query: str,
        session_id: Optional[str] = None,
    ) -> RAGAgentState:
        """Create a new RAG agent state."""
        now = datetime.utcnow()
        return RAGAgentState(
            user_id=user_id,
            tradition=tradition,
            session_id=session_id,
            input=query,
            output=None,
            created_at=now,
            updated_at=now,
            error=None,
            error_type=None,
            query=query,
            context=[],
            retrieved_documents=[],
            retrieval_scores=[],
            generated_response=None,
            response_metadata=None,
        )
    
    @staticmethod
    def create_journal_state(
        user_id: str,
        tradition: str,
        journal_entries: List[Dict[str, Any]],
        session_id: Optional[str] = None,
    ) -> JournalAgentState:
        """Create a new journal agent state."""
        now = datetime.utcnow()
        return JournalAgentState(
            user_id=user_id,
            tradition=tradition,
            session_id=session_id,
            input=None,
            output=None,
            created_at=now,
            updated_at=now,
            error=None,
            error_type=None,
            journal_entries=journal_entries,
            entry_count=len(journal_entries),
            summary=None,
            analysis=None,
            review=None,
            date_range=None,
            entry_types=list(set(entry.get("entry_type", "unknown") for entry in journal_entries)),
        )
    
    @staticmethod
    def create_coaching_state(
        user_id: str,
        tradition: str,
        session_type: str,
        session_id: Optional[str] = None,
    ) -> CoachingAgentState:
        """Create a new coaching agent state."""
        now = datetime.utcnow()
        return CoachingAgentState(
            user_id=user_id,
            tradition=tradition,
            session_id=session_id,
            input=None,
            output=None,
            created_at=now,
            updated_at=now,
            error=None,
            error_type=None,
            user_goals=None,
            user_preferences=None,
            user_history=None,
            session_type=session_type,
            session_data=None,
            recommendations=[],
            next_actions=[],
            progress_metrics=None,
        )
    
    @staticmethod
    def create_multi_agent_state(
        user_id: str,
        tradition: str,
        workflow_steps: List[str],
        session_id: Optional[str] = None,
    ) -> MultiAgentState:
        """Create a new multi-agent state."""
        now = datetime.utcnow()
        return MultiAgentState(
            user_id=user_id,
            tradition=tradition,
            session_id=session_id,
            input=None,
            output=None,
            created_at=now,
            updated_at=now,
            error=None,
            error_type=None,
            active_agents=[],
            agent_results={},
            coordination_data={},
            workflow_steps=workflow_steps,
            current_step=workflow_steps[0] if workflow_steps else "",
            completed_steps=[],
            external_data={},
            integration_results={},
        )


class StateManager:
    """
    Utility class for managing agent state updates and transformations.
    """
    
    @staticmethod
    def update_state(
        state: BaseAgentState,
        updates: Dict[str, Any],
    ) -> BaseAgentState:
        """
        Update a state with new values.
        
        Args:
            state: The current state
            updates: Dictionary of updates to apply
            
        Returns:
            Updated state
        """
        updated_state = state.copy()
        updated_state.update(updates)
        updated_state["updated_at"] = datetime.utcnow()
        return updated_state
    
    @staticmethod
    def add_error(
        state: BaseAgentState,
        error: str,
        error_type: str = "UnknownError",
    ) -> BaseAgentState:
        """
        Add error information to state.
        
        Args:
            state: The current state
            error: Error message
            error_type: Type of error
            
        Returns:
            Updated state with error information
        """
        return StateManager.update_state(state, {
            "error": error,
            "error_type": error_type,
        })
    
    @staticmethod
    def clear_error(state: BaseAgentState) -> BaseAgentState:
        """
        Clear error information from state.
        
        Args:
            state: The current state
            
        Returns:
            Updated state with cleared error information
        """
        return StateManager.update_state(state, {
            "error": None,
            "error_type": None,
        })
    
    @staticmethod
    def add_document_to_context(
        state: RAGAgentState,
        document: Document,
        score: Optional[float] = None,
    ) -> RAGAgentState:
        """
        Add a document to the RAG agent context.
        
        Args:
            state: The RAG agent state
            document: Document to add
            score: Retrieval score for the document
            
        Returns:
            Updated RAG agent state
        """
        updated_state = state.copy()
        # Create deep copies of lists to ensure immutability
        updated_state["context"] = state["context"].copy()
        updated_state["retrieved_documents"] = state["retrieved_documents"].copy()
        updated_state["retrieval_scores"] = state["retrieval_scores"].copy()
        
        updated_state["context"].append(document)
        updated_state["retrieved_documents"].append(document)
        if score is not None:
            updated_state["retrieval_scores"].append(score)
        updated_state["updated_at"] = datetime.utcnow()
        return updated_state
    
    @staticmethod
    def set_generated_response(
        state: RAGAgentState,
        response: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RAGAgentState:
        """
        Set the generated response in RAG agent state.
        
        Args:
            state: The RAG agent state
            response: Generated response
            metadata: Response metadata
            
        Returns:
            Updated RAG agent state
        """
        return StateManager.update_state(state, {
            "generated_response": response,
            "response_metadata": metadata or {},
            "output": response,
        })
    
    @staticmethod
    def set_journal_summary(
        state: JournalAgentState,
        summary: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> JournalAgentState:
        """
        Set the journal summary in journal agent state.
        
        Args:
            state: The journal agent state
            summary: Generated summary
            metadata: Summary metadata
            
        Returns:
            Updated journal agent state
        """
        return StateManager.update_state(state, {
            "summary": summary,
            "output": summary,
        })
    
    @staticmethod
    def set_performance_review(
        state: JournalAgentState,
        review: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> JournalAgentState:
        """
        Set the performance review in journal agent state.
        
        Args:
            state: The journal agent state
            review: Generated review data
            metadata: Review metadata
            
        Returns:
            Updated journal agent state
        """
        return StateManager.update_state(state, {
            "review": review,
            "output": review,
        }) 