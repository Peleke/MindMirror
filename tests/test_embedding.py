from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document

from src.embedding import create_vector_store, load_vector_store


@pytest.fixture
def mock_docs():
    """Provides a list of mock documents for testing."""
    return [
        Document(page_content="The sky is blue."),
        Document(page_content="The grass is green."),
    ]


@patch("src.embedding.FAISS")
@patch("src.embedding.get_embedding_model")
def test_create_vector_store(mock_get_embedding_model, mock_faiss, mock_docs, tmp_path):
    """
    Tests that create_vector_store successfully creates and saves a FAISS index
    by calling the embedding model factory.
    """
    # Arrange
    mock_embeddings_instance = MagicMock()
    mock_get_embedding_model.return_value = mock_embeddings_instance

    mock_faiss_instance = MagicMock()
    mock_faiss.from_documents.return_value = mock_faiss_instance

    # Act
    vs = create_vector_store(mock_docs, str(tmp_path))

    # Assert
    mock_get_embedding_model.assert_called_once()
    mock_faiss.from_documents.assert_called_once_with(
        mock_docs[:32], mock_embeddings_instance
    )
    mock_faiss_instance.save_local.assert_called_once_with(folder_path=str(tmp_path))
    assert vs == mock_faiss_instance


@patch("src.embedding.FAISS.load_local")
@patch("src.embedding.get_embedding_model")
def test_load_vector_store(mock_get_embedding_model, mock_load_local, tmp_path):
    """
    Tests that load_vector_store successfully loads a FAISS index from a directory,
    using the embedding model factory.
    """
    # Arrange
    db_path = str(tmp_path)
    mock_embeddings_instance = MagicMock()
    mock_get_embedding_model.return_value = mock_embeddings_instance

    mock_faiss_instance = MagicMock()
    mock_load_local.return_value = mock_faiss_instance

    # Act
    vs = load_vector_store(db_path)

    # Assert
    mock_get_embedding_model.assert_called_once()
    mock_load_local.assert_called_once_with(
        folder_path=db_path,
        embeddings=mock_embeddings_instance,
        allow_dangerous_deserialization=True,
    )
    assert vs == mock_faiss_instance
