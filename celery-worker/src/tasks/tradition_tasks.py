import json
import logging
import os
import tempfile
from datetime import datetime
from celery import current_app
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from src.clients.qdrant_client import get_celery_qdrant_client
from src.clients.gcs_client import get_gcs_client
from src.utils.embedding import get_embeddings

logger = logging.getLogger(__name__)


@current_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2, "countdown": 300},
    time_limit=3600,
    name="celery_worker.tasks.rebuild_tradition_knowledge_base",
)
async def rebuild_tradition_knowledge_base(self, tradition: str):
    """Celery task to rebuild a tradition's knowledge base from documents in GCS."""
    logger.info(f"Starting knowledge base rebuild for tradition: {tradition}")

    gcs_client = get_gcs_client()
    qdrant_client = get_celery_qdrant_client()

    # Clear existing knowledge data
    knowledge_collection_name = qdrant_client.get_knowledge_collection_name(tradition)
    try:
        qdrant_client.delete_collection(knowledge_collection_name)
        logger.info(f"Deleted existing collection: {knowledge_collection_name}")
    except Exception as e:
        logger.warning(f"Could not delete collection {knowledge_collection_name}: {e}")

    qdrant_client.get_or_create_knowledge_collection(tradition)

    # Process documents
    doc_prefix = f"{tradition}/"
    doc_blobs = gcs_client.list_files(prefix=doc_prefix)

    if not doc_blobs:
        logger.warning(f"No documents found for tradition '{tradition}'")
        return {"status": "success", "message": "No documents to process."}

    processed_files = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    for blob in doc_blobs:
        if not blob.name.endswith(".pdf"):
            continue

        logger.info(f"Processing document: {blob.name}")
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file_path = temp_file.name

            gcs_client.download_to_filename(blob.name, temp_file_path)
            loader = PyPDFLoader(temp_file_path)
            docs = loader.load_and_split(text_splitter)
            os.remove(temp_file_path)

            texts = [doc.page_content for doc in docs]

            # Generate embeddings using async function
            embeddings = await get_embeddings(texts)

            metadatas = [
                {
                    "source_type": "pdf",
                    "source_id": blob.name,
                    "document_type": "knowledge",
                    "page": doc.metadata.get("page", 0) + 1,
                }
                for doc in docs
            ]

            qdrant_client.index_knowledge_documents(
                tradition=tradition,
                texts=texts,
                embeddings=embeddings,
                metadatas=metadatas,
            )
            processed_files.append(blob.name)
            logger.info(f"Successfully processed {len(docs)} chunks from {blob.name}")

        except Exception as e:
            logger.error(f"Failed to process document {blob.name}: {e}")
            if "temp_file_path" in locals() and os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    # Update manifest
    manifest = {
        "last_updated": datetime.utcnow().isoformat(),
        "processed_files": processed_files,
        "tradition": tradition,
    }
    manifest_path = f"{tradition}/metadata/manifest.json"
    gcs_client.upload_from_string(manifest_path, json.dumps(manifest, indent=2))

    logger.info(f"Knowledge base rebuild complete for tradition: {tradition}")
    return {"status": "success", "processed_files": len(processed_files)}


def queue_tradition_reindex(tradition: str):
    """Queue a tradition reindexing task."""
    return current_app.send_task(
        "celery_worker.tasks.rebuild_tradition_knowledge_base",
        args=[tradition],
    )
