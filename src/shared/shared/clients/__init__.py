"""
Shared clients package for MindMirror services.

This package provides HTTP clients and authentication context managers
for inter-service communication.
"""

from .user_service_client import UsersServiceClient, users_service_client
from .journal_client import JournalServiceClient, create_journal_client, AuthContext

__all__ = [
    "UsersServiceClient",
    "users_service_client", 
    "JournalServiceClient",
    "create_journal_client",
    "AuthContext",
] 