"""
Task processors for handling business logic directly.

This module provides processors that execute business logic directly
without Celery, replacing the old task queue system.
"""

from .task_processors import (
    JournalIndexingProcessor,
    TraditionRebuildProcessor,
    HealthCheckProcessor,
    get_journal_processor,
    get_tradition_processor,
    get_health_processor,
)

__all__ = [
    "JournalIndexingProcessor",
    "TraditionRebuildProcessor", 
    "HealthCheckProcessor",
    "get_journal_processor",
    "get_tradition_processor",
    "get_health_processor",
]
