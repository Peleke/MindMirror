"""
Tests for GCS prompt store.

These tests verify that the GCSPromptStore correctly handles
GCS-based storage with proper error handling and edge cases.
"""

from datetime import datetime
from typing import List
from unittest.mock import MagicMock, Mock, patch

import pytest
import yaml

from agent_service.llms.prompts.exceptions import (
    PromptNotFoundError,
    PromptStorageError,
)
from agent_service.llms.prompts.models import PromptInfo, StorageConfig
from agent_service.llms.prompts.stores.gcs import GCSPromptStore
from agent_service.llms.prompts.stores.loaders.gcs import GCSStorageLoader


class TestGCSPromptStore:
    """Test GCSPromptStore implementation."""

    @pytest.fixture
    def mock_gcs_loader(self):
        """Create a mock GCS storage loader."""
        return Mock(spec=GCSStorageLoader)

    @pytest.fixture
    def store(self, mock_gcs_loader):
        """Create a GCSPromptStore instance."""
        return GCSPromptStore(loader=mock_gcs_loader)

    @pytest.fixture
    def sample_prompt(self):
        """Create a sample prompt."""
        return PromptInfo(
            name="test_prompt",
            version="1.0",
            content="Hello {{name}}!",
            metadata={"description": "A test prompt"},
            variables=["name"],
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

    def test_store_initialization(self, mock_gcs_loader):
        """Test store initialization."""
        store = GCSPromptStore(loader=mock_gcs_loader)
        assert store.loader == mock_gcs_loader

    def test_save_prompt_basic(self, store, sample_prompt, mock_gcs_loader):
        """Test basic prompt saving."""
        store.save_prompt(sample_prompt)

        # Verify the loader was called with correct path and content
        expected_path = f"prompts/{sample_prompt.name}/{sample_prompt.version}.yaml"
        mock_gcs_loader.write_file.assert_called_once()

        call_args = mock_gcs_loader.write_file.call_args
        assert call_args[0][0] == expected_path

        # Verify the content is YAML
        content = call_args[0][1]
        data = yaml.safe_load(content)
        assert data["name"] == "test_prompt"
        assert data["version"] == "1.0"
        assert data["content"] == "Hello {{name}}!"

    def test_save_prompt_overwrites_existing(
        self, store, sample_prompt, mock_gcs_loader
    ):
        """Test that saving overwrites existing prompt."""
        # Save initial prompt
        store.save_prompt(sample_prompt)

        # Modify and save again
        updated_prompt = PromptInfo(
            name="test_prompt",
            version="1.0",
            content="Updated content!",
            metadata={"description": "Updated prompt"},
            variables=["name"],
            created_at=sample_prompt.created_at,
            updated_at=datetime.utcnow().isoformat(),
        )

        store.save_prompt(updated_prompt)

        # Should have been called twice
        assert mock_gcs_loader.write_file.call_count == 2

        # Verify the second call has updated content
        second_call = mock_gcs_loader.write_file.call_args_list[1]
        content = yaml.safe_load(second_call[0][1])
        assert content["content"] == "Updated content!"

    def test_save_prompt_multiple_versions(self, store, sample_prompt, mock_gcs_loader):
        """Test saving multiple versions of the same prompt."""
        # Save version 1.0
        store.save_prompt(sample_prompt)

        # Save version 1.1
        prompt_v2 = PromptInfo(
            name="test_prompt",
            version="1.1",
            content="Hello {{name}}! Version 1.1",
            metadata={"description": "Updated test prompt"},
            variables=["name"],
            created_at=sample_prompt.created_at,
            updated_at=datetime.utcnow().isoformat(),
        )
        store.save_prompt(prompt_v2)

        # Should have been called twice with different paths
        assert mock_gcs_loader.write_file.call_count == 2

        calls = mock_gcs_loader.write_file.call_args_list
        assert calls[0][0][0] == "prompts/test_prompt/1.0.yaml"
        assert calls[1][0][0] == "prompts/test_prompt/1.1.yaml"

    def test_get_prompt_basic(self, store, sample_prompt, mock_gcs_loader):
        """Test basic prompt retrieval."""
        # Mock the loader to return YAML content
        prompt_data = sample_prompt.to_dict()
        yaml_content = yaml.dump(prompt_data, default_flow_style=False)
        mock_gcs_loader.read_file.return_value = yaml_content

        retrieved_prompt = store.get_prompt("test_prompt", "1.0")

        assert retrieved_prompt.name == "test_prompt"
        assert retrieved_prompt.version == "1.0"
        assert retrieved_prompt.content == "Hello {{name}}!"

        # Verify the loader was called with correct path
        expected_path = "prompts/test_prompt/1.0.yaml"
        mock_gcs_loader.read_file.assert_called_once_with(expected_path)

    def test_get_prompt_not_found(self, store, mock_gcs_loader):
        """Test getting non-existent prompt."""
        mock_gcs_loader.read_file.side_effect = PromptStorageError("File not found")

        with pytest.raises(PromptNotFoundError):
            store.get_prompt("non_existent", "1.0")

    def test_get_prompt_corrupted_file(self, store, mock_gcs_loader):
        """Test handling corrupted prompt file."""
        mock_gcs_loader.read_file.return_value = "invalid yaml content"

        with pytest.raises(PromptStorageError):
            store.get_prompt("test_prompt", "1.0")

    def test_get_prompt_invalid_format(self, store, mock_gcs_loader):
        """Test handling invalid YAML format."""
        mock_gcs_loader.read_file.return_value = "not_a_dict: but_a_string"

        with pytest.raises(PromptStorageError):
            store.get_prompt("test_prompt", "1.0")

    def test_get_latest_version(self, store, mock_gcs_loader):
        """Test getting latest version of a prompt."""
        # Mock the loader to return list of files
        mock_gcs_loader.list_files.return_value = [
            "prompts/test_prompt/1.0.yaml",
            "prompts/test_prompt/1.1.yaml",
            "prompts/test_prompt/2.0.yaml",
        ]

        latest_version = store.get_latest_version("test_prompt")
        assert latest_version == "2.0"

        # Verify the loader was called with correct prefix
        mock_gcs_loader.list_files.assert_called_once_with("prompts/test_prompt/")

    def test_get_latest_version_not_found(self, store, mock_gcs_loader):
        """Test getting latest version of non-existent prompt."""
        mock_gcs_loader.list_files.return_value = []

        with pytest.raises(PromptNotFoundError):
            store.get_latest_version("non_existent")

    def test_get_prompt_versions(self, store, mock_gcs_loader):
        """Test getting all versions of a prompt."""
        # Mock the loader to return list of files
        mock_gcs_loader.list_files.return_value = [
            "prompts/test_prompt/1.0.yaml",
            "prompts/test_prompt/1.1.yaml",
            "prompts/test_prompt/2.0.yaml",
        ]

        versions = store.get_prompt_versions("test_prompt")
        assert "1.0" in versions
        assert "1.1" in versions
        assert "2.0" in versions
        assert len(versions) == 3

        # Verify versions are sorted
        assert versions == ["1.0", "1.1", "2.0"]

    def test_get_prompt_versions_not_found(self, store, mock_gcs_loader):
        """Test getting versions of non-existent prompt."""
        mock_gcs_loader.list_files.return_value = []

        with pytest.raises(PromptNotFoundError):
            store.get_prompt_versions("non_existent")

    def test_delete_prompt(self, store, mock_gcs_loader):
        """Test deleting a prompt."""
        store.delete_prompt("test_prompt", "1.0")

        # Verify the loader was called with correct path
        expected_path = "prompts/test_prompt/1.0.yaml"
        mock_gcs_loader.delete_file.assert_called_once_with(expected_path)

    def test_delete_prompt_not_found(self, store, mock_gcs_loader):
        """Test deleting non-existent prompt."""
        mock_gcs_loader.delete_file.side_effect = PromptStorageError("File not found")

        with pytest.raises(PromptNotFoundError):
            store.delete_prompt("non_existent", "1.0")

    def test_list_prompts_empty(self, store, mock_gcs_loader):
        """Test listing prompts when store is empty."""
        mock_gcs_loader.list_files.return_value = []

        prompts = store.list_prompts()
        assert len(prompts) == 0

        # Verify the loader was called with correct prefix
        mock_gcs_loader.list_files.assert_called_once_with("prompts/")

    def test_list_prompts_single(self, store, sample_prompt, mock_gcs_loader):
        """Test listing single prompt."""
        # Mock the loader to return list of files and content
        mock_gcs_loader.list_files.return_value = ["prompts/test_prompt/1.0.yaml"]

        prompt_data = sample_prompt.to_dict()
        yaml_content = yaml.dump(prompt_data, default_flow_style=False)
        mock_gcs_loader.read_file.return_value = yaml_content

        prompts = store.list_prompts()
        assert len(prompts) == 1
        assert prompts[0].name == "test_prompt"
        assert prompts[0].version == "1.0"

    def test_list_prompts_multiple(self, store, sample_prompt, mock_gcs_loader):
        """Test listing multiple prompts."""
        # Mock the loader to return list of files
        mock_gcs_loader.list_files.return_value = [
            "prompts/test_prompt/1.0.yaml",
            "prompts/another_prompt/1.0.yaml",
        ]

        # Mock read_file to return different content for each prompt
        def mock_read_file(path):
            if "test_prompt" in path:
                prompt_data = sample_prompt.to_dict()
            else:
                prompt_data = PromptInfo(
                    name="another_prompt",
                    version="1.0",
                    content="Another prompt",
                    metadata={},
                    variables=[],
                    created_at=datetime.utcnow().isoformat(),
                    updated_at=datetime.utcnow().isoformat(),
                ).to_dict()
            return yaml.dump(prompt_data, default_flow_style=False)

        mock_gcs_loader.read_file.side_effect = mock_read_file

        prompts = store.list_prompts()
        assert len(prompts) == 2

        names = [p.name for p in prompts]
        assert "test_prompt" in names
        assert "another_prompt" in names

    def test_list_prompts_with_multiple_versions(
        self, store, sample_prompt, mock_gcs_loader
    ):
        """Test listing prompts with multiple versions."""
        # Mock the loader to return list of files
        mock_gcs_loader.list_files.return_value = [
            "prompts/test_prompt/1.0.yaml",
            "prompts/test_prompt/1.1.yaml",
        ]

        # Mock read_file to return different content for different versions
        def mock_read_file(path):
            if "1.0.yaml" in path:
                prompt_data = sample_prompt.to_dict()
            elif "1.1.yaml" in path:
                # Create a different prompt for version 1.1
                prompt_v2 = PromptInfo(
                    name="test_prompt",
                    version="1.1",
                    content="Hello {{name}}! Version 1.1",
                    metadata={"description": "Updated test prompt"},
                    variables=["name"],
                    created_at=sample_prompt.created_at,
                    updated_at=datetime.utcnow().isoformat(),
                )
                prompt_data = prompt_v2.to_dict()
            else:
                prompt_data = sample_prompt.to_dict()
            return yaml.dump(prompt_data, default_flow_style=False)

        mock_gcs_loader.read_file.side_effect = mock_read_file

        prompts = store.list_prompts()
        assert len(prompts) == 2

        versions = [p.version for p in prompts if p.name == "test_prompt"]
        assert "1.0" in versions
        assert "1.1" in versions

    def test_exists(self, store, mock_gcs_loader):
        """Test checking if prompt exists."""
        mock_gcs_loader.exists.return_value = True

        assert store.exists("test_prompt", "1.0")

        # Verify the loader was called with correct path
        expected_path = "prompts/test_prompt/1.0.yaml"
        mock_gcs_loader.exists.assert_called_once_with(expected_path)

    def test_exists_false(self, store, mock_gcs_loader):
        """Test checking if prompt doesn't exist."""
        mock_gcs_loader.exists.return_value = False

        assert not store.exists("test_prompt", "1.0")

    def test_search_prompts(self, store, sample_prompt, mock_gcs_loader):
        """Test searching prompts."""
        # Mock the loader to return list of files and content
        mock_gcs_loader.list_files.return_value = ["prompts/test_prompt/1.0.yaml"]

        prompt_data = sample_prompt.to_dict()
        yaml_content = yaml.dump(prompt_data, default_flow_style=False)
        mock_gcs_loader.read_file.return_value = yaml_content

        # Search by name
        results = store.search_prompts("test_prompt")
        assert len(results) == 1
        assert results[0].name == "test_prompt"

        # Search by content
        results = store.search_prompts("Hello")
        assert len(results) == 1
        assert results[0].name == "test_prompt"

        # Search with no results
        results = store.search_prompts("non_existent")
        assert len(results) == 0

    def test_get_stats(self, store, mock_gcs_loader):
        """Test getting store statistics."""
        # Mock the loader to return stats
        mock_stats = {"total_files": 5, "total_size_bytes": 1024}
        mock_gcs_loader.get_stats.return_value = mock_stats

        # Mock list_files for stats calculation
        mock_gcs_loader.list_files.return_value = [
            "prompts/test_prompt/1.0.yaml",
            "prompts/test_prompt/1.1.yaml",
            "prompts/another_prompt/1.0.yaml",
        ]

        stats = store.get_stats()

        # Verify the loader was called
        mock_gcs_loader.get_stats.assert_called_once()

        # Verify stats are passed through
        assert stats.total_prompts == 2  # Two unique prompt names
        assert stats.total_versions == 5
        assert stats.storage_size_bytes == 1024

    def test_yaml_error_handling(self, store, sample_prompt, mock_gcs_loader):
        """Test handling YAML errors during save."""
        mock_gcs_loader.write_file.side_effect = Exception("YAML error")

        with pytest.raises(PromptStorageError):
            store.save_prompt(sample_prompt)

    def test_gcs_error_handling(self, store, mock_gcs_loader):
        """Test handling GCS-specific errors."""
        mock_gcs_loader.read_file.side_effect = Exception("GCS error")

        with pytest.raises(PromptStorageError):
            store.get_prompt("test_prompt", "1.0")

    def test_retry_logic(self, store, sample_prompt, mock_gcs_loader):
        """Test retry logic for transient failures."""
        # Mock the loader to fail once then succeed
        mock_gcs_loader.write_file.side_effect = [
            Exception("Transient error"),  # First call fails
            None,  # Second call succeeds
        ]

        # Should retry and succeed
        store.save_prompt(sample_prompt)

        assert mock_gcs_loader.write_file.call_count == 2

    def test_version_sorting(self, store, mock_gcs_loader):
        """Test that versions are sorted correctly."""
        # Mock the loader to return unsorted versions
        mock_gcs_loader.list_files.return_value = [
            "prompts/test_prompt/2.0.yaml",
            "prompts/test_prompt/1.0.yaml",
            "prompts/test_prompt/1.1.yaml",
        ]

        versions = store.get_prompt_versions("test_prompt")

        # Verify versions are sorted correctly
        assert versions == ["1.0", "1.1", "2.0"]

    def test_filename_sanitization(self, store, sample_prompt, mock_gcs_loader):
        """Test that filenames are properly sanitized."""
        # Test with a valid prompt name that contains characters that need sanitization
        # We'll use a valid name but test the sanitization in the path generation
        prompt = PromptInfo(
            name="test_prompt_with_chars",  # Valid name that will be sanitized to same
            version="1.0",
            content="Test content",
            metadata={},
            variables=[],
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        store.save_prompt(prompt)

        # Verify the loader was called with sanitized path
        call_args = mock_gcs_loader.write_file.call_args
        path = call_args[0][0]
        assert "test_prompt_with_chars" in path
        assert "1.0.yaml" in path

        # Test that the sanitization method works correctly
        # Create a prompt with a name that would need sanitization if it were allowed
        # Since PromptInfo validation prevents invalid names, we'll test the sanitization method directly
        sanitized_name = store._sanitize_filename("test/prompt\\with*chars?")
        assert sanitized_name == "test_prompt_with_chars"
