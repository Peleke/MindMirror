"""
Prompt service implementation.

This module provides the PromptService class that orchestrates
storage operations, caching, and provides a high-level interface
for prompt management.
"""

import time
from collections import OrderedDict
from functools import lru_cache
from typing import Any, Dict, List, Optional

from jinja2 import Template, TemplateError

from .exceptions import PromptNotFoundError, PromptRenderError, PromptValidationError
from .models import PromptConfig, PromptInfo
from .stores import PromptStore


class LRUCache:
    """
    Simple LRU cache implementation.

    This provides a basic LRU cache with TTL support for caching
    prompt templates and rendered results.
    """

    def __init__(self, maxsize: int = 128, ttl: int = 3600):
        """Initialize the cache."""
        self.maxsize = maxsize
        self.ttl = ttl
        self._cache: OrderedDict = OrderedDict()
        self._timestamps: Dict[str, float] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if key not in self._cache:
            return None

        # Check TTL
        if time.time() - self._timestamps[key] > self.ttl:
            self._remove(key)
            return None

        # Move to end (most recently used)
        self._cache.move_to_end(key)
        return self._cache[key]

    def put(self, key: str, value: Any) -> None:
        """Put a value in cache."""
        # Remove if exists
        if key in self._cache:
            self._remove(key)

        # Add new item
        self._cache[key] = value
        self._timestamps[key] = time.time()

        # Evict if necessary
        if len(self._cache) > self.maxsize:
            oldest_key = next(iter(self._cache))
            self._remove(oldest_key)

    def _remove(self, key: str) -> None:
        """Remove an item from cache."""
        if key in self._cache:
            del self._cache[key]
            del self._timestamps[key]

    def clear(self) -> None:
        """Clear all items from cache."""
        self._cache.clear()
        self._timestamps.clear()

    def __len__(self) -> int:
        """Get cache size."""
        return len(self._cache)

    def __contains__(self, key: str) -> bool:
        """Check if key exists in cache."""
        return key in self._cache

    def __getitem__(self, key: str) -> Any:
        """Get item by key."""
        return self._cache[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item by key."""
        self.put(key, value)

    def __delitem__(self, key: str) -> None:
        """Delete item by key."""
        self._remove(key)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {"size": len(self._cache), "maxsize": self.maxsize, "ttl": self.ttl}


class PromptService:
    """
    High-level service for prompt management.

    This service provides a unified interface for prompt operations,
    including caching, rendering, and orchestration of storage operations.
    """

    def __init__(self, store: PromptStore, config: PromptConfig):
        """Initialize the prompt service."""
        self.store = store
        self.config = config

        # Initialize cache if enabled
        if config.enable_caching:
            self._cache = LRUCache(maxsize=config.cache_size, ttl=config.cache_ttl)
        else:
            self._cache = None

    def get_prompt(self, name: str, version: Optional[str] = None) -> PromptInfo:
        """Get a prompt by name and optional version."""
        # If no version provided, get the latest version
        if version is None:
            version = self.store.get_latest_version(name)

        cache_key = f"{name}:{version}"

        # Try cache first
        if self._cache is not None:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached

        # Get from store
        prompt = self.store.get_prompt(name, version)

        # Cache the result
        if self._cache is not None:
            self._cache.put(cache_key, prompt)

        return prompt

    def save_prompt(self, info: PromptInfo) -> None:
        """Save a prompt to storage."""
        # Validate if enabled
        if self.config.enable_validation:
            if not isinstance(info, PromptInfo):
                raise PromptValidationError("info must be a PromptInfo object")

        # Save to store
        self.store.save_prompt(info)

        # Invalidate cache
        if self._cache is not None:
            self._invalidate_cache_for_prompt(info.name)

    def delete_prompt(self, name: str, version: Optional[str] = None) -> None:
        """Delete a prompt from storage."""
        # If no version provided, get the latest version
        if version is None:
            version = self.store.get_latest_version(name)

        # Delete from store
        self.store.delete_prompt(name, version)

        # Invalidate cache
        if self._cache is not None:
            self._invalidate_cache_for_prompt(name)

    def list_prompts(self) -> List[PromptInfo]:
        """List all available prompts."""
        return self.store.list_prompts()

    def get_latest_version(self, name: str) -> str:
        """Get the latest version of a prompt."""
        return self.store.get_latest_version(name)

    def search_prompts(self, criteria: dict) -> List[PromptInfo]:
        """Search prompts based on criteria."""
        return self.store.search_prompts(criteria)

    def get_prompt_versions(self, name: str) -> List[str]:
        """Get all versions of a prompt."""
        return self.store.get_prompt_versions(name)

    def exists(self, name: str, version: Optional[str] = None) -> bool:
        """Check if a prompt exists."""
        return self.store.exists(name, version)

    def get_stats(self) -> dict:
        """Get storage statistics."""
        return self.store.get_stats()

    def render_prompt(
        self, name: str, variables: Dict[str, Any], version: Optional[str] = None
    ) -> str:
        """Render a prompt template with variables."""
        # Get the prompt
        prompt = self.get_prompt(name, version)

        try:
            # Create Jinja2 template
            template = Template(prompt.content)

            # Render the template
            rendered = template.render(**variables)

            return rendered
        except TemplateError as e:
            raise PromptRenderError(
                f"Failed to render template '{name}': {str(e)}",
                template_name=name,
                variables=variables,
            )
        except Exception as e:
            raise PromptRenderError(
                f"Unexpected error rendering template '{name}': {str(e)}",
                template_name=name,
                variables=variables,
            )

    def render_prompt_safe(
        self,
        name: str,
        variables: Dict[str, Any],
        version: Optional[str] = None,
        default: Optional[str] = None,
    ) -> str:
        """Render a prompt template safely with fallback."""
        try:
            return self.render_prompt(name, variables, version)
        except Exception:
            if default is not None:
                return default
            raise

    def create_prompt(
        self,
        name: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        version: str = "1.0",
    ) -> PromptInfo:
        """Create a new prompt."""
        info = PromptInfo(
            name=name, version=version, content=content, metadata=metadata or {}
        )

        self.save_prompt(info)
        return info

    def update_prompt(
        self,
        name: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        version: Optional[str] = None,
    ) -> PromptInfo:
        """Update an existing prompt."""
        # Get current prompt
        current = self.get_prompt(name, version)

        # Create updated version
        updated = current.update_content(content)

        # Update metadata if provided
        if metadata is not None:
            updated = updated.update_metadata(metadata)

        # Save the updated prompt
        self.save_prompt(updated)

        return updated

    def copy_prompt(
        self,
        source_name: str,
        target_name: str,
        source_version: Optional[str] = None,
        target_version: str = "1.0",
    ) -> PromptInfo:
        """Copy a prompt to a new name."""
        source = self.get_prompt(source_name, source_version)

        # Create new prompt with same content
        new_prompt = PromptInfo(
            name=target_name,
            version=target_version,
            content=source.content,
            metadata=source.metadata.copy(),
            variables=source.variables.copy(),
            created_at=source.created_at,
            updated_at=source.updated_at,
        )

        self.save_prompt(new_prompt)
        return new_prompt

    def validate_prompt(
        self, name: str, variables: Dict[str, Any], version: Optional[str] = None
    ) -> bool:
        """Validate that a prompt can be rendered with given variables."""
        try:
            self.render_prompt(name, variables, version)
            return True
        except Exception:
            return False

    def get_prompt_variables(
        self, name: str, version: Optional[str] = None
    ) -> List[str]:
        """Get the variables required by a prompt."""
        prompt = self.get_prompt(name, version)
        return prompt.variables.copy()

    def clear_cache(self) -> None:
        """Clear the prompt cache."""
        if self._cache is not None:
            self._cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if self._cache is None:
            return {"size": 0, "maxsize": 0, "hits": 0, "misses": 0}

        stats = self._cache.get_stats()
        # Note: This simple cache doesn't track hits/misses
        # A more sophisticated implementation would track these
        stats["hits"] = 0
        stats["misses"] = 0
        return stats

    def _invalidate_cache_for_prompt(self, name: str) -> None:
        """Invalidate all cache entries for a prompt."""
        if self._cache is None:
            return

        # Remove all cache entries for this prompt
        keys_to_remove = []
        for key in self._cache._cache.keys():
            if key.startswith(f"{name}:"):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            self._cache._remove(key)

    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the service."""
        try:
            # Test store connectivity
            stats = self.get_stats()

            # Test cache functionality
            cache_stats = self.get_cache_stats()

            return {
                "status": "healthy",
                "store_connected": True,
                "cache_enabled": self._cache is not None,
                "store_stats": stats,
                "cache_stats": cache_stats,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "store_connected": False,
                "cache_enabled": self._cache is not None,
            }
