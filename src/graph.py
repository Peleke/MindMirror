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

    # In older versions, one would use graph.add_graph_documents(graph_documents).
    # This method is deprecated. We now manually construct the graph.
    graph = NetworkxEntityGraph()
    for doc in graph_documents:
        for node in doc.nodes:
            # The node object has 'id' and 'type' attributes
            graph._graph.add_node(node.id, type=node.type)
        for rel in doc.relationships:
            # The relationship object has 'source', 'target', and 'type' attributes
            graph._graph.add_edge(rel.source.id, rel.target.id, relation=rel.type)
    
    logging.info(f"Graph created with {len(graph._graph.nodes())} nodes and {len(graph._graph.edges())} edges.")
    
    return graph
