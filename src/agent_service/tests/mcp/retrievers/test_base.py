"""
Test Suite for Retriever Architecture

Comprehensive tests for retriever interface, registry, and metadata management
following TDD principles and property-based testing.
"""

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch

import pytest
from langchain_core.documents import Document

from agent_service.mcp.retrievers.base import (Retriever, RetrieverMetadata,
                                               RetrieverRegistry)

# ============================================================================
# Test Data
# ============================================================================


@pytest.fixture
def sample_metadata():
    return RetrieverMetadata(
        name="test_retriever",
        type="vector",
        backend="qdrant",
        description="A test retriever",
        capabilities=["semantic_search", "filtering"],
        latency_ms=50.0,
        cost_per_query=0.001,
    )


@pytest.fixture
def sample_documents():
    return [
        Document(
            page_content="Test document 1", metadata={"source": "test", "id": "1"}
        ),
        Document(
            page_content="Test document 2", metadata={"source": "test", "id": "2"}
        ),
    ]


# ============================================================================
# RetrieverMetadata Tests
# ============================================================================


class TestRetrieverMetadata:
    """Test RetrieverMetadata dataclass."""

    def test_metadata_creation(self, sample_metadata):
        """Test metadata creation with valid data."""
        assert sample_metadata.name == "test_retriever"
        assert sample_metadata.type == "vector"
        assert sample_metadata.backend == "qdrant"
        assert sample_metadata.description == "A test retriever"
        assert "semantic_search" in sample_metadata.capabilities
        assert sample_metadata.latency_ms == 50.0
        assert sample_metadata.cost_per_query == 0.001

    def test_metadata_immutability(self, sample_metadata):
        """Test that metadata is immutable."""
        with pytest.raises(FrozenInstanceError):
            sample_metadata.name = "new_name"

    def test_metadata_equality(self):
        """Test metadata equality comparison."""
        metadata1 = RetrieverMetadata(
            name="test",
            type="vector",
            backend="qdrant",
            description="test",
            capabilities=["search"],
        )
        metadata2 = RetrieverMetadata(
            name="test",
            type="vector",
            backend="qdrant",
            description="test",
            capabilities=["search"],
        )
        assert metadata1 == metadata2

    def test_metadata_optional_fields(self):
        """Test metadata with optional fields."""
        metadata = RetrieverMetadata(
            name="test",
            type="vector",
            backend="qdrant",
            description="test",
            capabilities=["search"],
        )
        assert metadata.latency_ms is None
        assert metadata.cost_per_query is None

    def test_metadata_repr(self, sample_metadata):
        """Test metadata string representation."""
        repr_str = repr(sample_metadata)
        assert "test_retriever" in repr_str
        assert "vector" in repr_str
        assert "qdrant" in repr_str


# ============================================================================
# Retriever Interface Tests
# ============================================================================


