import streamlit as st
import os
from src.engine import CoachingEngine
from config import PDF_DIR

@st.cache_resource
def get_engine():
    """
    Initializes and returns the CoachingEngine.
    This is cached to avoid re-initializing the engine on every app rerun.
    """
    return CoachingEngine()

def main():
    """
    Main function to run the Streamlit UI.
    """
    st.title("📚 Librarian AI")

    # Get the coaching engine
    engine = get_engine()

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
                
                # Clear the engine's cache and reload
                engine.reload()
                # Clear the Streamlit cache to reflect changes
                st.cache_resource.clear()

            st.success(f"✅ Successfully added {len(uploaded_files)} file(s) to the knowledge base!")
            st.rerun()

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
                response = engine.ask(prompt)
                st.markdown(response)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main() 