import os

import uvicorn

# Default HTTP port for the Cyborg Coach API
DEFAULT_HTTP_PORT = 8000
HTTP_PORT = int(os.getenv("API_PORT", DEFAULT_HTTP_PORT))


def start() -> None:
    """Start the Uvicorn server for the Cyborg Coach API."""
    UVICORN_RELOAD = os.getenv("UVICORN_RELOAD", "True").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()

    uvicorn.run(
        "api:app",  # Path to the FastAPI app instance
        host="0.0.0.0",
        port=HTTP_PORT,
        reload=UVICORN_RELOAD,
        log_level=LOG_LEVEL,
    )


if __name__ == "__main__":
    start()
