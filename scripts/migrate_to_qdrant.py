#!/usr/bin/env python3
"""
Migration script to transfer existing FAISS vector stores to Qdrant.

This script:
1. Reads existing FAISS vector stores from data/{tradition}/vectorstore/
2. Extracts document chunks and metadata
3. Uploads to appropriate Qdrant collections (shared knowledge vs user-specific)
4. Verifies migration with test queries

Usage:
    python scripts/migrate_to_qdrant.py --tradition canon-default --user-id bob
    python scripts/migrate_to_qdrant.py --all-traditions --dry-run
"""

import argparse
import asyncio
import logging
import os
import pickle
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import DATA_DIR, PDF_DIR
from src.embedding import get_embedding_model, load_vector_store
from src.vector_stores.qdrant_client import QdrantClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class FAISSToQdrantMigrator:
    """Handles migration from FAISS to Qdrant vector stores."""

    def __init__(self, qdrant_client: QdrantClient, dry_run: bool = False):
        self.qdrant_client = qdrant_client
        self.dry_run = dry_run
        self.embedding_model = get_embedding_model()

    async def migrate_tradition(self, tradition: str, user_id: str) -> Dict[str, Any]:
        """
        Migrate a specific tradition's vector store to Qdrant.

        Args:
            tradition: The tradition name (e.g., "canon-default")
            user_id: User ID for personal collection naming

        Returns:
            Dictionary with migration statistics
        """
        logger.info(f"Starting migration for tradition: {tradition}")

        # Paths
        tradition_data_dir = Path(DATA_DIR) / tradition
        vector_store_path = tradition_data_dir / "vectorstore"

        if not vector_store_path.exists():
            logger.warning(f"Vector store not found at {vector_store_path}")
            return {"error": f"Vector store not found for tradition {tradition}"}

        try:
            # Load existing FAISS vector store
            logger.info(f"Loading FAISS vector store from {vector_store_path}")
            vector_store = load_vector_store(str(vector_store_path))

            # Extract documents and embeddings
            documents, embeddings = await self._extract_documents_from_faiss(
                vector_store
            )
            logger.info(f"Extracted {len(documents)} documents from FAISS")

            if self.dry_run:
                logger.info(f"DRY RUN: Would migrate {len(documents)} documents")
                return {
                    "tradition": tradition,
                    "documents_count": len(documents),
                    "dry_run": True,
                }

            # Migrate to Qdrant collections
            stats = await self._migrate_documents_to_qdrant(
                tradition=tradition,
                user_id=user_id,
                documents=documents,
                embeddings=embeddings,
            )

            logger.info(f"Migration completed for {tradition}: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Failed to migrate tradition {tradition}: {e}")
            return {"error": str(e)}

    async def _extract_documents_from_faiss(
        self, vector_store
    ) -> tuple[List[Dict], List[List[float]]]:
        """Extract documents and embeddings from FAISS vector store."""
        documents = []
        embeddings = []

        # Access FAISS internal structures
        # FAISS stores documents in docstore and embeddings in index
        docstore = vector_store.docstore
        index_to_docstore_id = vector_store.index_to_docstore_id

        # Extract embeddings from FAISS index
        faiss_index = vector_store.index
        num_vectors = faiss_index.ntotal

        logger.info(f"Extracting {num_vectors} vectors from FAISS index")

        # Get all embeddings
        all_embeddings = faiss_index.reconstruct_n(0, num_vectors)

        # Process each document
        for i in range(num_vectors):
            try:
                # Get document ID
                doc_id = index_to_docstore_id[i]

                # Get document from docstore
                doc = docstore.search(doc_id)

                # Get embedding
                embedding = all_embeddings[i].tolist()

                # Create document metadata
                metadata = {
                    "source_type": "pdf",  # Assume existing docs are PDFs
                    "source_id": doc.metadata.get("source", f"unknown_doc_{i}"),
                    "page": doc.metadata.get("page", 0),
                    "document_type": "knowledge",
                    "migration_id": str(uuid4()),
                    "original_faiss_id": doc_id,
                }

                documents.append({"text": doc.page_content, "metadata": metadata})
                embeddings.append(embedding)

            except Exception as e:
                logger.warning(f"Failed to extract document {i}: {e}")
                continue

        logger.info(f"Successfully extracted {len(documents)} documents")
        return documents, embeddings

    async def _migrate_documents_to_qdrant(
        self,
        tradition: str,
        user_id: str,
        documents: List[Dict],
        embeddings: List[List[float]],
    ) -> Dict[str, Any]:
        """Migrate documents to appropriate Qdrant collections."""

        stats = {
            "tradition": tradition,
            "total_documents": len(documents),
            "knowledge_documents": 0,
            "personal_documents": 0,
            "errors": 0,
        }

        # Since we're migrating from existing FAISS (PDFs), all documents go to knowledge collection
        knowledge_collection = (
            await self.qdrant_client.get_or_create_knowledge_collection(tradition)
        )

        logger.info(
            f"Migrating {len(documents)} documents to knowledge collection: {knowledge_collection}"
        )

        # Batch process documents
        batch_size = 50
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i : i + batch_size]
            batch_embeddings = embeddings[i : i + batch_size]

            logger.info(
                f"Processing batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}"
            )

            for doc, embedding in zip(batch_docs, batch_embeddings):
                try:
                    # Index in knowledge collection (shared)
                    point_id = await self.qdrant_client.index_knowledge_document(
                        tradition=tradition,
                        text=doc["text"],
                        embedding=embedding,
                        metadata=doc["metadata"],
                    )

                    stats["knowledge_documents"] += 1

                    if stats["knowledge_documents"] % 100 == 0:
                        logger.info(
                            f"Migrated {stats['knowledge_documents']} documents..."
                        )

                except Exception as e:
                    logger.error(f"Failed to migrate document: {e}")
                    stats["errors"] += 1

        return stats

    async def verify_migration(
        self, tradition: str, user_id: str, sample_query: str = "strength training"
    ) -> bool:
        """Verify migration by performing test searches."""
        logger.info(f"Verifying migration for tradition: {tradition}")

        try:
            # Generate query embedding
            query_embedding = self.embedding_model.embed_query(sample_query)

            # Test knowledge collection search
            knowledge_results = await self.qdrant_client.hybrid_search(
                query=sample_query,
                user_id=user_id,
                tradition=tradition,
                query_embedding=query_embedding,
                include_knowledge=True,
                include_personal=False,
                limit=5,
            )

            logger.info(
                f"Found {len(knowledge_results)} results in knowledge collection"
            )

            if knowledge_results:
                logger.info(f"Sample result: {knowledge_results[0].text[:100]}...")
                return True
            else:
                logger.warning("No results found in knowledge collection")
                return False

        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False


