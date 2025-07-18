"""
Tests for Pub/Sub client functionality.

These tests verify the Pub/Sub client's ability to publish messages
and parse incoming push subscription messages.
"""

import json
import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from src.clients.pubsub_client import (
    PubSubClient,
    PubSubMessage,
    get_pubsub_client,
    parse_push_message,
)


@pytest.fixture
def sample_message_data():
    """Create sample message data for testing."""
    return {
        "entry_id": str(uuid4()),
        "user_id": str(uuid4()),
        "tradition": "canon-default",
        "task_type": "journal_indexing",
    }


@pytest.fixture
def sample_attributes():
    """Create sample message attributes for testing."""
    return {
        "message_id": str(uuid4()),
        "publish_time": "2024-01-01T00:00:00Z",
    }


class TestPubSubClient:
    """Test suite for PubSubClient."""

    @patch("src.clients.pubsub_client.pubsub_v1.PublisherClient")
    @patch("src.clients.pubsub_client.pubsub_v1.SubscriberClient")
    def test_client_initialization(self, mock_subscriber, mock_publisher):
        """Test that Pub/Sub client initializes correctly."""
        mock_pub_client = MagicMock()
        mock_sub_client = MagicMock()
        mock_publisher.return_value = mock_pub_client
        mock_subscriber.return_value = mock_sub_client

        client = PubSubClient("test-project")

        assert client.project_id == "test-project"
        assert client.publisher == mock_pub_client
        assert client.subscriber == mock_sub_client

    @patch("src.clients.pubsub_client.pubsub_v1.PublisherClient")
    @patch("src.clients.pubsub_client.pubsub_v1.SubscriberClient")
    def test_client_initialization_with_env_var(self, mock_subscriber, mock_publisher):
        """Test that Pub/Sub client uses environment variable for project ID."""
        mock_pub_client = MagicMock()
        mock_sub_client = MagicMock()
        mock_publisher.return_value = mock_pub_client
        mock_subscriber.return_value = mock_sub_client

        with patch.dict("os.environ", {"GOOGLE_CLOUD_PROJECT": "env-project"}):
            client = PubSubClient()

        assert client.project_id == "env-project"

    @patch("src.clients.pubsub_client.pubsub_v1.PublisherClient")
    @patch("src.clients.pubsub_client.pubsub_v1.SubscriberClient")
    def test_client_initialization_no_project_id(self, mock_subscriber, mock_publisher):
        """Test that Pub/Sub client raises error when no project ID is provided."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="Project ID must be provided"):
                PubSubClient()

    @patch("src.clients.pubsub_client.pubsub_v1.PublisherClient")
    @patch("src.clients.pubsub_client.pubsub_v1.SubscriberClient")
    def test_publish_message_success(self, mock_subscriber, mock_publisher, sample_message_data):
        """Test successful message publishing."""
        # Setup mocks
        mock_pub_client = MagicMock()
        mock_sub_client = MagicMock()
        mock_publisher.return_value = mock_pub_client
        mock_subscriber.return_value = mock_sub_client

        mock_future = MagicMock()
        mock_future.result.return_value = "test-message-id"
        mock_pub_client.publish.return_value = mock_future

        # Create client and test
        client = PubSubClient("test-project")
        message_id = client.publish_message("test-topic", sample_message_data)

        assert message_id == "test-message-id"
        mock_pub_client.topic_path.assert_called_once_with("test-project", "test-topic")
        mock_pub_client.publish.assert_called_once()

    @patch("src.clients.pubsub_client.pubsub_v1.PublisherClient")
    @patch("src.clients.pubsub_client.pubsub_v1.SubscriberClient")
    def test_publish_message_with_attributes(self, mock_subscriber, mock_publisher, sample_message_data):
        """Test message publishing with attributes."""
        # Setup mocks
        mock_pub_client = MagicMock()
        mock_sub_client = MagicMock()
        mock_publisher.return_value = mock_pub_client
        mock_subscriber.return_value = mock_sub_client

        mock_future = MagicMock()
        mock_future.result.return_value = "test-message-id"
        mock_pub_client.publish.return_value = mock_future

        # Create client and test
        client = PubSubClient("test-project")
        attributes = {"priority": "high", "source": "test"}
        message_id = client.publish_message("test-topic", sample_message_data, attributes)

        assert message_id == "test-message-id"
        mock_pub_client.publish.assert_called_once()

    @patch("src.clients.pubsub_client.pubsub_v1.PublisherClient")
    @patch("src.clients.pubsub_client.pubsub_v1.SubscriberClient")
    def test_publish_message_failure(self, mock_subscriber, mock_publisher, sample_message_data):
        """Test message publishing failure."""
        # Setup mocks
        mock_pub_client = MagicMock()
        mock_sub_client = MagicMock()
        mock_publisher.return_value = mock_pub_client
        mock_subscriber.return_value = mock_sub_client

        mock_pub_client.publish.side_effect = Exception("Publishing failed")

        # Create client and test
        client = PubSubClient("test-project")
        with pytest.raises(Exception, match="Publishing failed"):
            client.publish_message("test-topic", sample_message_data)

    @patch("src.clients.pubsub_client.pubsub_v1.PublisherClient")
    @patch("src.clients.pubsub_client.pubsub_v1.SubscriberClient")
    @patch.dict("os.environ", {"JOURNAL_INDEXING_TOPIC": "journal-indexing"})
    def test_publish_journal_indexing(self, mock_subscriber, mock_publisher, sample_message_data):
        """Test publishing journal indexing message."""
        # Setup mocks
        mock_pub_client = MagicMock()
        mock_sub_client = MagicMock()
        mock_publisher.return_value = mock_pub_client
        mock_subscriber.return_value = mock_sub_client

        mock_future = MagicMock()
        mock_future.result.return_value = "test-message-id"
        mock_pub_client.publish.return_value = mock_future

        # Create client and test
        client = PubSubClient("test-project")
        message_id = client.publish_journal_indexing(
            entry_id=sample_message_data["entry_id"],
            user_id=sample_message_data["user_id"],
            tradition=sample_message_data["tradition"],
        )

        assert message_id == "test-message-id"
        mock_pub_client.publish.assert_called_once()

    @patch("src.clients.pubsub_client.pubsub_v1.PublisherClient")
    @patch("src.clients.pubsub_client.pubsub_v1.SubscriberClient")
    @patch.dict("os.environ", {"JOURNAL_BATCH_INDEXING_TOPIC": "journal-batch-indexing"})
    def test_publish_journal_batch_indexing(self, mock_subscriber, mock_publisher):
        """Test publishing batch journal indexing message."""
        # Setup mocks
        mock_pub_client = MagicMock()
        mock_sub_client = MagicMock()
        mock_publisher.return_value = mock_pub_client
        mock_subscriber.return_value = mock_sub_client

        mock_future = MagicMock()
        mock_future.result.return_value = "test-message-id"
        mock_pub_client.publish.return_value = mock_future

        # Create client and test
        client = PubSubClient("test-project")
        entry_ids = ["entry1", "entry2", "entry3"]
        message_id = client.publish_journal_batch_indexing(
            entry_ids=entry_ids,
            user_id="test-user",
            tradition="canon-default",
        )

        assert message_id == "test-message-id"
        mock_pub_client.publish.assert_called_once()

    @patch("src.clients.pubsub_client.pubsub_v1.PublisherClient")
    @patch("src.clients.pubsub_client.pubsub_v1.SubscriberClient")
    @patch.dict("os.environ", {"JOURNAL_REINDEX_TOPIC": "journal-reindex"})
    def test_publish_journal_reindex(self, mock_subscriber, mock_publisher):
        """Test publishing journal reindex message."""
        # Setup mocks
        mock_pub_client = MagicMock()
        mock_sub_client = MagicMock()
        mock_publisher.return_value = mock_pub_client
        mock_subscriber.return_value = mock_sub_client

        mock_future = MagicMock()
        mock_future.result.return_value = "test-message-id"
        mock_pub_client.publish.return_value = mock_future

        # Create client and test
        client = PubSubClient("test-project")
        message_id = client.publish_journal_reindex(tradition="canon-default")

        assert message_id == "test-message-id"
        mock_pub_client.publish.assert_called_once()

    @patch("src.clients.pubsub_client.pubsub_v1.PublisherClient")
    @patch("src.clients.pubsub_client.pubsub_v1.SubscriberClient")
    @patch.dict("os.environ", {"TRADITION_REBUILD_TOPIC": "tradition-rebuild"})
    def test_publish_tradition_rebuild(self, mock_subscriber, mock_publisher):
        """Test publishing tradition rebuild message."""
        # Setup mocks
        mock_pub_client = MagicMock()
        mock_sub_client = MagicMock()
        mock_publisher.return_value = mock_pub_client
        mock_subscriber.return_value = mock_sub_client

        mock_future = MagicMock()
        mock_future.result.return_value = "test-message-id"
        mock_pub_client.publish.return_value = mock_future

        # Create client and test
        client = PubSubClient("test-project")
        message_id = client.publish_tradition_rebuild(tradition="test-tradition")

        assert message_id == "test-message-id"
        mock_pub_client.publish.assert_called_once()

    @patch("src.clients.pubsub_client.pubsub_v1.PublisherClient")
    @patch("src.clients.pubsub_client.pubsub_v1.SubscriberClient")
    @patch.dict("os.environ", {"HEALTH_CHECK_TOPIC": "health-check"})
    def test_publish_health_check(self, mock_subscriber, mock_publisher):
        """Test publishing health check message."""
        # Setup mocks
        mock_pub_client = MagicMock()
        mock_sub_client = MagicMock()
        mock_publisher.return_value = mock_pub_client
        mock_subscriber.return_value = mock_sub_client

        mock_future = MagicMock()
        mock_future.result.return_value = "test-message-id"
        mock_pub_client.publish.return_value = mock_future

        # Create client and test
        client = PubSubClient("test-project")
        message_id = client.publish_health_check()

        assert message_id == "test-message-id"
        mock_pub_client.publish.assert_called_once()


class TestPubSubMessage:
    """Test suite for PubSubMessage model."""

    def test_pubsub_message_creation(self, sample_message_data, sample_attributes):
        """Test PubSubMessage creation."""
        message = PubSubMessage(data=sample_message_data, attributes=sample_attributes)

        assert message.data == sample_message_data
        assert message.attributes == sample_attributes

    def test_pubsub_message_creation_no_attributes(self, sample_message_data):
        """Test PubSubMessage creation without attributes."""
        message = PubSubMessage(data=sample_message_data)

        assert message.data == sample_message_data
        assert message.attributes is None


class TestParsePushMessage:
    """Test suite for push message parsing."""

    def test_parse_push_message_success(self, sample_message_data, sample_attributes):
        """Test successful push message parsing."""
        # Create JSON data
        json_data = json.dumps(sample_message_data).encode("utf-8")

        # Parse message
        message = parse_push_message(json_data, sample_attributes)

        assert isinstance(message, PubSubMessage)
        assert message.data == sample_message_data
        assert message.attributes == sample_attributes

    def test_parse_push_message_invalid_json(self, sample_attributes):
        """Test push message parsing with invalid JSON."""
        invalid_data = b"invalid json data"

        with pytest.raises(ValueError, match="Invalid message format"):
            parse_push_message(invalid_data, sample_attributes)

    def test_parse_push_message_invalid_encoding(self, sample_message_data, sample_attributes):
        """Test push message parsing with invalid encoding."""
        # Create data with invalid encoding
        invalid_data = b"\xff\xfe\xfd"  # Invalid UTF-8

        with pytest.raises(ValueError, match="Invalid message format"):
            parse_push_message(invalid_data, sample_attributes)


class TestGetPubSubClient:
    """Test suite for get_pubsub_client factory function."""

    @patch("src.clients.pubsub_client.PubSubClient")
    def test_get_pubsub_client_singleton(self, mock_client_class):
        """Test that get_pubsub_client returns the same instance."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        client1 = get_pubsub_client()
        client2 = get_pubsub_client()

        assert client1 is client2
        mock_client_class.assert_called_once() 