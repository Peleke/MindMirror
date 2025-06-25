"""
Tests for RAG node functionality.

These tests verify that the RAG node works correctly with LangGraph,
handles document retrieval and response generation properly,
and integrates well with the tracing system.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.prompts import ChatPromptTemplate

from agent_service.agents.nodes.rag_node import RAGNode, RAGNodeFactory
from agent_service.agents.state import RAGAgentState, AgentStateFactory


class TestRAGNode:
    """Test RAG node functionality."""
    
    def test_rag_node_initialization(self):
        """Test that RAG node initializes correctly."""
        mock_retriever = Mock(spec=BaseRetriever)
        
        node = RAGNode(
            retriever=mock_retriever,
            max_documents=3,
        )
        
        assert node.retriever == mock_retriever
        assert node.max_documents == 3
        assert node.prompt_template is not None
        assert node.llm is not None
        assert node.rag_chain is not None
    
    def test_rag_node_with_custom_prompt_and_llm(self):
        """Test RAG node with custom prompt template and LLM."""
        mock_retriever = Mock(spec=BaseRetriever)
        mock_prompt = ChatPromptTemplate.from_template("Custom: {context} {question}")
        mock_llm = Mock()
        
        node = RAGNode(
            retriever=mock_retriever,
            prompt_template=mock_prompt,
            llm=mock_llm,
        )
        
        assert node.prompt_template == mock_prompt
        assert node.llm == mock_llm
    
    @patch('agent_service.agents.nodes.rag_node.trace_runnable')
    def test_rag_node_tracing_integration(self, mock_trace_runnable):
        """Test that RAG node integrates with tracing."""
        mock_retriever = Mock(spec=BaseRetriever)
        mock_trace_runnable.return_value = Mock()
        
        node = RAGNode(retriever=mock_retriever)
        
        mock_trace_runnable.assert_called_once()
        call_args = mock_trace_runnable.call_args
        assert call_args[1]["name"] == "rag_node.chain"
        assert "rag" in call_args[1]["tags"]
        assert "node" in call_args[1]["tags"]
    
    def test_retrieve_documents_success(self):
        """Test successful document retrieval."""
        mock_retriever = Mock(spec=BaseRetriever)
        mock_documents = [
            Document(page_content="doc1", metadata={"source": "test1"}),
            Document(page_content="doc2", metadata={"source": "test2"}),
        ]
        mock_retriever.get_relevant_documents.return_value = mock_documents
        
        node = RAGNode(retriever=mock_retriever, max_documents=5)
        
        result = node.retrieve_documents("test query")
        
        assert result == mock_documents
        mock_retriever.get_relevant_documents.assert_called_once_with("test query")
    
    def test_retrieve_documents_with_limit(self):
        """Test that document retrieval respects max_documents limit."""
        mock_retriever = Mock(spec=BaseRetriever)
        mock_documents = [
            Document(page_content=f"doc{i}", metadata={"source": f"test{i}"})
            for i in range(10)
        ]
        mock_retriever.get_relevant_documents.return_value = mock_documents
        
        node = RAGNode(retriever=mock_retriever, max_documents=3)
        
        result = node.retrieve_documents("test query")
        
        assert len(result) == 3
        assert result == mock_documents[:3]
    
    def test_retrieve_documents_error_handling(self):
        """Test that document retrieval handles errors gracefully."""
        mock_retriever = Mock(spec=BaseRetriever)
        mock_retriever.get_relevant_documents.side_effect = Exception("Retrieval error")
        
        node = RAGNode(retriever=mock_retriever)
        
        result = node.retrieve_documents("test query")
        
        assert result == []
    
    @patch('agent_service.agents.nodes.rag_node.trace_runnable')
    def test_generate_response_success(self, mock_trace_runnable):
        """Test successful response generation."""
        mock_retriever = Mock(spec=BaseRetriever)
        mock_traced_chain = Mock()
        mock_traced_chain.invoke.return_value = "Generated response"
        mock_trace_runnable.return_value = mock_traced_chain
        
        node = RAGNode(retriever=mock_retriever)
        
        documents = [
            Document(page_content="test content", metadata={"source": "test"})
        ]
        
        result = node.generate_response("test query", documents)
        
        assert result == "Generated response"
        mock_traced_chain.invoke.assert_called_once()
    
    def test_generate_response_error_handling(self):
        """Test that response generation handles errors gracefully."""
        mock_retriever = Mock(spec=BaseRetriever)
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("Generation error")
        
        node = RAGNode(retriever=mock_retriever, llm=mock_llm)
        
        documents = [Document(page_content="test", metadata={})]
        result = node.generate_response("test query", documents)
        
        assert "I apologize" in result
        assert "error" in result.lower()
    
    def test_format_context_with_documents(self):
        """Test context formatting with documents."""
        mock_retriever = Mock(spec=BaseRetriever)
        node = RAGNode(retriever=mock_retriever)
        
        documents = [
            Document(page_content="content1", metadata={"source": "source1"}),
            Document(page_content="content2", metadata={"source": "source2"}),
        ]
        
        result = node._format_context(documents)
        
        assert "Document 1 (Source: source1)" in result
        assert "Document 2 (Source: source2)" in result
        assert "content1" in result
        assert "content2" in result
    
    def test_format_context_empty(self):
        """Test context formatting with empty document list."""
        mock_retriever = Mock(spec=BaseRetriever)
        node = RAGNode(retriever=mock_retriever)
        
        result = node._format_context([])
        
        assert result == "No relevant context found."
    
    def test_format_context_without_source(self):
        """Test context formatting when documents don't have source metadata."""
        mock_retriever = Mock(spec=BaseRetriever)
        node = RAGNode(retriever=mock_retriever)
        
        documents = [
            Document(page_content="content1", metadata={}),
        ]
        
        result = node._format_context(documents)
        
        assert "Document 1 (Source: Unknown source)" in result
        assert "content1" in result


