"""Embedding utilities for MindMirror CLI."""

import logging
import os
from typing import List

from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger(__name__)


def get_embedding_model():
    """Returns the embedding model based on the provider."""
    provider = os.getenv("EMBEDDING_PROVIDER", "ollama")
    
    if provider == "ollama":
        model = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return OllamaEmbeddings(model=model, base_url=base_url)
    else:
        # OpenAI fallback
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI embeddings")
        return OpenAIEmbeddings()


async def get_embedding(text: str) -> List[float]:
    """Generates an embedding for a single piece of text."""
    try:
        embedding_model = get_embedding_model()
        return await embedding_model.aembed_query(text)
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        return None


async def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Generates embeddings for a list of texts in a batch."""
    try:
        embedding_model = get_embedding_model()
        return await embedding_model.aembed_documents(texts)
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        return [] 