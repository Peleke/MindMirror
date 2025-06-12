from unittest.mock import MagicMock, patch

import networkx as nx
import pytest
from langchain_core.retrievers import BaseRetriever

from src.engine import CoachingEngine, SimpleGraphRetriever


@patch("src.engine.create_rag_chain")
@patch("src.engine.load_vector_store")
@patch("src.engine.create_vector_store")
@patch("src.engine.build_graph_from_documents")
@patch("src.engine.load_from_directory")
@patch("src.engine.chunk_documents")
@patch("src.engine.nx.read_gml")
@patch("src.engine.os.path.exists")
def test_coaching_engine_initialization(
    mock_exists,
    mock_read_gml,
    mock_chunk_documents,
    mock_load_from_directory,
    mock_build_graph,
    mock_create_vector_store,
    mock_load_vector_store,
    mock_create_rag_chain,
):
    """
    Tests that the CoachingEngine can be initialized, mocking out all
    expensive I/O and processing calls.
    """
    # Arrange: Mock that data stores exist
    mock_exists.return_value = True
    mock_create_rag_chain.return_value = MagicMock()

    # Mock the vector store and its as_retriever method
    mock_vector_store = MagicMock()
    mock_vector_store.as_retriever.return_value = MagicMock(spec=BaseRetriever)
    mock_load_vector_store.return_value = mock_vector_store

    # Mock the graph reading
    mock_read_gml.return_value = nx.DiGraph()

    # Act
    engine = CoachingEngine()

    # Assert
    assert engine is not None
    assert engine.retriever is not None
    assert engine.rag_chain is not None
    mock_load_vector_store.assert_called_once()
    mock_read_gml.assert_called_once()
    mock_create_rag_chain.assert_called_once()
