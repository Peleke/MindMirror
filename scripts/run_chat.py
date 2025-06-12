import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging

import networkx as nx
from langchain.retrievers import MergerRetriever
from langchain_community.graphs.networkx_graph import NetworkxEntityGraph

from config import GRAPH_STORE_PATH, PDF_DIR, VECTOR_STORE_DIR
from src.chain import create_rag_chain
from src.embedding import create_vector_store, load_vector_store
from src.graph import build_graph_from_documents
from src.loading import chunk_documents, load_from_directory

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    """
    Main function to run the Librarian AI chatbot.
    """
    # --- 1. Load and process documents ---
    logging.info(f"Loading documents from {PDF_DIR}...")
    docs = load_from_directory(PDF_DIR)
    if not docs:
        logging.error(
            "No documents found. Please add some PDFs to the 'pdfs' directory."
        )
        return

    chunks = chunk_documents(docs)

    # --- 2. Create or load the knowledge base ---
    # Vector store
    if not os.path.exists(VECTOR_STORE_DIR):
        logging.info("Creating new vector store...")
        vector_store = create_vector_store(chunks, VECTOR_STORE_DIR)
    else:
        logging.info("Loading existing vector store...")
        vector_store = load_vector_store(VECTOR_STORE_DIR)

    # Knowledge graph
    if not os.path.exists(GRAPH_STORE_PATH):
        logging.info("Building new knowledge graph...")
        graph = build_graph_from_documents(chunks)
        nx.write_gml(graph.graph, GRAPH_STORE_PATH)
    else:
        logging.info("Loading existing knowledge graph...")
        graph_nx = nx.read_gml(GRAPH_STORE_PATH)
        graph = NetworkxEntityGraph(graph=graph_nx)

    # --- 3. Create the RAG chain ---
    vector_retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    graph_retriever = graph.as_retriever()

    retriever = MergerRetriever(retrievers=[vector_retriever, graph_retriever])

    rag_chain = create_rag_chain(retrievers=[retriever])

    # --- 4. Start the chat loop ---
    print("📚 Librarian AI is ready. Ask your questions! (Type 'exit' to quit)")
    while True:
        try:
            query = input(">> ")
            if query.lower() in ["exit", "quit"]:
                break
            if not query.strip():
                continue

            logging.info(f"Invoking RAG chain with query: '{query}'")
            result = rag_chain.invoke(query)
            print("\n", result, "\n")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            print("\nSorry, an error occurred. Please try again.\n")


if __name__ == "__main__":
    main()
