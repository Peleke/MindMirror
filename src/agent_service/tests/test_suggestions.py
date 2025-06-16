import asyncio
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID

import pytest
from shared.auth import CurrentUser

from agent_service.clients.models import MealLog, PracticeInstance, UserGoals
from agent_service.engine import get_engine_for_tradition
from agent_service.models.journal import (GratitudePayload, JournalEntry,
                                          ReflectionPayload)
from agent_service.services.suggestion_service import SuggestionService

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
