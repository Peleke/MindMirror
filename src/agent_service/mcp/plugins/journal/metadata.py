"""
Journal Plugin Metadata

Centralized metadata management for the journal plugin with proper semver versioning.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, FrozenSet, List


class PluginCategory(Enum):
    """Plugin categories for classification."""

    ANALYSIS = "analysis"
    PROCESSING = "processing"
    INTEGRATION = "integration"
    UTILITY = "utility"


@dataclass(frozen=True)
class PluginMetadata:
    """Centralized metadata for MCP plugins."""

    # Core plugin information
    name: str
    version: str  # Semver format: MAJOR.MINOR.PATCH
    description: str
    category: PluginCategory

    # Dependencies and requirements
    dependencies: List[str] = field(default_factory=list)
    tags: FrozenSet[str] = field(default_factory=frozenset)

    # Plugin capabilities
    capabilities: List[str] = field(default_factory=list)

    # Configuration schema
    config_schema: Dict[str, Any] = field(default_factory=dict)

    # Author and license information
    author: str = "MindMirror Team"
    license: str = "MIT"

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


class JournalPluginMetadata:
    """Journal plugin specific metadata."""

    @staticmethod
    def get_metadata() -> PluginMetadata:
        """Get the journal plugin metadata."""
        return PluginMetadata(
            name="journal_plugin",
            version="1.0.0",  # Initial release
            description="Journal processing and analysis capabilities with real retriever integration",
            category=PluginCategory.ANALYSIS,
            dependencies=["retriever_registry", "llm_service", "journal_client"],
            tags=frozenset(["journal", "analysis", "summarization", "retriever_aware"]),
            capabilities=[
                "journal_summarization",
                "performance_review_generation",
                "entry_type_filtering",
                "time_based_querying",
                "retriever_integration",
            ],
            config_schema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID for journal data access",
                        "required": True,
                    },
                    "default_time_period": {
                        "type": "string",
                        "enum": ["week", "month", "quarter", "year"],
                        "description": "Default time period for queries",
                        "default": "month",
                    },
                    "max_entries_per_query": {
                        "type": "integer",
                        "description": "Maximum number of entries to retrieve per query",
                        "default": 100,
                    },
                },
                "required": ["user_id"],
            },
            metadata={
                "retriever_types": ["http"],
                "supported_entry_types": ["text", "mood", "goal"],
                "query_languages": ["natural_language", "time_based"],
                "output_formats": ["text", "json", "structured"],
            },
        )

    @staticmethod
    def get_tool_metadata() -> Dict[str, Dict[str, Any]]:
        """Get metadata for journal plugin tools."""
        return {
            "summarize_journals": {
                "name": "summarize_journals",
                "description": "Summarize journal entries using real retriever architecture",
                "category": "analysis",
                "uses_retriever": True,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Query to retrieve relevant journal entries (e.g., 'this week', 'last month')",
                        },
                        "style": {
                            "type": "string",
                            "enum": ["concise", "detailed", "analytical"],
                            "description": "Summary style",
                        },
                        "entry_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by entry types (e.g., ['text', 'mood', 'goal'])",
                        },
                    },
                    "required": ["query"],
                },
                "tags": frozenset(["journal", "summarization"]),
            },
            "generate_review": {
                "name": "generate_review",
                "description": "Generate a performance review from journal entries",
                "category": "analysis",
                "uses_retriever": True,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Query to retrieve relevant journal entries (e.g., 'this quarter', 'last month')",
                        },
                        "period": {
                            "type": "string",
                            "enum": ["week", "month", "quarter"],
                            "description": "Review period",
                        },
                        "focus_areas": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific areas to focus on in review",
                        },
                    },
                    "required": ["query"],
                },
                "tags": frozenset(["journal", "review"]),
            },
            "list_retrievers": {
                "name": "list_retrievers",
                "description": "List available retrievers for journal data",
                "category": "meta",
                "uses_retriever": False,
                "input_schema": {"type": "object", "properties": {}},
                "tags": frozenset(["journal", "meta"]),
            },
            "get_entries_by_type": {
                "name": "get_entries_by_type",
                "description": "Get journal entries filtered by type",
                "category": "query",
                "uses_retriever": True,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "entry_type": {
                            "type": "string",
                            "description": "Type of entries to retrieve (e.g., 'text', 'mood', 'goal')",
                        },
                        "days_back": {
                            "type": "integer",
                            "description": "Number of days back to search",
                            "default": 30,
                        },
                    },
                    "required": ["entry_type"],
                },
                "tags": frozenset(["journal", "query"]),
            },
        }

    @staticmethod
    def get_resource_metadata(user_id: str) -> Dict[str, Dict[str, Any]]:
        """Get metadata for journal plugin resources."""
        return {
            "retrievers": {
                "uri": "mindmirror://journal/retrievers",
                "name": "Journal Retrievers",
                "description": "Access to available journal retrievers",
                "mime_type": "application/json",
                "metadata": {"category": "meta", "retriever_aware": True},
            },
            "entries": {
                "uri": "mindmirror://journal/entries",
                "name": "Journal Entries",
                "description": "Access to journal entries via retriever",
                "mime_type": "application/json",
                "metadata": {"category": "data", "retriever_aware": True},
            },
            "user_entries": {
                "uri": f"mindmirror://journal/user/{user_id}/entries",
                "name": "User Journal Entries",
                "description": f"Access to journal entries for user {user_id}",
                "mime_type": "application/json",
                "metadata": {
                    "category": "data",
                    "user_specific": True,
                    "retriever_aware": True,
                },
            },
        }

    @staticmethod
    def get_prompt_metadata() -> Dict[str, Dict[str, Any]]:
        """Get metadata for journal plugin prompts."""
        return {
            "summarize_journals": {
                "name": "summarize_journals",
                "description": "Summarize journal entries using real retriever architecture",
                "arguments": [
                    {
                        "name": "query",
                        "description": "Query to retrieve relevant journal entries",
                        "required": True,
                    },
                    {
                        "name": "style",
                        "description": "Summary style (concise, detailed, analytical)",
                        "required": False,
                    },
                ],
                "metadata": {"category": "prompt", "retriever_aware": True},
            }
        }
