"""
Tests for prompt registry.

These tests verify that the PromptRegistry correctly manages
prompt registration, discovery, and metadata.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from agent_service.llms.prompts.exceptions import (
    PromptNotFoundError,
    PromptValidationError,
)
from agent_service.llms.prompts.models import (
    PromptConfig,
    PromptInfo,
    PromptSearchCriteria,
    StoreType,
)
from agent_service.llms.prompts.registry import PromptRegistry
from agent_service.llms.prompts.service import PromptService
from agent_service.llms.prompts.stores.memory import InMemoryPromptStore


class TestPromptRegistry:
    """Test PromptRegistry implementation."""

    @pytest.fixture
    def service(self):
        """Create a test service."""
        store = InMemoryPromptStore()
        config = PromptConfig(
            store_type=StoreType.MEMORY,
            cache_size=100,
            cache_ttl=3600,
            enable_validation=True,
            enable_caching=True,
        )
        return PromptService(store=store, config=config)

    @pytest.fixture
    def registry(self, service):
        """Create a test registry."""
        return PromptRegistry(service=service)

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

    def test_registry_initialization(self, registry):
        """Test registry initialization."""
        assert registry.service is not None
        assert registry._metadata == {}
        assert registry._tags == {}
        assert registry._categories == {}
        assert registry._aliases == {}

    def test_register_prompt_basic(self, registry, sample_prompt):
        """Test basic prompt registration."""
        registry.register_prompt(sample_prompt)

        # Verify prompt is saved
        saved_prompt = registry.service.get_prompt("test_prompt", "1.0")
        assert saved_prompt.name == "test_prompt"
        assert saved_prompt.version == "1.0"
        assert saved_prompt.content == "Hello {{name}}!"

    def test_register_prompt_with_tags(self, registry, sample_prompt):
        """Test prompt registration with tags."""
        registry.register_prompt(
            sample_prompt, tags=["greeting", "test"], category="examples"
        )

        # Verify metadata is stored
        prompt_key = "test_prompt:1.0"
        assert "greeting" in registry._tags[prompt_key]
        assert "test" in registry._tags[prompt_key]
        assert "examples" in registry._categories[prompt_key]

    def test_register_prompt_with_aliases(self, registry, sample_prompt):
        """Test prompt registration with aliases."""
        registry.register_prompt(
            sample_prompt, aliases=["greeting_prompt", "hello_template"]
        )

        # Verify aliases are stored
        assert registry._aliases["greeting_prompt"] == "test_prompt:1.0"
        assert registry._aliases["hello_template"] == "test_prompt:1.0"

    def test_register_prompt_with_metadata(self, registry, sample_prompt):
        """Test prompt registration with additional metadata."""
        metadata = {"author": "test_user", "priority": "high"}
        registry.register_prompt(sample_prompt, metadata=metadata)

        # Verify metadata is stored
        prompt_key = "test_prompt:1.0"
        assert registry._metadata[prompt_key]["author"] == "test_user"
        assert registry._metadata[prompt_key]["priority"] == "high"
        assert "registered_at" in registry._metadata[prompt_key]

    def test_register_prompt_duplicate_alias(self, registry, sample_prompt):
        """Test that duplicate aliases raise an error."""
        registry.register_prompt(sample_prompt, aliases=["test_alias"])

        # Try to register another prompt with the same alias
        another_prompt = PromptInfo(
            name="another_prompt",
            version="1.0",
            content="Another prompt",
            metadata={},
            variables=[],
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        with pytest.raises(PromptValidationError):
            registry.register_prompt(another_prompt, aliases=["test_alias"])

    def test_register_prompt_invalid_input(self, registry):
        """Test that invalid input raises an error."""
        with pytest.raises(PromptValidationError):
            registry.register_prompt("not_a_prompt_info")

    def test_get_prompt(self, registry, sample_prompt):
        """Test getting a prompt."""
        registry.register_prompt(sample_prompt)

        retrieved_prompt = registry.get_prompt("test_prompt", "1.0")
        assert retrieved_prompt.name == "test_prompt"
        assert retrieved_prompt.version == "1.0"

    def test_get_prompt_by_alias(self, registry, sample_prompt):
        """Test getting a prompt by alias."""
        registry.register_prompt(sample_prompt, aliases=["greeting"])

        retrieved_prompt = registry.get_prompt_by_alias("greeting")
        assert retrieved_prompt.name == "test_prompt"
        assert retrieved_prompt.version == "1.0"

    def test_get_prompt_by_alias_not_found(self, registry):
        """Test getting a prompt by non-existent alias."""
        with pytest.raises(PromptNotFoundError):
            registry.get_prompt_by_alias("non_existent")

    def test_list_prompts_empty(self, registry):
        """Test listing prompts when registry is empty."""
        prompts = registry.list_prompts()
        assert len(prompts) == 0

    def test_list_prompts_with_criteria(self, registry, sample_prompt):
        """Test listing prompts with search criteria."""
        registry.register_prompt(sample_prompt, tags=["greeting"], category="examples")

        # Test filtering by name pattern
        criteria = PromptSearchCriteria(name_pattern=r"test.*")
        prompts = registry.list_prompts(criteria)
        assert len(prompts) == 1
        assert prompts[0].name == "test_prompt"

        # Test filtering by content pattern
        criteria = PromptSearchCriteria(content_pattern=r"Hello.*")
        prompts = registry.list_prompts(criteria)
        assert len(prompts) == 1
        assert prompts[0].name == "test_prompt"

        # Test filtering by non-matching criteria
        criteria = PromptSearchCriteria(name_pattern=r"non_existent.*")
        prompts = registry.list_prompts(criteria)
        assert len(prompts) == 0

    def test_search_prompts(self, registry, sample_prompt):
        """Test searching prompts by text."""
        registry.register_prompt(sample_prompt)

        # Search by name
        results = registry.search_prompts("test_prompt")
        assert len(results) == 1
        assert results[0].name == "test_prompt"

        # Search by content
        results = registry.search_prompts("Hello")
        assert len(results) == 1
        assert results[0].name == "test_prompt"

        # Search with no results
        results = registry.search_prompts("non_existent")
        assert len(results) == 0

    def test_search_prompts_custom_fields(self, registry, sample_prompt):
        """Test searching prompts with custom fields."""
        registry.register_prompt(sample_prompt)

        # Search only in name field
        results = registry.search_prompts("test", search_fields=["name"])
        assert len(results) == 1

        # Search only in content field
        results = registry.search_prompts("Hello", search_fields=["content"])
        assert len(results) == 1

    def test_get_prompts_by_tag(self, registry, sample_prompt):
        """Test getting prompts by tag."""
        registry.register_prompt(sample_prompt, tags=["greeting", "test"])

        # Get prompts by tag
        prompts = registry.get_prompts_by_tag("greeting")
        assert len(prompts) == 1
        assert prompts[0].name == "test_prompt"

        # Get prompts by another tag
        prompts = registry.get_prompts_by_tag("test")
        assert len(prompts) == 1
        assert prompts[0].name == "test_prompt"

        # Get prompts by non-existent tag
        prompts = registry.get_prompts_by_tag("non_existent")
        assert len(prompts) == 0

    def test_get_prompts_by_category(self, registry, sample_prompt):
        """Test getting prompts by category."""
        registry.register_prompt(sample_prompt, category="examples")

        # Get prompts by category
        prompts = registry.get_prompts_by_category("examples")
        assert len(prompts) == 1
        assert prompts[0].name == "test_prompt"

        # Get prompts by non-existent category
        prompts = registry.get_prompts_by_category("non_existent")
        assert len(prompts) == 0

    def test_get_prompt_metadata(self, registry, sample_prompt):
        """Test getting prompt metadata."""
        metadata = {"author": "test_user", "priority": "high"}
        registry.register_prompt(sample_prompt, metadata=metadata)

        retrieved_metadata = registry.get_prompt_metadata("test_prompt", "1.0")
        assert retrieved_metadata["author"] == "test_user"
        assert retrieved_metadata["priority"] == "high"
        assert "registered_at" in retrieved_metadata

    def test_update_prompt_metadata(self, registry, sample_prompt):
        """Test updating prompt metadata."""
        registry.register_prompt(sample_prompt)

        new_metadata = {"status": "active", "reviewed": True}
        registry.update_prompt_metadata("test_prompt", new_metadata)

        retrieved_metadata = registry.get_prompt_metadata("test_prompt", "1.0")
        assert retrieved_metadata["status"] == "active"
        assert retrieved_metadata["reviewed"] is True

    def test_add_tags(self, registry, sample_prompt):
        """Test adding tags to a prompt."""
        registry.register_prompt(sample_prompt, tags=["initial"])

        registry.add_tags("test_prompt", ["new_tag", "another_tag"])

        prompt_key = "test_prompt:1.0"
        assert "initial" in registry._tags[prompt_key]
        assert "new_tag" in registry._tags[prompt_key]
        assert "another_tag" in registry._tags[prompt_key]

    def test_remove_tags(self, registry, sample_prompt):
        """Test removing tags from a prompt."""
        registry.register_prompt(sample_prompt, tags=["tag1", "tag2", "tag3"])

        registry.remove_tags("test_prompt", ["tag1", "tag3"])

        prompt_key = "test_prompt:1.0"
        assert "tag1" not in registry._tags[prompt_key]
        assert "tag2" in registry._tags[prompt_key]
        assert "tag3" not in registry._tags[prompt_key]

    def test_get_all_tags(self, registry, sample_prompt):
        """Test getting all unique tags."""
        registry.register_prompt(sample_prompt, tags=["tag1", "tag2"])

        another_prompt = PromptInfo(
            name="another_prompt",
            version="1.0",
            content="Another prompt",
            metadata={},
            variables=[],
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )
        registry.register_prompt(another_prompt, tags=["tag2", "tag3"])

        all_tags = registry.get_all_tags()
        assert "tag1" in all_tags
        assert "tag2" in all_tags
        assert "tag3" in all_tags
        assert len(all_tags) == 3

    def test_get_all_categories(self, registry, sample_prompt):
        """Test getting all unique categories."""
        registry.register_prompt(sample_prompt, category="category1")

        another_prompt = PromptInfo(
            name="another_prompt",
            version="1.0",
            content="Another prompt",
            metadata={},
            variables=[],
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )
        registry.register_prompt(another_prompt, category="category2")

        all_categories = registry.get_all_categories()
        assert "category1" in all_categories
        assert "category2" in all_categories
        assert len(all_categories) == 2

    def test_get_prompt_aliases(self, registry, sample_prompt):
        """Test getting aliases for a prompt."""
        registry.register_prompt(sample_prompt, aliases=["alias1", "alias2"])

        aliases = registry.get_prompt_aliases("test_prompt", "1.0")
        assert "alias1" in aliases
        assert "alias2" in aliases
        assert len(aliases) == 2

    def test_add_alias(self, registry, sample_prompt):
        """Test adding an alias to a prompt."""
        registry.register_prompt(sample_prompt)

        registry.add_alias("test_prompt", "new_alias")

        assert registry._aliases["new_alias"] == "test_prompt:1.0"

    def test_add_duplicate_alias(self, registry, sample_prompt):
        """Test that adding duplicate alias raises an error."""
        registry.register_prompt(sample_prompt, aliases=["existing_alias"])

        with pytest.raises(PromptValidationError):
            registry.add_alias("test_prompt", "existing_alias")

    def test_remove_alias(self, registry, sample_prompt):
        """Test removing an alias."""
        registry.register_prompt(sample_prompt, aliases=["alias1", "alias2"])

        registry.remove_alias("alias1")

        assert "alias1" not in registry._aliases
        assert "alias2" in registry._aliases

    def test_remove_nonexistent_alias(self, registry):
        """Test removing a non-existent alias."""
        with pytest.raises(PromptNotFoundError):
            registry.remove_alias("non_existent")

    def test_unregister_prompt(self, registry, sample_prompt):
        """Test unregistering a prompt."""
        registry.register_prompt(
            sample_prompt,
            tags=["tag1"],
            category="category1",
            aliases=["alias1"],
            metadata={"key": "value"},
        )

        registry.unregister_prompt("test_prompt", "1.0")

        # Verify prompt is removed from service
        with pytest.raises(PromptNotFoundError):
            registry.service.get_prompt("test_prompt", "1.0")

        # Verify metadata is cleaned up
        prompt_key = "test_prompt:1.0"
        assert prompt_key not in registry._metadata
        assert prompt_key not in registry._tags
        assert prompt_key not in registry._categories
        assert "alias1" not in registry._aliases

    def test_get_registry_stats(self, registry, sample_prompt):
        """Test getting registry statistics."""
        registry.register_prompt(sample_prompt, tags=["tag1"], category="cat1")

        stats = registry.get_registry_stats()

        assert stats["total_prompts"] == 1
        assert stats["total_versions"] == 1
        assert stats["total_tags"] == 1
        assert stats["total_categories"] == 1
        assert stats["total_aliases"] == 0
        assert stats["unique_prompts"] == 1
        assert stats["average_versions_per_prompt"] == 1.0

    def test_export_registry(self, registry, sample_prompt):
        """Test exporting registry data."""
        registry.register_prompt(
            sample_prompt,
            tags=["tag1"],
            category="category1",
            aliases=["alias1"],
            metadata={"key": "value"},
        )

        export_data = registry.export_registry()

        assert "prompts" in export_data
        assert "metadata" in export_data
        assert "tags" in export_data
        assert "categories" in export_data
        assert "aliases" in export_data
        assert "exported_at" in export_data

        assert len(export_data["prompts"]) == 1
        assert export_data["prompts"][0]["name"] == "test_prompt"

    def test_import_registry(self, registry, sample_prompt):
        """Test importing registry data."""
        # Create export data
        export_data = {
            "prompts": [sample_prompt.to_dict()],
            "metadata": {"test_prompt:1.0": {"key": "value"}},
            "tags": {"test_prompt:1.0": ["tag1", "tag2"]},
            "categories": {"test_prompt:1.0": ["category1"]},
            "aliases": {"alias1": "test_prompt:1.0"},
            "exported_at": datetime.utcnow().isoformat(),
        }

        registry.import_registry(export_data)

        # Verify data is imported
        assert len(registry.service.list_prompts()) == 1
        assert registry._metadata["test_prompt:1.0"]["key"] == "value"
        assert "tag1" in registry._tags["test_prompt:1.0"]
        assert "category1" in registry._categories["test_prompt:1.0"]
        assert registry._aliases["alias1"] == "test_prompt:1.0"

    def test_matches_criteria_complex(self, registry, sample_prompt):
        """Test complex criteria matching."""
        registry.register_prompt(
            sample_prompt, tags=["greeting", "test"], category="examples"
        )

        # Test multiple criteria
        criteria = PromptSearchCriteria(
            name_pattern=r"test.*", content_pattern=r"Hello.*"
        )

        prompts = registry.list_prompts(criteria)
        assert len(prompts) == 1
        assert prompts[0].name == "test_prompt"

        # Test non-matching criteria
        criteria = PromptSearchCriteria(name_pattern=r"non_existent.*")

        prompts = registry.list_prompts(criteria)
        assert len(prompts) == 0
