"""
State management for LangGraph agents.

This module defines the state classes and state management utilities
for different types of agent workflows in the system.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict, Union
from uuid import UUID

from langchain_core.documents import Document

logger = logging.getLogger(__name__)


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


class RAGAgentState(TypedDict):
    """
    State for RAG agent operations.

    This state tracks the conversation, user context, and
    retrieved documents for RAG operations.
    """

    # User context
    user_id: Optional[str]
    tradition_id: Optional[str]

    # Conversation
    messages: List[Dict[str, Any]]

    # Current query and response
    query: Optional[str]
    last_response: Optional[str]

    # Retrieved documents
    retrieved_documents: List[Dict[str, Any]]

    # Metadata
    metadata: Dict[str, Any]

    # Error handling
    error: Optional[str]
    error_type: Optional[str]


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
        return RAGAgentState(
            user_id=user_id,
            tradition_id=tradition,
            messages=[],
            query=query,
            last_response=None,
            retrieved_documents=[],
            metadata={},
            error=None,
            error_type=None,
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
            entry_types=list(
                set(entry.get("entry_type", "unknown") for entry in journal_entries)
            ),
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
        return StateManager.update_state(
            state,
            {
                "error": error,
                "error_type": error_type,
            },
        )

    @staticmethod
    def clear_error(state: BaseAgentState) -> BaseAgentState:
        """
        Clear error information from state.

        Args:
            state: The current state

        Returns:
            Updated state with cleared error information
        """
        return StateManager.update_state(
            state,
            {
                "error": None,
                "error_type": None,
            },
        )

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
        updated_state["retrieved_documents"] = state["retrieved_documents"].copy()

        updated_state["retrieved_documents"].append(document)
        if score is not None:
            updated_state["retrieved_documents"][-1]["score"] = score
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
        return StateManager.update_state(
            state,
            {
                "last_response": response,
                "output": response,
            },
        )

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
        return StateManager.update_state(
            state,
            {
                "summary": summary,
                "output": summary,
            },
        )

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
        return StateManager.update_state(
            state,
            {
                "review": review,
                "output": review,
            },
        )

    @staticmethod
    def create_initial_state(
        user_id: Optional[str] = None,
        tradition_id: Optional[str] = None,
        initial_message: Optional[str] = None,
    ) -> RAGAgentState:
        """
        Create initial state for a RAG agent.

        Args:
            user_id: User identifier
            tradition_id: Tradition identifier
            initial_message: Optional initial message

        Returns:
            Initial agent state
        """
        state: RAGAgentState = {
            "user_id": user_id,
            "tradition_id": tradition_id,
            "messages": [],
            "query": None,
            "last_response": None,
            "retrieved_documents": [],
            "metadata": {},
            "error": None,
            "error_type": None,
        }

        # Add initial message if provided
        if initial_message:
            state["messages"].append(
                {
                    "role": "user",
                    "content": initial_message,
                    "timestamp": StateManager._get_timestamp(),
                }
            )
            state["query"] = initial_message

        return state

    @staticmethod
    def add_user_message(
        state: RAGAgentState,
        message: str,
    ) -> RAGAgentState:
        """
        Add a user message to the state.

        Args:
            state: Current agent state
            message: User message content

        Returns:
            Updated state with user message
        """
        updated_state = state.copy()
        updated_state["messages"].append(
            {
                "role": "user",
                "content": message,
                "timestamp": StateManager._get_timestamp(),
            }
        )
        updated_state["query"] = message
        return updated_state

    @staticmethod
    def add_assistant_message(
        state: RAGAgentState,
        message: str,
    ) -> RAGAgentState:
        """
        Add an assistant message to the state.

        Args:
            state: Current agent state
            message: Assistant message content

        Returns:
            Updated state with assistant message
        """
        updated_state = state.copy()
        updated_state["messages"].append(
            {
                "role": "assistant",
                "content": message,
                "timestamp": StateManager._get_timestamp(),
            }
        )
        updated_state["last_response"] = message
        return updated_state

    @staticmethod
    def clear_documents(state: RAGAgentState) -> RAGAgentState:
        """
        Clear retrieved documents from state.

        Args:
            state: Current agent state

        Returns:
            Updated state with cleared documents
        """
        updated_state = state.copy()
        updated_state["retrieved_documents"] = []
        return updated_state

    @staticmethod
    def set_metadata(
        state: RAGAgentState,
        key: str,
        value: Any,
    ) -> RAGAgentState:
        """
        Set metadata in the state.

        Args:
            state: Current agent state
            key: Metadata key
            value: Metadata value

        Returns:
            Updated state with metadata set
        """
        updated_state = state.copy()
        updated_state["metadata"][key] = value
        return updated_state

    @staticmethod
    def get_metadata(
        state: RAGAgentState,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get metadata from the state.

        Args:
            state: Current agent state
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default
        """
        return state.get("metadata", {}).get(key, default)

    @staticmethod
    def get_latest_user_message(state: RAGAgentState) -> Optional[str]:
        """
        Get the latest user message from state.

        Args:
            state: Current agent state

        Returns:
            Latest user message or None
        """
        messages = state.get("messages", [])
        for message in reversed(messages):
            if message.get("role") == "user":
                return message.get("content")
        return None

    @staticmethod
    def get_latest_assistant_message(state: RAGAgentState) -> Optional[str]:
        """
        Get the latest assistant message from state.

        Args:
            state: Current agent state

        Returns:
            Latest assistant message or None
        """
        messages = state.get("messages", [])
        for message in reversed(messages):
            if message.get("role") == "assistant":
                return message.get("content")
        return None

    @staticmethod
    def get_conversation_history(
        state: RAGAgentState,
        max_messages: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history from state.

        Args:
            state: Current agent state
            max_messages: Maximum number of messages to return

        Returns:
            List of conversation messages
        """
        messages = state.get("messages", [])
        if max_messages is not None:
            messages = messages[-max_messages:]
        return messages

    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp string."""
        return datetime.now().isoformat()
