import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_processing import build_knowledge_base


def main():
    """
    This script runs the full data ingestion and processing pipeline to build
    the vector store and knowledge graph from the documents in the `pdfs` directory.
    """
    print("Starting knowledge base build process...")
    build_knowledge_base()
    print("Knowledge base built successfully.")


if __name__ == "__main__":
    main()
