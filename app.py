import streamlit as st
import os
import asyncio
import base64
from src.api_client import run_graphql_query

API_URL = "http://localhost:8000/graphql"

# --- GraphQL Queries and Mutations ---
ASK_MUTATION = """
    mutation Ask($query: String!) {
        ask(query: $query)
    }
"""

ASK_QUERY = """
    query Ask($query: String!) {
      ask(query: $query)
    }
"""

GENERATE_REVIEW_MUTATION = """
    mutation GenerateReview($userId: String!) {
      generateReview(userId: $userId) {
        keySuccess
        improvementArea
        journalPrompt
      }
    }
"""

UPLOAD_DOCUMENT_MUTATION = """
    mutation UploadDocument($fileName: String!, $content: Base64!) {
      uploadDocument(fileName: $fileName, content: $content)
    }
"""


def main():
    """
    Main function to run the Streamlit UI as a pure API client.
    """
    st.title("🧠 AI Coaching Platform")

    with st.sidebar:
        st.header("Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload new PDF or TXT files to the knowledge base.",
            type=["pdf", "txt"],
            accept_multiple_files=True,
        )
        if uploaded_files:
            for uploaded_file in uploaded_files:
                with st.spinner(f"Uploading {uploaded_file.name}..."):
                    file_content = uploaded_file.getvalue()
                    encoded_content = base64.b64encode(file_content).decode("utf-8")
                    variables = {
                        "fileName": uploaded_file.name,
                        "content": encoded_content
                    }
                    result = asyncio.run(run_graphql_query(UPLOAD_DOCUMENT_MUTATION, variables))
                    if "errors" in result:
                        st.error(f"Failed to upload {uploaded_file.name}: {result['errors'][0]['message']}")
                    else:
                        st.success(f"✅ Successfully uploaded {uploaded_file.name}!")
            st.rerun()

        st.header("Actions")
        if st.button("Generate My Bi-Weekly Review"):
            with st.spinner("Generating your performance review..."):
                variables = {"userId": "demo-user-123"} # Static user ID for demo
                result = asyncio.run(run_graphql_query(GENERATE_REVIEW_MUTATION, variables))

                if "errors" in result:
                    st.error(f"Failed to generate review: {result['errors'][0]['message']}")
                else:
                    review = result['data']['generateReview']
                    st.session_state.review = review

    # Display the performance review if it exists in the session state
    if "review" in st.session_state:
        st.subheader("Your Bi-Weekly Performance Review")
        review = st.session_state.review
        st.success(f"**Key Success:** {review['keySuccess']}")
        st.warning(f"**Area for Improvement:** {review['improvementArea']}")
        st.info(f"**Journal Prompt:** {review['journalPrompt']}")
        st.markdown("---") # Visual separator


    # --- Chat Interface ---
    st.subheader("Conversational AI Coach")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I am your AI Coach. Ask me anything about your documents or your performance."
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
                variables = {"query": prompt}
                result = asyncio.run(run_graphql_query(ASK_QUERY, variables))
                
                if "errors" in result:
                    response = f"Sorry, there was an error: {result['errors'][0]['message']}"
                else:
                    response = result['data']['ask']
                
                st.markdown(response)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main() 