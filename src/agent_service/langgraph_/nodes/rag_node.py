"""
RAG node for chat operations.

This module provides a LangGraph node that handles retrieval-augmented
generation for chat operations using Qdrant for document retrieval.
"""

import logging
from typing import Any, Dict, List, Optional

from langchain_core.documents import Document
from langchain_core.language_models import BaseLanguageModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langgraph.prebuilt import ToolNode

from ...app.services.embedding_service import EmbeddingService
from ...app.services.qdrant_service import QdrantService
from ...app.services.search_service import SearchService
from ..state import RAGAgentState
from ...llms.provider_manager import get_provider_manager

logger = logging.getLogger(__name__)


class RAGNode:
    """
    RAG node for chat operations.

    This node handles retrieval-augmented generation by:
    1. Retrieving relevant documents from Qdrant
    2. Generating responses using the retrieved context
    """

    def __init__(
        self,
        retriever=None,  # Will be set dynamically
        provider: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the RAG node.

        Args:
            retriever: QdrantRetriever instance (set dynamically)
            provider: Optional LLM provider to use
            overrides: Optional configuration overrides
        """
        self.retriever = retriever
        self.provider = provider
        self.overrides = overrides or {}

        # Initialize services
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()
        self.search_service = SearchService(
            embedding_service=self.embedding_service,
            qdrant_service=self.qdrant_service,
        )

        # Set up the RAG chain
        self._setup_rag_chain()

    def _setup_rag_chain(self):
        """Set up the RAG chain with prompt and LLM."""
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_template(
            """You are a helpful AI assistant that answers questions based on the provided context.

Context:
{context}

Question: {question}

Please provide a helpful and accurate answer based on the context above. If the context doesn't contain enough information to answer the question, say so clearly.

Answer:"""
        )

        # Get the LLM (will be set dynamically based on provider)
        self.llm = self._get_llm()

        # Create the RAG chain - fix to use proper callable
        self.rag_chain = (
            {"context": lambda x: self._retrieve_documents(x), "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def _get_llm(self) -> BaseLanguageModel:
        """
        Get the language model using the ProviderManager.

        Returns:
            Configured language model
        """
        try:
            provider_manager = get_provider_manager()
            
            # Create config from environment variables first
            config = provider_manager.create_config_from_env()
            
            # Override with any specified provider
            if self.provider:
                config["provider"] = self.provider
                
            # Add any overrides
            config.update(self.overrides)
            
            # Use provider manager to create model with fallback
            return provider_manager.create_model_with_fallback(config if config else None)
            
        except Exception as e:
            logger.error(f"Failed to create LLM using ProviderManager: {e}")
            # Fallback to default provider manager behavior
            provider_manager = get_provider_manager()
            return provider_manager.create_model_with_fallback()

    def _retrieve_documents(self, query: str) -> str:
        """
        Retrieve relevant documents for the query.

        Args:
            query: The query string to search for

        Returns:
            Formatted context string from retrieved documents
        """
        try:
            if not query:
                return "No query provided."

            # Use search service if no retriever is set
            if not self.retriever:
                logger.warning("No retriever set, using search service with default parameters")
                # For now, return a placeholder context
                return f"Context for query: {query}\n[Note: Retriever not properly configured]"

            # Retrieve documents using the retriever with modern interface
            documents = self.retriever.invoke(query)

            # Format context
            context_parts = []
            for i, doc in enumerate(documents, 1):
                content = doc.page_content
                metadata = doc.metadata
                source = metadata.get("source", "Unknown")
                context_parts.append(f"Document {i} (Source: {source}):\n{content}\n")

            context = (
                "\n".join(context_parts)
                if context_parts
                else "No relevant documents found."
            )

            logger.info(
                f"Retrieved {len(documents)} documents for query: {query[:100]}..."
            )
            return context

        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return f"Error retrieving documents: {str(e)}"

    def __call__(self, state: RAGAgentState) -> RAGAgentState:
        """
        Process the state and generate a response.

        Args:
            state: Current agent state

        Returns:
            Updated state with generated response
        """
        try:
            # Get the latest message
            messages = state.get("messages", [])
            if not messages:
                return state

            latest_message = messages[-1]
            query = latest_message.get("content", "")

            if not query:
                return state

            # Set up retriever dynamically if not already set
            if not self.retriever and state.get("user_id") and state.get("tradition_id"):
                try:
                    user_id = state.get("user_id")
                    tradition_id = state.get("tradition_id")
                    logger.info(f"RAG Node: Creating retriever with user_id={user_id}, tradition_id='{tradition_id}'")
                    self.retriever = self.search_service.create_retriever(
                        user_id=user_id, tradition_id=tradition_id, search_type="hybrid"
                    )
                    logger.info(f"Created retriever for user {user_id} with tradition {tradition_id}")
                except Exception as e:
                    logger.warning(f"Failed to create retriever: {e}", exc_info=True)

            # Generate response using RAG chain
            response = self.rag_chain.invoke(query)

            # Add response to messages
            messages.append(
                {
                    "role": "assistant",
                    "content": response,
                    "timestamp": self._get_timestamp(),
                }
            )

            # Update state
            state["messages"] = messages
            state["last_response"] = response

            logger.info(f"Generated response for query: {query[:100]}...")
            return state

        except Exception as e:
            logger.error(f"Error in RAG node: {e}")
            # Add error response to messages
            messages = state.get("messages", [])
            messages.append(
                {
                    "role": "assistant",
                    "content": f"I apologize, but I encountered an error: {str(e)}",
                    "timestamp": self._get_timestamp(),
                }
            )
            state["messages"] = messages
            state["error"] = str(e)
            return state

    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        from datetime import datetime

        return datetime.now().isoformat()
