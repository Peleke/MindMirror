import asyncio
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from uuid import UUID, uuid4

import pytest
import pytest_asyncio

from agent_service.api.types.suggestion_types import PerformanceReview
from agent_service.clients.models import MealLog, PracticeInstance, UserGoals
from agent_service.engine import get_engine_for_tradition
from agent_service.models.journal import (GratitudePayload, JournalEntry,
                                          ReflectionPayload)
from agent_service.services.llm_service import LLMService
from agent_service.services.suggestion_service import SuggestionService
from shared.auth import CurrentUser

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_get_meal_suggestion_constructs_correct_prompt():
    """
    Tests that the SuggestionService correctly constructs a prompt
    by combining user goals and recent workout history.
    """
    # 1. Arrange: Create mocks for all external dependencies
    mock_users_client = AsyncMock()
    mock_history_client = AsyncMock()
    mock_engine = Mock()
    mock_journal_client = AsyncMock()

    # Configure the mocks to return specific data models
    mock_users_client.get_user_goals.return_value = UserGoals(
        daily_calorie_goal=3500.0,
        daily_protein_goal=200.0,
    )
    mock_history_client.get_last_workout.return_value = PracticeInstance(
        title="Heavy Leg Day",
        completed_at=date(2024, 7, 29),
    )
    # The journal client is called, but its result isn't used in the prompt for this specific feature
    mock_journal_client.list_by_user_for_period.return_value = []

    mock_engine.ask.return_value = "A grilled chicken salad."

    # Instantiate the service with our mocks
    suggestion_service = SuggestionService(
        users_client=mock_users_client,
        history_client=mock_history_client,
        journal_client=mock_journal_client,
        engine=mock_engine,
    )

    # 2. Act: Call the method we want to test with a proper CurrentUser object
    current_user = CurrentUser(
        id=UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6"), email="test@example.com"
    )
    tradition = "canon-default"
    meal_type = "dinner"

    suggestion = await suggestion_service.get_meal_suggestion(
        current_user, tradition, meal_type
    )

    # 3. Assert: Verify the interaction with the engine
    assert suggestion == "A grilled chicken salad."

    # Crucially, check that the prompt sent to the LLM is correct
    mock_engine.ask.assert_called_once()
    call_args, _ = mock_engine.ask.call_args
    prompt = call_args[0]

    assert "dinner" in prompt
    assert "3500" in prompt
    assert "200" in prompt
    assert "Heavy Leg Day" in prompt


@pytest.mark.asyncio
@patch("agent_service.embedding.get_embedding", new_callable=AsyncMock)
@patch("agent_service.vector_stores.qdrant_client.get_qdrant_client")
async def test_generate_biweekly_review_constructs_correct_prompt(
    mock_get_qdrant_client, mock_get_embedding
):
    """
    Tests that the SuggestionService correctly constructs a prompt for a
    performance review by combining journal, meal, and workout history.
    """
    # 1. Arrange
    mock_users_client = AsyncMock()
    mock_history_client = AsyncMock()
    mock_journal_client = AsyncMock()
    mock_engine = Mock()

    # Configure semantic search mocks to prevent real network calls
    mock_qdrant_instance = AsyncMock()
    mock_qdrant_instance.hybrid_search.return_value = []  # Return no insights
    mock_get_qdrant_client.return_value = mock_qdrant_instance
    mock_get_embedding.return_value = [0.5] * 384  # Return a dummy vector

    # Configure mock return values for history and journal
    mock_history_client.get_meal_logs_for_period.return_value = [
        MealLog(
            name="Steak and Eggs",
            calories=800,
            protein=60,
            carbs=5,
            fat=50,
            date=date(2024, 7, 28),
        ),
    ]
    mock_history_client.get_workouts_for_period.return_value = [
        PracticeInstance(title="Morning Run", completed_at=date(2024, 7, 28)),
    ]

    # Configure the async mock for the journal repository
    mock_journal_client.list_by_user_for_period.return_value = [
        JournalEntry(
            id="1",
            user_id="test-user-123",
            entry_type="GRATITUDE",
            payload=GratitudePayload(
                grateful_for=["coffee", "sunshine", "a good book"],
                excited_about=["my workout", "seeing friends", "the weekend"],
                focus="finish report",
                affirmation="I am capable",
            ),
            created_at=datetime(2024, 7, 28),
        ),
        JournalEntry(
            id="2",
            user_id="test-user-123",
            entry_type="FREEFORM",
            payload="Felt a bit sluggish today.",
            created_at=datetime(2024, 7, 29),
        ),
    ]
    mock_engine.ask.return_value = "A great review."

    # 2. Act with a proper CurrentUser object
    service = SuggestionService(
        users_client=mock_users_client,
        history_client=mock_history_client,
        journal_client=mock_journal_client,
        engine=mock_engine,
    )

    current_user = CurrentUser(
        id=UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6"), email="test@example.com"
    )

    review = await service.generate_biweekly_review(current_user, "canon-default")

    # 3. Assert
    assert review == "A great review."
    mock_journal_client.list_by_user_for_period.assert_awaited_once()
    mock_engine.ask.assert_called_once()
    prompt = mock_engine.ask.call_args[0][0]

    # Check that key data points are in the prompt
    assert "Meal History" in prompt
    assert "Steak and Eggs" in prompt
    assert "Workout History" in prompt
    assert "Morning Run" in prompt
    assert "Journal Entries" in prompt
    assert "grateful for coffee" in prompt.lower()
    assert "sluggish" in prompt


