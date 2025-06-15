from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.documents import Document

from agent_service.loading import (_load_file, chunk_documents, load_from_directory,
                         load_from_url)


@pytest.fixture
def mock_loader():
    """Fixture to create a mock loader that can be injected."""
    loader_instance = MagicMock()
    dummy_doc = Document(page_content="This is a test document.")
    loader_instance.load.return_value = [dummy_doc]

    # The loader class is instantiated, so we return the instance
    loader_class = MagicMock(return_value=loader_instance)
    return loader_class, loader_instance


def test_load_file_pdf_success(mock_loader):
    """
    Tests that _load_file successfully loads a PDF using a mocked loader.
    """
    # Arrange
    mock_loader_class, mock_loader_instance = mock_loader
    file_path = Path("dummy/test.pdf")

    with patch.dict("agent_service.loading.LOADER_MAPPING", {".pdf": mock_loader_class}):
        # Act
        documents = _load_file(file_path)

        # Assert
        mock_loader_class.assert_called_once_with(str(file_path))
        mock_loader_instance.load.assert_called_once()
        assert len(documents) == 1
        assert documents[0].page_content == "This is a test document."


def test_load_file_txt_success(mock_loader):
    """
    Tests that _load_file successfully loads a TXT using a mocked loader.
    """
    # Arrange
    mock_loader_class, mock_loader_instance = mock_loader
    file_path = Path("dummy/notes.txt")

    with patch.dict("agent_service.loading.LOADER_MAPPING", {".txt": mock_loader_class}):
        # Act
        documents = _load_file(file_path)

        # Assert
        mock_loader_class.assert_called_once_with(str(file_path))
        mock_loader_instance.load.assert_called_once()
        assert len(documents) == 1


def test_load_file_unsupported():
    """
    Tests that _load_file returns an empty list for unsupported file types.
    """
    file_path = Path("dummy/archive.zip")
    documents = _load_file(file_path)
    assert documents == []


@patch("agent_service.loading._load_file")
def test_load_from_directory(mock_load_file, tmp_path):
    """
    Tests that load_from_directory finds and loads all supported files.
    """
    (tmp_path / "doc1.pdf").touch()
    (tmp_path / "notes.txt").touch()
    (tmp_path / "doc2.pdf").touch()
    (tmp_path / "archive.zip").touch()

    dummy_doc = Document(page_content="content")
    mock_load_file.return_value = [dummy_doc]

    documents = load_from_directory(str(tmp_path))

    assert mock_load_file.call_count == 3
    assert len(documents) == 3


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.get")
async def test_load_from_url_success(mock_get, tmp_path):
    """
    Tests that load_from_url successfully downloads and processes a file asynchronously.
    """

    # Create mock response inside context manager
    mock_response = AsyncMock()
    mock_response.read.return_value = b"fake pdf content"
    mock_response.raise_for_status = MagicMock()

    # Make mock_get return an async context manager that yields `mock_response`
    mock_get.return_value.__aenter__.return_value = mock_response

    dummy_doc = Document(page_content="content")

    with patch("agent_service.loading._load_file", return_value=[dummy_doc]) as mock_load_file:
        url = "http://example.com/test.pdf"
        target_path = tmp_path / "test.pdf"

        documents = await load_from_url(url, tmp_path)

        # Assert download + file read happened
        mock_get.assert_called_once_with(url)
        mock_load_file.assert_called_once_with(target_path)
        assert target_path.exists()
        assert documents[0].page_content == "content"


def test_chunk_documents():
    """
    Tests that chunk_documents correctly splits a list of documents.
    """
    # Arrange
    docs = [
        Document(page_content="This is a long sentence. " * 500),
        Document(page_content="This is another long sentence. " * 500),
    ]

    # Act
    chunked_docs = chunk_documents(docs)

    # Assert
    assert len(chunked_docs) > len(docs)
    assert len(chunked_docs[0].page_content) < len(docs[0].page_content)
