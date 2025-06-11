import pytest
from unittest.mock import MagicMock, patch
from langchain_core.runnables import Runnable

from src.chain import create_rag_chain

@patch("src.chain.MergerRetriever")
@patch("src.chain.get_llm")
def test_create_rag_chain(mock_get_llm, mock_merger):
    """
    Tests that create_rag_chain correctly builds a runnable RAG chain.
    """
    # Arrange
    mock_retriever = MagicMock()
    mock_llm = MagicMock()
    mock_get_llm.return_value = mock_llm
    
    # Act
    rag_chain = create_rag_chain([mock_retriever])
    
    # Assert
    mock_merger.assert_called_once_with(retrievers=[mock_retriever])
    
    assert isinstance(rag_chain, Runnable)
    
    # Check that our LLM was used
    mock_get_llm.assert_called_once()
