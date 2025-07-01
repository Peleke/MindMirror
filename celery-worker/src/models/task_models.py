from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class IndexJournalEntryRequest(BaseModel):
    """Request model for indexing a journal entry."""

    entry_id: str
    user_id: str
    content: str
    created_at: datetime
    metadata: Optional[dict] = None


class ReindexTraditionRequest(BaseModel):
    """Request model for reindexing a tradition's knowledge base."""

    tradition_name: str
    collection_name: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Response model for health check."""

    status: str
    timestamp: datetime
    services: dict
    error: Optional[str] = None


class TaskResponse(BaseModel):
    """Response model for task submission."""

    task_id: str
    status: str
    message: str
