import os

import uvicorn

# Use a different default port for the meals service to avoid conflicts
# when running multiple services locally.
DEFAULT_HTTP_PORT = 8089
HTTP_PORT = int(os.getenv("MEALS_HTTP_PORT", DEFAULT_HTTP_PORT))  # Use a specific env var for meals port


def start() -> None:
    """Start the Uvicorn server for the Meals API."""
    UVICORN_RELOAD = os.getenv("UVICORN_RELOAD", "True").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()

    uvicorn.run(
        "meals.web.app:app",  # Path to the FastAPI app instance
        host="0.0.0.0",
        port=HTTP_PORT,
        reload=UVICORN_RELOAD,
        log_level=LOG_LEVEL,
    )


if __name__ == "__main__":
    start()
