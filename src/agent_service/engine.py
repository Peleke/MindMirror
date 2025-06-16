import os
from typing import List

import networkx as nx
from langchain.retrievers.merger_retriever import MergerRetriever
from langchain_community.graphs.networkx_graph import NetworkxEntityGraph
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables.base import Runnable

from agent_service.chain import create_rag_chain
from agent_service.embedding import create_vector_store, load_vector_store
from agent_service.graph import build_graph_from_documents
from agent_service.loading import chunk_documents, load_from_directory
from config import DATA_DIR, GRAPH_STORE_PATH, PDF_DIR, VECTOR_STORE_DIR


class SimpleGraphRetriever(BaseRetriever):
    """
    A simple custom retriever for a NetworkX graph.
    It retrieves all triplets and returns them as a single document.
    """

    graph: NetworkxEntityGraph

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        # Serialize all triplets into a single string
        triplets = ""
        for source, target, data in self.graph._graph.edges(data=True):
            relation = data.get("relation", "related to")
            triplets += f"{source} -[{relation}]-> {target}\n"

        if not triplets:
            return []

        return [Document(page_content=triplets)]


class CoachingEngine:
    """
    Encapsulates the core logic for the RAG-based coaching assistant.
    It handles document loading, processing, and the retrieval/generation chain.
    """

    def __init__(
        self,
        tradition: str = "canon-default",
        data_dir: str = DATA_DIR,
    ):
        self.tradition = tradition
        self.data_dir = data_dir

        tradition_data_dir = os.path.join(self.data_dir, self.tradition)
        self.vector_store_dir = os.path.join(tradition_data_dir, "vectorstore")
        self.graph_store_path = os.path.join(tradition_data_dir, "graph_store.json")

        self.retriever = None
        self.rag_chain = None
        self._initialize()

    def _initialize(self):
        """
        Loads documents, builds the vector store and graph, and initializes
        the retriever and RAG chain. This is the main data processing pipeline.
        """
        docs = None
        chunks = None

        # Load vector store or create it if it doesn't exist
        if not os.path.exists(self.vector_store_dir):
            raise FileNotFoundError(
                f"Vector store not found at {self.vector_store_dir}. "
                "Please run `scripts/build_knowledge_base.py` to create it."
            )
        print(f"Loading existing vector store from {self.vector_store_dir}")
        vector_store = load_vector_store(self.vector_store_dir)

        # Load knowledge graph or create it if it doesn't exist
        if not os.path.exists(self.graph_store_path):
            raise FileNotFoundError(
                f"Knowledge graph not found at {self.graph_store_path}. "
                "Please run `scripts/build_knowledge_base.py` to create it."
            )
        print(f"Loading existing knowledge graph from {self.graph_store_path}")
        graph_nx = nx.read_gml(self.graph_store_path)
        graph = NetworkxEntityGraph(graph=graph_nx)

        # Initialize retrievers
        vector_retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        graph_retriever = SimpleGraphRetriever(graph=graph)
        self.retriever = MergerRetriever(retrievers=[vector_retriever, graph_retriever])

        # Initialize RAG chain
        self.rag_chain = create_rag_chain(retrievers=[self.retriever])
        print("CoachingEngine initialized successfully.")

    def ask(self, query: str) -> str:
        """Invokes the RAG chain to answer a query."""
        if not self.rag_chain:
            raise ValueError("RAG chain is not initialized.")
        return self.rag_chain.invoke(query)

    def get_rag_chain(self) -> Runnable:
        """Returns the underlying RAG chain."""
        if not self.rag_chain:
            raise ValueError("RAG chain is not initialized.")
        return self.rag_chain

    def reload(self):
        """Forces a re-initialization of the engine and its data sources."""
        print("Reloading CoachingEngine...")
        self._initialize()


# --- Engine Cache ---
# A simple cache to hold engine instances for different traditions.
# This avoids re-initializing the engine for every request.
engine_cache = {}


def get_engine_for_tradition(tradition: str) -> CoachingEngine:
    """
    Retrieves or creates a CoachingEngine instance for a given tradition.
    """
    if tradition not in engine_cache:
        print(f"Engine for tradition '{tradition}' not in cache. Initializing...")
        try:
            engine_cache[tradition] = CoachingEngine(tradition=tradition)
            print(f"Engine for '{tradition}' initialized and cached.")
        except FileNotFoundError:
            print(f"ERROR: Knowledge base for tradition '{tradition}' not found.")
            return None  # Or raise a specific GraphQL error
    return engine_cache[tradition]
