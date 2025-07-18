"""
Google Cloud Pub/Sub client for MindMirror celery-worker service.

This module provides functionality to publish messages to Pub/Sub topics
and handle push subscription messages from Cloud Run endpoints.
"""

import json
import logging
import os
from typing import Any, Dict, Optional

from google.cloud import pubsub_v1
from google.auth import default
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class PubSubMessage(BaseModel):
    """Base model for Pub/Sub messages."""
    data: Dict[str, Any]
    attributes: Optional[Dict[str, str]] = None


class PubSubClient:
    """Client for Google Cloud Pub/Sub operations."""
    
    def __init__(self, project_id: Optional[str] = None):
        """Initialize the Pub/Sub client.
        
        Args:
            project_id: Google Cloud project ID. If None, will use default credentials.
        """
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        if not self.project_id:
            raise ValueError("Project ID must be provided or set in GOOGLE_CLOUD_PROJECT env var")
        
        # Initialize the publisher client
        self.publisher = pubsub_v1.PublisherClient()
        
        # Initialize the subscriber client (for pull subscriptions if needed)
        self.subscriber = pubsub_v1.SubscriberClient()
        
        logger.info(f"Initialized Pub/Sub client for project: {self.project_id}")
    
    def publish_message(
        self, 
        topic_name: str, 
        data: Dict[str, Any], 
        attributes: Optional[Dict[str, str]] = None
    ) -> str:
        """Publish a message to a Pub/Sub topic.
        
        Args:
            topic_name: Name of the Pub/Sub topic
            data: Message data to publish
            attributes: Optional message attributes
            
        Returns:
            Message ID of the published message
            
        Raises:
            Exception: If publishing fails
        """
        topic_path = self.publisher.topic_path(self.project_id, topic_name)
        
        # Convert data to JSON string
        json_data = json.dumps(data).encode("utf-8")
        
        try:
            # Publish the message
            future = self.publisher.publish(
                topic_path, 
                data=json_data,
                **(attributes or {})
            )
            
            message_id = future.result()
            logger.info(f"Published message {message_id} to topic {topic_name}")
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to publish message to topic {topic_name}: {e}")
            raise
    
    def publish_journal_indexing(
        self, 
        entry_id: str, 
        user_id: str, 
        tradition: str = "canon-default",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Publish a journal entry indexing message.
        
        Args:
            entry_id: Journal entry ID to index
            user_id: User ID who owns the entry
            tradition: Tradition to use for indexing
            metadata: Additional metadata
            
        Returns:
            Message ID of the published message
        """
        topic_name = os.getenv("JOURNAL_INDEXING_TOPIC", "journal-indexing")
        
        data = {
            "entry_id": entry_id,
            "user_id": user_id,
            "tradition": tradition,
            "metadata": metadata or {},
            "task_type": "journal_indexing"
        }
        
        return self.publish_message(topic_name, data)
    
    def publish_journal_batch_indexing(
        self, 
        entry_ids: list[str], 
        user_id: str, 
        tradition: str = "canon-default"
    ) -> str:
        """Publish a batch journal entry indexing message.
        
        Args:
            entry_ids: List of journal entry IDs to index
            user_id: User ID who owns the entries
            tradition: Tradition to use for indexing
            
        Returns:
            Message ID of the published message
        """
        topic_name = os.getenv("JOURNAL_BATCH_INDEXING_TOPIC", "journal-batch-indexing")
        
        data = {
            "entry_ids": entry_ids,
            "user_id": user_id,
            "tradition": tradition,
            "task_type": "journal_batch_indexing"
        }
        
        return self.publish_message(topic_name, data)
    
    def publish_journal_reindex(
        self, 
        tradition: str = "canon-default"
    ) -> str:
        """Publish a journal reindexing message.
        
        Args:
            tradition: Tradition to reindex
            
        Returns:
            Message ID of the published message
        """
        topic_name = os.getenv("JOURNAL_REINDEX_TOPIC", "journal-reindex")
        
        data = {
            "tradition": tradition,
            "task_type": "journal_reindex"
        }
        
        return self.publish_message(topic_name, data)
    
    def publish_tradition_rebuild(
        self, 
        tradition: str
    ) -> str:
        """Publish a tradition rebuild message.
        
        Args:
            tradition: Tradition to rebuild
            
        Returns:
            Message ID of the published message
        """
        topic_name = os.getenv("TRADITION_REBUILD_TOPIC", "tradition-rebuild")
        
        data = {
            "tradition": tradition,
            "task_type": "tradition_rebuild"
        }
        
        return self.publish_message(topic_name, data)
    
    def publish_health_check(self) -> str:
        """Publish a health check message.
        
        Returns:
            Message ID of the published message
        """
        topic_name = os.getenv("HEALTH_CHECK_TOPIC", "health-check")
        
        data = {
            "task_type": "health_check",
            "timestamp": str(pubsub_v1.time_helpers.utcnow())
        }
        
        return self.publish_message(topic_name, data)


# Global client instance
_pubsub_client: Optional[PubSubClient] = None


def get_pubsub_client() -> PubSubClient:
    """Get or create the global Pub/Sub client instance.
    
    Returns:
        PubSubClient instance
    """
    global _pubsub_client
    if _pubsub_client is None:
        _pubsub_client = PubSubClient()
    return _pubsub_client


def parse_push_message(request_data: bytes, attributes: Dict[str, str]) -> PubSubMessage:
    """Parse a push subscription message.
    
    Args:
        request_data: Raw message data from push subscription
        attributes: Message attributes from push subscription
        
    Returns:
        Parsed PubSubMessage object
    """
    try:
        # Decode the message data
        data_str = request_data.decode("utf-8")
        data = json.loads(data_str)
        
        return PubSubMessage(data=data, attributes=attributes)
        
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logger.error(f"Failed to parse push message: {e}")
        raise ValueError(f"Invalid message format: {e}") 