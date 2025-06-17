import json
import os

import aiohttp


def _is_docker_environment() -> bool:
    """Check if running inside Docker container."""
    return (
        os.path.exists("/.dockerenv")
        or os.getenv("DOCKER_CONTAINER") == "true"
        or os.getenv("IN_DOCKER") == "true"
        or os.getenv("I_AM_IN_A_DOCKER_CONTAINER") is not None
    )


# Use Hive Gateway for all GraphQL operations
if _is_docker_environment():
    # In Docker, gateway service will be accessible via service name
    GATEWAY_URL = "http://gateway:4000/graphql"
else:
    # In local development, gateway runs on localhost
    GATEWAY_URL = "http://localhost:4000/graphql"

# Demo user ID that matches our test fixtures
DEMO_USER_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

print(f"API Client configured to use Hive Gateway:")
print(f"  Gateway URL: {GATEWAY_URL}")


async def run_graphql_query(
    query: str, variables: dict = None, user_id: str = None, jwt_token: str = None
):
    """
    Asynchronously runs a GraphQL query or mutation with authentication.
    All requests are routed through the Hive Gateway.

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

    # Debug logging to verify headers are being sent
    print(f"🔍 DEBUG: Sending request to {GATEWAY_URL}")
    print(f"🔍 DEBUG: Headers being sent: {headers}")
    print(f"🔍 DEBUG: Payload: {payload}")

    try:
        timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                GATEWAY_URL, json=payload, headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    print(f"API Error: {response.status} - {error_text}")
                    print(f"Gateway URL: {GATEWAY_URL}")
                    return {
                        "errors": [
                            {
                                "message": f"API request failed with status {response.status}: {error_text}"
                            }
                        ]
                    }
    except aiohttp.ClientError as e:
        print(f"Network Error: {e}")
        print(f"Gateway URL: {GATEWAY_URL}")
        return {
            "errors": [
                {
                    "message": f"Network error: Could not connect to Gateway at {GATEWAY_URL}. Error: {str(e)}"
                }
            ]
        }
    except Exception as e:
        print(f"Unexpected Error: {e}")
        print(f"Gateway URL: {GATEWAY_URL}")
        return {"errors": [{"message": f"Unexpected error: {str(e)}"}]}
