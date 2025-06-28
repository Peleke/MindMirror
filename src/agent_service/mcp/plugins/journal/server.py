"""
Journal Plugin Server

MCP plugin for journal processing capabilities with real retriever integration.
"""

from typing import Any, Dict, List, Optional

from agent_service.mcp.core.base import (MCPPlugin, MCPPrompt, MCPResource,
                                         MCPTool)
from agent_service.mcp.retrievers.base import Retriever, RetrieverRegistry
from agent_service.mcp.retrievers.journal import JournalRetrieverFactory

from .metadata import JournalPluginMetadata


class JournalPlugin(MCPPlugin):
    """MCP plugin for journal processing capabilities with real retriever integration."""

    def __init__(self, config: Dict[str, Any], dependencies: Dict[str, Any]):
        # Get metadata from the centralized metadata class
        metadata = JournalPluginMetadata.get_metadata()

        # Initialize with metadata
        super().__init__(config, dependencies)

        # Set metadata attributes
        self.version = metadata.version
        self.description = metadata.description
        self.dependencies = metadata.dependencies
        self.tags = metadata.tags

        # Extract dependencies
        self.retriever_registry = dependencies["retriever_registry"]
        self.llm_service = dependencies["llm_service"]
        self.journal_client = dependencies["journal_client"]

        # Get user_id from config
        self.user_id = config.get("user_id")
        if not self.user_id:
            raise ValueError("JournalPlugin requires user_id in config")

        # Create and register journal retriever if not already present
        if "journal" not in self.retriever_registry.list():
            factory = JournalRetrieverFactory(self.journal_client)
            retriever = factory.create_retriever(self.user_id)
            self.retriever_registry.register("journal", retriever)

        self.journal_retriever = self.retriever_registry.get("journal")
        if not self.journal_retriever:
            raise ValueError("Journal retriever not found in registry")

    def _validate_dependencies(self) -> None:
        """Validate required dependencies."""
        required_deps = ["retriever_registry", "llm_service", "journal_client"]
        for dep in required_deps:
            if dep not in self.dependencies:
                raise ValueError(f"JournalPlugin requires {dep} dependency")

        if not isinstance(self.dependencies["retriever_registry"], RetrieverRegistry):
            raise ValueError(
                "retriever_registry must be an instance of RetrieverRegistry"
            )

    def _create_tools(self) -> List[MCPTool]:
        """Create journal plugin tools using metadata."""
        tool_metadata = JournalPluginMetadata.get_tool_metadata()
        tools = []

        for tool_name, metadata in tool_metadata.items():
            tool = MCPTool(
                name=metadata["name"],
                description=metadata["description"],
                input_schema=metadata["input_schema"],
                tags=metadata["tags"],
                metadata={
                    "category": metadata["category"],
                    "uses_retriever": metadata["uses_retriever"],
                },
            )
            tools.append(tool)

        return tools

    def _create_resources(self) -> List[MCPResource]:
        """Create journal plugin resources using metadata."""
        resource_metadata = JournalPluginMetadata.get_resource_metadata(self.user_id)
        resources = []

        for resource_name, metadata in resource_metadata.items():
            resource = MCPResource(
                uri=metadata["uri"],
                name=metadata["name"],
                description=metadata["description"],
                mime_type=metadata["mime_type"],
                metadata=metadata["metadata"],
            )
            resources.append(resource)

        return resources

    def _create_prompts(self) -> List[MCPPrompt]:
        """Create journal plugin prompts using metadata."""
        prompt_metadata = JournalPluginMetadata.get_prompt_metadata()
        prompts = []

        for prompt_name, metadata in prompt_metadata.items():
            prompt = MCPPrompt(
                name=metadata["name"],
                description=metadata["description"],
                arguments=metadata["arguments"],
                metadata=metadata["metadata"],
            )
            prompts.append(prompt)

        return prompts

    async def execute_tool(
        self, name: str, arguments: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute journal plugin tools."""
        if name == "summarize_journals":
            return await self._summarize_journals(arguments)
        elif name == "generate_review":
            return await self._generate_review(arguments)
        elif name == "list_retrievers":
            return await self._list_retrievers(arguments)
        elif name == "get_entries_by_type":
            return await self._get_entries_by_type(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

    async def read_resource(self, uri: str) -> List[Dict[str, Any]]:
        """Read journal plugin resources."""
        if uri == "mindmirror://journal/retrievers":
            return await self._get_retrievers_info()
        elif uri == "mindmirror://journal/entries":
            return await self._get_journal_entries()
        elif uri == f"mindmirror://journal/user/{self.user_id}/entries":
            return await self._get_user_journal_entries()
        else:
            raise ValueError(f"Unknown resource: {uri}")

    async def get_prompt_content(
        self, name: str, arguments: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get journal plugin prompt content."""
        if name == "summarize_journals":
            return await self._get_summarize_prompt(arguments)
        else:
            raise ValueError(f"Unknown prompt: {name}")

    async def _summarize_journals(
        self, arguments: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Summarize journal entries using real retriever architecture."""
        query = arguments["query"]
        style = arguments.get("style", "concise")
        entry_types = arguments.get("entry_types", [])

        # Get retriever
        retriever = self._get_retriever()

        # Retrieve relevant documents
        documents = await retriever.retrieve(query)

        # Filter by entry types if specified
        if entry_types:
            documents = [
                doc
                for doc in documents
                if doc.metadata.get("entry_type") in entry_types
            ]

        # Generate summary using LLM service
        content = "\n\n".join([doc.page_content for doc in documents])
        summary = await self.llm_service.get_journal_summary(content, style)

        return [{"type": "text", "text": summary}]

    async def _generate_review(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate a performance review from journal entries."""
        query = arguments["query"]
        period = arguments.get("period", "month")
        focus_areas = arguments.get("focus_areas", [])

        # Get retriever
        retriever = self._get_retriever()

        # Retrieve relevant documents
        documents = await retriever.retrieve(query)

        # Generate review using LLM service
        content = "\n\n".join([doc.page_content for doc in documents])
        review = await self.llm_service.get_performance_review(content, period)

        return [{"type": "text", "text": review}]

    async def _get_entries_by_type(
        self, arguments: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get journal entries filtered by type."""
        entry_type = arguments["entry_type"]
        days_back = arguments.get("days_back", 30)

        # Get retriever
        retriever = self._get_retriever()

        # Use the specialized method for type filtering
        if hasattr(retriever, "get_entries_by_type"):
            documents = await retriever.get_entries_by_type(entry_type, days_back)
        else:
            # Fallback to general retrieve and filter
            documents = await retriever.retrieve(f"entries from last {days_back} days")
            documents = [
                doc for doc in documents if doc.metadata.get("entry_type") == entry_type
            ]

        return [{"type": "text", "text": doc.page_content} for doc in documents]

    async def _list_retrievers(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """List available retrievers for journal data."""
        retrievers = []
        for name in self.retriever_registry.list():
            metadata = self.retriever_registry.get_metadata(name)
            if metadata:
                retrievers.append(
                    {
                        "name": name,
                        "type": metadata.type,
                        "backend": metadata.backend,
                        "description": metadata.description,
                        "capabilities": metadata.capabilities,
                    }
                )

        return [{"type": "text", "text": str(retrievers)}]

    def _get_retriever(self) -> Retriever:
        """Get the journal retriever."""
        return self.journal_retriever

    async def _get_retrievers_info(self) -> List[Dict[str, Any]]:
        """Get information about available retrievers."""
        info = []
        for name in self.retriever_registry.list():
            metadata = self.retriever_registry.get_metadata(name)
            if metadata:
                info.append(
                    {
                        "name": name,
                        "metadata": {
                            "type": metadata.type,
                            "backend": metadata.backend,
                            "description": metadata.description,
                            "capabilities": metadata.capabilities,
                        },
                    }
                )

        return [{"type": "text", "text": str(info)}]

    async def _get_journal_entries(self) -> List[Dict[str, Any]]:
        """Get journal entries via retriever."""
        # Use default retriever to get recent entries
        documents = await self.journal_retriever.retrieve("recent entries")
        return [{"type": "text", "text": doc.page_content} for doc in documents]

    async def _get_user_journal_entries(self) -> List[Dict[str, Any]]:
        """Get journal entries for the specific user."""
        # Use default retriever to get recent entries for this user
        documents = await self.journal_retriever.retrieve("recent entries")
        return [{"type": "text", "text": doc.page_content} for doc in documents]

    async def _get_summarize_prompt(
        self, arguments: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get summarize prompt content."""
        query = arguments.get("query", "") if arguments else ""
        style = arguments.get("style", "concise") if arguments else "concise"

        return {
            "description": f"Summarize journal entries for query '{query}' in {style} style",
            "messages": [
                {
                    "role": "user",
                    "content": f"Please summarize the following journal entries in a {style} style:\n\nQuery: {query}\n\n[Retrieved content will be inserted here]",
                }
            ],
        }
