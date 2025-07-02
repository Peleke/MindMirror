"""
Graph Tool Implementations

Enhanced MCP tools that wrap existing LangGraph builders with multi-domain ownership,
versioning, observability, and schema introspection.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type

from .base import EffectBoundary, MCPTool, ToolBackend, ToolMetadata
from .decorators import register_tool


@dataclass
class GraphToolConfig:
    """Configuration for graph-based tools."""

    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    owner_domain: str
    version: str
    tags: List[str]
    effect_boundary: EffectBoundary
    subtools: List[str]


class GraphTool(MCPTool):
    """Base class for wrapping LangGraph builders as MCP tools."""

    def __init__(
        self, config: GraphToolConfig, graph_builder_class: Type, **builder_kwargs
    ):
        self.config = config
        self.graph_builder_class = graph_builder_class
        self.builder_kwargs = builder_kwargs
        self._graph_builder = None
        self._compiled_graph = None

    @property
    def owner_domain(self) -> str:
        """Get the owner domain for this tool."""
        return self.config.owner_domain

    @property
    def version(self) -> str:
        """Get the tool version (semver)."""
        return self.config.version

    @property
    def output_schema(self) -> Dict[str, Any]:
        """Get the output schema for this tool."""
        return self.config.output_schema

    def get_metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        return ToolMetadata(
            name=self.config.name,
            description=self.config.description,
            input_schema=self.config.input_schema,
            output_schema=self.output_schema,
            backend=ToolBackend.LANGGRAPH,
            owner_domain=self.owner_domain,
            version=self.version,
            tags=frozenset(self.config.tags),
            effect_boundary=self.config.effect_boundary,
            subtools=frozenset(self.config.subtools),
        )

    def _get_graph_builder(self):
        """Get or create the graph builder instance."""
        if self._graph_builder is None:
            self._graph_builder = self.graph_builder_class(**self.builder_kwargs)
        return self._graph_builder

    def _get_compiled_graph(self):
        """Get or create the compiled graph."""
        if self._compiled_graph is None:
            builder = self._get_graph_builder()
            self._compiled_graph = builder.build()
        return self._compiled_graph

    def list_subtools(self) -> List[str]:
        """List available subtools (graph nodes)."""
        builder = self._get_graph_builder()
        return builder.list_nodes()

    async def execute_subtool(self, name: str, args: Dict[str, Any]) -> Any:
        """Execute a subtool (individual graph node)."""
        builder = self._get_graph_builder()
        node = builder.get_node(name)
        if not node:
            raise ValueError(f"Subtool {name} not found")

        # Execute the node directly
        return await node.ainvoke(args)

    async def execute(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the graph tool."""
        try:
            # Get the compiled graph
            graph = self._get_compiled_graph()

            # Execute the graph
            result = await graph.ainvoke(arguments)

            # Convert result to MCP format
            return [
                {
                    "type": "graph_result",
                    "graph_name": self.config.name,
                    "result": result,
                    "arguments": arguments,
                }
            ]

        except Exception as e:
            # Return error in MCP format
            return [
                {
                    "type": "error",
                    "error": str(e),
                    "graph_name": self.config.name,
                    "arguments": arguments,
                }
            ]


# Enhanced Journal Graph Tool
@register_tool(
    name="journal_summary_graph",
    description="Generate journal summaries using LangGraph workflow",
    input_schema={
        "type": "object",
        "properties": {
            "journal_entries": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Journal entries to summarize",
            },
            "style": {
                "type": "string",
                "enum": ["concise", "detailed", "analytical"],
                "description": "Summary style",
            },
            "provider": {"type": "string", "description": "LLM provider to use"},
        },
        "required": ["journal_entries"],
    },
    output_schema={
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "graph_name": {"type": "string"},
                "result": {"type": "object"},
                "arguments": {"type": "object"},
            },
        },
    },
    backend="langgraph",
    owner_domain="journaling",
    version="2.1.0",
    tags=["journal", "summary", "langgraph"],
    effect_boundary="llm",
    subtools=["summarizer"],
)
class JournalSummaryGraphTool(GraphTool):
    """Enhanced tool for journal summary generation using LangGraph."""

    def __init__(
        self, provider: Optional[str] = None, overrides: Optional[Dict[str, Any]] = None
    ):
        config = GraphToolConfig(
            name="journal_summary_graph",
            description="Generate journal summaries using LangGraph workflow",
            input_schema={
                "type": "object",
                "properties": {
                    "journal_entries": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Journal entries to summarize",
                    },
                    "style": {
                        "type": "string",
                        "enum": ["concise", "detailed", "analytical"],
                        "description": "Summary style",
                    },
                    "provider": {
                        "type": "string",
                        "description": "LLM provider to use",
                    },
                },
                "required": ["journal_entries"],
            },
            output_schema={
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "graph_name": {"type": "string"},
                        "result": {"type": "object"},
                        "arguments": {"type": "object"},
                    },
                },
            },
            owner_domain="journaling",
            version="2.1.0",
            tags=["journal", "summary", "langgraph"],
            effect_boundary=EffectBoundary.LLM,
            subtools=["summarizer"],
        )

        # Import here to avoid circular imports
        from agent_service.langgraph_.graphs.journal_graph import JournalGraphBuilder

        super().__init__(
            config=config,
            graph_builder_class=JournalGraphBuilder,
            name="journal_summary_graph",
            description="Graph for journal summary generation",
            provider=provider,
            overrides=overrides,
        )


