import logging
import os

import networkx as nx

from config import DATA_DIR, GRAPH_STORE_PATH, PDF_DIR, VECTOR_STORE_DIR
from src.embedding import create_vector_store
from src.graph import build_graph_from_documents
from src.loading import chunk_documents, load_from_directory

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def build_knowledge_base(
    pdf_dir: str = PDF_DIR,
    data_dir: str = DATA_DIR,
):
    """
    Scans for tradition-specific subdirectories in the `pdf_dir`,
    and for each one, builds and saves a vector store and knowledge graph
    to a corresponding subdirectory in the `data_dir`.
    """
    logging.info(f"Scanning for traditions in {pdf_dir}...")

    traditions = [
        d for d in os.listdir(pdf_dir) if os.path.isdir(os.path.join(pdf_dir, d))
    ]

    if not traditions:
        logging.warning(
            f"No tradition subdirectories found in {pdf_dir}. Nothing to build."
        )
        return

    for tradition in traditions:
        logging.info(f"--- Building knowledge base for tradition: {tradition} ---")

        tradition_pdf_dir = os.path.join(pdf_dir, tradition)
        tradition_data_dir = os.path.join(data_dir, tradition)

        vector_store_path = os.path.join(tradition_data_dir, "vectorstore")
        graph_store_path = os.path.join(tradition_data_dir, "graph_store.json")

        # Ensure data directories exist
        os.makedirs(tradition_data_dir, exist_ok=True)

        logging.info(f"Loading documents from {tradition_pdf_dir}...")
        docs = load_from_directory(tradition_pdf_dir)
        chunks = chunk_documents(docs)
        logging.info(f"Processed {len(docs)} documents into {len(chunks)} chunks.")

        # Build and save the vector store
        logging.info(f"Building vector store at {vector_store_path}...")
        create_vector_store(chunks, vector_store_path)
        logging.info("Vector store built successfully.")

        # Build and save the knowledge graph
        logging.info(f"Building knowledge graph at {graph_store_path}...")
        graph = build_graph_from_documents(chunks)
        nx.write_gml(graph._graph, graph_store_path)
        logging.info("Knowledge graph built successfully.")
        logging.info(f"--- Finished building for tradition: {tradition} ---")
