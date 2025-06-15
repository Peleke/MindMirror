from typing import List, Optional

import strawberry


@strawberry.type
class MealSuggestion:
    """
    GraphQL type for a meal suggestion.
    For now, it's a simple string, but can be expanded to be a structured object.
    """

    suggestion: str


@strawberry.type
class PerformanceReview:
    """
    GraphQL type for a user's performance review.
    """

    key_success: str
    improvement_area: str
    journal_prompt: str
