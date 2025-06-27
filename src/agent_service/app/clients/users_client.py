from typing import Optional

from agent_service.clients.models import UserGoals


class UsersClient:
    """
    A client to interact with the external 'users' service.
    For now, this is a mock that returns hardcoded data.
    """

    def get_user_goals(self, user_id: str) -> Optional[UserGoals]:
        """
        Retrieves the nutritional goals for a given user.
        """
        print(f"MOCK UsersClient: Fetching goals for user {user_id}")
        # In a real implementation, this would make an HMAC-signed API call.
        if user_id == "test-user-123":
            return UserGoals(
                daily_calorie_goal=3500.0,
                daily_protein_goal=200.0,
                daily_carbs_goal=300.0,
                daily_fat_goal=100.0,
            )
        return None