class TestRAGNodeLangGraphIntegration:
    """Test RAG node integration with LangGraph state management."""
    
    def test_rag_node_call_with_state(self):
        """Test that RAG node works with LangGraph state."""
        mock_retriever = Mock(spec=BaseRetriever)
        mock_documents = [
            Document(page_content="test content", metadata={"source": "test", "score": 0.95})
        ]
        mock_retriever.get_relevant_documents.return_value = mock_documents
        
        # Mock the LLM chain
        mock_llm = Mock()
        mock_llm.invoke.return_value = "Generated response"
        
        node = RAGNode(retriever=mock_retriever, llm=mock_llm)
        
        # Create test state
        state = AgentStateFactory.create_rag_state(
            user_id="test-user",
            tradition="canon-default",
            query="test query",
        )
        
        # Execute the node
        result_state = node(state)
        
        # Verify state updates
        assert result_state["generated_response"] == "Generated response"
        assert result_state["output"] == "Generated response"
        assert len(result_state["retrieved_documents"]) == 1
        assert len(result_state["retrieval_scores"]) == 1
        assert result_state["retrieval_scores"][0] == 0.95
        assert result_state["response_metadata"]["documents_retrieved"] == 1
        assert result_state["error"] is None
    
    def test_rag_node_call_with_error(self):
        """Test that RAG node handles errors in state execution."""
        mock_retriever = Mock(spec=BaseRetriever)
        mock_retriever.get_relevant_documents.side_effect = Exception("Test error")
        
        node = RAGNode(retriever=mock_retriever)
        
        state = AgentStateFactory.create_rag_state(
            user_id="test-user",
            tradition="canon-default",
            query="test query",
        )
        
        result_state = node(state)
        
        assert result_state["error"] == "Test error"
        assert result_state["error_type"] == "Exception"
        assert result_state["generated_response"] is None
    
    def test_rag_node_call_with_documents_without_score(self):
        """Test RAG node with documents that don't have scores."""
        mock_retriever = Mock(spec=BaseRetriever)
        mock_documents = [
            Document(page_content="test content", metadata={"source": "test"})
        ]
        mock_retriever.get_relevant_documents.return_value = mock_documents
        
        mock_llm = Mock()
        mock_llm.invoke.return_value = "Generated response"
        
        node = RAGNode(retriever=mock_retriever, llm=mock_llm)
        
        state = AgentStateFactory.create_rag_state(
            user_id="test-user",
            tradition="canon-default",
            query="test query",
        )
        
        result_state = node(state)
        
        assert len(result_state["retrieved_documents"]) == 1
        assert len(result_state["retrieval_scores"]) == 0  # No score in metadata


