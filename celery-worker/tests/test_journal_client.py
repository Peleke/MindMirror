"""Tests for the CeleryJournalClient."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
import httpx

from src.clients.journal_client import CeleryJournalClient


class TestCeleryJournalClient:
    """Test the CeleryJournalClient."""

    def test_init_default_values(self):
        """Test client initialization with default values."""
        client = CeleryJournalClient()
        assert client.base_url == "http://journal_service:8001"
        assert client.graphql_endpoint == "http://journal_service:8001/graphql"
        assert client.client is not None

    def test_init_custom_base_url(self):
        """Test client initialization with custom base URL."""
        custom_url = "http://custom-journal:9001"
        client = CeleryJournalClient(base_url=custom_url)
        assert client.base_url == custom_url
        assert client.graphql_endpoint == f"{custom_url}/graphql"

    @pytest.mark.asyncio
    async def test_execute_query_success(self):
        """Test successful GraphQL query execution."""
        client = CeleryJournalClient()

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"data": {"test": "response"}}

        with patch.object(client.client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await client._execute_query("query { test }", user_id="test-user")

            assert result == {"test": "response"}
            mock_post.assert_called_once()

            # Check the call arguments
            call_args = mock_post.call_args
            assert call_args[0][0] == client.graphql_endpoint

            # Check headers include user ID
            headers = call_args[1]["headers"]
            assert headers["x-internal-id"] == "test-user"
            assert headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_execute_query_without_user_id(self):
        """Test GraphQL query execution without user ID."""
        client = CeleryJournalClient()

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"data": {"test": "response"}}

        with patch.object(client.client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await client._execute_query("query { test }")

            # Check headers don't include user ID
            headers = mock_post.call_args[1]["headers"]
            assert "x-internal-id" not in headers

    @pytest.mark.asyncio
    async def test_execute_query_graphql_error(self):
        """Test GraphQL query with errors in response."""
        client = CeleryJournalClient()

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"errors": [{"message": "GraphQL error"}]}

        with patch.object(client.client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            with pytest.raises(Exception, match="GraphQL errors"):
                await client._execute_query("query { test }")

    @pytest.mark.asyncio
    async def test_execute_query_http_error(self):
        """Test GraphQL query with HTTP error."""
        client = CeleryJournalClient()

        with patch.object(client.client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.HTTPStatusError(
                "404 Not Found", request=Mock(), response=Mock(status_code=404)
            )

            with pytest.raises(httpx.HTTPStatusError):
                await client._execute_query("query { test }")

    @pytest.mark.asyncio
    async def test_get_entry_by_id_success(self):
        """Test successful journal entry retrieval by ID."""
        client = CeleryJournalClient()

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "data": {
                "journalEntry": {
                    "id": "test-entry-id",
                    "entryType": "FREEFORM",
                    "payload": {"content": "Test entry content"},
                    "createdAt": "2023-01-01T00:00:00Z",
                    "user_id": "test-user-id",  # Add user_id to the response
                }
            }
        }

        with patch.object(client.client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await client.get_entry_by_id("test-entry-id", "test-user-id")

            assert result is not None
            assert result["id"] == "test-entry-id"
            assert result["entry_type"] == "FREEFORM"
            assert result["user_id"] == "test-user-id"
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_entry_by_id_not_found(self):
        """Test journal entry retrieval when entry not found."""
        client = CeleryJournalClient()

        with patch.object(
            client, "_execute_query", new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.return_value = {"journalEntry": None}

            result = await client.get_entry_by_id("nonexistent-id", "test-user-id")
            assert result is None

    @pytest.mark.asyncio
    async def test_list_by_user_for_period_success(self):
        """Test successful journal entries listing for a period."""
        client = CeleryJournalClient()

        expected_entries = [
            {
                "id": "entry-1",
                "content": "Content 1",
                "entryType": "FREEFORM",
                "createdAt": "2024-01-01T00:00:00Z",
            },
            {
                "id": "entry-2",
                "content": "Content 2",
                "entryType": "GRATITUDE",
                "createdAt": "2024-01-02T00:00:00Z",
            },
        ]

        with patch.object(
            client, "_execute_query", new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.return_value = {"journalEntries": expected_entries}

            result = await client.list_by_user_for_period(
                "test-user-id", "2024-01-01T00:00:00Z", "2024-01-31T23:59:59Z"
            )

            assert len(result) == 2
            assert result[0]["id"] == "entry-1"
            assert result[0]["entry_type"] == "FREEFORM"
            assert result[1]["id"] == "entry-2"
            assert result[1]["entry_type"] == "GRATITUDE"

            # Check the GraphQL query parameters
            call_args = mock_execute.call_args
            variables = call_args[0][1]
            assert variables["userId"] == "test-user-id"
            assert variables["startDate"] == "2024-01-01T00:00:00Z"
            assert variables["endDate"] == "2024-01-31T23:59:59Z"

    @pytest.mark.asyncio
    async def test_list_by_user_for_period_empty(self):
        """Test journal entries listing with no results."""
        client = CeleryJournalClient()

        with patch.object(
            client, "_execute_query", new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.return_value = {"journalEntries": []}

            result = await client.list_by_user_for_period(
                "test-user-id", "2024-01-01T00:00:00Z", "2024-01-31T23:59:59Z"
            )

            assert result == []
