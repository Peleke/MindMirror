"""
Chat API endpoints for ask operations.

This module provides FastAPI endpoints for chat/ask operations
using LangGraph workflows with RAG capabilities.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from shared.auth import CurrentUser, get_current_user

from agent_service.langgraph_.graphs.chat_graph import ChatGraphFactory
from agent_service.langgraph_.state import RAGAgentState, StateManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    """Model for a chat message."""

    content: str = Field(..., description="Message content")
    role: str = Field(default="user", description="Message role (user/assistant)")


class ChatRequest(BaseModel):
    """Model for chat request."""

    message: str = Field(..., min_length=1, description="User message")
    tradition_id: Optional[str] = Field(None, description="Tradition ID for context")
    conversation_id: Optional[str] = Field(
        None, description="Conversation ID for continuity"
    )
    search_type: str = Field(
        default="hybrid", description="Search type (vector/keyword/hybrid)"
    )


class ChatResponse(BaseModel):
    """Model for chat response."""

    response: str = Field(..., description="Assistant response")
    conversation_id: str = Field(..., description="Conversation ID")
    retrieved_documents: List[Dict[str, Any]] = Field(
        default_factory=list, description="Retrieved documents"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Response metadata"
    )


class ConversationHistory(BaseModel):
    """Model for conversation history."""

    conversation_id: str = Field(..., description="Conversation ID")
    messages: List[ChatMessage] = Field(..., description="Conversation messages")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


# In-memory conversation storage (in production, use a proper database)
_conversations: Dict[str, RAGAgentState] = {}


@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ChatResponse:
    """
    Ask a question using RAG with LangGraph.

    Args:
        request: Chat request with message and context
        current_user: Authenticated user

    Returns:
        Chat response with answer and metadata
    """
    try:
        logger.info(f"Processing chat request for user {current_user.id}")

        # Get or create conversation state
        conversation_id = (
            request.conversation_id or f"conv_{current_user.id}_{len(_conversations)}"
        )

        if conversation_id in _conversations:
            # Continue existing conversation
            state = _conversations[conversation_id]
            state = StateManager.add_user_message(state, request.message)
        else:
            # Create new conversation
            state = StateManager.create_initial_state(
                user_id=str(current_user.id),
                tradition_id=request.tradition_id,
                initial_message=request.message,
            )
            _conversations[conversation_id] = state

        # Create chat graph
        chat_graph_builder = ChatGraphFactory.create_default_chat_graph(
            provider="openai",  # Could be configurable
        )

        # Build and execute the graph
        chat_graph = chat_graph_builder.get_chat_graph()
        updated_state = chat_graph.invoke(state)

        # Update conversation storage
        _conversations[conversation_id] = updated_state

        # Extract response
        response = updated_state.get(
            "last_response", "I apologize, but I couldn't generate a response."
        )
        retrieved_docs = updated_state.get("retrieved_documents", [])

        # Prepare metadata
        metadata = {
            "user_id": str(current_user.id),
            "tradition_id": request.tradition_id,
            "search_type": request.search_type,
            "documents_retrieved": len(retrieved_docs),
            "has_error": updated_state.get("error") is not None,
        }

        if updated_state.get("error"):
            metadata["error"] = updated_state["error"]

        logger.info(f"Chat response generated for user {current_user.id}")

        return ChatResponse(
            response=response,
            conversation_id=conversation_id,
            retrieved_documents=retrieved_docs,
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Error in chat request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat request: {str(e)}",
        )


@router.get("/conversations", response_model=List[ConversationHistory])
async def get_conversations(
    current_user: CurrentUser = Depends(get_current_user),
    limit: int = 10,
) -> List[ConversationHistory]:
    """
    Get user's conversation history.

    Args:
        current_user: Authenticated user
        limit: Maximum number of conversations to return

    Returns:
        List of conversation histories
    """
    try:
        user_conversations = []

        for conv_id, state in _conversations.items():
            if state.get("user_id") == str(current_user.id):
                # Convert state to conversation history
                messages = []
                for msg in state.get("messages", []):
                    messages.append(
                        ChatMessage(
                            content=msg.get("content", ""), role=msg.get("role", "user")
                        )
                    )

                # Get timestamps (use first and last message timestamps)
                timestamps = [
                    msg.get("timestamp", "") for msg in state.get("messages", [])
                ]
                created_at = timestamps[0] if timestamps else ""
                updated_at = timestamps[-1] if timestamps else ""

                user_conversations.append(
                    ConversationHistory(
                        conversation_id=conv_id,
                        messages=messages,
                        created_at=created_at,
                        updated_at=updated_at,
                    )
                )

        # Sort by updated_at (most recent first) and limit
        user_conversations.sort(key=lambda x: x.updated_at, reverse=True)
        return user_conversations[:limit]

    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversations: {str(e)}",
        )


@router.get("/conversations/{conversation_id}", response_model=ConversationHistory)
async def get_conversation(
    conversation_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> ConversationHistory:
    """
    Get a specific conversation.

    Args:
        conversation_id: Conversation ID
        current_user: Authenticated user

    Returns:
        Conversation history
    """
    try:
        if conversation_id not in _conversations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        state = _conversations[conversation_id]

        # Check if user owns this conversation
        if state.get("user_id") != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation",
            )

        # Convert state to conversation history
        messages = []
        for msg in state.get("messages", []):
            messages.append(
                ChatMessage(
                    content=msg.get("content", ""), role=msg.get("role", "user")
                )
            )

        # Get timestamps
        timestamps = [msg.get("timestamp", "") for msg in state.get("messages", [])]
        created_at = timestamps[0] if timestamps else ""
        updated_at = timestamps[-1] if timestamps else ""

        return ConversationHistory(
            conversation_id=conversation_id,
            messages=messages,
            created_at=created_at,
            updated_at=updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation: {str(e)}",
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> Dict[str, str]:
    """
    Delete a conversation.

    Args:
        conversation_id: Conversation ID
        current_user: Authenticated user

    Returns:
        Success message
    """
    try:
        if conversation_id not in _conversations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        state = _conversations[conversation_id]

        # Check if user owns this conversation
        if state.get("user_id") != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation",
            )

        # Delete conversation
        del _conversations[conversation_id]

        logger.info(
            f"Deleted conversation {conversation_id} for user {current_user.id}"
        )

        return {"message": "Conversation deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete conversation: {str(e)}",
        )


@router.post("/conversations/{conversation_id}/clear")
async def clear_conversation(
    conversation_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> Dict[str, str]:
    """
    Clear a conversation (remove all messages but keep the conversation).

    Args:
        conversation_id: Conversation ID
        current_user: Authenticated user

    Returns:
        Success message
    """
    try:
        if conversation_id not in _conversations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        state = _conversations[conversation_id]

        # Check if user owns this conversation
        if state.get("user_id") != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation",
            )

        # Clear messages but keep conversation
        state["messages"] = []
        state["query"] = None
        state["last_response"] = None
        state["retrieved_documents"] = []
        state["error"] = None
        state["error_type"] = None

        logger.info(
            f"Cleared conversation {conversation_id} for user {current_user.id}"
        )

        return {"message": "Conversation cleared successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear conversation: {str(e)}",
        )
