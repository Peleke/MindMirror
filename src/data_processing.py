import os
import networkx as nx
import logging

from src.embedding import create_vector_store
from src.graph import build_graph_from_documents
from src.loading import load_from_directory, chunk_documents
from config import PDF_DIR, VECTOR_STORE_DIR, GRAPH_STORE_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def build_knowledge_base(
    pdf_dir: str = PDF_DIR,
    vector_store_dir: str = VECTOR_STORE_DIR,
    graph_store_path: str = GRAPH_STORE_PATH
):
    """
    Loads documents from the PDF directory, processes them into chunks,
    and then builds and saves the vector store and knowledge graph to disk.
    This is an idempotent operation; it will overwrite existing stores.
    """
    # Ensure data directories exist
    os.makedirs(os.path.dirname(vector_store_dir), exist_ok=True)
    os.makedirs(os.path.dirname(graph_store_path), exist_ok=True)

    logging.info(f"Loading documents from {pdf_dir}...")
    docs = load_from_directory(pdf_dir)
    chunks = chunk_documents(docs)
    logging.info(f"Processed {len(docs)} documents into {len(chunks)} chunks.")

    # Build and save the vector store
    logging.info(f"Building vector store at {vector_store_dir}...")
    create_vector_store(chunks, vector_store_dir)
    logging.info("Vector store built successfully.")

    # Build and save the knowledge graph
    logging.info(f"Building knowledge graph at {graph_store_path}...")
    graph = build_graph_from_documents(chunks)
    nx.write_gml(graph._graph, graph_store_path)
    logging.info("Knowledge graph built successfully.") 