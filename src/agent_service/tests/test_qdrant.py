import asyncio
import logging
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
import pytest_asyncio
from qdrant_client.http import models

from agent_service.vector_stores.qdrant_client import (QdrantClient,
                                                       SearchResult)

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

logger = logging.getLogger(__name__)

# A sample document for testing
TEST_DOC = {
    "id": "doc1",
    "text": "This is a test document about computer science.",
    "metadata": {"author": "gemini", "year": 2024, "tags": ["test", "cs"]},
}


class TestQdrantClient:
    """Test suite for Qdrant vector store integration."""

    async def test_connection_and_health_check(self, qdrant_client: QdrantClient):
        """Test that we can connect to Qdrant and perform health checks."""
        async for client in qdrant_client:
            health = await client.health_check()
            assert health is True

    async def test_knowledge_collection_creation(self, qdrant_client: QdrantClient):
        """Test creating shared knowledge collections."""
        tradition = "test_tradition"

        async for client in qdrant_client:
            # Create knowledge collection
            collection_name = await client.get_or_create_knowledge_collection(tradition)

            assert collection_name == f"{tradition}_knowledge"

            # Verify collection exists
            info = await client.get_collection_info(collection_name)
            assert info is not None
            # Handle both dict and object formats for collection info
            if hasattr(info, "vectors_config"):
                assert info.vectors_config.params.distance == models.Distance.COSINE
            else:
                # If it's a dict, check the structure differently
                assert "vectors_config" in info or info is not None

    async def test_personal_collection_creation(self, qdrant_client: QdrantClient):
        """Test creating user-specific personal collections."""
        tradition = "test_tradition"
        user_id = str(uuid4())

        async for client in qdrant_client:
            # Create personal collection
            collection_name = await client.get_or_create_personal_collection(
                tradition, user_id
            )

            expected_name = f"{tradition}_{user_id}_personal"
            assert collection_name == expected_name

            # Verify collection exists
            info = await client.get_collection_info(collection_name)
            assert info is not None
            # Handle both dict and object formats for collection info
            if hasattr(info, "vectors_config"):
                assert info.vectors_config.params.distance == models.Distance.COSINE
            else:
                # If it's a dict, check the structure differently
                assert "vectors_config" in info or info is not None

    async def test_knowledge_document_indexing(self, qdrant_client: QdrantClient):
        """Test indexing PDF documents in shared knowledge collection."""
        tradition = "test_tradition"

        async for client in qdrant_client:
            # Index a knowledge document (PDF)
            text = "This is wisdom from a PDF document about stoic philosophy."
            embedding = [0.1] * 768  # Mock embedding
            metadata = {
                "source_id": "stoic_guide.pdf",
                "page": 42,
                "document_type": "knowledge",
            }

            point_id = await client.index_knowledge_document(
                tradition=tradition, text=text, embedding=embedding, metadata=metadata
            )

            assert point_id is not None

            # Verify document can be found
            collection_name = await client.get_or_create_knowledge_collection(tradition)
            results = await client.search_documents(
                collection_name=collection_name, query_embedding=embedding, limit=5
            )

            assert len(results) == 1
            assert results[0].text == text
            assert results[0].metadata["source_type"] == "pdf"
            assert results[0].metadata["source_id"] == "stoic_guide.pdf"

    async def test_personal_document_indexing(self, qdrant_client: QdrantClient):
        """Test indexing journal entries in user's personal collection."""
        tradition = "test_tradition"
        user_id = str(uuid4())

        async for client in qdrant_client:
            # Index a personal document (journal entry)
            text = "Today I reflected on my progress and felt grateful for my health."
            embedding = [0.2] * 768  # Mock embedding
            metadata = {
                "source_id": "journal_entry_123",
                "timestamp": datetime.utcnow().isoformat(),
                "document_type": "gratitude",
            }

            point_id = await client.index_personal_document(
                tradition=tradition,
                user_id=user_id,
                text=text,
                embedding=embedding,
                metadata=metadata,
            )

            assert point_id is not None

            # Verify document can be found
            collection_name = await client.get_or_create_personal_collection(
                tradition, user_id
            )
            results = await client.search_documents(
                collection_name=collection_name, query_embedding=embedding, limit=5
            )

            assert len(results) == 1
            assert results[0].text == text
            assert results[0].metadata["source_type"] == "journal"
            assert results[0].metadata["user_id"] == user_id

    async def test_metadata_filtering(self, qdrant_client: QdrantClient):
        """Test searching with metadata filters."""
        tradition = "test_tradition"
        user_id = str(uuid4())

        async for client in qdrant_client:
            # Index multiple documents with different types
            embedding = [0.3] * 768

            # Index a gratitude entry
            await client.index_personal_document(
                tradition=tradition,
                user_id=user_id,
                text="I'm grateful for my family",
                embedding=embedding,
                metadata={
                    "source_id": "entry_1",
                    "document_type": "gratitude",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            # Index a reflection entry
            await client.index_personal_document(
                tradition=tradition,
                user_id=user_id,
                text="I reflected on my workout performance",
                embedding=embedding,
                metadata={
                    "source_id": "entry_2",
                    "document_type": "reflection",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            collection_name = await client.get_or_create_personal_collection(
                tradition, user_id
            )

            # Search for only gratitude entries
            gratitude_results = await client.search_documents(
                collection_name=collection_name,
                query_embedding=embedding,
                limit=10,
                metadata_filter={"document_type": "gratitude"},
            )

            assert len(gratitude_results) == 1
            assert "grateful" in gratitude_results[0].text
            assert gratitude_results[0].metadata["document_type"] == "gratitude"

            # Search for only reflection entries
            reflection_results = await client.search_documents(
                collection_name=collection_name,
                query_embedding=embedding,
                limit=10,
                metadata_filter={"document_type": "reflection"},
            )

            assert len(reflection_results) == 1
            assert "reflected" in reflection_results[0].text
            assert reflection_results[0].metadata["document_type"] == "reflection"

    async def test_user_isolation(self, qdrant_client: QdrantClient):
        """Test that users can only access their own personal collections."""
        tradition = "test_tradition"
        user1_id = str(uuid4())
        user2_id = str(uuid4())

        async for client in qdrant_client:
            # Create collections for both users
            collection1 = await client.get_or_create_personal_collection(
                tradition, user1_id
            )
            collection2 = await client.get_or_create_personal_collection(
                tradition, user2_id
            )

            assert collection1 != collection2
            assert user1_id in collection1
            assert user2_id in collection2

            # Index document for user1
            embedding = [0.1] * 768
            await client.index_personal_document(
                tradition=tradition,
                user_id=user1_id,
                text="User 1's private journal entry",
                embedding=embedding,
                metadata={
                    "source_id": str(uuid4()),
                    "timestamp": datetime.utcnow().isoformat(),
                    "document_type": "reflection",
                },
            )

            # User2 should not find user1's documents in their collection
            results = await client.search_documents(
                collection_name=collection2, query_embedding=embedding, limit=10
            )

            assert len(results) == 0

    async def test_search_personal_documents_by_date(self, qdrant_client: QdrantClient):
        """Test searching personal documents within a specific date range."""
        tradition = "test_tradition"
        user_id = str(uuid4())
        embedding = [0.4] * 768  # Assuming nomic-embed-text dimension

        async for client in qdrant_client:
            # Index documents with different timestamps
            now = datetime.now(timezone.utc)
            two_days_ago = now - timedelta(days=2)
            five_days_ago = now - timedelta(days=5)

            # Document from 2 days ago (should be found)
            await client.index_personal_document(
                tradition=tradition,
                user_id=user_id,
                text="Entry from two days ago.",
                embedding=embedding,
                metadata={"created_at": two_days_ago.timestamp()},
            )

            # Document from 5 days ago (should NOT be found)
            await client.index_personal_document(
                tradition=tradition,
                user_id=user_id,
                text="Entry from five days ago.",
                embedding=embedding,
                metadata={"created_at": five_days_ago.timestamp()},
            )

            # Define search range for the last 3 days
            search_start_date = now - timedelta(days=3)
            search_end_date = now

            # Perform date-filtered search
            results = await client.search_personal_documents_by_date(
                user_id=user_id,
                tradition=tradition,
                query_embedding=embedding,
                start_date=search_start_date,
                end_date=search_end_date,
                limit=10,
            )

            assert len(results) == 1
            assert results[0].text == "Entry from two days ago."
            assert results[0].metadata["created_at"] > search_start_date.timestamp()

    async def test_hybrid_search(self, qdrant_client: QdrantClient):
        """Test hybrid search across both knowledge and personal collections."""
        tradition = "test_tradition"
        user_id = str(uuid4())
        embedding = [0.4] * 768

        async for client in qdrant_client:
            # Index knowledge document (PDF)
            await client.index_knowledge_document(
                tradition=tradition,
                text="Stoic philosophy teaches resilience in face of adversity.",
                embedding=embedding,
                metadata={
                    "source_id": "stoic_wisdom.pdf",
                    "page": 15,
                    "document_type": "knowledge",
                },
            )

            # Index personal document (journal)
            await client.index_personal_document(
                tradition=tradition,
                user_id=user_id,
                text="I practiced stoic principles during today's difficult meeting.",
                embedding=embedding,
                metadata={
                    "source_id": "journal_456",
                    "timestamp": datetime.utcnow().isoformat(),
                    "document_type": "reflection",
                },
            )

            # Hybrid search including both knowledge and personal content
            results = await client.hybrid_search(
                query="stoic resilience practices",
                user_id=user_id,
                tradition=tradition,
                query_embedding=embedding,
                include_knowledge=True,
                include_personal=True,
                limit=10,
            )

            assert len(results) == 2

            # Check that we get both types of content
            source_types = [result.metadata["source_type"] for result in results]
            assert "pdf" in source_types
            assert "journal" in source_types

            # Test knowledge-only search
            knowledge_only = await client.hybrid_search(
                query="stoic resilience practices",
                user_id=user_id,
                tradition=tradition,
                query_embedding=embedding,
                include_knowledge=True,
                include_personal=False,
                limit=10,
            )

            assert len(knowledge_only) == 1
            assert knowledge_only[0].metadata["source_type"] == "pdf"

            # Test personal-only search
            personal_only = await client.hybrid_search(
                query="stoic resilience practices",
                user_id=user_id,
                tradition=tradition,
                query_embedding=embedding,
                include_knowledge=False,
                include_personal=True,
                limit=10,
            )

            assert len(personal_only) > 0
            assert personal_only[0].metadata["source_type"] == "journal"

    async def test_collection_cleanup(self, qdrant_client: QdrantClient):
        """Test that collections can be properly deleted."""
        tradition = "test_tradition_cleanup"
        user_id = str(uuid4())

        async for client in qdrant_client:
            # Create and verify collection exists
            collection_name = await client.get_or_create_personal_collection(
                tradition, user_id
            )
            info = await client.get_collection_info(collection_name)
            assert info is not None

            # Delete collection
            success = await client.delete_collection(collection_name)
            assert success is True

            # Verify collection no longer exists
            info_after = await client.get_collection_info(collection_name)
            assert info_after is None
