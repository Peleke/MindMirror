import os

import uvicorn

TEST_HTTP_PORT = int(os.getenv("HTTP_PORT", 8001))


def start() -> None:
    """Start the server."""
    UVICORN_RELOAD = os.getenv("UVICORN_RELOAD", "True").lower() == "true"
    uvicorn.run(
        "users.web.app:app", host="0.0.0.0", port=TEST_HTTP_PORT, reload=UVICORN_RELOAD, loop="asyncio", workers=1
    )
