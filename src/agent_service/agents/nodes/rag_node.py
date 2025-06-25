"""
RAG (Retrieval-Augmented Generation) node for LangGraph agents.

This node handles the core RAG functionality: retrieving relevant documents
and generating responses based on the retrieved context.
"""

import logging
from typing import Any, Dict, List, Optional

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import Runnable, RunnablePassthrough

from agent_service.agents.state import RAGAgentState, StateManager
from agent_service.llms.factory import get_llm
from agent_service.tracing.decorators import trace_langchain_operation, trace_runnable

logger = logging.getLogger(__name__)


class RAGNode:
    """
    LangGraph node for RAG operations.
    
    This node handles document retrieval and response generation
    in a modular, testable way.
    """
    
    def __init__(
        self,
        retriever: BaseRetriever,
        prompt_template: Optional[ChatPromptTemplate] = None,
        llm: Optional[Runnable] = None,
        max_documents: int = 5,
    ):
        """
        Initialize the RAG node.
        
        Args:
            retriever: Document retriever to use
            prompt_template: Custom prompt template (optional)
            llm: Language model to use (optional)
            max_documents: Maximum number of documents to retrieve
        """
        self.retriever = retriever
        self.max_documents = max_documents
        
        # Use default prompt template if none provided
        if prompt_template is None:
            self.prompt_template = self._create_default_prompt()
        else:
            self.prompt_template = prompt_template
        
        # Use default LLM if none provided
        if llm is None:
            self.llm = get_llm(temperature=0, streaming=False)
        else:
            self.llm = llm
        
        # Create the RAG chain
        self.rag_chain = self._create_rag_chain()
        
        # Wrap with tracing
        self.traced_rag_chain = trace_runnable(
            self.rag_chain,
            name="rag_node.chain",
            tags=["rag", "node"],
        )
    
    def _create_default_prompt(self) -> ChatPromptTemplate:
        """Create the default RAG prompt template."""
        template = """Answer the question based only on the following context:
{context}

Question: {question}

Answer:"""
        
        return ChatPromptTemplate.from_template(template)
    
    def _create_rag_chain(self) -> Runnable:
        """Create the RAG chain."""
        return (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | self.prompt_template
            | self.llm
            | StrOutputParser()
        )
    
    @trace_langchain_operation("rag_retrieval", tags=["retrieval"])
    def retrieve_documents(self, query: str) -> List[Document]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: The search query
            
        Returns:
            List of relevant documents
        """
        try:
            documents = self.retriever.get_relevant_documents(query)
            logger.info(f"Retrieved {len(documents)} documents for query: {query[:50]}...")
            return documents[:self.max_documents]
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    @trace_langchain_operation("rag_generation", tags=["generation"])
    def generate_response(self, query: str, context: List[Document]) -> str:
        """
        Generate a response based on query and context.
        
        Args:
            query: The user query
            context: Retrieved documents for context
            
        Returns:
            Generated response
        """
        try:
            # Format context for the prompt
            context_text = self._format_context(context)
            
            # Generate response
            response = self.traced_rag_chain.invoke({
                "context": context_text,
                "question": query,
            })
            
            logger.info(f"Generated response for query: {query[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error while processing your question: {str(e)}"
    
    def _format_context(self, documents: List[Document]) -> str:
        """
        Format documents into context string.
        
        Args:
            documents: List of documents to format
            
        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant context found."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "Unknown source")
            context_parts.append(f"Document {i} (Source: {source}):\n{doc.page_content}")
        
        return "\n\n".join(context_parts)
    
    def __call__(self, state: RAGAgentState) -> RAGAgentState:
        """
        Execute the RAG node on a state.
        
        This is the main entry point for LangGraph integration.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state
        """
        try:
            query = state["query"]
            
            # Step 1: Retrieve documents
            documents = self.retrieve_documents(query)
            
            # Update state with retrieved documents
            updated_state = state.copy()
            for doc in documents:
                score = doc.metadata.get("score", None)
                updated_state = StateManager.add_document_to_context(
                    updated_state, doc, score
                )
            
            # Step 2: Generate response
            response = self.generate_response(query, documents)
            
            # Update state with generated response
            updated_state = StateManager.set_generated_response(
                updated_state,
                response,
                metadata={
                    "documents_retrieved": len(documents),
                    "max_documents": self.max_documents,
                }
            )
            
            logger.info(f"RAG node completed for user {state['user_id']}")
            return updated_state
            
        except Exception as e:
            logger.error(f"Error in RAG node: {e}")
            return StateManager.add_error(
                state,
                error=str(e),
                error_type=type(e).__name__,
            )


class RAGNodeFactory:
    """
    Factory for creating RAG nodes with different configurations.
    """
    
    @staticmethod
    def create_standard_rag_node(
        retriever: BaseRetriever,
        max_documents: int = 5,
    ) -> RAGNode:
        """
        Create a standard RAG node with default settings.
        
        Args:
            retriever: Document retriever
            max_documents: Maximum documents to retrieve
            
        Returns:
            Configured RAG node
        """
        return RAGNode(
            retriever=retriever,
            max_documents=max_documents,
        )
    
    @staticmethod
    def create_custom_rag_node(
        retriever: BaseRetriever,
        prompt_template: ChatPromptTemplate,
        llm: Runnable,
        max_documents: int = 5,
    ) -> RAGNode:
        """
        Create a custom RAG node with specific prompt and LLM.
        
        Args:
            retriever: Document retriever
            prompt_template: Custom prompt template
            llm: Custom language model
            max_documents: Maximum documents to retrieve
            
        Returns:
            Configured RAG node
        """
        return RAGNode(
            retriever=retriever,
            prompt_template=prompt_template,
            llm=llm,
            max_documents=max_documents,
        )
    
    @staticmethod
    def create_coaching_rag_node(
        retriever: BaseRetriever,
        max_documents: int = 5,
    ) -> RAGNode:
        """
        Create a RAG node specifically for coaching tasks.
        
        Args:
            retriever: Document retriever
            max_documents: Maximum documents to retrieve
            
        Returns:
            Configured coaching RAG node
        """
        # Create coaching-specific prompt
        coaching_template = ChatPromptTemplate.from_template("""
You are a knowledgeable coaching assistant. Answer the question based on the following context,
providing practical, actionable advice when appropriate.

Context:
{context}

Question: {question}

Provide a helpful, encouraging response that draws from the context:
""")
        
        # Use a slightly more creative LLM for coaching
        coaching_llm = get_llm(temperature=0.3, streaming=False)
        
        return RAGNode(
            retriever=retriever,
            prompt_template=coaching_template,
            llm=coaching_llm,
            max_documents=max_documents,
        ) 