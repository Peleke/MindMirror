"""
Retriever Architecture Foundation

Defines the modular retriever architecture with abstract base classes,
metadata management, and registry functionality for MCP plugins.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from langchain_core.documents import Document


@dataclass(frozen=True)
class RetrieverMetadata:
    """Metadata for retriever capabilities and configuration."""
    name: str
    type: str  # "vector", "sql", "graph", "hybrid", "composite", "http"
    backend: str  # "qdrant", "postgres", "memgraph", "journal_service", etc.
    description: str
    capabilities: List[str]  # ["semantic_search", "structured_query", etc.]
    latency_ms: Optional[float] = None
    cost_per_query: Optional[float] = None


class Retriever(ABC):
    """Base interface for all retrievers."""
    
    @abstractmethod
    async def retrieve(self, query: str) -> List[Document]:
        """Retrieve documents for a given query."""
        pass
    
    async def batch_retrieve(self, queries: List[str]) -> List[List[Document]]:
        """Retrieve documents for multiple queries."""
        results = []
        for query in queries:
            result = await self.retrieve(query)
            results.append(result)
        return results
    
    @abstractmethod
    def get_metadata(self) -> RetrieverMetadata:
        """Get retriever metadata."""
        pass
    
    def set_context(self, context: Dict[str, Any]) -> None:
        """Set context for the retriever (optional)."""
        pass
    
    def reload(self) -> None:
        """Reload retriever state (optional)."""
        pass


class RetrieverRegistry:
    """Registry for managing retrievers."""
    
    def __init__(self):
        self._retrievers: Dict[str, Retriever] = {}
        self._metadata: Dict[str, RetrieverMetadata] = {}
    
    def register(self, name: str, retriever: Retriever) -> None:
        """Register a retriever."""
        if retriever is None:
            raise ValueError("Retriever cannot be None")
        
        if not isinstance(retriever, Retriever):
            raise ValueError("Retriever must implement Retriever interface")
        
        if name in self._retrievers:
            raise ValueError(f"Retriever {name} is already registered")
        
        self._retrievers[name] = retriever
        self._metadata[name] = retriever.get_metadata()
    
    def get(self, name: str) -> Optional[Retriever]:
        """Get a retriever by name."""
        return self._retrievers.get(name)
    
    def list(self) -> List[str]:
        """List all registered retriever names."""
        return list(self._retrievers.keys())
    
    def get_metadata(self, name: str) -> Optional[RetrieverMetadata]:
        """Get metadata for a retriever."""
        return self._metadata.get(name)
    
    def get_by_type(self, retriever_type: str) -> List[Retriever]:
        """Get retrievers by type."""
        return [
            retriever for retriever in self._retrievers.values()
            if retriever.get_metadata().type == retriever_type
        ]
    
    def unregister(self, name: str) -> None:
        """Unregister a retriever."""
        if name in self._retrievers:
            del self._retrievers[name]
            del self._metadata[name]


# ============================================================================
# Stub Retriever Implementations
# ============================================================================

class VectorRetriever(Retriever):
    """Stub implementation for vector-based retrievers."""
    
    async def retrieve(self, query: str) -> List[Document]:
        raise NotImplementedError("VectorRetriever not implemented yet")
    
    def get_metadata(self) -> RetrieverMetadata:
        return RetrieverMetadata(
            name="vector_retriever",
            type="vector",
            backend="qdrant",
            description="Vector-based retriever (stub)",
            capabilities=["semantic_search"],
            latency_ms=50.0,
            cost_per_query=0.001
        )


class SQLRetriever(Retriever):
    """Stub implementation for SQL-based retrievers."""
    
    async def retrieve(self, query: str) -> List[Document]:
        raise NotImplementedError("SQLRetriever not implemented yet")
    
    def get_metadata(self) -> RetrieverMetadata:
        return RetrieverMetadata(
            name="sql_retriever",
            type="sql",
            backend="postgres",
            description="SQL-based retriever (stub)",
            capabilities=["structured_query"],
            latency_ms=25.0,
            cost_per_query=0.0005
        )


class GraphRetriever(Retriever):
    """Stub implementation for graph-based retrievers."""
    
    async def retrieve(self, query: str) -> List[Document]:
        raise NotImplementedError("GraphRetriever not implemented yet")
    
    def get_metadata(self) -> RetrieverMetadata:
        return RetrieverMetadata(
            name="graph_retriever",
            type="graph",
            backend="memgraph",
            description="Graph-based retriever (stub)",
            capabilities=["graph_traversal"],
            latency_ms=75.0,
            cost_per_query=0.002
        )


class HybridRetriever(Retriever):
    """Stub implementation for hybrid retrievers."""
    
    async def retrieve(self, query: str) -> List[Document]:
        raise NotImplementedError("HybridRetriever not implemented yet")
    
    def get_metadata(self) -> RetrieverMetadata:
        return RetrieverMetadata(
            name="hybrid_retriever",
            type="hybrid",
            backend="composite",
            description="Hybrid retriever combining multiple backends (stub)",
            capabilities=["semantic_search", "structured_query", "graph_traversal"],
            latency_ms=100.0,
            cost_per_query=0.003
        )


class CompositeRetriever(Retriever):
    """Stub implementation for composite retrievers."""
    
    async def retrieve(self, query: str) -> List[Document]:
        raise NotImplementedError("CompositeRetriever not implemented yet")
    
    def get_metadata(self) -> RetrieverMetadata:
        return RetrieverMetadata(
            name="composite_retriever",
            type="composite",
            backend="ensemble",
            description="Composite retriever with ensemble methods (stub)",
            capabilities=["semantic_search", "structured_query", "graph_traversal", "ranking"],
            latency_ms=150.0,
            cost_per_query=0.005
        ) 