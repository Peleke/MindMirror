import json
import os
import re

import aiohttp

# Detect if we're running in Docker and set appropriate service endpoints
if os.getenv("I_AM_IN_A_DOCKER_CONTAINER"):
    AGENT_SERVICE_URL = "http://agent_service:8000/graphql"
    JOURNAL_SERVICE_URL = "http://journal_service:8001/graphql"
else:
    AGENT_SERVICE_URL = "http://localhost:8000/graphql"
    JOURNAL_SERVICE_URL = "http://localhost:8001/graphql"

# Demo user ID that matches our test fixtures
DEMO_USER_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

print(f"API Client configured for:")
print(f"  Agent Service: {AGENT_SERVICE_URL}")
print(f"  Journal Service: {JOURNAL_SERVICE_URL}")

# Define which operations belong to which service
AGENT_SERVICE_OPERATIONS = {
    # Queries
    "ask",
    "listTraditions",
    "getMealSuggestion",
    # Mutations
    "uploadDocument",
    "generateReview",
}

JOURNAL_SERVICE_OPERATIONS = {
    # Queries
    "journalEntries",
    "journalEntryExistsToday",
    # Mutations
    "createFreeformJournalEntry",
    "createGratitudeJournalEntry",
    "createReflectionJournalEntry",
    "deleteJournalEntry",
}


def determine_service_endpoint(query: str) -> str:
    """
    Determine which service endpoint to use based on the GraphQL operation.

    Args:
        query: The GraphQL query string

    Returns:
        The appropriate service URL
    """
    # Extract operation names from the query using regex
    # Look for both query/mutation definitions and field names
    operation_pattern = (
        r"(?:query|mutation|subscription)\s+\w*\s*(?:\([^)]*\))?\s*\{[^{]*?(\w+)"
    )
    field_pattern = r"\{\s*(\w+)"

    # Try to find operation names
    operation_matches = re.findall(operation_pattern, query, re.IGNORECASE | re.DOTALL)
    field_matches = re.findall(field_pattern, query)

    # Combine all potential operation names
    potential_operations = operation_matches + field_matches

    # Check which service this operation belongs to
    for op in potential_operations:
        if op in AGENT_SERVICE_OPERATIONS:
            return AGENT_SERVICE_URL
        elif op in JOURNAL_SERVICE_OPERATIONS:
            return JOURNAL_SERVICE_URL

    # Default to agent service if we can't determine
    print(
        f"Warning: Could not determine service for query, defaulting to agent service"
    )
    print(f"Query: {query[:100]}...")
    return AGENT_SERVICE_URL


async def run_graphql_query(
    query: str, variables: dict = None, user_id: str = None, jwt_token: str = None
):
    """
    Asynchronously runs a GraphQL query or mutation with authentication.
    Routes the request to the appropriate service based on the operation.

    Args:
        query: The GraphQL query string.
        variables: A dictionary of variables for the query.
        user_id: The business logic user ID (for x-internal-id header)
        jwt_token: The JWT token (for Authorization header)

    Returns:
        The JSON response from the API.
    """
    # Determine which service to call
    service_url = determine_service_endpoint(query)

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
            async with session.post(
                service_url, json=payload, headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    print(f"API Error: {response.status} - {error_text}")
                    print(f"Service URL: {service_url}")
                    return {
                        "errors": [
                            {
                                "message": f"API request failed with status {response.status}: {error_text}"
                            }
                        ]
                    }
    except aiohttp.ClientError as e:
        print(f"Network Error: {e}")
        print(f"Service URL: {service_url}")
        return {
            "errors": [
                {
                    "message": f"Network error: Could not connect to API at {service_url}. Error: {str(e)}"
                }
            ]
        }
    except Exception as e:
        print(f"Unexpected Error: {e}")
        print(f"Service URL: {service_url}")
        return {"errors": [{"message": f"Unexpected error: {str(e)}"}]}
