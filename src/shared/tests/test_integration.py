"""
Integration tests demonstrating HTTP client usage across services.

These tests show how the shared HTTP clients enable real communication
between services, replacing the previous mock-based approach.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from shared.clients import (AuthContext, ServiceClientError,
                            create_agent_client, create_journal_client)


class TestServiceIntegration:
    """Integration tests showing cross-service communication."""
    
    @pytest.mark.asyncio
    async def test_agent_service_calls_journal_service(self):
        """
        Test that demonstrates how the agent service would use the journal client
        to fetch data for RAG operations.
        """
        # Mock the HTTP response from journal service
        mock_journal_response = {
            "data": {
                "journalEntries": [
                    {
                        "__typename": "GratitudeJournalEntry",
                        "id": "test-entry-123",
                        "userId": "user-456",
                        "createdAt": "2024-01-15T10:30:00Z",
                        "modifiedAt": None,
                        "gratitudePayload": {
                            "gratefulFor": "Morning coffee and productive work",
                            "mood": 8
                        }
                    }
                ]
            }
        }
        
        with patch('shared.clients.base.httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.is_success = True
            mock_response.json.return_value = mock_journal_response
            mock_post.return_value = mock_response
            
            # Agent service creates journal client to fetch user data
            journal_client = create_journal_client("http://journal-service:8001")
            user_id = uuid4()
            
            async with journal_client as client:
                entries = await client.list_entries_for_user(user_id)
                
                # Verify the agent service got the data it needs
                assert len(entries) == 1
                assert entries[0].entry_type == "GRATITUDE"
                assert entries[0].user_id == "user-456"
                assert "Morning coffee" in str(entries[0].payload)
    
    @pytest.mark.asyncio
    async def test_journal_service_triggers_agent_indexing(self):
        """
        Test that demonstrates how the journal service would notify
        the agent service about new entries for indexing.
        """
        # Mock the HTTP response from agent service
        mock_index_response = {"success": True}
        
        with patch('shared.clients.base.httpx.AsyncClient.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.is_success = True
            mock_response.json.return_value = mock_index_response
            mock_request.return_value = mock_response
            
            # Journal service creates agent client to trigger indexing
            agent_client = create_agent_client("http://agent-service:8000")
            user_id = uuid4()
            
            async with agent_client as client:
                success = await client.index_document(
                    user_id=user_id,
                    document_id="journal-entry-789",
                    content="Today I learned about microservices communication",
                    metadata={
                        "source_type": "journal_entry",
                        "entry_type": "reflection",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
                
                # Verify the indexing was successful
                assert success is True
                
                # Verify the correct API was called
                mock_request.assert_called_once()
                call_args = mock_request.call_args
                assert call_args[1]['method'] == 'POST'
                assert call_args[1]['url'].endswith('/index/document')
                
                # Verify the payload
                request_data = call_args[1]['json']
                assert request_data['document_id'] == "journal-entry-789"
                assert request_data['content'] == "Today I learned about microservices communication"
                assert request_data['metadata']['source_type'] == "journal_entry"
    
    @pytest.mark.asyncio
    async def test_error_handling_across_services(self):
        """
        Test that errors are properly propagated across service boundaries.
        """
        with patch('shared.clients.base.httpx.AsyncClient.request') as mock_request:
            # Simulate agent service being down
            mock_response = MagicMock()
            mock_response.status_code = 503
            mock_response.is_success = False
            mock_request.return_value = mock_response
            
            agent_client = create_agent_client("http://agent-service:8000")
            user_id = uuid4()
            
            async with agent_client as client:
                with pytest.raises(ServiceClientError) as exc_info:
                    await client.search_documents(
                        user_id=user_id,
                        query="test search"
                    )
                
                # Verify error details
                assert exc_info.value.status_code == 503
                assert exc_info.value.service == "agent-service"
    
    @pytest.mark.asyncio
    async def test_authentication_context_propagation(self):
        """
        Test that authentication context is properly propagated between services.
        """
        mock_response_data = {"results": []}
        
        with patch('shared.clients.base.httpx.AsyncClient.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.is_success = True
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            agent_client = create_agent_client("http://agent-service:8000")
            user_id = uuid4()
            
            async with agent_client as client:
                await client.search_documents(
                    user_id=user_id,
                    query="test"
                )
                
                # Verify authentication headers were set
                call_args = mock_request.call_args
                headers = call_args[1]['headers']
                assert headers['x-internal-id'] == str(user_id)
                assert 'Content-Type' in headers


class TestClientFactories:
    """Test the convenience factory functions."""
    
    def test_journal_client_factory_with_custom_config(self):
        """Test creating journal client with custom configuration."""
        client = create_journal_client("http://custom-journal:9000")
        
        assert client.config.base_url == "http://custom-journal:9000"
        assert client.config.service_name == "journal-service"
        assert client.config.timeout == 15.0
    
    def test_agent_client_factory_with_custom_config(self):
        """Test creating agent client with custom configuration."""
        client = create_agent_client("http://custom-agent:9001")
        
        assert client.config.base_url == "http://custom-agent:9001"
        assert client.config.service_name == "agent-service"
        assert client.config.timeout == 30.0 