"""
LLM service using the new prompt system with LangChain.

This service provides LLM functionality using the new prompt storage
and rendering system with LangChain for better integration with LangGraph workflows.
Now integrates with the enhanced MCP tool registry for tool orchestration.
"""

import logging
import os
from typing import List, Dict, Any, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.language_models import BaseLanguageModel

from agent_service.app.graphql.types.suggestion_types import PerformanceReview
from agent_service.llms.prompts.service import PromptService
from agent_service.llms.prompts.factory import PromptServiceFactory, get_prompt_service
from agent_service.llms.provider_manager import ProviderManager, get_provider_manager
from agent_service.mcp.tools.base import ToolRegistry, get_global_registry

logger = logging.getLogger(__name__)


class LLMService:
    """
    LLM service using the new prompt system with LangChain.
    
    This service provides LLM functionality using the new prompt storage
    and rendering system with LangChain for better integration with LangGraph workflows.
    
    Now integrates with the new provider system for enhanced LLM management and fallbacks.
    Enhanced with MCP tool registry integration for tool orchestration.
    """

    def __init__(
        self, 
        prompt_service: Optional[PromptService] = None, 
        llm: Optional[BaseLanguageModel] = None,
        provider_manager: Optional[ProviderManager] = None,
        tool_registry: Optional[ToolRegistry] = None
    ):
        """
        Initialize the LLM service.
        
        Args:
            prompt_service: Optional prompt service instance. If not provided,
                          creates a default service based on environment configuration.
            llm: DEPRECATED - Optional LangChain LLM instance. If not provided, will be created per request.
                 Use provider_manager for better LLM management.
            provider_manager: Optional provider manager instance. If not provided,
                            uses the global provider manager.
            tool_registry: Optional tool registry instance. If not provided,
                          uses the global tool registry.
        """
        if prompt_service is None:
            # Use the configurable factory to create prompt service
            self.prompt_service = PromptServiceFactory.create_from_environment()
            logger.info("Created LLM service with environment-configured prompt service")
        else:
            self.prompt_service = prompt_service
            logger.info("Created LLM service with provided prompt service")
        
        # DEPRECATED: Store the LLM instance (will be configured per request if not provided)
        # This is kept for backward compatibility but should be replaced with provider_manager
        self.llm = llm
        
        # NEW: Provider manager for enhanced LLM management
        if provider_manager is None:
            self.provider_manager = get_provider_manager()
            logger.info("Created LLM service with global provider manager")
        else:
            self.provider_manager = provider_manager
            logger.info("Created LLM service with provided provider manager")
        
        # NEW: Tool registry for enhanced tool orchestration
        if tool_registry is None:
            self.tool_registry = get_global_registry()
            logger.info("Created LLM service with global tool registry")
        else:
            self.tool_registry = tool_registry
            logger.info("Created LLM service with provided tool registry")

    # NEW: Tool Registry Integration Methods
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any], version: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Execute a tool from the registry.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool
            version: Optional version of the tool to use
            
        Returns:
            Tool execution results
            
        Raises:
            ValueError: If tool is not found
        """
        try:
            return await self.tool_registry.execute_tool(tool_name, arguments, version)
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            raise
    
    def get_tool_metadata(self, tool_name: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific tool.
        
        Args:
            tool_name: Name of the tool
            version: Optional version of the tool
            
        Returns:
            Tool metadata or None if not found
        """
        metadata = self.tool_registry.get_tool_metadata(tool_name, version)
        if metadata:
            return {
                "name": metadata.name,
                "description": metadata.description,
                "owner_domain": metadata.owner_domain,
                "version": metadata.version,
                "backend": metadata.backend.value,
                "effect_boundary": metadata.effect_boundary.value,
                "tags": list(metadata.tags),
                "subtools": list(metadata.subtools),
                "input_schema": metadata.input_schema,
                "output_schema": metadata.output_schema
            }
        return None
    
    def list_tools(self, 
                   backend: Optional[str] = None, 
                   tags: Optional[List[str]] = None,
                   owner_domain: Optional[str] = None,
                   version: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available tools with optional filtering.
        
        Args:
            backend: Filter by backend (langgraph, prompt, retriever, etc.)
            tags: Filter by tags
            owner_domain: Filter by owner domain
            version: Filter by version
            
        Returns:
            List of tool metadata dictionaries
        """
        tools = self.tool_registry.list_tools(backend, tags, owner_domain, version)
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "owner_domain": tool.owner_domain,
                "version": tool.version,
                "backend": tool.backend.value,
                "effect_boundary": tool.effect_boundary.value,
                "tags": list(tool.tags),
                "subtools": list(tool.subtools),
                "input_schema": tool.input_schema,
                "output_schema": tool.output_schema
            }
            for tool in tools
        ]
    
    def list_tool_names(self) -> List[str]:
        """
        List all registered tool names.
        
        Returns:
            List of tool names
        """
        return self.tool_registry.list_tool_names()
    
    async def execute_subtool(self, tool_name: str, subtool_name: str, arguments: Dict[str, Any], version: Optional[str] = None) -> Any:
        """
        Execute a subtool of a specific tool.
        
        Args:
            tool_name: Name of the parent tool
            subtool_name: Name of the subtool to execute
            arguments: Arguments to pass to the subtool
            version: Optional version of the tool
            
        Returns:
            Subtool execution result
            
        Raises:
            ValueError: If tool or subtool is not found
        """
        tool = self.tool_registry.get_tool(tool_name, version)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")
        
        if subtool_name not in tool.list_subtools():
            raise ValueError(f"Subtool {subtool_name} not found in tool {tool_name}")
        
        try:
            return await tool.execute_subtool(subtool_name, arguments)
        except Exception as e:
            logger.error(f"Error executing subtool {subtool_name} of tool {tool_name}: {e}")
            raise

    # ENHANCED: Journal Summary with Tool Registry Integration
    
    async def get_journal_summary(self, journal_entries: List[Dict[str, Any]], style: str = "concise") -> str:
        """
        Generates a concise summary from a list of journal entries.
        
        Enhanced to use tool registry if available, with fallback to direct prompt execution.

        Args:
            journal_entries: A list of journal entries, each represented as a dict.
            style: Summary style ("concise" or "detailed")

        Returns:
            A string containing the AI-generated summary.
        """
        if not journal_entries:
            return "No recent journal entries to summarize."

        # Try to use tool registry first
        try:
            if self.tool_registry and "journal_summary_graph" in self.tool_registry.list_tool_names():
                logger.info("Using journal_summary_graph tool from registry")
                result = await self.execute_tool("journal_summary_graph", {
                    "journal_entries": journal_entries,
                    "style": style
                })
                
                if result and len(result) > 0:
                    # Extract summary from tool result
                    if isinstance(result[0], dict) and "summary" in result[0]:
                        return result[0]["summary"]
                    elif isinstance(result[0], dict) and "text" in result[0]:
                        return result[0]["text"]
                    elif isinstance(result[0], str):
                        return result[0]
                    else:
                        # Fallback to string representation
                        return str(result[0])
                        
        except Exception as e:
            logger.warning(f"Tool registry execution failed, falling back to direct prompt: {e}")

        # Fallback to direct prompt execution (original implementation)
        logger.info("Using direct prompt execution for journal summary")
        return await self._get_journal_summary_direct(journal_entries, style)

    async def _get_journal_summary_direct(self, journal_entries: List[Dict[str, Any]], style: str = "concise") -> str:
        """
        Direct prompt execution for journal summary (fallback method).
        
        Args:
            journal_entries: A list of journal entries
            style: Summary style
            
        Returns:
            Generated summary
        """
        # Consolidate journal content into a single block for the prompt
        content_block = "\n\n---\n\n".join(
            [entry.get("text", "") for entry in journal_entries]
        )

        try:
            # Render the prompt using the prompt service
            rendered_prompt = self.prompt_service.render_prompt(
                "journal_summary",
                {"content_block": content_block, "style": style}
            )
            
            # Get prompt metadata for LLM configuration
            prompt_info = self.prompt_service.get_prompt("journal_summary")
            metadata = prompt_info.metadata
            
            # Get LLM using new provider system
            llm = self._get_llm_for_task("journal_summary", metadata)
            
            # Create the message and invoke the LLM
            message = HumanMessage(content=rendered_prompt)
            response = await llm.ainvoke([message])
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating journal summary: {e}")
            return f"Error generating summary: {str(e)}"

    # ENHANCED: Performance Review with Tool Registry Integration
    
    async def get_performance_review(
        self, journal_entries: List[Dict[str, Any]], period: str = "month"
    ) -> PerformanceReview:
        """
        Generates a performance review from a list of journal entries.
        
        Enhanced to use tool registry if available, with fallback to direct prompt execution.

        Args:
            journal_entries: A list of journal entries, each represented as a dict.
            period: Review period ("week", "month", "quarter", "year")

        Returns:
            A PerformanceReview object containing the AI-generated review.
        """
        if not journal_entries:
            return PerformanceReview(
                key_success="No recent journal entries to review.",
                improvement_area="Consider adding more journal entries for better insights.",
                journal_prompt="What would you like to focus on in your next journal entry?"
            )

        # Try to use tool registry first
        try:
            if self.tool_registry and "performance_review_graph" in self.tool_registry.list_tool_names():
                logger.info("Using performance_review_graph tool from registry")
                result = await self.execute_tool("performance_review_graph", {
                    "journal_entries": journal_entries,
                    "period": period
                })
                
                if result and len(result) > 0:
                    # Extract review from tool result
                    if isinstance(result[0], dict):
                        if "review" in result[0]:
                            return self._parse_performance_review_response(result[0]["review"])
                        elif "text" in result[0]:
                            return self._parse_performance_review_response(result[0]["text"])
                        elif "result" in result[0] and isinstance(result[0]["result"], dict):
                            return self._parse_performance_review_response(str(result[0]["result"]))
                        
        except Exception as e:
            logger.warning(f"Tool registry execution failed, falling back to direct prompt: {e}")

        # Fallback to direct prompt execution (original implementation)
        logger.info("Using direct prompt execution for performance review")
        return await self._get_performance_review_direct(journal_entries, period)

    async def _get_performance_review_direct(self, journal_entries: List[Dict[str, Any]], period: str = "month") -> PerformanceReview:
        """
        Direct prompt execution for performance review (fallback method).
        
        Args:
            journal_entries: A list of journal entries
            period: Review period
            
        Returns:
            Generated performance review
        """
        # Consolidate journal content into a single block for the prompt
        content_block = "\n\n---\n\n".join(
            [entry.get("text", "") for entry in journal_entries]
        )

        try:
            # Render the prompt using the prompt service
            rendered_prompt = self.prompt_service.render_prompt(
                "performance_review",
                {"content_block": content_block, "period": period}
            )
            
            # Get prompt metadata for LLM configuration
            prompt_info = self.prompt_service.get_prompt("performance_review")
            metadata = prompt_info.metadata
            
            # Get LLM using new provider system
            llm = self._get_llm_for_task("performance_review", metadata)
            
            # Create the message and invoke the LLM
            message = HumanMessage(content=rendered_prompt)
            response = llm.invoke([message])

            # Parse the structured response
            return self._parse_performance_review_response(response.content)
            
        except Exception as e:
            logger.error(f"Error generating performance review: {e}")
            return PerformanceReview(
                key_success="Unable to generate performance review.",
                improvement_area="Consider adding more detailed journal entries.",
                journal_prompt="What would you like to focus on in your next journal entry?"
            )

    # ENHANCED: Tool Registry Health Check
    
    def get_tool_registry_health(self) -> Dict[str, Any]:
        """
        Get health status of the tool registry.
        
        Returns:
            Tool registry health information
        """
        try:
            return self.tool_registry.health_check()
        except Exception as e:
            logger.error(f"Error getting tool registry health: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    # EXISTING METHODS (unchanged for backward compatibility)

    def _get_llm_for_task(self, task_name: str, metadata: Dict[str, Any]) -> BaseLanguageModel:
        """
        Get an LLM instance configured for a specific task.
        
        Args:
            task_name: Name of the task (e.g., "journal_summary", "performance_review")
            metadata: Prompt metadata containing LLM configuration
            
        Returns:
            Configured LLM instance
        """
        try:
            # Try to create LLM using provider manager with fallback
            config = {
                "model": metadata.get("model", "gpt-4o"),
                "temperature": metadata.get("temperature", 0.7),
                "max_tokens": metadata.get("max_tokens", 1000),
                "streaming": metadata.get("streaming", False)
            }
            
            # Use provider manager to create LLM with fallback
            return self.provider_manager.create_model_with_fallback(config)
            
        except Exception as e:
            logger.warning(f"Failed to create LLM with provider manager: {e}")
            
            # DEPRECATED: Fallback to direct ChatOpenAI creation
            logger.warning("Falling back to direct ChatOpenAI creation (DEPRECATED)")
            return ChatOpenAI(
                model=metadata.get("model", "gpt-4o"),
                temperature=metadata.get("temperature", 0.7),
                max_tokens=metadata.get("max_tokens", 1000),
            )

    def _parse_performance_review_response(self, response: str) -> PerformanceReview:
        """
        Parse the structured response from the LLM into a PerformanceReview object.
        
        Args:
            response: The raw response from the LLM
            
        Returns:
            Parsed PerformanceReview object
        """
        try:
            # Extract sections from the structured response
            lines = response.strip().split('\n')
            key_success = ""
            improvement_area = ""
            journal_prompt = ""
            
            current_section = None
            for line in lines:
                line = line.strip()
                if line.startswith("SUCCESS:"):
                    current_section = "success"
                    key_success = line.replace("SUCCESS:", "").strip()
                elif line.startswith("IMPROVEMENT:"):
                    current_section = "improvement"
                    improvement_area = line.replace("IMPROVEMENT:", "").strip()
                elif line.startswith("PROMPT:"):
                    current_section = "prompt"
                    journal_prompt = line.replace("PROMPT:", "").strip()
                elif current_section and line:
                    # Continue building the current section
                    if current_section == "success":
                        key_success += " " + line
                    elif current_section == "improvement":
                        improvement_area += " " + line
                    elif current_section == "prompt":
                        journal_prompt += " " + line
            
            # Clean up the extracted text
            key_success = key_success.strip()
            improvement_area = improvement_area.strip()
            journal_prompt = journal_prompt.strip()
            
            # Provide defaults if sections are missing
            if not key_success:
                key_success = "No specific success identified in the review period."
            if not improvement_area:
                improvement_area = "Consider adding more detailed journal entries for better insights."
            if not journal_prompt:
                journal_prompt = "What would you like to focus on in your next journal entry?"
            
            return PerformanceReview(
                key_success=key_success,
                improvement_area=improvement_area,
                journal_prompt=journal_prompt
            )
            
        except Exception as e:
            logger.error(f"Error parsing performance review response: {e}")
            return PerformanceReview(
                key_success="Unable to parse performance review response.",
                improvement_area="Consider adding more detailed journal entries.",
                journal_prompt="What would you like to focus on in your next journal entry?"
            )
    
    # NEW: Provider-aware methods
    
    def get_llm(self, task: str, provider: Optional[str] = None, overrides: Optional[Dict[str, Any]] = None) -> BaseLanguageModel:
        """
        Get an LLM instance for a specific task with optional provider and overrides.
        
        Args:
            task: Name of the task (e.g., "journal_summary", "performance_review")
            provider: Optional provider name to use (e.g., "openai", "ollama", "gemini")
            overrides: Optional configuration overrides
            
        Returns:
            Configured LLM instance
        """
        try:
            # Get prompt metadata for the task
            prompt_info = self.prompt_service.get_prompt(task)
            metadata = prompt_info.metadata
            
            # Start with metadata configuration
            config = {
                "model": metadata.get("model", "gpt-4o"),
                "temperature": metadata.get("temperature", 0.7),
                "max_tokens": metadata.get("max_tokens", 1000),
                "streaming": metadata.get("streaming", False)
            }
            
            # Apply overrides if provided
            if overrides:
                config.update(overrides)
            
            # Use specific provider if requested
            if provider:
                config["provider"] = provider
                return self.provider_manager.create_model(config)
            else:
                # Use provider manager with fallback
                return self.provider_manager.create_model_with_fallback(config)
                
        except Exception as e:
            logger.error(f"Error getting LLM for task '{task}': {e}")
            raise
    
    def get_provider_status(self, provider_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get status of LLM providers.
        
        Args:
            provider_name: Optional provider name to check
            
        Returns:
            Provider status information
        """
        return self.provider_manager.get_provider_status(provider_name)
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available LLM providers.
        
        Returns:
            List of available provider names
        """
        return self.provider_manager.list_available_providers()
    
    def get_working_providers(self) -> List[str]:
        """
        Get list of working LLM providers.
        
        Returns:
            List of working provider names
        """
        return self.provider_manager.get_working_providers()
    
    # DEPRECATED: Legacy methods for backward compatibility
    
    def get_prompt_service(self) -> PromptService:
        """Get the underlying prompt service."""
        return self.prompt_service
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the LLM service.
        
        Returns:
            Health status dictionary
        """
        try:
            # Check prompt service health
            prompt_health = self.prompt_service.health_check()
            
            # Check if required prompts exist
            required_prompts = ["journal_summary", "performance_review"]
            missing_prompts = []
            
            for prompt_name in required_prompts:
                try:
                    self.prompt_service.get_prompt(prompt_name)
                except Exception:
                    missing_prompts.append(prompt_name)
            
            # Check provider status
            provider_status = self.get_provider_status()
            working_providers = self.get_working_providers()
            
            # Check tool registry health
            tool_registry_health = self.get_tool_registry_health()
            
            return {
                "status": "healthy" if not missing_prompts and working_providers else "degraded",
                "prompt_service": prompt_health,
                "missing_prompts": missing_prompts,
                "provider_status": provider_status,
                "working_providers": working_providers,
                "tool_registry": tool_registry_health,
                "llm_configured": self.llm is not None  # DEPRECATED
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            } 