# Enhanced Review Graph Tool
@register_tool(
    name="performance_review_graph",
    description="Generate performance reviews using LangGraph workflow",
    input_schema={
        "type": "object",
        "properties": {
            "journal_entries": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Journal entries to analyze",
            },
            "period": {
                "type": "string",
                "enum": ["week", "month", "quarter", "year"],
                "description": "Review period",
            },
            "focus_areas": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific areas to focus on",
            },
            "provider": {"type": "string", "description": "LLM provider to use"},
        },
        "required": ["journal_entries", "period"],
    },
    output_schema={
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "graph_name": {"type": "string"},
                "result": {"type": "object"},
                "arguments": {"type": "object"},
            },
        },
    },
    backend="langgraph",
    owner_domain="review",
    version="1.0.0",
    tags=["review", "performance", "langgraph"],
    effect_boundary="llm",
    subtools=["analyzer", "evaluator"],
)
class PerformanceReviewGraphTool(GraphTool):
    """Enhanced tool for performance review generation using LangGraph."""

    def __init__(
        self, provider: Optional[str] = None, overrides: Optional[Dict[str, Any]] = None
    ):
        config = GraphToolConfig(
            name="performance_review_graph",
            description="Generate performance reviews using LangGraph workflow",
            input_schema={
                "type": "object",
                "properties": {
                    "journal_entries": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Journal entries to analyze",
                    },
                    "period": {
                        "type": "string",
                        "enum": ["week", "month", "quarter", "year"],
                        "description": "Review period",
                    },
                    "focus_areas": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific areas to focus on",
                    },
                    "provider": {
                        "type": "string",
                        "description": "LLM provider to use",
                    },
                },
                "required": ["journal_entries", "period"],
            },
            output_schema={
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "graph_name": {"type": "string"},
                        "result": {"type": "object"},
                        "arguments": {"type": "object"},
                    },
                },
            },
            owner_domain="review",
            version="1.0.0",
            tags=["review", "performance", "langgraph"],
            effect_boundary=EffectBoundary.LLM,
            subtools=["analyzer", "evaluator"],
        )

        # Import here to avoid circular imports
        from agent_service.langgraph_.graphs.review_graph import ReviewGraphBuilder

        super().__init__(
            config=config,
            graph_builder_class=ReviewGraphBuilder,
            name="performance_review_graph",
            description="Graph for performance review generation",
            provider=provider,
            overrides=overrides,
        )


class GraphToolFactory:
    """Factory for creating graph tools with different configurations."""

    @staticmethod
    def create_journal_summary_tool(
        provider: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
        version: str = "2.1.0",
    ) -> JournalSummaryGraphTool:
        """Create a journal summary graph tool."""
        return JournalSummaryGraphTool(provider=provider, overrides=overrides)

    @staticmethod
    def create_performance_review_tool(
        provider: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
        version: str = "1.0.0",
    ) -> PerformanceReviewGraphTool:
        """Create a performance review graph tool."""
        return PerformanceReviewGraphTool(provider=provider, overrides=overrides)

    @staticmethod
    def list_available_tools() -> List[str]:
        """List all available graph tool types."""
        return ["journal_summary_graph", "performance_review_graph"]

    @staticmethod
    def get_tool_metadata(tool_name: str) -> Optional[ToolMetadata]:
        """Get metadata for a specific tool."""
        if tool_name == "journal_summary_graph":
            tool = JournalSummaryGraphTool()
            return tool.get_metadata()
        elif tool_name == "performance_review_graph":
            tool = PerformanceReviewGraphTool()
            return tool.get_metadata()
        return None
