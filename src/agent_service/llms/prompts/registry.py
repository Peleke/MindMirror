"""
Prompt registry for managing prompt templates.

This module provides a centralized registry for managing prompt templates
with versioning, validation, and retrieval functionality.
"""

import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from .exceptions import PromptNotFoundError, PromptValidationError
from .loader import PromptLoader, TemplateError
from .models import PromptInfo, PromptSearchCriteria, StoreType
from .service import PromptService


class PromptRegistry:
    """
    Central registry for prompt management.

    This registry provides methods for registering, discovering,
    and managing prompts with metadata and search capabilities.
    """

    def __init__(self, service: PromptService):
        """Initialize the registry with a prompt service."""
        self.service = service
        self._metadata: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._tags: Dict[str, Set[str]] = defaultdict(set)
        self._categories: Dict[str, Set[str]] = defaultdict(set)
        self._aliases: Dict[str, str] = {}

    def register_prompt(
        self,
        prompt_info: PromptInfo,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Register a prompt with metadata.

        Args:
            prompt_info: The prompt information to register
            tags: Optional list of tags for categorization
            category: Optional category for grouping
            aliases: Optional list of alternative names
            metadata: Optional additional metadata
        """
        if not isinstance(prompt_info, PromptInfo):
            raise PromptValidationError("prompt_info must be a PromptInfo object")

        # Save the prompt
        self.service.save_prompt(prompt_info)

        # Store metadata
        prompt_key = f"{prompt_info.name}:{prompt_info.version}"

        if tags:
            self._tags[prompt_key].update(tags)

        if category:
            self._categories[prompt_key].add(category)

        if aliases:
            for alias in aliases:
                if alias in self._aliases:
                    raise PromptValidationError(f"Alias '{alias}' already exists")
                self._aliases[alias] = prompt_key

        if metadata:
            self._metadata[prompt_key].update(metadata)

        # Add registration timestamp
        self._metadata[prompt_key]["registered_at"] = datetime.utcnow().isoformat()

    def unregister_prompt(self, name: str, version: Optional[str] = None) -> None:
        """
        Unregister a prompt and its metadata.

        Args:
            name: The prompt name
            version: Optional version (uses latest if not specified)
        """
        if version is None:
            version = self.service.get_latest_version(name)

        prompt_key = f"{name}:{version}"

        # Remove from service
        self.service.delete_prompt(name, version)

        # Clean up metadata
        self._metadata.pop(prompt_key, None)
        self._tags.pop(prompt_key, None)
        self._categories.pop(prompt_key, None)

        # Remove aliases
        aliases_to_remove = [
            alias for alias, key in self._aliases.items() if key == prompt_key
        ]
        for alias in aliases_to_remove:
            del self._aliases[alias]

    def get_prompt(self, name: str, version: Optional[str] = None) -> PromptInfo:
        """
        Get a prompt by name and optional version.

        Args:
            name: The prompt name
            version: Optional version (uses latest if not specified)

        Returns:
            The prompt information
        """
        return self.service.get_prompt(name, version)

    def get_prompt_by_alias(self, alias: str) -> PromptInfo:
        """
        Get a prompt by its alias.

        Args:
            alias: The prompt alias

        Returns:
            The prompt information
        """
        if alias not in self._aliases:
            raise PromptNotFoundError(f"Alias '{alias}' not found")

        prompt_key = self._aliases[alias]
        name, version = prompt_key.split(":", 1)
        return self.service.get_prompt(name, version)

    def list_prompts(
        self, criteria: Optional[PromptSearchCriteria] = None
    ) -> List[PromptInfo]:
        """
        List prompts based on search criteria.

        Args:
            criteria: Optional search criteria

        Returns:
            List of matching prompts
        """
        if criteria is None:
            criteria = PromptSearchCriteria()

        all_prompts = self.service.list_prompts()
        filtered_prompts = []

        for prompt in all_prompts:
            if self._matches_criteria(prompt, criteria):
                filtered_prompts.append(prompt)

        return filtered_prompts

    def search_prompts(
        self, query: str, search_fields: Optional[List[str]] = None
    ) -> List[PromptInfo]:
        """
        Search prompts by text query.

        Args:
            query: The search query
            search_fields: Optional list of fields to search (default: name, content)

        Returns:
            List of matching prompts
        """
        if search_fields is None:
            search_fields = ["name", "content"]

        all_prompts = self.service.list_prompts()
        matching_prompts = []

        query_lower = query.lower()

        for prompt in all_prompts:
            for field in search_fields:
                if hasattr(prompt, field):
                    value = getattr(prompt, field)
                    if isinstance(value, str) and query_lower in value.lower():
                        matching_prompts.append(prompt)
                        break

        return matching_prompts

    def get_prompts_by_tag(self, tag: str) -> List[PromptInfo]:
        """
        Get prompts by tag.

        Args:
            tag: The tag to search for

        Returns:
            List of prompts with the specified tag
        """
        matching_prompts = []

        for prompt_key, tags in self._tags.items():
            if tag in tags:
                name, version = prompt_key.split(":", 1)
                try:
                    prompt = self.service.get_prompt(name, version)
                    matching_prompts.append(prompt)
                except PromptNotFoundError:
                    # Skip if prompt no longer exists
                    continue

        return matching_prompts

    def get_prompts_by_category(self, category: str) -> List[PromptInfo]:
        """
        Get prompts by category.

        Args:
            category: The category to search for

        Returns:
            List of prompts in the specified category
        """
        matching_prompts = []

        for prompt_key, categories in self._categories.items():
            if category in categories:
                name, version = prompt_key.split(":", 1)
                try:
                    prompt = self.service.get_prompt(name, version)
                    matching_prompts.append(prompt)
                except PromptNotFoundError:
                    # Skip if prompt no longer exists
                    continue

        return matching_prompts

    def get_prompt_metadata(
        self, name: str, version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get metadata for a prompt.

        Args:
            name: The prompt name
            version: Optional version (uses latest if not specified)

        Returns:
            Dictionary of metadata
        """
        if version is None:
            version = self.service.get_latest_version(name)

        prompt_key = f"{name}:{version}"
        return dict(self._metadata[prompt_key])

    def update_prompt_metadata(
        self, name: str, metadata: Dict[str, Any], version: Optional[str] = None
    ) -> None:
        """
        Update metadata for a prompt.

        Args:
            name: The prompt name
            metadata: The metadata to update
            version: Optional version (uses latest if not specified)
        """
        if version is None:
            version = self.service.get_latest_version(name)

        prompt_key = f"{name}:{version}"
        self._metadata[prompt_key].update(metadata)

    def add_tags(
        self, name: str, tags: List[str], version: Optional[str] = None
    ) -> None:
        """
        Add tags to a prompt.

        Args:
            name: The prompt name
            tags: List of tags to add
            version: Optional version (uses latest if not specified)
        """
        if version is None:
            version = self.service.get_latest_version(name)

        prompt_key = f"{name}:{version}"
        self._tags[prompt_key].update(tags)

    def remove_tags(
        self, name: str, tags: List[str], version: Optional[str] = None
    ) -> None:
        """
        Remove tags from a prompt.

        Args:
            name: The prompt name
            tags: List of tags to remove
            version: Optional version (uses latest if not specified)
        """
        if version is None:
            version = self.service.get_latest_version(name)

        prompt_key = f"{name}:{version}"
        for tag in tags:
            self._tags[prompt_key].discard(tag)

    def get_all_tags(self) -> Set[str]:
        """
        Get all unique tags in the registry.

        Returns:
            Set of all tags
        """
        all_tags = set()
        for tags in self._tags.values():
            all_tags.update(tags)
        return all_tags

    def get_all_categories(self) -> Set[str]:
        """
        Get all unique categories in the registry.

        Returns:
            Set of all categories
        """
        all_categories = set()
        for categories in self._categories.values():
            all_categories.update(categories)
        return all_categories

    def get_prompt_aliases(self, name: str, version: Optional[str] = None) -> List[str]:
        """
        Get aliases for a prompt.

        Args:
            name: The prompt name
            version: Optional version (uses latest if not specified)

        Returns:
            List of aliases
        """
        if version is None:
            version = self.service.get_latest_version(name)

        prompt_key = f"{name}:{version}"
        return [alias for alias, key in self._aliases.items() if key == prompt_key]

    def add_alias(self, name: str, alias: str, version: Optional[str] = None) -> None:
        """
        Add an alias for a prompt.

        Args:
            name: The prompt name
            alias: The alias to add
            version: Optional version (uses latest if not specified)
        """
        if version is None:
            version = self.service.get_latest_version(name)

        if alias in self._aliases:
            raise PromptValidationError(f"Alias '{alias}' already exists")

        prompt_key = f"{name}:{version}"
        self._aliases[alias] = prompt_key

    def remove_alias(self, alias: str) -> None:
        """
        Remove an alias.

        Args:
            alias: The alias to remove
        """
        if alias not in self._aliases:
            raise PromptNotFoundError(f"Alias '{alias}' not found")

        del self._aliases[alias]

    def get_registry_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the registry.

        Returns:
            Dictionary of registry statistics
        """
        all_prompts = self.service.list_prompts()

        stats = {
            "total_prompts": len(all_prompts),
            "total_versions": sum(
                len(self.service.get_prompt_versions(p.name)) for p in all_prompts
            ),
            "total_tags": len(self.get_all_tags()),
            "total_categories": len(self.get_all_categories()),
            "total_aliases": len(self._aliases),
            "unique_prompts": len(set(p.name for p in all_prompts)),
            "average_versions_per_prompt": len(all_prompts)
            / max(1, len(set(p.name for p in all_prompts))),
        }

        return stats

    def _matches_criteria(
        self, prompt: PromptInfo, criteria: PromptSearchCriteria
    ) -> bool:
        """Check if a prompt matches the search criteria."""
        prompt_key = f"{prompt.name}:{prompt.version}"

        # Check name pattern
        if criteria.name_pattern:
            if not re.search(criteria.name_pattern, prompt.name):
                return False

        # Check version pattern
        if criteria.version_pattern:
            if not re.search(criteria.version_pattern, prompt.version):
                return False

        # Check content pattern
        if criteria.content_pattern:
            if not re.search(criteria.content_pattern, prompt.content):
                return False

        # Check metadata filters
        if criteria.metadata_filters:
            for key, value in criteria.metadata_filters.items():
                if key not in prompt.metadata or prompt.metadata[key] != value:
                    return False

        # Check created date range
        if criteria.created_after and prompt.created_at:
            try:
                created_at = datetime.fromisoformat(prompt.created_at)
                if created_at < criteria.created_after:
                    return False
            except ValueError:
                # Skip date comparison if invalid format
                pass

        if criteria.created_before and prompt.created_at:
            try:
                created_at = datetime.fromisoformat(prompt.created_at)
                if created_at > criteria.created_before:
                    return False
            except ValueError:
                # Skip date comparison if invalid format
                pass

        # Check updated date range
        if criteria.updated_after and prompt.updated_at:
            try:
                updated_at = datetime.fromisoformat(prompt.updated_at)
                if updated_at < criteria.updated_after:
                    return False
            except ValueError:
                # Skip date comparison if invalid format
                pass

        if criteria.updated_before and prompt.updated_at:
            try:
                updated_at = datetime.fromisoformat(prompt.updated_at)
                if updated_at > criteria.updated_before:
                    return False
            except ValueError:
                # Skip date comparison if invalid format
                pass

        return True

    def export_registry(self) -> Dict[str, Any]:
        """
        Export the registry data for backup or migration.

        Returns:
            Dictionary containing registry data
        """
        all_prompts = self.service.list_prompts()

        export_data = {
            "prompts": [prompt.to_dict() for prompt in all_prompts],
            "metadata": dict(self._metadata),
            "tags": {k: list(v) for k, v in self._tags.items()},
            "categories": {k: list(v) for k, v in self._categories.items()},
            "aliases": dict(self._aliases),
            "exported_at": datetime.utcnow().isoformat(),
        }

        return export_data

    def import_registry(self, data: Dict[str, Any]) -> None:
        """
        Import registry data from backup or migration.

        Args:
            data: Dictionary containing registry data
        """
        # Import prompts
        for prompt_dict in data.get("prompts", []):
            prompt_info = PromptInfo.from_dict(prompt_dict)
            self.service.save_prompt(prompt_info)

        # Import metadata
        self._metadata.update(data.get("metadata", {}))

        # Import tags
        for key, tags_list in data.get("tags", {}).items():
            self._tags[key] = set(tags_list)

        # Import categories
        for key, categories_list in data.get("categories", {}).items():
            self._categories[key] = set(categories_list)

        # Import aliases
        self._aliases.update(data.get("aliases", {}))
