import logging
from typing import List

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings

from config import EMBEDDING_PROVIDER, OLLAMA_BASE_URL, OLLAMA_EMBEDDING_MODEL

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_embedding_model():
    """
    Returns the embedding model based on the provider.
    """
    if EMBEDDING_PROVIDER == "ollama":
        return OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL)
    else:
        return OpenAIEmbeddings()


def create_vector_store(
    documents: List[Document],
    db_path: str,
    batch_size: int = 32,
    progress_callback: callable = None,
) -> FAISS:
    """
    Creates a FAISS vector store from a list of documents in batches.

    Args:
        documents (List[Document]): The documents to embed.
        db_path (str): The path to save the FAISS index to.
        batch_size (int): The number of documents to process in each batch.
        progress_callback (callable, optional): A function to call with the number of processed documents.

    Returns:
        The created FAISS vector store instance.
    """
    logger.info("Creating embeddings...")
    embeddings = get_embedding_model()

    if not documents:
        raise ValueError("No documents provided to create a vector store.")

    logger.info(f"Processing {len(documents)} documents in batches of {batch_size}...")

    # Initialize the vector store with the first batch
    first_batch = documents[:batch_size]
    logger.info(f"Processing batch from document 0 to {len(first_batch)}...")
    vectorstore = FAISS.from_documents(first_batch, embeddings)
    if progress_callback:
        progress_callback(len(first_batch))

    # Add subsequent batches
    for i in range(batch_size, len(documents), batch_size):
        batch = documents[i : i + batch_size]
        texts = [doc.page_content for doc in batch]
        metadatas = [doc.metadata for doc in batch]

        logger.info(f"Embedding batch from document {i} to {i+len(batch)}...")
        batch_embeddings = embeddings.embed_documents(texts)

        text_embedding_pairs = list(zip(texts, batch_embeddings))

        logger.info(f"Adding batch to vector store...")
        vectorstore.add_embeddings(text_embedding_pairs, metadatas=metadatas)

        if progress_callback:
            progress_callback(i + len(batch))

    logger.info(f"Saving vector store to {db_path}...")
    vectorstore.save_local(folder_path=db_path)

    return vectorstore


def load_vector_store(db_path: str) -> FAISS:
    """
    Loads a FAISS vector store from a local path.

    Args:
        db_path (str): The path to the FAISS index.

    Returns:
        The loaded FAISS vector store instance.
    """
    logger.info(f"Loading vector store from {db_path}...")
    embeddings = get_embedding_model()
    vectorstore = FAISS.load_local(
        folder_path=db_path,
        embeddings=embeddings,
        allow_dangerous_deserialization=True,  # Required for FAISS
    )
    logger.info("Vector store loaded successfully.")
    return vectorstore