async def migrate_all_traditions(user_id: str, dry_run: bool = False) -> Dict[str, Any]:
    """Migrate all available traditions."""
    logger.info("Starting migration for all traditions")

    # Initialize Qdrant client
    qdrant_client = QdrantClient()
    health = await qdrant_client.health_check()

    if not health:
        raise RuntimeError("Qdrant is not available. Please start Qdrant service.")

    migrator = FAISSToQdrantMigrator(qdrant_client, dry_run=dry_run)

    # Find all traditions
    data_dir = Path(DATA_DIR)
    traditions = [
        d.name
        for d in data_dir.iterdir()
        if d.is_dir() and (d / "vectorstore").exists()
    ]

    logger.info(f"Found traditions: {traditions}")

    results = {}
    for tradition in traditions:
        logger.info(f"\n{'='*50}")
        logger.info(f"Migrating tradition: {tradition}")
        logger.info(f"{'='*50}")

        try:
            stats = await migrator.migrate_tradition(tradition, user_id)
            results[tradition] = stats

            # Verify migration if not dry run
            if not dry_run and "error" not in stats:
                verification_success = await migrator.verify_migration(
                    tradition, user_id
                )
                results[tradition]["verification_passed"] = verification_success

        except Exception as e:
            logger.error(f"Failed to migrate tradition {tradition}: {e}")
            results[tradition] = {"error": str(e)}

    return results


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Migrate FAISS vector stores to Qdrant"
    )
    parser.add_argument(
        "--tradition",
        type=str,
        help="Specific tradition to migrate (e.g., canon-default)",
    )
    parser.add_argument(
        "--user-id",
        type=str,
        default="bob",
        help="User ID for personal collection naming (default: bob)",
    )
    parser.add_argument(
        "--all-traditions", action="store_true", help="Migrate all available traditions"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview migration without making changes",
    )
    parser.add_argument(
        "--verify-only", action="store_true", help="Only run verification tests"
    )

    args = parser.parse_args()

    if not args.tradition and not args.all_traditions and not args.verify_only:
        parser.error("Must specify --tradition, --all-traditions, or --verify-only")

    async def run_migration():
        try:
            if args.verify_only:
                # Just run verification
                qdrant_client = QdrantClient()
                migrator = FAISSToQdrantMigrator(qdrant_client)

                if args.tradition:
                    success = await migrator.verify_migration(
                        args.tradition, args.user_id
                    )
                    print(f"Verification {'PASSED' if success else 'FAILED'}")
                else:
                    print("Please specify --tradition for verification")
                return

            if args.all_traditions:
                results = await migrate_all_traditions(args.user_id, args.dry_run)
            else:
                qdrant_client = QdrantClient()
                health = await qdrant_client.health_check()

                if not health:
                    raise RuntimeError(
                        "Qdrant is not available. Please start Qdrant service."
                    )

                migrator = FAISSToQdrantMigrator(qdrant_client, args.dry_run)
                result = await migrator.migrate_tradition(args.tradition, args.user_id)
                results = {args.tradition: result}

            # Print summary
            print("\n" + "=" * 60)
            print("MIGRATION SUMMARY")
            print("=" * 60)

            for tradition, stats in results.items():
                print(f"\nTradition: {tradition}")
                if "error" in stats:
                    print(f"  ❌ Error: {stats['error']}")
                else:
                    print(f"  📊 Total documents: {stats.get('total_documents', 0)}")
                    print(f"  📚 Knowledge docs: {stats.get('knowledge_documents', 0)}")
                    print(f"  👤 Personal docs: {stats.get('personal_documents', 0)}")
                    print(f"  ⚠️  Errors: {stats.get('errors', 0)}")

                    if "verification_passed" in stats:
                        status = (
                            "✅ PASSED" if stats["verification_passed"] else "❌ FAILED"
                        )
                        print(f"  🔍 Verification: {status}")

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            sys.exit(1)

    # Run the migration
    asyncio.run(run_migration())


if __name__ == "__main__":
    main()
