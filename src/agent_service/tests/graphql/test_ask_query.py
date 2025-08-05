import pytest
from unittest.mock import patch, MagicMock

from agent_service.app.graphql.schemas.query import Query
from shared.auth import CurrentUser
from shared.data_models import UserRole

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_graphql_info():
    """Provides a mock Strawberry Info object with a current_user in the context."""
    mock_info = MagicMock()
    mock_info.context = {
        "current_user": CurrentUser(
            id="3fa85f64-5717-4562-b3fc-2c963f66afa6",
            roles=[UserRole(role="user", domain="coaching")]
        )
    }
    return mock_info

# The target for patch should be the module where the object is defined,
# because the code under test uses a local import within the resolver function.
@patch('agent_service.langgraph_.state.StateManager')
@patch('agent_service.langgraph_.graphs.chat_graph.ChatGraphFactory')
async def test_ask_with_journal_context_true(
    mock_chat_graph_factory, mock_state_manager, mock_graphql_info
):
    """
    Verify that when include_journal_context is True,
    the StateManager is called correctly.
    """
    # Arrange
    query_instance = Query()
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {"last_response": "Test response"}
    mock_chat_graph_factory.create_default_chat_graph.return_value.get_chat_graph.return_value = mock_graph

    # Act
    await query_instance.ask(
        info=mock_graphql_info,
        query="test query",
        tradition="canon-default",
        include_journal_context=True,
    )

    # Assert
    mock_state_manager.create_initial_state.assert_called_once_with(
        user_id=str(mock_graphql_info.context["current_user"].id),
        tradition_id="canon-default",
        initial_message="test query",
        include_journal_context=True, # This must be True
    )

@patch('agent_service.langgraph_.state.StateManager')
@patch('agent_service.langgraph_.graphs.chat_graph.ChatGraphFactory')
async def test_ask_with_journal_context_false(
    mock_chat_graph_factory, mock_state_manager, mock_graphql_info
):
    """
    Verify that when include_journal_context is False or omitted,
    the StateManager is called correctly.
    """
    # Arrange
    query_instance = Query()
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {"last_response": "Test response"}
    mock_chat_graph_factory.create_default_chat_graph.return_value.get_chat_graph.return_value = mock_graph

    # Act
    await query_instance.ask(
        info=mock_graphql_info,
        query="test query",
        tradition="canon-default",
        include_journal_context=False, # Explicitly False
    )

    # Assert
    mock_state_manager.create_initial_state.assert_called_once_with(
        user_id=str(mock_graphql_info.context["current_user"].id),
        tradition_id="canon-default",
        initial_message="test query",
        include_journal_context=False, # This must be False
    )

    # Act again with the parameter omitted
    mock_state_manager.create_initial_state.reset_mock()
    await query_instance.ask(
        info=mock_graphql_info,
        query="test query",
        tradition="canon-default",
    )

    # Assert
    mock_state_manager.create_initial_state.assert_called_once_with(
        user_id=str(mock_graphql_info.context["current_user"].id),
        tradition_id="canon-default",
        initial_message="test query",
        include_journal_context=False, # This must default to False
    )