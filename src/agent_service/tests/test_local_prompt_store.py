"""
Tests for local prompt store.

These tests verify that the LocalPromptStore correctly handles
file-based storage with proper error handling and edge cases.
"""

import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest
import yaml

from agent_service.llms.prompts.exceptions import (
    PromptNotFoundError,
    PromptStorageError,
)
from agent_service.llms.prompts.models import PromptInfo, StoreType
from agent_service.llms.prompts.stores.local import LocalPromptStore


class TestLocalPromptStore:
    """Test LocalPromptStore implementation."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def store(self, temp_dir):
        """Create a LocalPromptStore instance."""
        return LocalPromptStore(base_path=temp_dir)

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

    def test_store_initialization(self, temp_dir):
        """Test store initialization."""
        store = LocalPromptStore(base_path=temp_dir)
        assert store.store_path == Path(temp_dir)
        assert store.store_path.exists()

    def test_store_initialization_creates_directory(self, temp_dir):
        """Test that store creates directory if it doesn't exist."""
        new_dir = os.path.join(temp_dir, "new_store")
        store = LocalPromptStore(base_path=new_dir)
        assert Path(new_dir).exists()

    def test_store_initialization_with_invalid_path(self):
        """Test store initialization with invalid path."""
        with pytest.raises(PromptStorageError):
            LocalPromptStore(base_path="/invalid/path/that/cannot/be/created")

    def test_save_prompt_basic(self, store, sample_prompt):
        """Test basic prompt saving."""
        store.save_prompt(sample_prompt)

        # Verify file was created
        prompt_file = store.store_path / "test_prompt" / "1.0.yaml"
        assert prompt_file.exists()

        # Verify content is correct
        with open(prompt_file, "r") as f:
            data = yaml.safe_load(f)
            assert data["name"] == "test_prompt"
            assert data["version"] == "1.0"
            assert data["content"] == "Hello {{name}}!"

    def test_save_prompt_creates_directory_structure(self, store, sample_prompt):
        """Test that saving creates proper directory structure."""
        store.save_prompt(sample_prompt)

        prompt_dir = store.store_path / "test_prompt"
        assert prompt_dir.exists()
        assert prompt_dir.is_dir()

        prompt_file = prompt_dir / "1.0.yaml"
        assert prompt_file.exists()

    def test_save_prompt_overwrites_existing(self, store, sample_prompt):
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

        # Verify content was updated
        prompt_file = store.store_path / "test_prompt" / "1.0.yaml"
        with open(prompt_file, "r") as f:
            data = yaml.safe_load(f)
            assert data["content"] == "Updated content!"

    def test_save_prompt_multiple_versions(self, store, sample_prompt):
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

        # Verify both files exist
        assert (store.store_path / "test_prompt" / "1.0.yaml").exists()
        assert (store.store_path / "test_prompt" / "1.1.yaml").exists()

    def test_save_prompt_with_special_characters(self, store):
        """Test saving prompt with special characters in name."""
        prompt = PromptInfo(
            name="test-prompt_with_underscores",
            version="1.0",
            content="Special content!",
            metadata={},
            variables=[],
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        store.save_prompt(prompt)

        # Verify file was created with correct name
        prompt_file = store.store_path / "test-prompt_with_underscores" / "1.0.yaml"
        assert prompt_file.exists()

    def test_get_prompt_basic(self, store, sample_prompt):
        """Test basic prompt retrieval."""
        store.save_prompt(sample_prompt)

        retrieved_prompt = store.get_prompt("test_prompt", "1.0")
        assert retrieved_prompt.name == "test_prompt"
        assert retrieved_prompt.version == "1.0"
        assert retrieved_prompt.content == "Hello {{name}}!"

    def test_get_prompt_not_found(self, store):
        """Test getting non-existent prompt."""
        with pytest.raises(PromptNotFoundError):
            store.get_prompt("non_existent", "1.0")

    def test_get_prompt_version_not_found(self, store, sample_prompt):
        """Test getting non-existent version."""
        store.save_prompt(sample_prompt)

        with pytest.raises(PromptNotFoundError):
            store.get_prompt("test_prompt", "2.0")

    def test_get_prompt_corrupted_file(self, store, sample_prompt):
        """Test handling corrupted prompt file."""
        store.save_prompt(sample_prompt)

        # Corrupt the file
        prompt_file = store.store_path / "test_prompt" / "1.0.yaml"
        with open(prompt_file, "w") as f:
            f.write("invalid yaml content")

        with pytest.raises(PromptStorageError):
            store.get_prompt("test_prompt", "1.0")

    def test_get_latest_version(self, store, sample_prompt):
        """Test getting latest version of a prompt."""
        # Save multiple versions
        store.save_prompt(sample_prompt)

        prompt_v2 = PromptInfo(
            name="test_prompt",
            version="1.1",
            content="Version 1.1",
            metadata={},
            variables=[],
            created_at=sample_prompt.created_at,
            updated_at=datetime.utcnow().isoformat(),
        )
        store.save_prompt(prompt_v2)

        prompt_v3 = PromptInfo(
            name="test_prompt",
            version="2.0",
            content="Version 2.0",
            metadata={},
            variables=[],
            created_at=sample_prompt.created_at,
            updated_at=datetime.utcnow().isoformat(),
        )
        store.save_prompt(prompt_v3)

        latest_version = store.get_latest_version("test_prompt")
        assert latest_version == "2.0"

    def test_get_latest_version_not_found(self, store):
        """Test getting latest version of non-existent prompt."""
        with pytest.raises(PromptNotFoundError):
            store.get_latest_version("non_existent")

    def test_get_prompt_versions(self, store, sample_prompt):
        """Test getting all versions of a prompt."""
        # Save multiple versions
        store.save_prompt(sample_prompt)

        prompt_v2 = PromptInfo(
            name="test_prompt",
            version="1.1",
            content="Version 1.1",
            metadata={},
            variables=[],
            created_at=sample_prompt.created_at,
            updated_at=datetime.utcnow().isoformat(),
        )
        store.save_prompt(prompt_v2)

        versions = store.get_prompt_versions("test_prompt")
        assert "1.0" in versions
        assert "1.1" in versions
        assert len(versions) == 2

    def test_get_prompt_versions_not_found(self, store):
        """Test getting versions of non-existent prompt."""
        with pytest.raises(PromptNotFoundError):
            store.get_prompt_versions("non_existent")

    def test_delete_prompt(self, store, sample_prompt):
        """Test deleting a prompt."""
        store.save_prompt(sample_prompt)

        # Verify file exists
        prompt_file = store.store_path / "test_prompt" / "1.0.yaml"
        assert prompt_file.exists()

        # Delete prompt
        store.delete_prompt("test_prompt", "1.0")

        # Verify file is deleted
        assert not prompt_file.exists()

    def test_delete_prompt_not_found(self, store):
        """Test deleting non-existent prompt."""
        with pytest.raises(PromptNotFoundError):
            store.delete_prompt("non_existent", "1.0")

    def test_delete_prompt_removes_directory_if_empty(self, store, sample_prompt):
        """Test that deleting removes empty directories."""
        store.save_prompt(sample_prompt)

        prompt_dir = store.store_path / "test_prompt"
        assert prompt_dir.exists()

        store.delete_prompt("test_prompt", "1.0")

        # Directory should be removed if empty
        assert not prompt_dir.exists()

    def test_delete_prompt_keeps_directory_if_other_versions_exist(
        self, store, sample_prompt
    ):
        """Test that deleting keeps directory if other versions exist."""
        # Save multiple versions
        store.save_prompt(sample_prompt)

        prompt_v2 = PromptInfo(
            name="test_prompt",
            version="1.1",
            content="Version 1.1",
            metadata={},
            variables=[],
            created_at=sample_prompt.created_at,
            updated_at=datetime.utcnow().isoformat(),
        )
        store.save_prompt(prompt_v2)

        prompt_dir = store.store_path / "test_prompt"
        assert prompt_dir.exists()

        # Delete one version
        store.delete_prompt("test_prompt", "1.0")

        # Directory should still exist
        assert prompt_dir.exists()
        assert (prompt_dir / "1.1.yaml").exists()

    def test_list_prompts_empty(self, store):
        """Test listing prompts when store is empty."""
        prompts = store.list_prompts()
        assert len(prompts) == 0

    def test_list_prompts_single(self, store, sample_prompt):
        """Test listing single prompt."""
        store.save_prompt(sample_prompt)

        prompts = store.list_prompts()
        assert len(prompts) == 1
        assert prompts[0].name == "test_prompt"
        assert prompts[0].version == "1.0"

    def test_list_prompts_multiple(self, store, sample_prompt):
        """Test listing multiple prompts."""
        # Save first prompt
        store.save_prompt(sample_prompt)

        # Save second prompt
        prompt2 = PromptInfo(
            name="another_prompt",
            version="1.0",
            content="Another prompt",
            metadata={},
            variables=[],
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )
        store.save_prompt(prompt2)

        prompts = store.list_prompts()
        assert len(prompts) == 2

        names = [p.name for p in prompts]
        assert "test_prompt" in names
        assert "another_prompt" in names

    def test_list_prompts_with_multiple_versions(self, store, sample_prompt):
        """Test listing prompts with multiple versions."""
        # Save multiple versions
        store.save_prompt(sample_prompt)

        prompt_v2 = PromptInfo(
            name="test_prompt",
            version="1.1",
            content="Version 1.1",
            metadata={},
            variables=[],
            created_at=sample_prompt.created_at,
            updated_at=datetime.utcnow().isoformat(),
        )
        store.save_prompt(prompt_v2)

        prompts = store.list_prompts()
        assert len(prompts) == 2

        versions = [p.version for p in prompts if p.name == "test_prompt"]
        assert "1.0" in versions
        assert "1.1" in versions

    def test_exists(self, store, sample_prompt):
        """Test checking if prompt exists."""
        assert not store.exists("test_prompt", "1.0")

        store.save_prompt(sample_prompt)
        assert store.exists("test_prompt", "1.0")
        assert not store.exists("test_prompt", "2.0")

    def test_search_prompts(self, store, sample_prompt):
        """Test searching prompts."""
        store.save_prompt(sample_prompt)

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

    def test_get_stats(self, store, sample_prompt):
        """Test getting store statistics."""
        # Empty store
        stats = store.get_stats()
        assert stats.total_prompts == 0
        assert stats.total_versions == 0
        assert stats.storage_size_bytes == 0

        # Add some prompts
        store.save_prompt(sample_prompt)

        prompt_v2 = PromptInfo(
            name="test_prompt",
            version="1.1",
            content="Version 1.1",
            metadata={},
            variables=[],
            created_at=sample_prompt.created_at,
            updated_at=datetime.utcnow().isoformat(),
        )
        store.save_prompt(prompt_v2)

        stats = store.get_stats()
        assert stats.total_prompts == 1  # One unique prompt name
        assert stats.total_versions == 2  # Two versions of the same prompt
        assert stats.storage_size_bytes > 0

    def test_permission_error_handling(self, store, sample_prompt):
        """Test handling permission errors."""
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with pytest.raises(PromptStorageError):
                store.save_prompt(sample_prompt)

    def test_io_error_handling(self, store, sample_prompt):
        """Test handling IO errors."""
        with patch("builtins.open", side_effect=IOError("Disk full")):
            with pytest.raises(PromptStorageError):
                store.save_prompt(sample_prompt)

    def test_yaml_error_handling(self, store, sample_prompt):
        """Test handling YAML errors."""
        with patch("yaml.dump", side_effect=yaml.YAMLError("Invalid data")):
            with pytest.raises(PromptStorageError):
                store.save_prompt(sample_prompt)

    def test_base_path_validation(self):
        """Test base path validation."""
        # Test with None path
        with pytest.raises(PromptStorageError):
            LocalPromptStore(base_path=None)

        # Test with empty path
        with pytest.raises(PromptStorageError):
            LocalPromptStore(base_path="")

    def test_filename_sanitization(self, store):
        """Test that filenames are properly sanitized."""
        # Test with potentially problematic characters that will be sanitized
        prompt = PromptInfo(
            name="test_prompt_with_underscores",
            version="1.0",
            content="Test content",
            metadata={},
            variables=[],
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        # This should not raise an error
        store.save_prompt(prompt)

        # Verify the file was created with a safe name
        prompt_dir = store.store_path / "test_prompt_with_underscores"
        assert prompt_dir.exists()

        # Test that the sanitization method works correctly
        sanitized_name = store._sanitize_filename("test/prompt\\with*chars?")
        assert sanitized_name == "test_prompt_with_chars"
