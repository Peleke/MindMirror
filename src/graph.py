import logging
from typing import List
from langchain_core.documents import Document
from langchain_community.graphs import NetworkxEntityGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer

from src.llm import get_llm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def build_graph_from_documents(
    documents: List[Document],
) -> NetworkxEntityGraph:
    """
    Builds a knowledge graph from a list of documents using an LLM.

    Args:
        documents (List[Document]): The documents to process.

    Returns:
        The populated NetworkxEntityGraph object.
    """
    logging.info("Initializing LLM for graph extraction...")
    llm = get_llm()
    
    logging.info("Initializing LLMGraphTransformer...")
    transformer = LLMGraphTransformer(llm=llm)

    logging.info("Converting documents to graph documents...")
    graph_documents = transformer.convert_to_graph_documents(documents)
    
    logging.info("Initializing NetworkxEntityGraph...")
    graph = NetworkxEntityGraph()
    
    logging.info("Adding graph documents to NetworkX graph...")
    graph.add_graph_documents(graph_documents)
    
    logging.info(f"Graph created with {len(graph.nodes)} nodes and {len(graph.edges)} edges.")
    
    return graph
