import os
import networkx as nx
from langchain.retrievers.merger_retriever import MergerRetriever
from langchain_community.graphs.networkx_graph import NetworkxEntityGraph
from langchain_core.runnables.base import Runnable
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from typing import List

from src.chain import create_rag_chain
from src.embedding import load_vector_store, create_vector_store
from src.graph import build_graph_from_documents
from src.loading import load_from_directory, chunk_documents
from config import VECTOR_STORE_DIR, GRAPH_STORE_PATH, PDF_DIR


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
        for source, target, data in self.graph.graph.edges(data=True):
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
        pdf_dir: str = PDF_DIR,
        vector_store_dir: str = VECTOR_STORE_DIR,
        graph_store_path: str = GRAPH_STORE_PATH,
    ):
        self.pdf_dir = pdf_dir
        self.vector_store_dir = vector_store_dir
        self.graph_store_path = graph_store_path
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