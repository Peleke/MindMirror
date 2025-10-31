"""
Test Driven Development tests for JournalServiceClient.

These tests validate the client behavior against mocked HTTP responses,
ensuring the client correctly handles all success and error scenarios.
"""

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import httpx
import pytest

from shared.clients.base import (AuthContext, AuthenticationError,
                                 DataNotFoundError, ServiceClientError,
                                 ServiceConfig, ServiceUnavailableError)
from shared.clients.journal_client import (JournalEntry, JournalServiceClient,
                                           create_journal_client)


# Fixtures
@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def auth_context(user_id):
    return AuthContext(user_id=user_id)


@pytest.fixture
def service_config():
    return ServiceConfig(
        base_url="http://test-journal-service:8001",
        service_name="test-journal-service",
        timeout=5.0,
        max_retries=1,
    )


@pytest.fixture
def journal_client(service_config):
    return JournalServiceClient(service_config)


@pytest.fixture
def mock_graphql_response():
    """Sample GraphQL response matching the journal service format."""
    return {
        "data": {
            "journalEntries": [
                {
                    "__typename": "GratitudeJournalEntry",
                    "id": "550e8400-e29b-41d4-a716-446655440001",
                    "userId": "550e8400-e29b-41d4-a716-446655440000",
                    "createdAt": "2024-01-15T10:30:00Z",
                    "modifiedAt": "2024-01-15T10:35:00Z",
                    "gratitudePayload": {
                        "gratefulFor": "Morning coffee",
                        "excitedAbout": "New project",
                        "focus": "Productivity",
                        "affirmation": "I am capable",
                        "mood": 8
                    }
                },
                {
                    "__typename": "FreeformJournalEntry",
                    "id": "550e8400-e29b-41d4-a716-446655440002",
                    "userId": "550e8400-e29b-41d4-a716-446655440000",
                    "createdAt": "2024-01-14T15:20:00Z",
                    "modifiedAt": None,
                    "freeformPayload": "Today was a good day for reflection..."
                },
                {
                    "__typename": "ReflectionJournalEntry",
                    "id": "550e8400-e29b-41d4-a716-446655440003",
                    "userId": "550e8400-e29b-41d4-a716-446655440000",
                    "createdAt": "2024-01-13T20:00:00Z",
                    "modifiedAt": None,
                    "reflectionPayload": {
                        "wins": "Completed the presentation",
                        "improvements": "Better time management",
                        "mood": 7
                    }
                }
            ]
        }
    }


@pytest.fixture
def mock_exists_response():
    return {"data": {"journalEntryExistsToday": True}}


# Test JournalEntry Data Transfer Object
class TestJournalEntry:
    """Test the JournalEntry DTO creation and data handling."""
    
    def test_gratitude_entry_from_graphql_response(self):
        """Test creating GratitudeJournalEntry from GraphQL response."""
        graphql_data = {
            "__typename": "GratitudeJournalEntry",
            "id": "test-id",
            "userId": "test-user",
            "createdAt": "2024-01-15T10:30:00Z",
            "modifiedAt": "2024-01-15T10:35:00Z",
            "gratitudePayload": {
                "gratefulFor": "Test gratitude",
                "mood": 8
            }
        }
        
        entry = JournalEntry.from_graphql_response(graphql_data)
        
        assert entry.id == "test-id"
        assert entry.user_id == "test-user"
        assert entry.entry_type == "GRATITUDE"
        assert entry.payload == {"gratefulFor": "Test gratitude", "mood": 8}
        assert entry.created_at == datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        assert entry.modified_at == datetime(2024, 1, 15, 10, 35, 0, tzinfo=timezone.utc)
    
    def test_freeform_entry_from_graphql_response(self):
        """Test creating FreeformJournalEntry from GraphQL response."""
        graphql_data = {
            "__typename": "FreeformJournalEntry",
            "id": "test-id-2",
            "userId": "test-user",
            "createdAt": "2024-01-14T15:20:00Z",
            "modifiedAt": None,
            "freeformPayload": "Free form text content"
        }
        
        entry = JournalEntry.from_graphql_response(graphql_data)
        
        assert entry.id == "test-id-2"
        assert entry.entry_type == "FREEFORM"
        assert entry.payload == "Free form text content"
        assert entry.modified_at is None
    
    def test_reflection_entry_from_graphql_response(self):
        """Test creating ReflectionJournalEntry from GraphQL response."""
        graphql_data = {
            "__typename": "ReflectionJournalEntry",
            "id": "test-id-3",
            "userId": "test-user",
            "createdAt": "2024-01-13T20:00:00Z",
            "modifiedAt": None,
            "reflectionPayload": {
                "wins": "Big win today",
                "improvements": "Could do better"
            }
        }
        
        entry = JournalEntry.from_graphql_response(graphql_data)
        
        assert entry.entry_type == "REFLECTION"
        assert entry.payload == {"wins": "Big win today", "improvements": "Could do better"}