@pytest.mark.asyncio
class TestLLMService:
    """Test suite for the LLMService."""

    @patch("agent_service.services.llm_service.acompletion", new_callable=AsyncMock)
    async def test_get_journal_summary(self, mock_acompletion):
        """Test generating a journal summary."""
        # Arrange
        llm_service = LLMService()
        journal_entries = [{"text": "Today was a good day."}]

        # Mock the LLM response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "You had a good day."
        mock_acompletion.return_value = mock_response

        # Act
        summary = await llm_service.get_journal_summary(journal_entries)

        # Assert
        assert summary == "You had a good day."
        mock_acompletion.assert_called_once()
        prompt = mock_acompletion.call_args[1]["messages"][0]["content"]
        assert "Today was a good day." in prompt

    @patch("agent_service.services.llm_service.acompletion", new_callable=AsyncMock)
    async def test_generate_performance_review(self, mock_acompletion):
        """Test generating a structured performance review."""
        # Arrange
        llm_service = LLMService()
        journal_entries = [{"text": "I succeeded in my goal to wake up early."}]
        
        # Mock the structured LLM response
        mock_response_text = """
        SUCCESS: Consistently waking up early.
        IMPROVEMENT: Integrating a morning workout.
        PROMPT: How can you add a short workout to your new morning routine?
        """
        mock_response = MagicMock()
        mock_response.choices[0].message.content = mock_response_text
        mock_acompletion.return_value = mock_response

        # Act
        review = await llm_service.generate_performance_review(journal_entries)

        # Assert
        assert isinstance(review, PerformanceReview)
        assert review.key_success == "Consistently waking up early."
        assert review.improvement_area == "Integrating a morning workout."
        assert review.journal_prompt == "How can you add a short workout to your new morning routine?"
        mock_acompletion.assert_called_once()
        prompt = mock_acompletion.call_args[1]["messages"][0]["content"]
        assert "I succeeded in my goal to wake up early." in prompt


@patch("agent_service.web.app.get_current_user")
class TestGraphQLAPI:
    """Test suite for the GraphQL API resolvers."""

    @patch("agent_service.web.app.JournalClient")
    @patch("agent_service.web.app.LLMService")
    async def test_summarize_journals_resolver(
        self, mock_llm_service, mock_journal_client, mock_get_current_user
    ):
        """Test the summarize_journals resolver."""
        # Arrange
        from agent_service.web.app import Query
        test_user = CurrentUser(id=uuid4(), email="test@test.com")

        # Mock the dependencies
        mock_get_current_user.return_value = test_user
        
        mock_journal_instance = AsyncMock()
        mock_journal_instance.list_by_user_for_period.return_value = [
            JournalEntry(id="1", user_id=str(test_user.id), entry_type="FREEFORM", payload="test", created_at=datetime.now())
        ]
        mock_journal_client.return_value = mock_journal_instance

        # Configure the LLMService mock to have an AWAITABLE method
        mock_llm_instance = AsyncMock()
        mock_llm_instance.get_journal_summary.return_value = "A great summary."
        mock_llm_service.return_value = mock_llm_instance
        
        # Mock the info object
        info = MagicMock()
        info.context = {"current_user": test_user}

        # Act
        resolver = Query()
        result = await resolver.summarize_journals(info=info)

        # Assert
        assert result.summary == "A great summary."
        mock_journal_instance.list_by_user_for_period.assert_awaited_once()
        mock_llm_instance.get_journal_summary.assert_awaited_once()


    @patch("agent_service.web.app.get_qdrant_client")
    @patch("agent_service.web.app.get_embedding", new_callable=AsyncMock)
    @patch("agent_service.web.app.LLMService")
    async def test_generate_review_resolver(
        self, mock_llm_service, mock_get_embedding, mock_qdrant_client, mock_get_current_user
    ):
        """Test the generate_review resolver."""
        # Arrange
        from agent_service.web.app import Mutation
        test_user = CurrentUser(id=uuid4(), email="test@test.com")

        # Mock the dependencies
        mock_get_current_user.return_value = test_user
        mock_get_embedding.return_value = [0.1] * 768

        # Configure the mock instance and its async method
        mock_qdrant_instance = AsyncMock()
        mock_qdrant_instance.search_personal_documents_by_date.return_value = [
            MagicMock(text="Test entry", score=0.9, metadata={})
        ]
        mock_qdrant_client.return_value = mock_qdrant_instance

        # Configure the LLMService mock to have an AWAITABLE method
        mock_llm_instance = AsyncMock()
        mock_llm_instance.generate_performance_review.return_value = PerformanceReview(
            key_success="Tested well",
            improvement_area="More tests",
            journal_prompt="Write more tests"
        )
        mock_llm_service.return_value = mock_llm_instance
        
        # Mock the info object
        info = MagicMock()
        info.context = {"current_user": test_user}
        
        # Act
        resolver = Mutation()
        result = await resolver.generate_review(
            info=info,
            tradition="canon-default"
        )

        # Assert
        assert result.key_success == "Tested well"
        mock_qdrant_instance.search_personal_documents_by_date.assert_awaited_once()
        mock_llm_instance.generate_performance_review.assert_awaited_once()
