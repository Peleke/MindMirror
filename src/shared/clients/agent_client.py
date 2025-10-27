"""
Agent Service Client - Focused client for RAG and AI operations.

This client provides methods for interacting with the agent service's RAG capabilities,
including document indexing, search, and AI-powered suggestions.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from shared.clients.base import AuthContext, BaseServiceClient, ServiceConfig


class DocumentSearchResult:
    """Search result from document RAG system."""
    
    def __init__(
        self,
        content: str,
        score: float,
        metadata: Dict[str, Any],
        document_id: Optional[str] = None,
        source_type: Optional[str] = None
    ):
        self.content = content
        self.score = score
        self.metadata = metadata
        self.document_id = document_id
        self.source_type = source_type
    
    @classmethod
    def from_response(cls, data: Dict) -> "DocumentSearchResult":
        """Create DocumentSearchResult from API response."""
        return cls(
            content=data["content"],
            score=data.get("score", 0.0),
            metadata=data.get("metadata", {}),
            document_id=data.get("document_id"),
            source_type=data.get("source_type")
        )


class SuggestionResponse:
    """AI-generated suggestion response."""
    
    def __init__(
        self,
        suggestion: str,
        confidence: float,
        reasoning: Optional[str] = None,
        sources: Optional[List[str]] = None
    ):
        self.suggestion = suggestion
        self.confidence = confidence
        self.reasoning = reasoning
        self.sources = sources or []
    
    @classmethod
    def from_response(cls, data: Dict) -> "SuggestionResponse":
        """Create SuggestionResponse from API response."""
        return cls(
            suggestion=data["suggestion"],
            confidence=data.get("confidence", 0.0),
            reasoning=data.get("reasoning"),
            sources=data.get("sources", [])
        )


class AgentServiceClient(BaseServiceClient):
    """
    Client for the Agent Service.
    
    Provides focused methods for RAG operations, document search, and AI suggestions
    that are needed by other services in the system.
    """
    
    async def search_documents(
        self,
        user_id: UUID,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[DocumentSearchResult]:
        """
        Search through indexed documents using semantic search.
        
        Args:
            user_id: User performing the search
            query: Search query text
            limit: Maximum number of results to return
            filters: Optional filters for document types, dates, etc.
        """
        auth = AuthContext(user_id=user_id)
        
        data = await self.execute_rest(
            auth=auth,
            method="POST",
            path="/search/documents",
            data={
                "query": query,
                "limit": limit,
                "filters": filters or {}
            }
        )
        
        return [
            DocumentSearchResult.from_response(result)
            for result in data.get("results", [])
        ]
    
    async def get_ai_suggestions(
        self,
        user_id: UUID,
        context: str,
        suggestion_type: str = "general",
        include_sources: bool = True
    ) -> SuggestionResponse:
        """
        Get AI-powered suggestions based on user context.
        
        Args:
            user_id: User requesting suggestions
            context: Context information for generating suggestions
            suggestion_type: Type of suggestion (e.g., "journal_prompt", "reflection", "general")
            include_sources: Whether to include source documents in response
        """
        auth = AuthContext(user_id=user_id)
        
        data = await self.execute_rest(
            auth=auth,
            method="POST",
            path="/ai/suggestions",
            data={
                "context": context,
                "suggestion_type": suggestion_type,
                "include_sources": include_sources
            }
        )
        
        return SuggestionResponse.from_response(data)
    
    async def index_document(
        self,
        user_id: UUID,
        document_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        source_type: str = "user_upload"
    ) -> bool:
        """
        Index a document for semantic search.
        
        Args:
            user_id: Owner of the document
            document_id: Unique identifier for the document
            content: Text content to index
            metadata: Additional metadata about the document
            source_type: Type of document source
            
        Returns:
            True if indexing was successful
        """
        auth = AuthContext(user_id=user_id)
        
        data = await self.execute_rest(
            auth=auth,
            method="POST",
            path="/index/document",
            data={
                "document_id": document_id,
                "content": content,
                "metadata": metadata or {},
                "source_type": source_type
            }
        )
        
        return data.get("success", False)
    
    async def delete_document(
        self,
        user_id: UUID,
        document_id: str
    ) -> bool:
        """
        Remove a document from the search index.
        
        Args:
            user_id: Owner of the document
            document_id: Unique identifier for the document
            
        Returns:
            True if deletion was successful
        """
        auth = AuthContext(user_id=user_id)
        
        data = await self.execute_rest(
            auth=auth,
            method="DELETE",
            path=f"/index/document/{document_id}"
        )
        
        return data.get("success", False)
    
    async def get_user_stats(
        self,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Get user's RAG system statistics.
        
        Args:
            user_id: User to get stats for
            
        Returns:
            Dictionary with user statistics (document count, index size, etc.)
        """
        auth = AuthContext(user_id=user_id)
        
        data = await self.execute_rest(
            auth=auth,
            method="GET",
            path="/user/stats"
        )
        
        return data.get("stats", {})


def create_agent_client(base_url: str = "http://localhost:8000") -> AgentServiceClient:
    """Factory function to create an agent service client with standard config."""
    config = ServiceConfig(
        base_url=base_url,
        service_name="agent-service",
        timeout=30.0,  # AI operations can take longer
        max_retries=3,  # More retries for AI operations
    )
    return AgentServiceClient(config) 