from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document
from langchain_experimental.graph_transformers.llm import (GraphDocument, Node,
                                                           Relationship)

from agent_service.graph import build_graph_from_documents


@pytest.fixture
def mock_docs():
    """Fixture to create a list of dummy documents."""
    return [
        Document(page_content="Elon Musk founded SpaceX."),
        Document(page_content="SpaceX launches rockets."),
    ]


@patch("agent_service.graph.LLMGraphTransformer")
@patch("agent_service.graph.get_llm")
def test_build_graph_from_documents(mock_get_llm, mock_transformer, mock_docs):
    """
    Tests that build_graph_from_documents successfully processes documents
    and builds a knowledge graph using the LLMGraphTransformer.
    """
    # Arrange
    # Mock the LLM and Transformer
    mock_llm_instance = MagicMock()
    mock_get_llm.return_value = mock_llm_instance

    mock_transformer_instance = MagicMock()
    mock_transformer.return_value = mock_transformer_instance

    # Mock the output of the transformer with real data classes
    node1 = Node(id="Elon Musk", type="Person")
    node2 = Node(id="SpaceX", type="Organization")
    rel1 = Relationship(source=node1, target=node2, type="FOUNDED")

    mock_graph_docs = [
        GraphDocument(
            nodes=[node1, node2],
            relationships=[rel1],
            source=mock_docs[0],  # The source document is required
        )
    ]
    mock_transformer_instance.convert_to_graph_documents.return_value = mock_graph_docs

    # Act
    graph = build_graph_from_documents(mock_docs)

    # Assert
    mock_get_llm.assert_called_once()
    mock_transformer.assert_called_once_with(llm=mock_llm_instance)
    mock_transformer_instance.convert_to_graph_documents.assert_called_once_with(
        mock_docs
    )

    # Verify the graph was constructed correctly from the mocked GraphDocument
    assert "Elon Musk" in graph._graph.nodes
    assert "SpaceX" in graph._graph.nodes
    assert graph._graph.has_edge("Elon Musk", "SpaceX")
    edge_data = graph._graph.get_edge_data("Elon Musk", "SpaceX")
    assert edge_data["relation"] == "FOUNDED"
