import pytest
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document
from langchain_community.graphs import NetworkxEntityGraph

from src.graph import build_graph_from_documents

@pytest.fixture
def mock_docs():
    """Fixture to create a list of dummy documents for graph extraction."""
    return [
        Document(page_content="Elon Musk founded SpaceX."),
        Document(page_content="SpaceX launches rockets.")
    ]

@patch("src.graph.NetworkxEntityGraph")
@patch("src.graph.LLMGraphTransformer")
@patch("src.graph.get_llm")
def test_build_graph_from_documents(mock_get_llm, mock_transformer, mock_graph, mock_docs):
    """
    Tests that build_graph_from_documents successfully processes documents
    and builds a knowledge graph.
    """
    # Arrange
    # Mock the LLM and Transformer
    mock_llm_instance = MagicMock()
    mock_get_llm.return_value = mock_llm_instance
    
    mock_transformer_instance = MagicMock()
    mock_transformer.return_value = mock_transformer_instance
    
    # Mock the graph object
    mock_graph_instance = MagicMock()
    mock_graph.return_value = mock_graph_instance

    # Act
    graph = build_graph_from_documents(mock_docs)

    # Assert
    mock_get_llm.assert_called_once()
    mock_transformer.assert_called_once_with(llm=mock_llm_instance)
    mock_transformer_instance.convert_to_graph_documents.assert_called_once_with(mock_docs)
    mock_graph().add_graph_documents.assert_called_once()
    assert graph == mock_graph_instance
