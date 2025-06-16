#!/usr/bin/env python3
"""
Script to load local documents into the Qdrant knowledge base.

This script reads text files from the local_gcs_bucket and indexes them
into the Qdrant vector store for the specified tradition.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import List

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent_service.embedding import get_embedding
from agent_service.vector_stores.qdrant_client import QdrantClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def load_documents_to_qdrant(tradition: str = "canon-default"):
    """Load local text documents into Qdrant knowledge base."""

    # Path to local documents
    docs_path = Path("local_gcs_bucket") / tradition / "documents"

    if not docs_path.exists():
        logger.error(f"Documents path not found: {docs_path}")
        return False

    # Get all text files
    text_files = list(docs_path.glob("*.txt"))

    if not text_files:
        logger.warning(f"No text files found in {docs_path}")
        return False

    logger.info(f"Found {len(text_files)} text files to process")

    # Initialize Qdrant client
    qdrant_client = QdrantClient()

    # Check health
    health = await qdrant_client.health_check()
    if not health:
        logger.error("Qdrant is not available. Please ensure Qdrant is running.")
        return False

    # Prepare documents for indexing
    texts = []
    embeddings = []
    metadatas = []

    for file_path in text_files:
        logger.info(f"Processing {file_path.name}")

        try:
            # Read file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            if not content:
                logger.warning(f"File {file_path.name} is empty, skipping")
                continue

            # Generate embedding
            embedding = await get_embedding(content)
            if not embedding:
                logger.error(f"Failed to generate embedding for {file_path.name}")
                continue

            # Prepare metadata
            metadata = {
                "source_type": "pdf",  # Keep consistent with expected format
                "source_id": file_path.name,
                "document_type": "knowledge",
                "page": 1,
                "file_type": "txt",
            }

            texts.append(content)
            embeddings.append(embedding)
            metadatas.append(metadata)

            logger.info(f"Prepared {file_path.name} for indexing")

        except Exception as e:
            logger.error(f"Failed to process {file_path.name}: {e}")
            continue

    if not texts:
        logger.error("No documents were successfully processed")
        return False

    # Index documents in batch
    logger.info(f"Indexing {len(texts)} documents into Qdrant...")

    try:
        point_ids = await qdrant_client.index_knowledge_documents(
            tradition=tradition, texts=texts, embeddings=embeddings, metadatas=metadatas
        )

        logger.info(f"Successfully indexed {len(point_ids)} documents")
        logger.info(f"Knowledge base for tradition '{tradition}' is now ready!")
        return True

    except Exception as e:
        logger.error(f"Failed to index documents: {e}")
        return False


async def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Load local documents into Qdrant")
    parser.add_argument(
        "--tradition",
        type=str,
        default="canon-default",
        help="Tradition name (default: canon-default)",
    )

    args = parser.parse_args()

    logger.info(f"Loading documents for tradition: {args.tradition}")

    success = await load_documents_to_qdrant(args.tradition)

    if success:
        logger.info("✅ Document loading completed successfully!")
        print(
            "\n🎉 Knowledge base is ready! You can now ask questions to the AI coach."
        )
    else:
        logger.error("❌ Document loading failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
