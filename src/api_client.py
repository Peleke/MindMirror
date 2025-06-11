import aiohttp
import json
import os

API_HOST = os.getenv("API_HOST", "localhost")
API_URL = f"http://{API_HOST}:8000/graphql"

async def run_graphql_query(query: str, variables: dict = None):
    """
    Asynchronously runs a GraphQL query or mutation.

    Args:
        query: The GraphQL query string.
        variables: A dictionary of variables for the query.

    Returns:
        The JSON response from the API.
    """
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, json=payload) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                return {
                    "errors": [
                        {
                            "message": f"API request failed with status {response.status}: {error_text}"
                        }
                    ]
                } 