class TestRetriever:
    """Test Retriever abstract base class."""

    def test_retriever_abstract_methods(self):
        """Test that Retriever cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Retriever()

    def test_concrete_retriever_implementation(self, sample_documents):
        """Test a concrete retriever implementation."""

        class TestRetriever(Retriever):
            def __init__(self):
                self.documents = sample_documents

            async def retrieve(self, query: str) -> List[Document]:
                return self.documents

            def get_metadata(self) -> RetrieverMetadata:
                return RetrieverMetadata(
                    name="test_retriever",
                    type="test",
                    backend="test",
                    description="Test retriever",
                    capabilities=["test"],
                )

        retriever = TestRetriever()
        assert isinstance(retriever, Retriever)

        # Test retrieve method
        import asyncio

        docs = asyncio.run(retriever.retrieve("test query"))
        assert len(docs) == 2
        assert docs[0].page_content == "Test document 1"

        # Test batch_retrieve method
        batch_docs = asyncio.run(retriever.batch_retrieve(["query1", "query2"]))
        assert len(batch_docs) == 2
        assert len(batch_docs[0]) == 2
        assert len(batch_docs[1]) == 2

        # Test metadata
        metadata = retriever.get_metadata()
        assert metadata.name == "test_retriever"
        assert metadata.type == "test"

        # Test optional methods
        retriever.set_context({"test": "context"})
        retriever.reload()

    def test_retriever_context_setting(self):
        """Test retriever context setting."""

        class TestRetriever(Retriever):
            def __init__(self):
                self.context = {}

            async def retrieve(self, query: str) -> List[Document]:
                return []

            def get_metadata(self) -> RetrieverMetadata:
                return RetrieverMetadata(
                    name="test",
                    type="test",
                    backend="test",
                    description="test",
                    capabilities=[],
                )

            def set_context(self, context: Dict[str, Any]) -> None:
                self.context.update(context)

        retriever = TestRetriever()
        retriever.set_context({"user_id": "123", "filter": "active"})
        assert retriever.context["user_id"] == "123"
        assert retriever.context["filter"] == "active"

    def test_retriever_reload(self):
        """Test retriever reload functionality."""

        class TestRetriever(Retriever):
            def __init__(self):
                self.reload_count = 0

            async def retrieve(self, query: str) -> List[Document]:
                return []

            def get_metadata(self) -> RetrieverMetadata:
                return RetrieverMetadata(
                    name="test",
                    type="test",
                    backend="test",
                    description="test",
                    capabilities=[],
                )

            def reload(self) -> None:
                self.reload_count += 1

        retriever = TestRetriever()
        assert retriever.reload_count == 0
        retriever.reload()
        assert retriever.reload_count == 1
        retriever.reload()
        assert retriever.reload_count == 2


# ============================================================================
# RetrieverRegistry Tests
# ============================================================================


class TestRetrieverRegistry:
    """Test RetrieverRegistry functionality."""

    def test_registry_initialization(self):
        """Test registry initialization."""
        registry = RetrieverRegistry()
        assert registry._retrievers == {}
        assert registry._metadata == {}

    def test_register_retriever(self, sample_documents):
        """Test retriever registration."""
        registry = RetrieverRegistry()

        class TestRetriever(Retriever):
            async def retrieve(self, query: str) -> List[Document]:
                return sample_documents

            def get_metadata(self) -> RetrieverMetadata:
                return RetrieverMetadata(
                    name="test_retriever",
                    type="vector",
                    backend="qdrant",
                    description="Test retriever",
                    capabilities=["search"],
                )

        retriever = TestRetriever()
        registry.register("test_retriever", retriever)

        assert "test_retriever" in registry._retrievers
        assert registry._retrievers["test_retriever"] is retriever
        assert "test_retriever" in registry._metadata
        assert registry._metadata["test_retriever"].name == "test_retriever"

    def test_duplicate_registration(self, sample_documents):
        """Test that duplicate registration raises error."""
        registry = RetrieverRegistry()

        class TestRetriever(Retriever):
            async def retrieve(self, query: str) -> List[Document]:
                return sample_documents

            def get_metadata(self) -> RetrieverMetadata:
                return RetrieverMetadata(
                    name="test_retriever",
                    type="vector",
                    backend="qdrant",
                    description="Test retriever",
                    capabilities=["search"],
                )

        retriever1 = TestRetriever()
        retriever2 = TestRetriever()

        registry.register("test_retriever", retriever1)

        with pytest.raises(
            ValueError, match="Retriever test_retriever is already registered"
        ):
            registry.register("test_retriever", retriever2)

    def test_get_retriever(self, sample_documents):
        """Test getting retriever by name."""
        registry = RetrieverRegistry()

        class TestRetriever(Retriever):
            async def retrieve(self, query: str) -> List[Document]:
                return sample_documents

            def get_metadata(self) -> RetrieverMetadata:
                return RetrieverMetadata(
                    name="test_retriever",
                    type="vector",
                    backend="qdrant",
                    description="Test retriever",
                    capabilities=["search"],
                )

        retriever = TestRetriever()
        registry.register("test_retriever", retriever)

        retrieved = registry.get("test_retriever")
        assert retrieved is retriever

        # Test non-existent retriever
        assert registry.get("non_existent") is None

    def test_list_retrievers(self, sample_documents):
        """Test listing registered retrievers."""
        registry = RetrieverRegistry()

        class TestRetriever(Retriever):
            async def retrieve(self, query: str) -> List[Document]:
                return sample_documents

            def get_metadata(self) -> RetrieverMetadata:
                return RetrieverMetadata(
                    name="test_retriever",
                    type="vector",
                    backend="qdrant",
                    description="Test retriever",
                    capabilities=["search"],
                )

        retriever1 = TestRetriever()
        retriever2 = TestRetriever()

        registry.register("retriever1", retriever1)
        registry.register("retriever2", retriever2)

        retrievers = registry.list()
        assert len(retrievers) == 2
        assert "retriever1" in retrievers
        assert "retriever2" in retrievers

    def test_get_metadata(self, sample_documents):
        """Test getting retriever metadata."""
        registry = RetrieverRegistry()

        class TestRetriever(Retriever):
            async def retrieve(self, query: str) -> List[Document]:
                return sample_documents

            def get_metadata(self) -> RetrieverMetadata:
                return RetrieverMetadata(
                    name="test_retriever",
                    type="vector",
                    backend="qdrant",
                    description="Test retriever",
                    capabilities=["search"],
                )

        retriever = TestRetriever()
        registry.register("test_retriever", retriever)

        metadata = registry.get_metadata("test_retriever")
        assert metadata is not None
        assert metadata.name == "test_retriever"
        assert metadata.type == "vector"
        assert metadata.backend == "qdrant"

        # Test non-existent retriever
        assert registry.get_metadata("non_existent") is None

    def test_get_by_type(self, sample_documents):
        """Test getting retrievers by type."""
        registry = RetrieverRegistry()

        class VectorRetriever(Retriever):
            async def retrieve(self, query: str) -> List[Document]:
                return sample_documents

            def get_metadata(self) -> RetrieverMetadata:
                return RetrieverMetadata(
                    name="vector_retriever",
                    type="vector",
                    backend="qdrant",
                    description="Vector retriever",
                    capabilities=["search"],
                )

        class SQLRetriever(Retriever):
            async def retrieve(self, query: str) -> List[Document]:
                return sample_documents

            def get_metadata(self) -> RetrieverMetadata:
                return RetrieverMetadata(
                    name="sql_retriever",
                    type="sql",
                    backend="postgres",
                    description="SQL retriever",
                    capabilities=["query"],
                )

        vector_retriever = VectorRetriever()
        sql_retriever = SQLRetriever()

        registry.register("vector1", vector_retriever)
        registry.register("vector2", vector_retriever)
        registry.register("sql1", sql_retriever)

        vector_retrievers = registry.get_by_type("vector")
        assert len(vector_retrievers) == 2

        sql_retrievers = registry.get_by_type("sql")
        assert len(sql_retrievers) == 1

        # Test non-existent type
        assert len(registry.get_by_type("non_existent")) == 0


# ============================================================================
# Integration Tests
# ============================================================================


class TestRetrieverIntegration:
    """Integration tests for retriever architecture."""

    def test_complete_retriever_workflow(self, sample_documents):
        """Test complete retriever workflow from registration to retrieval."""
        registry = RetrieverRegistry()

        class WorkflowRetriever(Retriever):
            def __init__(self):
                self.documents = sample_documents
                self.context = {}

            async def retrieve(self, query: str) -> List[Document]:
                # Use context if available
                if self.context.get("filter"):
                    return [
                        doc
                        for doc in self.documents
                        if self.context["filter"] in doc.page_content
                    ]
                return self.documents

            def get_metadata(self) -> RetrieverMetadata:
                return RetrieverMetadata(
                    name="workflow_retriever",
                    type="hybrid",
                    backend="custom",
                    description="Workflow retriever for testing",
                    capabilities=["search", "filtering", "context_aware"],
                    latency_ms=25.0,
                    cost_per_query=0.0005,
                )

            def set_context(self, context: Dict[str, Any]) -> None:
                self.context.update(context)

        # Create and register retriever
        retriever = WorkflowRetriever()
        registry.register("workflow", retriever)

        # Verify registration
        assert "workflow" in registry.list()
        assert registry.get("workflow") is retriever

        # Test metadata
        metadata = registry.get_metadata("workflow")
        assert metadata.name == "workflow_retriever"
        assert metadata.type == "hybrid"
        assert metadata.capabilities == ["search", "filtering", "context_aware"]

        # Test retrieval
        import asyncio

        docs = asyncio.run(retriever.retrieve("test query"))
        assert len(docs) == 2

        # Test context setting
        retriever.set_context({"filter": "document 1"})
        filtered_docs = asyncio.run(retriever.retrieve("test query"))
        assert len(filtered_docs) == 1
        assert "document 1" in filtered_docs[0].page_content

        # Test type-based filtering
        hybrid_retrievers = registry.get_by_type("hybrid")
        assert len(hybrid_retrievers) == 1
        assert hybrid_retrievers[0] is retriever

    def test_multiple_retriever_types(self, sample_documents):
        """Test working with multiple retriever types."""
        registry = RetrieverRegistry()

        # Create different types of retrievers
        class VectorRetriever(Retriever):
            async def retrieve(self, query: str) -> List[Document]:
                return sample_documents

            def get_metadata(self) -> RetrieverMetadata:
                return RetrieverMetadata(
                    name="vector_retriever",
                    type="vector",
                    backend="qdrant",
                    description="Vector retriever",
                    capabilities=["semantic_search"],
                )

        class SQLRetriever(Retriever):
            async def retrieve(self, query: str) -> List[Document]:
                return sample_documents

            def get_metadata(self) -> RetrieverMetadata:
                return RetrieverMetadata(
                    name="sql_retriever",
                    type="sql",
                    backend="postgres",
                    description="SQL retriever",
                    capabilities=["structured_query"],
                )

        class GraphRetriever(Retriever):
            async def retrieve(self, query: str) -> List[Document]:
                return sample_documents

            def get_metadata(self) -> RetrieverMetadata:
                return RetrieverMetadata(
                    name="graph_retriever",
                    type="graph",
                    backend="memgraph",
                    description="Graph retriever",
                    capabilities=["graph_traversal"],
                )

        # Register all retrievers
        registry.register("vector", VectorRetriever())
        registry.register("sql", SQLRetriever())
        registry.register("graph", GraphRetriever())

        # Test listing
        assert len(registry.list()) == 3

        # Test type-based filtering
        vector_retrievers = registry.get_by_type("vector")
        assert len(vector_retrievers) == 1

        sql_retrievers = registry.get_by_type("sql")
        assert len(sql_retrievers) == 1

        graph_retrievers = registry.get_by_type("graph")
        assert len(graph_retrievers) == 1

        # Test metadata for each type
        vector_metadata = registry.get_metadata("vector")
        assert vector_metadata.backend == "qdrant"

        sql_metadata = registry.get_metadata("sql")
        assert sql_metadata.backend == "postgres"

        graph_metadata = registry.get_metadata("graph")
        assert graph_metadata.backend == "memgraph"


# ============================================================================
# Property-Based Tests
# ============================================================================


class TestPropertyBased:
    """Property-based tests for complex behaviors."""

    def test_metadata_roundtrip(self):
        """Test that metadata can be round-tripped correctly."""
        original_metadata = RetrieverMetadata(
            name="complex_retriever",
            type="hybrid",
            backend="custom_backend",
            description="A complex retriever with many capabilities",
            capabilities=[
                "semantic_search",
                "structured_query",
                "graph_traversal",
                "filtering",
            ],
            latency_ms=123.456,
            cost_per_query=0.00789,
        )

        # Verify all fields are preserved
        assert original_metadata.name == "complex_retriever"
        assert original_metadata.type == "hybrid"
        assert original_metadata.backend == "custom_backend"
        assert (
            original_metadata.description
            == "A complex retriever with many capabilities"
        )
        assert len(original_metadata.capabilities) == 4
        assert "semantic_search" in original_metadata.capabilities
        assert original_metadata.latency_ms == 123.456
        assert original_metadata.cost_per_query == 0.00789

    def test_registry_retriever_lifecycle(self, sample_documents):
        """Test complete retriever lifecycle in registry."""
        registry = RetrieverRegistry()

        class LifecycleRetriever(Retriever):
            def __init__(self):
                self.documents = sample_documents
                self.initialized = True

            async def retrieve(self, query: str) -> List[Document]:
                return self.documents

            def get_metadata(self) -> RetrieverMetadata:
                return RetrieverMetadata(
                    name="lifecycle_retriever",
                    type="test",
                    backend="test",
                    description="Test retriever",
                    capabilities=["test"],
                )

        # Register retriever
        retriever = LifecycleRetriever()
        registry.register("lifecycle", retriever)

        # Verify registration
        assert "lifecycle" in registry.list()
        assert registry.get("lifecycle") is retriever
        assert retriever.initialized is True

        # Test retrieval
        import asyncio

        docs = asyncio.run(retriever.retrieve("test"))
        assert len(docs) == 2

        # Test metadata
        metadata = registry.get_metadata("lifecycle")
        assert metadata.name == "lifecycle_retriever"

        # Test type filtering
        test_retrievers = registry.get_by_type("test")
        assert len(test_retrievers) == 1
        assert test_retrievers[0] is retriever


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_register_none_retriever(self):
        """Test that registering None retriever raises error."""
        registry = RetrieverRegistry()

        with pytest.raises(ValueError, match="Retriever cannot be None"):
            registry.register("test", None)

    def test_register_invalid_retriever(self):
        """Test that registering invalid retriever raises error."""
        registry = RetrieverRegistry()

        class InvalidRetriever:
            pass

        with pytest.raises(
            ValueError, match="Retriever must implement Retriever interface"
        ):
            registry.register("test", InvalidRetriever())

    def test_retriever_missing_retrieve_method(self):
        """Test that retriever without retrieve method raises error."""

        class InvalidRetriever(Retriever):
            def get_metadata(self) -> RetrieverMetadata:
                return RetrieverMetadata(
                    name="test",
                    type="test",
                    backend="test",
                    description="test",
                    capabilities=[],
                )

        with pytest.raises(TypeError):
            InvalidRetriever()

    def test_retriever_missing_metadata_method(self):
        """Test that retriever without get_metadata method raises error."""

        class InvalidRetriever(Retriever):
            async def retrieve(self, query: str) -> List[Document]:
                return []

        with pytest.raises(TypeError):
            InvalidRetriever()
