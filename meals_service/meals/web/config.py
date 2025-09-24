import os
from pydantic import BaseModel


class MealsWebConfig(BaseModel):
    API_VERSION: str = os.getenv("API_VERSION", "0.1.0")
    DEBUG_GRAPHQL_SERVER: bool = os.getenv("DEBUG_GRAPHQL_SERVER", "true").lower() == "true"

    # Database Configuration - loaded from environment variables
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5433")  # Changed port to avoid conflict with practices
    DB_NAME: str = os.getenv("DB_NAME", "swae_meals")  # Using a different DB name

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    off_user_agent: str = os.getenv("OFF_USER_AGENT", "MindMirrorMeals/1.0 (+support@mindmirror.app)")
    off_searchalicious_enabled: bool = os.getenv("OFF_SEARCHALICIOUS_ENABLED", "false").lower() == "true"
    off_default_fields: list[str] = [
        "code",
        "product_name",
        "brands",
        "image_url",
        "nutrition_grades",
        "nutriscore_data",
        "nutriments",
        "serving_size",
        "serving_quantity",
    ]

    # Add any other meals-specific configurations here
    # For example, if you had external service URLs, API keys, etc.


# Backward compatible alias used throughout the codebase
Config = MealsWebConfig()
