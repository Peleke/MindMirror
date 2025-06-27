"""Retriever architecture for MCP plugins."""

from .base import Retriever, RetrieverMetadata, RetrieverRegistry
from .journal import JournalRetriever, JournalRetrieverFactory

__all__ = [
    "Retriever",
    "RetrieverMetadata", 
    "RetrieverRegistry",
    "JournalRetriever",
    "JournalRetrieverFactory"
]

def create_journal_retriever_registry(journal_client, user_id: str) -> RetrieverRegistry:
    """Create a registry with a journal retriever for the given user."""
    registry = RetrieverRegistry()
    
    factory = JournalRetrieverFactory(journal_client)
    retriever = factory.create_retriever(user_id)
    
    registry.register("journal", retriever)
    return registry 