# Test JournalServiceClient
class TestJournalServiceClient:
    """Test the JournalServiceClient functionality."""
    
    @pytest.mark.asyncio
    async def test_list_entries_for_user_success(
        self, journal_client, auth_context, mock_graphql_response
    ):
        """Test successful retrieval of journal entries."""
        with patch('shared.clients.base.httpx.AsyncClient.post') as mock_post:
            # Mock successful HTTP response
            mock_response = MagicMock()  # Use MagicMock for synchronous methods
            mock_response.status_code = 200
            mock_response.is_success = True
            mock_response.json.return_value = mock_graphql_response  # Synchronous return
            mock_post.return_value = mock_response
            
            async with journal_client as client:
                entries = await client.list_entries_for_user(auth_context.user_id)
            
            # Verify the request was made correctly
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            
            # Check GraphQL query
            assert call_args[1]['json']['query'] is not None
            assert 'journalEntries' in call_args[1]['json']['query']
            
            # Check headers
            headers = call_args[1]['headers']
            assert headers['x-internal-id'] == str(auth_context.user_id)
            assert headers['Content-Type'] == 'application/json'
            
            # Verify entries were parsed correctly
            assert len(entries) == 3
            assert entries[0].entry_type == "GRATITUDE"
            assert entries[1].entry_type == "FREEFORM"
            assert entries[2].entry_type == "REFLECTION"
    
    @pytest.mark.asyncio
    async def test_list_entries_with_date_filtering(
        self, journal_client, auth_context, mock_graphql_response
    ):
        """Test client-side date filtering of journal entries."""
        with patch('shared.clients.base.httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.is_success = True
            mock_response.json.return_value = mock_graphql_response
            mock_post.return_value = mock_response
            
            # Filter to only entries after 2024-01-14
            start_date = datetime(2024, 1, 14, 0, 0, 0, tzinfo=timezone.utc)
            
            async with journal_client as client:
                entries = await client.list_entries_for_user(
                    auth_context.user_id, 
                    start_date=start_date
                )
            
            # Should only return 2 entries (Jan 15 and Jan 14, not Jan 13)
            assert len(entries) == 2
            assert all(entry.created_at >= start_date for entry in entries)
    
    @pytest.mark.asyncio
    async def test_check_entry_exists_today_success(
        self, journal_client, auth_context, mock_exists_response
    ):
        """Test checking if entry exists today."""
        with patch('shared.clients.base.httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.is_success = True
            mock_response.json.return_value = mock_exists_response
            mock_post.return_value = mock_response
            
            async with journal_client as client:
                exists = await client.check_entry_exists_today(
                    auth_context.user_id, 
                    "GRATITUDE"
                )
            
            # Verify request was made with correct variables
            call_args = mock_post.call_args
            request_json = call_args[1]['json']
            assert request_json['variables'] == {"entryType": "GRATITUDE"}
            assert request_json['operationName'] == "JournalEntryExistsToday"
            
            # Verify response
            assert exists is True
    
    @pytest.mark.asyncio
    async def test_graphql_error_handling(self, journal_client, auth_context):
        """Test handling of GraphQL errors in response."""
        with patch('shared.clients.base.httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.is_success = True
            mock_response.json.return_value = {
                "errors": [
                    {"message": "Field 'invalidField' doesn't exist"},
                    {"message": "Another error"}
                ]
            }
            mock_post.return_value = mock_response
            
            async with journal_client as client:
                with pytest.raises(ServiceClientError) as exc_info:
                    await client.list_entries_for_user(auth_context.user_id)
                
                assert "GraphQL errors" in str(exc_info.value)
                assert "Field 'invalidField'" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_authentication_error_handling(self, journal_client, auth_context):
        """Test handling of authentication errors."""
        with patch('shared.clients.base.httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.is_success = False
            mock_post.return_value = mock_response
            
            async with journal_client as client:
                with pytest.raises(AuthenticationError) as exc_info:
                    await client.list_entries_for_user(auth_context.user_id)
                
                assert exc_info.value.status_code == 401
                assert exc_info.value.service == "test-journal-service"
    
    @pytest.mark.asyncio
    async def test_service_unavailable_error_handling(self, journal_client, auth_context):
        """Test handling of 5xx server errors."""
        with patch('shared.clients.base.httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 503
            mock_response.is_success = False
            mock_post.return_value = mock_response
            
            async with journal_client as client:
                with pytest.raises(ServiceUnavailableError) as exc_info:
                    await client.list_entries_for_user(auth_context.user_id)
                
                assert exc_info.value.status_code == 503
    
    @pytest.mark.asyncio
    async def test_empty_response_handling(self, journal_client, auth_context):
        """Test handling of empty or missing data in response."""
        with patch('shared.clients.base.httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.is_success = True
            mock_response.json.return_value = {"data": {"journalEntries": []}}
            mock_post.return_value = mock_response
            
            async with journal_client as client:
                entries = await client.list_entries_for_user(auth_context.user_id)
            
            assert entries == []


# Test Factory Function
class TestJournalClientFactory:
    """Test the factory function for creating journal clients."""
    
    def test_create_journal_client_default_config(self):
        """Test creating client with default configuration."""
        client = create_journal_client()
        
        assert client.config.base_url == "http://localhost:8001"
        assert client.config.service_name == "journal-service"
        assert client.config.timeout == 15.0
        assert client.config.max_retries == 2
    
    def test_create_journal_client_custom_url(self):
        """Test creating client with custom base URL."""
        custom_url = "http://production-journal:8001"
        client = create_journal_client(base_url=custom_url)
        
        assert client.config.base_url == custom_url 