"""Qdrant-based knowledge base builder for MindMirror CLI."""

import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

from mindmirror_cli.core.client import QdrantClient
from mindmirror_cli.core.embedding import get_embedding
from mindmirror_cli.core.tradition_loader import create_tradition_loader, TraditionLoader
from mindmirror_cli.core.utils import get_qdrant_url, get_qdrant_api_key

logger = logging.getLogger(__name__)


class QdrantKnowledgeBaseBuilder:
    """
    Modern knowledge base builder using Qdrant vector store.

    Supports multiple document sources, enhanced metadata, and
    robust error handling with progress reporting.
    """

    def __init__(self, qdrant_client: Optional[QdrantClient] = None, tradition_loader: TraditionLoader = None):
        self.qdrant_client = qdrant_client or QdrantClient()
        self.tradition_loader = tradition_loader or create_tradition_loader()
        
        # Get chunking configuration from environment
        chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
        chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        self.stats = {
            "processed_files": 0,
            "failed_files": 0,
            "total_chunks": 0,
            "start_time": None,
            "end_time": None,
        }

    async def health_check(self) -> bool:
        """Verify Qdrant connectivity before processing."""
        try:
            health = await self.qdrant_client.health_check()
            if not health:
                logger.error("Qdrant health check failed")
                return False
            logger.info("✅ Qdrant connection verified")
            return True
        except Exception as e:
            logger.error(f"❌ Qdrant connection failed: {e}")
            return False

    def discover_source_directories(self, base_dirs: List[str]) -> Dict[str, List[Path]]:
        """
        Discover traditions using the loader (GCS-first, local fallback).
        If local source directories are provided, use local discovery.
        """
        traditions = {}
        
        # Check if we have local source directories that actually exist
        local_dirs_exist = any(Path(base_dir).exists() for base_dir in base_dirs)
        
        if local_dirs_exist:
            # Use local discovery for the provided directories
            logger.info(f"Using local discovery for directories: {base_dirs}")
            for base_dir in base_dirs:
                base_path = Path(base_dir)
                if not base_path.exists():
                    logger.warning(f"Base directory not found: {base_dir}")
                    continue
                
                # If the base directory itself contains files, treat it as a tradition
                if base_path.is_dir() and (any(base_path.glob("*.pdf")) or any(base_path.glob("*.txt"))):
                    tradition_name = base_path.name
                    if tradition_name not in traditions:
                        traditions[tradition_name] = []
                    traditions[tradition_name].append(base_path)
                    logger.info(f"Found tradition '{tradition_name}' in {base_path}")
                
                # Look for subdirectories that might be traditions
                for item in base_path.iterdir():
                    if item.is_dir():
                        tradition_name = item.name
                        # Check if this directory contains documents
                        if any(item.glob("*.pdf")) or any(item.glob("*.txt")):
                            if tradition_name not in traditions:
                                traditions[tradition_name] = []
                            traditions[tradition_name].append(item)
                            logger.info(f"Found tradition '{tradition_name}' in {item}")
        else:
            # Use tradition loader (GCS-first, local fallback)
            logger.info("Using tradition loader for discovery")
            for tradition in self.tradition_loader.list_traditions():
                traditions[tradition] = []  # We don't resolve actual directories in GCS mode
        
        return traditions

    async def load_documents_from_directory(self, directory: Path) -> List[Document]:
        """
        Load and chunk documents from a directory.

        Args:
            directory: Path to directory containing documents

        Returns:
            List of chunked Document objects
        """
        documents = []

        # Process PDF files
        for pdf_file in directory.glob("*.pdf"):
            try:
                logger.info(f"Loading PDF: {pdf_file.name}")
                loader = PyPDFLoader(str(pdf_file))
                pdf_docs = loader.load_and_split(self.text_splitter)

                # Add file metadata
                for doc in pdf_docs:
                    doc.metadata.update(
                        {"source_id": pdf_file.name, "file_type": "pdf"}
                    )

                documents.extend(pdf_docs)
                logger.info(f"Loaded {len(pdf_docs)} chunks from {pdf_file.name}")

            except Exception as e:
                logger.error(f"Failed to load PDF {pdf_file}: {e}")
                self.stats["failed_files"] += 1
                continue

        # Process text files
        for txt_file in directory.glob("*.txt"):
            try:
                logger.info(f"Loading text file: {txt_file.name}")
                loader = TextLoader(str(txt_file), encoding="utf-8")
                txt_docs = loader.load()

                # Split text documents
                chunks = self.text_splitter.split_documents(txt_docs)

                # Add file metadata and page numbers
                for i, doc in enumerate(chunks):
                    doc.metadata.update(
                        {
                            "source_id": txt_file.name,
                            "file_type": "txt",
                            "page": i + 1,  # Chunk number for text files
                        }
                    )

                documents.extend(chunks)
                logger.info(f"Loaded {len(chunks)} chunks from {txt_file.name}")

            except Exception as e:
                logger.error(f"Failed to load text file {txt_file}: {e}")
                self.stats["failed_files"] += 1
                continue

        self.stats["processed_files"] += len(
            [f for f in directory.glob("*.pdf")]
        ) + len([f for f in directory.glob("*.txt")])
        return documents

    def prepare_metadata(self, doc: Document, tradition: str) -> Dict[str, Any]:
        """
        Prepare enhanced metadata for Qdrant storage.

        Args:
            doc: LangChain Document object
            tradition: Tradition name

        Returns:
            Enhanced metadata dictionary
        """
        metadata = {
            "source_type": "pdf",  # Keep consistent with existing system
            "source_id": doc.metadata.get("source_id", "unknown"),
            "document_type": "knowledge",
            "tradition": tradition,
            "file_type": doc.metadata.get("file_type", "unknown"),
            "page": doc.metadata.get("page", 1),
            "indexed_at": datetime.utcnow().isoformat(),
            "chunk_size": len(doc.page_content),
        }

        # Preserve any additional metadata from the original document
        for key, value in doc.metadata.items():
            if key not in metadata:
                metadata[key] = value

        return metadata

    async def build_tradition_knowledge_base(
        self, tradition: str, source_dirs: List[Path], clear_existing: bool = False
    ) -> Dict[str, Any]:
        """
        Build knowledge base for a specific tradition.

        Args:
            tradition: Tradition name
            source_dirs: List of source directories for this tradition
            clear_existing: Whether to clear existing collection

        Returns:
            Build statistics
        """
        logger.info(f"🏗️  Building knowledge base for tradition: {tradition}")

        # Clear existing collection if requested
        if clear_existing:
            collection_name = self.qdrant_client.get_knowledge_collection_name(
                tradition
            )
            try:
                await self.qdrant_client.delete_collection(collection_name)
                logger.info(f"🗑️  Cleared existing collection: {collection_name}")
            except Exception as e:
                logger.warning(f"Could not clear collection {collection_name}: {e}")

        # Ensure collection exists
        await self.qdrant_client.get_or_create_knowledge_collection(tradition)

        # Load documents from all source directories
        all_documents = []
        for source_dir in source_dirs:
            logger.info(f"📁 Processing directory: {source_dir}")
            docs = await self.load_documents_from_directory(source_dir)
            all_documents.extend(docs)

        if not all_documents:
            logger.warning(f"⚠️  No documents found for tradition '{tradition}'")
            return {
                "tradition": tradition,
                "status": "warning",
                "message": "No documents found",
                "processed_chunks": 0,
            }

        logger.info(f"📄 Total documents loaded: {len(all_documents)} chunks")

        # Prepare for batch indexing
        texts = []
        embeddings = []
        metadatas = []

        for doc in all_documents:
            try:
                # Generate embedding
                embedding = await get_embedding(doc.page_content)
                if not embedding:
                    logger.error(f"Failed to generate embedding for chunk")
                    continue

                # Prepare metadata
                metadata = self.prepare_metadata(doc, tradition)

                texts.append(doc.page_content)
                embeddings.append(embedding)
                metadatas.append(metadata)

            except Exception as e:
                logger.error(f"Failed to process document chunk: {e}")
                continue

        if not texts:
            return {
                "tradition": tradition,
                "status": "error",
                "message": "No embeddings generated",
                "processed_chunks": 0,
            }

        # Batch index to Qdrant
        logger.info(f"🚀 Indexing {len(texts)} chunks to Qdrant...")
        try:
            point_ids = await self.qdrant_client.index_knowledge_documents(
                tradition=tradition,
                texts=texts,
                embeddings=embeddings,
                metadatas=metadatas,
            )

            self.stats["total_chunks"] += len(point_ids)

            logger.info(
                f"✅ Successfully indexed {len(point_ids)} chunks for '{tradition}'"
            )

            return {
                "tradition": tradition,
                "status": "success",
                "processed_chunks": len(point_ids),
                "processed_files": self.stats["processed_files"],
                "failed_files": self.stats["failed_files"],
            }

        except Exception as e:
            logger.error(f"❌ Failed to index chunks for '{tradition}': {e}")
            return {
                "tradition": tradition,
                "status": "error",
                "message": str(e),
                "processed_chunks": 0,
            }

    async def build_all_traditions(
        self,
        source_dirs: List[str] = None,
        specific_tradition: str = None,
        clear_existing: bool = False,
    ) -> Dict[str, Any]:
        """
        Build knowledge bases for all discovered traditions.

        Args:
            source_dirs: List of base directories to scan
            specific_tradition: Build only this tradition if specified
            clear_existing: Whether to clear existing collections

        Returns:
            Overall build statistics
        """
        self.stats["start_time"] = datetime.utcnow()

        # Default source directories
        if source_dirs is None:
            source_dirs = [
                "local_gcs_bucket",  # Modern structure
                "pdfs",  # Legacy structure
            ]

        # Discover traditions
        traditions_map = self.discover_source_directories(source_dirs)

        if not traditions_map:
            logger.error("❌ No traditions found in source directories")
            return {
                "status": "error",
                "message": "No traditions found",
                "traditions": {},
            }

        # Filter to specific tradition if requested
        if specific_tradition:
            if specific_tradition in traditions_map:
                traditions_map = {
                    specific_tradition: traditions_map[specific_tradition]
                }
            else:
                logger.error(f"❌ Tradition '{specific_tradition}' not found")
                return {
                    "status": "error",
                    "message": f"Tradition '{specific_tradition}' not found",
                    "traditions": {},
                }

        logger.info(f"🎯 Found traditions: {list(traditions_map.keys())}")

        # Build each tradition
        results = {}
        for tradition, source_dirs_list in traditions_map.items():
            try:
                result = await self.build_tradition_knowledge_base(
                    tradition=tradition,
                    source_dirs=source_dirs_list,
                    clear_existing=clear_existing,
                )
                results[tradition] = result

            except Exception as e:
                logger.error(f"❌ Failed to build tradition '{tradition}': {e}")
                results[tradition] = {"status": "error", "message": str(e)}

        self.stats["end_time"] = datetime.utcnow()
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()

        # Overall statistics
        successful_traditions = [
            t for t, r in results.items() if r.get("status") == "success"
        ]
        total_chunks = sum(r.get("processed_chunks", 0) for r in results.values())

        logger.info(f"🎉 Build completed in {duration:.2f}s")
        logger.info(f"✅ Successful traditions: {len(successful_traditions)}")
        logger.info(f"📊 Total chunks indexed: {total_chunks}")

        return {
            "status": "success" if successful_traditions else "error",
            "duration_seconds": duration,
            "successful_traditions": successful_traditions,
            "total_chunks": total_chunks,
            "total_files_processed": self.stats["processed_files"],
            "total_files_failed": self.stats["failed_files"],
            "traditions": results,
        } 