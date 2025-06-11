import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock
import streamlit as st
import app

@pytest.fixture(autouse=True)
def patch_rag_chain(monkeypatch):
    """
    Fixture to clear cache and monkeypatch the RAG chain creation.
    """
    st.cache_resource.clear()
    
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "This is a mock response."
    monkeypatch.setattr(app, "get_rag_chain", lambda: mock_chain)
    return mock_chain

def test_initial_state():
    """
    Tests that the app starts with a welcome message.
    """
    at = AppTest.from_file("app.py").run()
    
    # Check that session_state has been initialized
    assert "messages" in at.session_state
    assert len(at.session_state.messages) == 1
    
    first_message = at.session_state.messages[0]
    assert first_message["role"] == "assistant"
    assert "How can I help you" in first_message["content"]
    
    # Also check that the message is displayed on screen
    assert len(at.chat_message) == 1
    assert "How can I help you" in at.chat_message[0].markdown[0].value