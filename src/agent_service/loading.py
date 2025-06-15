import asyncio
import logging
import os
import tempfile
from pathlib import Path
from typing import Callable, Dict, List

import aiohttp
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_core.documents import Document

from config import CHUNK_OVERLAP, CHUNK_SIZE

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Defines mapping from file extension to loader class
LOADER_MAPPING: Dict[str, Callable] = {
    ".pdf": PyMuPDFLoader,
    ".txt": TextLoader,
}


def _load_file(file_path: Path) -> List[Document]:
    """Loads a single file using the appropriate loader based on its extension."""
    ext = file_path.suffix.lower()
    if ext not in LOADER_MAPPING:
        logging.warning(f"Unsupported file type: {ext}. Skipping {file_path.name}.")
        return []

    loader_class = LOADER_MAPPING[ext]
    loader = loader_class(str(file_path))

    try:
        docs = loader.load()
        logging.info(f"Loaded {len(docs)} document(s) from {file_path.name}")
        return docs
    except Exception as e:
        logging.error(f"Failed to load {file_path.name}: {e}")
        return []


def load_from_directory(directory_path: str) -> List[Document]:
    """
    Loads all supported files (.pdf, .txt) from a specified directory.

    Args:
        directory_path (str): The path to the directory.

    Returns:
        A list of Document objects from all supported files in the directory.
    """
    path = Path(directory_path)
    if not path.is_dir():
        logging.error(f"Directory not found: {directory_path}")
        return []

    all_docs = []
    supported_extensions = LOADER_MAPPING.keys()

    logging.info(
        f"Scanning {directory_path} for supported files: {list(supported_extensions)}"
    )

    for ext in supported_extensions:
        files = list(path.glob(f"**/*{ext}"))
        logging.info(f"Found {len(files)} '{ext}' file(s)")
        for file_path in files:
            docs = _load_file(file_path)
            all_docs.extend(docs)

    return all_docs


async def load_from_url(url: str, save_dir: Path) -> List[Document]:
    """
    Asynchronously downloads a file from a URL, saves it, and loads it.

    Args:
        url (str): The URL of the file to download.
        save_dir (Path): The directory to save the downloaded file in.

    Returns:
        A list of Document objects from the downloaded file.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()  # Raise an exception for bad status codes

                content = await response.read()
                file_name = Path(url).name
                save_path = save_dir / file_name

                with open(save_path, "wb") as f:
                    f.write(content)

                logging.info(f"Successfully downloaded {url} to {save_path}")
                return _load_file(save_path)

    except aiohttp.ClientError as e:
        logging.error(f"Failed to download {url}: {e}")
        return []


def chunk_documents(documents: List[Document]) -> List[Document]:
    """
    Splits a list of documents into smaller chunks.

    Args:
        documents (List[Document]): The documents to chunk.

    Returns:
        A list of smaller Document objects.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    chunked_documents = text_splitter.split_documents(documents)
    logging.info(
        f"Split {len(documents)} documents into {len(chunked_documents)} chunks."
    )
    return chunked_documents
