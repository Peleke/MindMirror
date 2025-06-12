import asyncio
from datetime import datetime, timedelta

from shared.auth import CurrentUser
from src.clients.history_client import HistoryClient
from src.clients.users_client import UsersClient
from src.engine import CoachingEngine
from src.repositories.journal_repository import JournalRepository


class SuggestionService:
    """
    A service for generating contextual suggestions and reviews.
    """

    def __init__(
        self,
        users_client: UsersClient,
        history_client: HistoryClient,
        journal_repo: JournalRepository,
        engine: CoachingEngine,
    ):
        self._users_client = users_client
        self._history_client = history_client
        self._journal_repo = journal_repo
        self._engine = engine

    async def get_meal_suggestion(
        self, current_user: CurrentUser, tradition: str, meal_type: str
    ) -> str:
        """
        Generates a meal suggestion based on user goals and recent activity.
        """
        if not self._engine:
            raise ValueError("CoachingEngine is not initialized.")

        # 1. Fetch external context
        goals = self._users_client.get_user_goals(current_user.id)
        last_workout = self._history_client.get_last_workout(current_user.id)

        # 2. Build a detailed, structured prompt
        prompt_parts = [
            f"Please suggest a {meal_type} for a user with the following context."
        ]

        if goals:
            prompt_parts.append("\nUser's Goals:")
            if goals.daily_calorie_goal:
                prompt_parts.append(
                    f"- Daily Calorie Target: ~{int(goals.daily_calorie_goal)} kcal"
                )
            if goals.daily_protein_goal:
                prompt_parts.append(
                    f"- Daily Protein Target: ~{int(goals.daily_protein_goal)}g of protein"
                )

        if last_workout:
            prompt_parts.append("\nRecent Activity:")
            prompt_parts.append(f"- Their last workout was '{last_workout.title}'.")

        prompt_parts.append(
            "\nBased on the provided documents for this tradition, what is a suitable meal? Be specific."
        )

        prompt = "\n".join(prompt_parts)

        # 3. Call the RAG chain with timeout
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self._engine.ask, prompt),
                timeout=60.0,  # 1 minute timeout for meal suggestions
            )
        except asyncio.TimeoutError:
            raise RuntimeError("Meal suggestion request timed out after 1 minute")
        except Exception as e:
            raise RuntimeError(f"Meal suggestion request failed: {str(e)}") from e

    async def generate_biweekly_review(
        self, current_user: CurrentUser, tradition: str
    ) -> str:
        """
        Generates a bi-weekly performance review by synthesizing user history.
        """
        if not self._engine:
            raise ValueError("CoachingEngine is not initialized.")

        # 1. Fetch all context
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=14)

        meal_logs = self._history_client.get_meal_logs_for_period(
            current_user.id, start_date.date(), end_date.date()
        )
        workout_logs = self._history_client.get_workouts_for_period(
            current_user.id, start_date.date(), end_date.date()
        )
        journal_entries = await self._journal_repo.list_by_user_for_period(
            str(current_user.id), start_date, end_date
        )

        # 2. Build the prompt
        prompt_parts = [
            "Please generate a concise bi-weekly performance review for a user based on the following data from the last 14 days.",
            "",
            "IMPORTANT: Please format your response with these exact sections:",
            "Key Success: [one key achievement or positive trend]",
            "Area for Improvement: [one main area to focus on improving]",
            "Journal Prompt: [a specific, actionable question for reflection]",
            "",
            "Data from the last 14 days:",
            "",
            "--- Meal History ---",
        ]
        if meal_logs:
            for log in meal_logs:
                prompt_parts.append(
                    f"- {log.date}: {log.name} (~{int(log.calories)} kcal)"
                )
        else:
            prompt_parts.append("No meal logs recorded.")

        prompt_parts.append("\n--- Workout History ---")
        if workout_logs:
            for log in workout_logs:
                prompt_parts.append(f"- {log.completed_at}: {log.title}")
        else:
            prompt_parts.append("No workouts recorded.")

        prompt_parts.append("\n--- Journal Entries ---")
        if journal_entries:
            for entry in journal_entries:
                entry_date = entry.created_at.strftime("%Y-%m-%d")
                if entry.entry_type == "FREEFORM":
                    prompt_parts.append(f"- {entry_date} (Freeform): {entry.payload}")
                elif entry.entry_type == "GRATITUDE":
                    payload = entry.payload
                    grateful_items = ", ".join(payload.grateful_for)
                    prompt_parts.append(
                        f"- {entry_date} (Gratitude): Felt grateful for {grateful_items}."
                    )
                elif entry.entry_type == "REFLECTION":
                    payload = entry.payload
                    win_items = ", ".join(payload.wins)
                    prompt_parts.append(
                        f"- {entry_date} (Reflection): Celebrated wins like {win_items}."
                    )
        else:
            prompt_parts.append("No journal entries recorded.")

        prompt_parts.append("\n--- End of Data ---")
        prompt_parts.append("")
        prompt_parts.append(
            "Based on this data and the principles of the provided knowledge base, generate the review using the exact format specified above."
        )

        prompt = "\n".join(prompt_parts)

        # 3. Call the RAG chain with timeout
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self._engine.ask, prompt),
                timeout=120.0,  # 2 minute timeout
            )
        except asyncio.TimeoutError:
            raise RuntimeError("LLM request timed out after 2 minutes")
        except Exception as e:
            raise RuntimeError(f"LLM request failed: {str(e)}") from e
