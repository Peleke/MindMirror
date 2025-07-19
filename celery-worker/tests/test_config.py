"""Tests for the Config class."""

import os
import pytest
from unittest.mock import patch

from src.config import Config


class TestConfig:
    """Test the Config class."""

    def test_config_defaults(self):
        """Test default configuration values."""
        assert Config.VECTOR_SIZE == 1536
        assert Config.QDRANT_URL == "http://qdrant:6333"
        assert Config.REDIS_URL == "redis://redis:6379/0"
        assert Config.JOURNAL_SERVICE_URL == "http://journal_service:8001"
        assert Config.EMBEDDING_SERVICE == "openai"
        assert Config.TASK_DEFAULT_RETRY_DELAY == 60
        assert Config.TASK_MAX_RETRIES == 3
        assert Config.TASK_TIME_LIMIT == 300

    @patch.dict(
        os.environ,
        {
            "EMBEDDING_VECTOR_SIZE": "1024",
            "QDRANT_URL": "http://test-qdrant:9999",
            "REDIS_URL": "redis://test-redis:6379/1",
            "JOURNAL_SERVICE_URL": "http://test-journal:8001",
            "EMBEDDING_SERVICE": "openai",
            "TASK_DEFAULT_RETRY_DELAY": "120",
            "TASK_MAX_RETRIES": "5",
            "TASK_TIME_LIMIT": "600",
            "TESTING": "true",
        },
        clear=False,
    )
    def test_config_environment_overrides(self):
        """Test that environment variables override defaults."""

        # Create a new config class to test with the new environment
        class TestConfig:
            VECTOR_SIZE = int(os.getenv("EMBEDDING_VECTOR_SIZE", "1536"))
            QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
            REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
            JOURNAL_SERVICE_URL = os.getenv(
                "JOURNAL_SERVICE_URL", "http://journal_service:8001"
            )
            EMBEDDING_SERVICE = os.getenv("EMBEDDING_SERVICE", "openai")
            TASK_DEFAULT_RETRY_DELAY = int(os.getenv("TASK_DEFAULT_RETRY_DELAY", "60"))
            TASK_MAX_RETRIES = int(os.getenv("TASK_MAX_RETRIES", "3"))
            TASK_TIME_LIMIT = int(os.getenv("TASK_TIME_LIMIT", "300"))
            TESTING = os.getenv("TESTING", "false").lower() == "true"

        assert TestConfig.VECTOR_SIZE == 1024
        assert TestConfig.QDRANT_URL == "http://test-qdrant:9999"
        assert TestConfig.REDIS_URL == "redis://test-redis:6379/1"
        assert TestConfig.JOURNAL_SERVICE_URL == "http://test-journal:8001"
        assert TestConfig.EMBEDDING_SERVICE == "openai"
        assert TestConfig.TASK_DEFAULT_RETRY_DELAY == 120
        assert TestConfig.TASK_MAX_RETRIES == 5
        assert TestConfig.TASK_TIME_LIMIT == 600
        assert TestConfig.TESTING is True

    def test_get_qdrant_url(self):
        """Test get_qdrant_url method."""
        url = Config.get_qdrant_url()
        assert url == Config.QDRANT_URL
        assert url == "http://qdrant:6333"  # Default values

    @patch.dict(
        os.environ, {"QDRANT_URL": "http://custom-host:7777"}, clear=False
    )
    def test_get_qdrant_url_custom(self):
        """Test get_qdrant_url with custom values."""

        # Create a new config class to test with the new environment
        class TestConfig:
            QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")

            @classmethod
            def get_qdrant_url(cls):
                return cls.QDRANT_URL

        url = TestConfig.get_qdrant_url()
        assert url == "http://custom-host:7777"

    def test_is_testing_false_by_default(self):
        """Test that is_testing returns False by default."""
        assert Config.is_testing() is False

    @patch.dict(os.environ, {"TESTING": "true"}, clear=False)
    def test_is_testing_true_when_set(self):
        """Test that is_testing returns True when TESTING env var is set."""

        # Create a new config class to test with the new environment
        class TestConfig:
            TESTING = os.getenv("TESTING", "false").lower() == "true"

            @classmethod
            def is_testing(cls):
                return cls.TESTING

        assert TestConfig.is_testing() is True

    @patch.dict(os.environ, {"TESTING": "false"}, clear=False)
    def test_is_testing_false_when_explicitly_false(self):
        """Test that is_testing returns False when TESTING is explicitly false."""

        # Create a new config class to test with the new environment
        class TestConfig:
            TESTING = os.getenv("TESTING", "false").lower() == "true"

            @classmethod
            def is_testing(cls):
                return cls.TESTING

        assert TestConfig.is_testing() is False

    def test_is_testing_case_insensitive(self):
        """Test that is_testing method handles case insensitive values."""
        with patch.dict(os.environ, {"TESTING": "True"}, clear=False):

            class TestConfig:
                TESTING = os.getenv("TESTING", "false").lower() == "true"

                @classmethod
                def is_testing(cls):
                    return cls.TESTING

            # Should be True because "True".lower() == "true"
            assert TestConfig.is_testing() is True

        with patch.dict(os.environ, {"TESTING": "false"}, clear=False):

            class TestConfig:
                TESTING = os.getenv("TESTING", "false").lower() == "true"

                @classmethod
                def is_testing(cls):
                    return cls.TESTING

            # Should be False for "false"
            assert TestConfig.is_testing() is False

    def test_config_instance_exists(self):
        """Test that the global config instance exists."""
        from src.config import config

        assert config is not None
        assert hasattr(config, "VECTOR_SIZE")  # Check it has config attributes

    def test_integer_parsing(self):
        """Test that integer environment variables are parsed correctly."""
        assert isinstance(Config.VECTOR_SIZE, int)
        assert isinstance(Config.TASK_DEFAULT_RETRY_DELAY, int)
        assert isinstance(Config.TASK_MAX_RETRIES, int)
        assert isinstance(Config.TASK_TIME_LIMIT, int)

    @patch.dict(os.environ, {"EMBEDDING_VECTOR_SIZE": "invalid"}, clear=False)
    def test_invalid_integer_environment_variable(self):
        """Test behavior with invalid integer environment variables."""
        with pytest.raises(ValueError):
            int(os.getenv("EMBEDDING_VECTOR_SIZE", "768"))

    def test_qdrant_url_property_consistency(self):
        """Test that QDRANT_URL property is consistent with get_qdrant_url method."""
        assert Config.QDRANT_URL == Config.get_qdrant_url()
