from datetime import date, timedelta
from typing import List, Optional

from agent_service.clients.models import MealLog, PracticeInstance


class HistoryClient:
    """
    A client to interact with external history services (e.g., meals, practices).
    For now, this is a mock that returns hardcoded data.
    """

    def get_last_workout(self, user_id: str) -> Optional[PracticeInstance]:
        """
        Retrieves the most recent completed workout for a user.
        """
        print(f"MOCK HistoryClient: Fetching last workout for user {user_id}")
        if user_id == "test-user-123":
            return PracticeInstance(
                title="Heavy Leg Day", completed_at=date.today() - timedelta(days=1)
            )
        return None

    def get_workouts_for_period(
        self, user_id: str, start_date: date, end_date: date
    ) -> List[PracticeInstance]:
        """
        Retrieves all workouts for a user within a given date range.
        """
        print(
            f"MOCK HistoryClient: Fetching workouts for user {user_id} from {start_date} to {end_date}"
        )
        if user_id == "test-user-123":
            return [
                PracticeInstance(
                    title="Morning Run", completed_at=date.today() - timedelta(days=2)
                ),
                PracticeInstance(
                    title="Heavy Leg Day", completed_at=date.today() - timedelta(days=1)
                ),
            ]
        return []

    def get_meal_logs_for_period(
        self, user_id: str, start_date: date, end_date: date
    ) -> List[MealLog]:
        """
        Retrieves all meal logs for a user within a given date range.
        """
        print(
            f"MOCK HistoryClient: Fetching meal logs for user {user_id} from {start_date} to {end_date}"
        )
        if user_id == "test-user-123":
            return [
                MealLog(
                    name="Chicken and Rice",
                    calories=600,
                    protein=50,
                    carbs=70,
                    fat=10,
                    date=date.today() - timedelta(days=1),
                ),
                MealLog(
                    name="Protein Shake",
                    calories=300,
                    protein=40,
                    carbs=20,
                    fat=5,
                    date=date.today() - timedelta(days=2),
                ),
            ]
        return []
