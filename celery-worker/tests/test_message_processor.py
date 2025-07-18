"""
Tests for message processing utilities.

These tests verify the retry logic, error handling, and message processing
utilities used by Pub/Sub message handlers.
"""

import time
import pytest
from unittest.mock import MagicMock, patch

from src.utils.message_processor import (
    retry_on_failure,
    MessageProcessor,
    should_retry_message,
    log_message_processing,
)


class TestRetryOnFailure:
    """Test suite for retry_on_failure decorator."""

    def test_retry_on_failure_success_first_try(self):
        """Test that function succeeds on first try."""
        call_count = 0

        @retry_on_failure(max_retries=3)
        def test_function():
            nonlocal call_count
            call_count += 1
            return "success"

        result = test_function()

        assert result == "success"
        assert call_count == 1

    def test_retry_on_failure_succeeds_after_retries(self):
        """Test that function succeeds after some retries."""
        call_count = 0

        @retry_on_failure(max_retries=3, base_delay=0.01)
        def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"

        result = test_function()

        assert result == "success"
        assert call_count == 3

    def test_retry_on_failure_exceeds_max_retries(self):
        """Test that function raises exception after max retries."""
        call_count = 0

        @retry_on_failure(max_retries=2, base_delay=0.01)
        def test_function():
            nonlocal call_count
            call_count += 1
            raise Exception("Persistent failure")

        with pytest.raises(Exception, match="Persistent failure"):
            test_function()

        assert call_count == 3  # Initial call + 2 retries

    def test_retry_on_failure_exponential_backoff(self):
        """Test that retry delay increases exponentially."""
        call_count = 0
        delays = []

        @retry_on_failure(max_retries=3, base_delay=0.1, backoff_factor=2.0)
        def test_function():
            nonlocal call_count
            call_count += 1
            delays.append(time.time())
            raise Exception("Failure")

        start_time = time.time()
        with pytest.raises(Exception):
            test_function()

        # Check that delays are increasing
        assert len(delays) == 4  # Initial call + 3 retries
        assert delays[1] - delays[0] >= 0.1  # First retry delay
        assert delays[2] - delays[1] >= 0.2  # Second retry delay
        assert delays[3] - delays[2] >= 0.4  # Third retry delay

    def test_retry_on_failure_respects_max_delay(self):
        """Test that retry delay doesn't exceed max_delay."""
        call_count = 0

        @retry_on_failure(max_retries=3, base_delay=0.1, max_delay=0.15, backoff_factor=2.0)
        def test_function():
            nonlocal call_count
            call_count += 1
            raise Exception("Failure")

        start_time = time.time()
        with pytest.raises(Exception):
            test_function()

        # The delay should be capped at 0.15 seconds
        elapsed_time = time.time() - start_time
        assert elapsed_time < 0.5  # Should be much less than if max_delay wasn't respected

    def test_retry_on_failure_specific_exceptions(self):
        """Test that retry only happens for specific exceptions."""
        call_count = 0

        @retry_on_failure(max_retries=3, exceptions=(ValueError,))
        def test_function():
            nonlocal call_count
            call_count += 1
            raise TypeError("Wrong exception type")

        with pytest.raises(TypeError):
            test_function()

        assert call_count == 1  # Should not retry for TypeError


class TestMessageProcessor:
    """Test suite for MessageProcessor class."""

    def test_message_processor_initialization(self):
        """Test that MessageProcessor initializes correctly."""
        processor = MessageProcessor(max_retries=5)
        assert processor.max_retries == 5

    def test_process_message_success(self):
        """Test successful message processing."""
        processor = MessageProcessor(max_retries=3)
        message_data = {"task_type": "test_task", "message_id": "test-123"}

        def test_processor_func(arg1, arg2):
            return f"processed {arg1} {arg2}"

        result = processor.process_message(
            message_data, test_processor_func, "value1", "value2"
        )

        assert result["status"] == "success"
        assert result["result"] == "processed value1 value2"
        assert result["task_type"] == "test_task"
        assert result["message_id"] == "test-123"
        assert "processing_time" in result

    def test_process_message_failure(self):
        """Test failed message processing."""
        processor = MessageProcessor(max_retries=2)
        message_data = {"task_type": "test_task", "message_id": "test-123"}

        def test_processor_func():
            raise Exception("Processing failed")

        result = processor.process_message(message_data, test_processor_func)

        assert result["status"] == "error"
        assert result["error"] == "Processing failed"
        assert result["task_type"] == "test_task"
        assert result["message_id"] == "test-123"
        assert result["retry_count"] == 2
        assert "processing_time" in result

    def test_process_message_with_kwargs(self):
        """Test message processing with keyword arguments."""
        processor = MessageProcessor(max_retries=3)
        message_data = {"task_type": "test_task"}

        def test_processor_func(name, age=25):
            return f"Hello {name}, age {age}"

        result = processor.process_message(
            message_data, test_processor_func, "Alice", age=30
        )

        assert result["status"] == "success"
        assert result["result"] == "Hello Alice, age 30"


