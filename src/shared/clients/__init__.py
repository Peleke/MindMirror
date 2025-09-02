"""
Shared HTTP clients for inter-service communication.

This module provides functional, composable HTTP clients for all services
in the system, following TDD principles and focusing on reliability.
"""

# Agent Service Client
from .agent_client import (AgentServiceClient, DocumentSearchResult,
                           SuggestionResponse, create_agent_client)
# Base components
from .base import (AuthContext, AuthenticationError, BaseServiceClient,
                   DataNotFoundError, ServiceClientError, ServiceConfig,
                   ServiceUnavailableError)
# Journal Service Client
from .journal_client import (JournalEntry, JournalServiceClient,
                             create_journal_client)

__all__ = [
    # Base components
    "AuthContext",
    "ServiceConfig",
    "ServiceClientError",
    "ServiceUnavailableError",
    "AuthenticationError",
    "DataNotFoundError",
    "BaseServiceClient",
    
    # Journal Service
    "JournalEntry",
    "JournalServiceClient",
    "create_journal_client",
    
    # Agent Service
    "DocumentSearchResult",
    "SuggestionResponse",
    "AgentServiceClient",
    "create_agent_client",
] 