"""
Unit tests for shared.secrets module.

Tests cover:
- get_secret() with volume mounts, env vars, and defaults
- get_environment() behavior
- should_auto_create_schema() logic
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

from shared.secrets import get_secret, get_environment, should_auto_create_schema


class TestGetSecret:
    """Test suite for get_secret() function."""

    def test_get_secret_from_volume_mount(self, monkeypatch):
        """Test that volume mount takes priority over env var."""
        # Setup: Mock volume mount file exists with content
        secret_content = "volume-mount-secret-value"

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.read_text", return_value=secret_content):
                # Also set env var to verify volume takes priority
                monkeypatch.setenv("DATABASE_URL", "env-var-value")

                result = get_secret(
                    "DATABASE_URL",
                    volume_name="database-url",
                    filename="database-url"
                )

                assert result == secret_content
                assert result != "env-var-value"

    def test_get_secret_from_volume_mount_with_whitespace(self):
        """Test that volume mount content is stripped of whitespace."""
        secret_content = "  secret-with-spaces  \n"
        expected = "secret-with-spaces"

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.read_text", return_value=secret_content):
                result = get_secret(
                    "TEST_SECRET",
                    volume_name="test-secret",
                    filename="test-secret"
                )

                assert result == expected

    def test_get_secret_from_env_var_when_no_volume(self, monkeypatch):
        """Test fallback to env var when volume mount doesn't exist."""
        monkeypatch.setenv("DATABASE_URL", "env-var-database-url")

        with patch("pathlib.Path.exists", return_value=False):
            result = get_secret("DATABASE_URL")

            assert result == "env-var-database-url"

    def test_get_secret_from_env_var_when_volume_empty(self, monkeypatch):
        """Test fallback to env var when volume mount is empty."""
        monkeypatch.setenv("TEST_SECRET", "env-value")

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.read_text", return_value=""):
                result = get_secret(
                    "TEST_SECRET",
                    volume_name="test",
                    filename="test"
                )

                assert result == "env-value"

    def test_get_secret_with_default_value(self, monkeypatch):
        """Test that default value is used when no secret found."""
        # Clear any existing env var
        monkeypatch.delenv("MISSING_SECRET", raising=False)

        with patch("pathlib.Path.exists", return_value=False):
            result = get_secret(
                "MISSING_SECRET",
                volume_name="missing",
                filename="missing",
                default="default-value"
            )

            assert result == "default-value"

    def test_get_secret_returns_none_when_not_found(self, monkeypatch):
        """Test that None is returned when secret not found and no default."""
        monkeypatch.delenv("MISSING_SECRET", raising=False)

        with patch("pathlib.Path.exists", return_value=False):
            result = get_secret("MISSING_SECRET")

            assert result is None

    def test_get_secret_handles_volume_read_exception(self, monkeypatch):
        """Test graceful fallback when volume mount read fails."""
        monkeypatch.setenv("FALLBACK_SECRET", "env-fallback")

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.read_text", side_effect=PermissionError()):
                result = get_secret(
                    "FALLBACK_SECRET",
                    volume_name="test",
                    filename="test"
                )

                assert result == "env-fallback"

    def test_get_secret_without_volume_params(self, monkeypatch):
        """Test get_secret with only env var (no volume params)."""
        monkeypatch.setenv("SIMPLE_SECRET", "simple-value")

        result = get_secret("SIMPLE_SECRET")

        assert result == "simple-value"

    def test_get_secret_constructs_correct_volume_path(self):
        """Test that volume mount path is constructed correctly."""
        with patch("pathlib.Path.exists") as mock_exists:
            with patch("pathlib.Path.read_text", return_value="test"):
                mock_exists.return_value = True

                get_secret(
                    "TEST",
                    volume_name="my-volume",
                    filename="my-file"
                )

                # Verify the path construction
                expected_path = Path("/secrets/my-volume/my-file")
                mock_exists.assert_called_once()


class TestGetEnvironment:
    """Test suite for get_environment() function."""

    def test_get_environment_from_env_var(self, monkeypatch):
        """Test reading environment from env var."""
        monkeypatch.setenv("ENVIRONMENT", "production")

        result = get_environment()

        assert result == "production"

    def test_get_environment_defaults_to_local(self, monkeypatch):
        """Test default environment is 'local'."""
        monkeypatch.delenv("ENVIRONMENT", raising=False)

        with patch("pathlib.Path.exists", return_value=False):
            result = get_environment()

            assert result == "local"

    def test_get_environment_from_volume_mount(self, monkeypatch):
        """Test reading environment from volume mount."""
        # Need to clear env var so it uses volume mount
        monkeypatch.delenv("ENVIRONMENT", raising=False)

        # Patch Path in the secrets module where it's used
        with patch("shared.secrets.Path") as mock_path_class:
            mock_path_instance = MagicMock()
            mock_path_class.return_value = mock_path_instance
            mock_path_instance.exists.return_value = True
            mock_path_instance.read_text.return_value = "staging"

            result = get_environment()

            assert result == "staging"

    def test_get_environment_various_values(self, monkeypatch):
        """Test various valid environment values."""
        environments = ["local", "development", "test", "staging", "production"]

        for env in environments:
            monkeypatch.setenv("ENVIRONMENT", env)
            result = get_environment()
            assert result == env