class TestShouldRetryMessage:
    """Test suite for should_retry_message function."""

    def test_should_retry_message_max_retries_exceeded(self):
        """Test that message is not retried when max retries exceeded."""
        error = Exception("Test error")
        result = should_retry_message(error, retry_count=3, max_retries=3)
        assert result is False

    def test_should_retry_message_retry_count_under_limit(self):
        """Test that message is retried when retry count is under limit."""
        error = Exception("Test error")
        result = should_retry_message(error, retry_count=1, max_retries=3)
        assert result is True

    def test_should_retry_message_non_retryable_errors(self):
        """Test that non-retryable errors are not retried."""
        non_retryable_errors = [
            ValueError("Invalid value"),
            TypeError("Wrong type"),
            AttributeError("No attribute"),
            KeyError("Missing key"),
            IndexError("Index out of range"),
        ]

        for error in non_retryable_errors:
            result = should_retry_message(error, retry_count=0, max_retries=3)
            assert result is False, f"Should not retry {type(error).__name__}"

    def test_should_retry_message_retryable_errors(self):
        """Test that retryable errors are retried."""
        retryable_errors = [
            Exception("Generic error"),
            RuntimeError("Runtime error"),
            ConnectionError("Connection failed"),
        ]

        for error in retryable_errors:
            result = should_retry_message(error, retry_count=0, max_retries=3)
            assert result is True, f"Should retry {type(error).__name__}"


class TestLogMessageProcessing:
    """Test suite for log_message_processing function."""

    @patch("src.utils.message_processor.logger")
    def test_log_message_processing_success(self, mock_logger):
        """Test logging for successful message processing."""
        message_data = {"task_type": "test_task", "message_id": "test-123"}
        result = {"status": "success", "result": "processed"}
        processing_time = 1.5

        log_message_processing(message_data, result, processing_time)

        mock_logger.info.assert_called_once()
        log_message = mock_logger.info.call_args[0][0]
        assert "Successfully processed test_task message test-123" in log_message
        assert "1.50s" in log_message

    @patch("src.utils.message_processor.logger")
    def test_log_message_processing_failure(self, mock_logger):
        """Test logging for failed message processing."""
        message_data = {"task_type": "test_task", "message_id": "test-123"}
        result = {"status": "error", "error": "Processing failed"}
        processing_time = 2.1

        log_message_processing(message_data, result, processing_time)

        mock_logger.error.assert_called_once()
        log_message = mock_logger.error.call_args[0][0]
        assert "Failed to process test_task message test-123" in log_message
        assert "2.10s" in log_message
        assert "Processing failed" in log_message

    @patch("src.utils.message_processor.logger")
    def test_log_message_processing_unknown_task_type(self, mock_logger):
        """Test logging when task type is unknown."""
        message_data = {"message_id": "test-123"}  # No task_type
        result = {"status": "success"}
        processing_time = 0.5

        log_message_processing(message_data, result, processing_time)

        mock_logger.info.assert_called_once()
        log_message = mock_logger.info.call_args[0][0]
        assert "Successfully processed unknown message test-123" in log_message

    @patch("src.utils.message_processor.logger")
    def test_log_message_processing_unknown_message_id(self, mock_logger):
        """Test logging when message ID is unknown."""
        message_data = {"task_type": "test_task"}  # No message_id
        result = {"status": "error", "error": "Failed"}
        processing_time = 1.0

        log_message_processing(message_data, result, processing_time)

        mock_logger.error.assert_called_once()
        log_message = mock_logger.error.call_args[0][0]
        assert "Failed to process test_task message unknown" in log_message 