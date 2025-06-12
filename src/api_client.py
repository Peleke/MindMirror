import json
import os

import aiohttp

# Detect if we're running in Docker and set appropriate API host
if os.getenv("I_AM_IN_A_DOCKER_CONTAINER"):
    API_HOST = os.getenv("API_HOST", "api")
    API_PORT = os.getenv("API_PORT", "8000")
else:
    API_HOST = os.getenv("API_HOST", "localhost")
    API_PORT = os.getenv("API_PORT", "8000")

API_URL = f"http://{API_HOST}:{API_PORT}/graphql"

# Demo user ID that matches our test fixtures
DEMO_USER_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

print(f"API Client configured for: {API_URL}")


async def run_graphql_query(
    query: str, variables: dict = None, user_id: str = None, jwt_token: str = None
):
    """
    Asynchronously runs a GraphQL query or mutation with authentication.

    Args:
        query: The GraphQL query string.
        variables: A dictionary of variables for the query.
        user_id: The business logic user ID (for x-internal-id header)
        jwt_token: The JWT token (for Authorization header)

    Returns:
        The JSON response from the API.
    """
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    # Setup headers for authentication
    headers = {"Content-Type": "application/json"}

    # Use demo user if no specific user provided
    if not user_id:
        user_id = DEMO_USER_ID

    # Add auth headers for production or use demo JWT for development
    if jwt_token:
        headers["Authorization"] = f"Bearer {jwt_token}"
    else:
        # Demo JWT for development
        headers["Authorization"] = (
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXN1YmplY3QifQ.s-0-gH8G0-t9P1-r_Gg_y_g"
        )

    headers["x-internal-id"] = user_id

    try:
        timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(API_URL, json=payload, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    print(f"API Error: {response.status} - {error_text}")
                    return {
                        "errors": [
                            {
                                "message": f"API request failed with status {response.status}: {error_text}"
                            }
                        ]
                    }
    except aiohttp.ClientError as e:
        print(f"Network Error: {e}")
        return {
            "errors": [
                {
                    "message": f"Network error: Could not connect to API at {API_URL}. Error: {str(e)}"
                }
            ]
        }
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return {"errors": [{"message": f"Unexpected error: {str(e)}"}]}
