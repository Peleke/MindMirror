from unittest.mock import MagicMock, patch

import networkx as nx
import pytest
from langchain_core.retrievers import BaseRetriever

from agent_service.engine import CoachingEngine, SimpleGraphRetriever


@patch("agent_service.engine.create_rag_chain")
@patch("agent_service.engine.load_vector_store")
@patch("agent_service.engine.create_vector_store")
@patch("agent_service.engine.build_graph_from_documents")
@patch("agent_service.engine.load_from_directory")
@patch("agent_service.engine.chunk_documents")
@patch("agent_service.engine.nx.read_gml")
@patch("agent_service.engine.os.path.exists")
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
