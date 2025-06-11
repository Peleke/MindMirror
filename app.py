import streamlit as st
import os
import networkx as nx
from langchain.retrievers.merger_retriever import MergerRetriever
from langchain_community.graphs.networkx_graph import NetworkxEntityGraph

from src.chain import create_rag_chain
from src.embedding import load_vector_store, create_vector_store
from src.graph import build_graph_from_documents
from config import VECTOR_STORE_DIR, GRAPH_STORE_PATH, PDF_DIR
from src.loading import load_from_directory, chunk_documents

@st.cache_resource
def get_retriever():
    """
    Initializes and returns the retriever.
    """
    # Vector store
    if not os.path.exists(VECTOR_STORE_DIR):
        docs = load_from_directory(PDF_DIR)
        chunks = chunk_documents(docs)

        # Use a progress bar for the long-running embedding process
        progress_bar = st.progress(0, text="Building knowledge base... (Embedding documents)")
        total_chunks = len(chunks)

        def progress_callback(processed_chunks):
            progress_bar.progress(processed_chunks / total_chunks, text=f"Building knowledge base... (Embedding documents {processed_chunks}/{total_chunks})")

        vector_store = create_vector_store(chunks, VECTOR_STORE_DIR, progress_callback=progress_callback)
        progress_bar.empty() # Clear the progress bar
    else:
        vector_store = load_vector_store(VECTOR_STORE_DIR)

    # Knowledge graph (this is generally faster)
    with st.spinner("Building knowledge graph..."):
        if not os.path.exists(GRAPH_STORE_PATH):
            docs = load_from_directory(PDF_DIR)
            chunks = chunk_documents(docs)
            graph = build_graph_from_documents(chunks)
            nx.write_gml(graph.graph, GRAPH_STORE_PATH)
        else:
            graph_nx = nx.read_gml(GRAPH_STORE_PATH)
            graph = NetworkxEntityGraph(graph=graph_nx)

    vector_retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    graph_retriever = graph.as_retriever()
    
    retriever = MergerRetriever(retrievers=[vector_retriever, graph_retriever])
    return retriever

@st.cache_resource
def get_rag_chain():
    """
    Initializes and returns the RAG chain.
    """
    retriever = get_retriever()
    return create_rag_chain(retrievers=[retriever])

def main():
    """
    Main function to run the Streamlit UI.
    """
    st.title("📚 Librarian AI")

    with st.sidebar:
        st.header("Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload new PDF files to the knowledge base.",
            type="pdf",
            accept_multiple_files=True,
        )
        if uploaded_files:
            file_names = [f.name for f in uploaded_files]
            with st.spinner(f"Processing {', '.join(file_names)}..."):
                # Ensure the PDF directory exists
                os.makedirs(PDF_DIR, exist_ok=True)

                for uploaded_file in uploaded_files:
                    # Save the file to the PDF directory
                    file_path = os.path.join(PDF_DIR, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                # Clear the cache to force re-reading of documents
                st.cache_resource.clear()

            st.success(f"✅ Successfully added {len(uploaded_files)} file(s) to the knowledge base!")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I am Librarian AI. How can I help you today?"
            }
        ]

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Ask a question..."):
        # Display user message in chat message container
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                rag_chain = get_rag_chain()
                response = rag_chain.invoke(prompt)
                st.markdown(response)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main() 