class TestRAGNodeFactory:
    """Test RAG node factory methods."""
    
    def test_create_standard_rag_node(self):
        """Test creation of standard RAG node."""
        mock_retriever = Mock(spec=BaseRetriever)
        
        node = RAGNodeFactory.create_standard_rag_node(
            retriever=mock_retriever,
            max_documents=3,
        )
        
        assert isinstance(node, RAGNode)
        assert node.retriever == mock_retriever
        assert node.max_documents == 3
    
    def test_create_custom_rag_node(self):
        """Test creation of custom RAG node."""
        mock_retriever = Mock(spec=BaseRetriever)
        mock_prompt = ChatPromptTemplate.from_template("Custom: {context} {question}")
        mock_llm = Mock()
        
        node = RAGNodeFactory.create_custom_rag_node(
            retriever=mock_retriever,
            prompt_template=mock_prompt,
            llm=mock_llm,
            max_documents=5,
        )
        
        assert isinstance(node, RAGNode)
        assert node.retriever == mock_retriever
        assert node.prompt_template == mock_prompt
        assert node.llm == mock_llm
        assert node.max_documents == 5
    
    def test_create_coaching_rag_node(self):
        """Test creation of coaching-specific RAG node."""
        mock_retriever = Mock(spec=BaseRetriever)
        
        node = RAGNodeFactory.create_coaching_rag_node(
            retriever=mock_retriever,
            max_documents=4,
        )
        
        assert isinstance(node, RAGNode)
        assert node.retriever == mock_retriever
        assert node.max_documents == 4
        
        # Check that it has coaching-specific prompt
        prompt_text = node.prompt_template.template
        assert "coaching assistant" in prompt_text.lower()
        assert "practical, actionable advice" in prompt_text.lower()


class TestRAGNodeEdgeCases:
    """Test RAG node edge cases and error conditions."""
    
    def test_rag_node_with_none_retriever(self):
        """Test that RAG node handles None retriever gracefully."""
        with pytest.raises(TypeError):
            RAGNode(retriever=None)
    
    def test_rag_node_with_invalid_max_documents(self):
        """Test that RAG node handles invalid max_documents."""
        mock_retriever = Mock(spec=BaseRetriever)
        
        with pytest.raises(ValueError):
            RAGNode(retriever=mock_retriever, max_documents=0)
        
        with pytest.raises(ValueError):
            RAGNode(retriever=mock_retriever, max_documents=-1)
    
    def test_rag_node_with_empty_query(self):
        """Test RAG node with empty query."""
        mock_retriever = Mock(spec=BaseRetriever)
        mock_retriever.get_relevant_documents.return_value = []
        
        node = RAGNode(retriever=mock_retriever)
        
        state = AgentStateFactory.create_rag_state(
            user_id="test-user",
            tradition="canon-default",
            query="",
        )
        
        result_state = node(state)
        
        assert len(result_state["retrieved_documents"]) == 0
        assert result_state["generated_response"] is not None
    
    def test_rag_node_with_very_long_query(self):
        """Test RAG node with very long query."""
        mock_retriever = Mock(spec=BaseRetriever)
        mock_documents = [Document(page_content="test", metadata={})]
        mock_retriever.get_relevant_documents.return_value = mock_documents
        
        mock_llm = Mock()
        mock_llm.invoke.return_value = "Generated response"
        
        node = RAGNode(retriever=mock_retriever, llm=mock_llm)
        
        long_query = "x" * 10000  # Very long query
        state = AgentStateFactory.create_rag_state(
            user_id="test-user",
            tradition="canon-default",
            query=long_query,
        )
        
        result_state = node(state)
        
        assert result_state["generated_response"] == "Generated response"
        assert result_state["error"] is None 