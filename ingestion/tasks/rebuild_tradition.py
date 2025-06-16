import logging
import json
from datetime import datetime

from agent_service.celery_app import celery_app
from agent_service.vector_stores.qdrant_client import get_qdrant_client
from agent_service.embedding import get_embedding
from ingestion.utils.gcs_client import get_gcs_client
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import tempfile
import os

logger = logging.getLogger(__name__)

@celery_app.task(name="rebuild_tradition_knowledge_base")
def rebuild_tradition_knowledge_base(tradition: str):
    """
    Celery task to rebuild a tradition's knowledge base from documents in GCS.
    """
    logger.info(f"Starting knowledge base rebuild for tradition: {tradition}")
    
    gcs_client = get_gcs_client()
    qdrant_client = get_qdrant_client()
    
    # 1. Clear existing knowledge data for this tradition in Qdrant
    knowledge_collection_name = qdrant_client.get_knowledge_collection_name(tradition)
    try:
        qdrant_client.delete_collection(knowledge_collection_name)
        logger.info(f"Deleted existing collection: {knowledge_collection_name}")
    except Exception as e:
        logger.warning(f"Could not delete collection {knowledge_collection_name} (it may not exist): {e}")
    
    qdrant_client.get_or_create_knowledge_collection(tradition)
    logger.info(f"Ensured collection exists: {knowledge_collection_name}")

    # 2. List all documents in the tradition's GCS folder
    doc_prefix = f"{tradition}/documents/"
    doc_blobs = gcs_client.list_files(prefix=doc_prefix)
    
    if not doc_blobs:
        logger.warning(f"No documents found in GCS for tradition '{tradition}' with prefix '{doc_prefix}'.")
        return {"status": "success", "message": "No documents to process."}

    # 3. Process each document
    processed_files = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    for blob in doc_blobs:
        if not blob.name.endswith(".pdf"):
            continue

        logger.info(f"Processing document: {blob.name}")
        try:
            # Create a temporary file to download the PDF to.
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file_path = temp_file.name
            
            # Use the GCS client to download the file.
            gcs_client.download_to_filename(blob.name, temp_file_path)

            loader = PyPDFLoader(temp_file_path)
            docs = loader.load_and_split(text_splitter)
            os.remove(temp_file_path)
            
            # 4. Extract text, generate embeddings, and prepare for Qdrant
            texts = [doc.page_content for doc in docs]
            embeddings = [get_embedding(text) for text in texts] # This should be batched in a real scenario
            
            metadatas = [{
                "source_type": "pdf",
                "source_id": blob.name,
                "document_type": "knowledge",
                "page": doc.metadata.get("page", 0) + 1,
            } for doc in docs]

            # 5. Bulk upload to Qdrant
            qdrant_client.index_knowledge_documents(
                tradition=tradition,
                texts=texts,
                embeddings=embeddings,
                metadatas=metadatas
            )
            processed_files.append(blob.name)
            logger.info(f"Successfully processed and indexed {len(docs)} chunks from {blob.name}")

        except Exception as e:
            logger.error(f"Failed to process document {blob.name}: {e}")
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    # 6. Update manifest file
    manifest = {
        "last_updated": datetime.utcnow().isoformat(),
        "processed_files": processed_files,
        "tradition": tradition,
    }
    manifest_path = f"{tradition}/metadata/manifest.json"
    gcs_client.upload_from_string(manifest_path, json.dumps(manifest, indent=2))
    
    logger.info(f"Knowledge base rebuild complete for tradition: {tradition}")
    return {"status": "success", "processed_files": len(processed_files)} 