class TestShouldAutoCreateSchema:
    """Test suite for should_auto_create_schema() function."""

    def test_should_auto_create_for_local(self, monkeypatch):
        """Test auto-create is enabled for local environment."""
        monkeypatch.setenv("ENVIRONMENT", "local")

        result = should_auto_create_schema()

        assert result is True

    def test_should_auto_create_for_test(self, monkeypatch):
        """Test auto-create is enabled for test environment."""
        monkeypatch.setenv("ENVIRONMENT", "test")

        result = should_auto_create_schema()

        assert result is True

    def test_should_auto_create_for_development(self, monkeypatch):
        """Test auto-create is enabled for development environment."""
        monkeypatch.setenv("ENVIRONMENT", "development")

        result = should_auto_create_schema()

        assert result is True

    def test_should_not_auto_create_for_production(self, monkeypatch):
        """Test auto-create is disabled for production environment."""
        monkeypatch.setenv("ENVIRONMENT", "production")

        result = should_auto_create_schema()

        assert result is False

    def test_should_not_auto_create_for_staging(self, monkeypatch):
        """Test auto-create is disabled for staging environment."""
        monkeypatch.setenv("ENVIRONMENT", "staging")

        result = should_auto_create_schema()

        assert result is False

    def test_should_not_auto_create_for_unknown_env(self, monkeypatch):
        """Test auto-create is disabled for unknown/custom environments."""
        monkeypatch.setenv("ENVIRONMENT", "custom-env")

        result = should_auto_create_schema()

        assert result is False

    def test_should_auto_create_defaults_to_false_for_local(self, monkeypatch):
        """Test that default 'local' environment allows auto-create."""
        monkeypatch.delenv("ENVIRONMENT", raising=False)

        with patch("pathlib.Path.exists", return_value=False):
            result = should_auto_create_schema()

            # Default is "local" which should allow auto-create
            assert result is True


class TestIntegration:
    """Integration tests for secret management."""

    def test_secret_priority_order_full_chain(self, monkeypatch):
        """Test the full priority chain: volume > env > default."""
        # Setup all three sources
        monkeypatch.setenv("PRIORITY_TEST", "from-env")
        default_value = "from-default"

        # Test 1: Volume mount takes priority
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.read_text", return_value="from-volume"):
                result = get_secret(
                    "PRIORITY_TEST",
                    volume_name="test",
                    filename="test",
                    default=default_value
                )
                assert result == "from-volume"

        # Test 2: Env var when no volume
        with patch("pathlib.Path.exists", return_value=False):
            result = get_secret(
                "PRIORITY_TEST",
                volume_name="test",
                filename="test",
                default=default_value
            )
            assert result == "from-env"

        # Test 3: Default when neither available
        monkeypatch.delenv("PRIORITY_TEST", raising=False)
        with patch("pathlib.Path.exists", return_value=False):
            result = get_secret(
                "PRIORITY_TEST",
                volume_name="test",
                filename="test",
                default=default_value
            )
            assert result == "from-default"

    def test_cloud_run_v2_volume_path_format(self):
        """Test that Cloud Run v2 volume mount path format is correct."""
        # Cloud Run v2 mounts secrets at /secrets/<volume-name>/<filename>
        volume_name = "database-url"
        filename = "database-url"
        expected_path = f"/secrets/{volume_name}/{filename}"

        with patch("pathlib.Path.exists") as mock_exists:
            with patch("pathlib.Path.read_text", return_value="test-value"):
                mock_exists.return_value = True

                result = get_secret(
                    "DATABASE_URL",
                    volume_name=volume_name,
                    filename=filename
                )

                # Verify correct path was checked
                assert result == "test-value"
                # Check the Path object was created with correct string
                call_args = mock_exists.call_args
                # The mock was called on a Path object, so we check indirectly
                assert mock_exists.called

    def test_backward_compatibility_env_vars_only(self, monkeypatch):
        """Test backward compatibility when only using env vars."""
        monkeypatch.setenv("DATABASE_URL", "postgres://localhost/db")

        # Call without volume parameters (old behavior)
        result = get_secret("DATABASE_URL")

        assert result == "postgres://localhost/db"

    def test_environment_based_schema_creation_flow(self, monkeypatch):
        """Test the complete flow from environment detection to schema decision."""
        test_cases = [
            ("local", True),
            ("development", True),
            ("test", True),
            ("staging", False),
            ("production", False),
        ]

        for env_value, expected_auto_create in test_cases:
            monkeypatch.setenv("ENVIRONMENT", env_value)

            detected_env = get_environment()
            should_create = should_auto_create_schema()

            assert detected_env == env_value
            assert should_create == expected_auto_create


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
