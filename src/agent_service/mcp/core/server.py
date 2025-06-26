"""
Base MCP Server Implementation

Generalized MCP server that can load plugins dynamically and handle
MCP protocol requests with proper error handling and routing.
"""

from typing import Dict, List, Any, Optional
import logging
import time
from datetime import datetime

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, Resource, Prompt, TextContent, ErrorData
    from mcp.shared.exceptions import McpError
    MCP_AVAILABLE = True
except ImportError:
    # Fallback for development/testing
    class Server:
        def __init__(self, name: str, version: str):
            self.name = name
            self.version = version
            
        def list_tools(self):
            def decorator(func):
                return func
            return decorator
            
        def list_resources(self):
            def decorator(func):
                return func
            return decorator
            
        def list_prompts(self):
            def decorator(func):
                return func
            return decorator
            
        def call_tool(self):
            def decorator(func):
                return func
            return decorator
            
        def read_resource(self):
            def decorator(func):
                return func
            return decorator
            
        def get_prompt(self):
            def decorator(func):
                return func
            return decorator
            
        def create_initialization_options(self):
            return {}
    
    class stdio_server:
        async def __aenter__(self):
            return (None, None)
        async def __aexit__(self, *args):
            pass
    
    class Tool:
        def __init__(self, name: str, description: str, inputSchema: Dict[str, Any]):
            self.name = name
            self.description = description
            self.inputSchema = inputSchema
    
    class Resource:
        def __init__(self, uri: str, name: str, description: str, mimeType: str):
            self.uri = uri
            self.name = name
            self.description = description
            self.mimeType = mimeType
    
    class Prompt:
        def __init__(self, name: str, description: str, arguments: List[Dict[str, Any]]):
            self.name = name
            self.description = description
            self.arguments = arguments
    
    class TextContent:
        def __init__(self, type: str, text: str):
            self.type = type
            self.text = text
    
    class ErrorData:
        def __init__(self, code: str, message: str):
            self.code = code
            self.message = message
    
    class McpError(Exception):
        def __init__(self, error_data: ErrorData):
            self.error_data = error_data
    
    MCP_AVAILABLE = False

from .base import MCPPlugin, MCPTool, MCPResource, MCPPrompt, create_checkpoint
from .registry import MCPPluginRegistry

logger = logging.getLogger(__name__)

# ============================================================================
# Base MCP Server
# ============================================================================

class BaseMCPServer:
    """
    Generalized MCP server that can load plugins dynamically.
    
    This server provides a complete MCP implementation with plugin support,
    proper error handling, and checkpointing capabilities.
    """
    
    def __init__(self, name: str, version: str, config: Dict[str, Any]):
        """
        Initialize the MCP server.
        
        Args:
            name: Server name
            version: Server version
            config: Server configuration
        """
        self.name = name
        self.version = version
        self.config = config
        self.server = Server(name, version)
        self.plugins: Dict[str, MCPPlugin] = {}
        self.registry = MCPPluginRegistry()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Setup MCP protocol handlers only if MCP is available
        if MCP_AVAILABLE:
            self.setup_handlers()
        
        self.logger.info(f"Initialized MCP Server: {name} v{version}")
    
    def register_plugin(self, plugin_name: str, plugin: MCPPlugin) -> None:
        """
        Register a plugin with the server.
        
        Args:
            plugin_name: Name for the plugin
            plugin: Plugin instance
        """
        self.plugins[plugin_name] = plugin
        self.logger.info(f"Registered plugin: {plugin_name}")
    
    def register_plugin_from_registry(
        self, 
        plugin_name: str, 
        config: Dict[str, Any], 
        dependencies: Dict[str, Any]
    ) -> MCPPlugin:
        """
        Register a plugin from the registry.
        
        Args:
            plugin_name: Name of the plugin to register
            config: Plugin configuration
            dependencies: Plugin dependencies
            
        Returns:
            Plugin instance
        """
        plugin = self.registry.get_or_create_instance(plugin_name, config, dependencies)
        self.register_plugin(plugin_name, plugin)
        return plugin
    
    def setup_handlers(self) -> None:
        """Setup MCP protocol handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available tools from all plugins."""
            tools = []
            for plugin_name, plugin in self.plugins.items():
                try:
                    plugin_tools = await plugin.get_tools()
                    for tool in plugin_tools:
                        tools.append(Tool(
                            name=tool.name,
                            description=tool.description,
                            inputSchema=tool.input_schema,
                        ))
                except Exception as e:
                    self.logger.error(f"Failed to get tools from plugin {plugin_name}: {e}")
            
            self.logger.debug(f"Listed {len(tools)} tools")
            return tools
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List all available resources from all plugins."""
            resources = []
            for plugin_name, plugin in self.plugins.items():
                try:
                    plugin_resources = await plugin.get_resources()
                    for resource in plugin_resources:
                        resources.append(Resource(
                            uri=resource.uri,
                            name=resource.name,
                            description=resource.description,
                            mimeType=resource.mime_type,
                        ))
                except Exception as e:
                    self.logger.error(f"Failed to get resources from plugin {plugin_name}: {e}")
            
            self.logger.debug(f"Listed {len(resources)} resources")
            return resources
        
        @self.server.list_prompts()
        async def list_prompts() -> List[Prompt]:
            """List all available prompts from all plugins."""
            prompts = []
            for plugin_name, plugin in self.plugins.items():
                try:
                    plugin_prompts = await plugin.get_prompts()
                    for prompt in plugin_prompts:
                        prompts.append(Prompt(
                            name=prompt.name,
                            description=prompt.description,
                            arguments=prompt.arguments,
                        ))
                except Exception as e:
                    self.logger.error(f"Failed to get prompts from plugin {plugin_name}: {e}")
            
            self.logger.debug(f"Listed {len(prompts)} prompts")
            return prompts
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute a tool by name with arguments."""
            start_time = time.time()
            thread_id = self._get_thread_id()
            
            try:
                # Find which plugin provides this tool
                plugin_name = None
                for p_name, plugin in self.plugins.items():
                    try:
                        plugin_tools = await plugin.get_tools()
                        if any(tool.name == name for tool in plugin_tools):
                            plugin_name = p_name
                            break
                    except Exception as e:
                        self.logger.error(f"Failed to get tools from plugin {p_name}: {e}")
                        continue
                
                if plugin_name is None:
                    raise McpError(ErrorData(
                        code="INVALID_PARAMS",
                        message=f"Unknown tool: {name}"
                    ))
                
                # Execute the tool
                plugin = self.plugins[plugin_name]
                result = await plugin.execute_tool(name, arguments)
                
                # Create checkpoint
                execution_time = time.time() - start_time
                checkpoint = create_checkpoint(
                    plugin_name=plugin_name,
                    tool_name=name,
                    input_state=arguments,
                    output_state=result,
                    execution_time=execution_time,
                    thread_id=thread_id,
                    metadata={"server_name": self.name}
                )
                
                # Log checkpoint (in production, this would be saved to persistent storage)
                self.logger.debug(f"Tool execution checkpoint: {checkpoint}")
                
                # Convert result to MCP format
                content = []
                for item in result:
                    if isinstance(item, dict):
                        if "type" in item and "text" in item:
                            content.append(TextContent(type=item["type"], text=item["text"]))
                        else:
                            content.append(TextContent(type="text", text=str(item)))
                    else:
                        content.append(TextContent(type="text", text=str(item)))
                
                self.logger.info(f"Executed tool {name} from plugin {plugin_name} in {execution_time:.3f}s")
                return content
                
            except McpError:
                # Re-raise MCP errors as-is
                raise
            except Exception as e:
                execution_time = time.time() - start_time
                self.logger.error(f"Tool execution failed: {name} - {e}")
                
                # Create error checkpoint
                checkpoint = create_checkpoint(
                    plugin_name=plugin_name or "unknown",
                    tool_name=name,
                    input_state=arguments,
                    output_state={"error": str(e)},
                    execution_time=execution_time,
                    thread_id=thread_id,
                    metadata={"server_name": self.name, "error": True}
                )
                
                self.logger.debug(f"Error checkpoint: {checkpoint}")
                
                raise McpError(ErrorData(
                    code="INTERNAL_ERROR",
                    message=f"Tool execution failed: {str(e)}"
                ))
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> List[TextContent]:
            """Read a resource by URI."""
            start_time = time.time()
            thread_id = self._get_thread_id()
            
            try:
                # Find which plugin provides this resource
                plugin_name = None
                for p_name, plugin in self.plugins.items():
                    try:
                        plugin_resources = await plugin.get_resources()
                        if any(resource.uri == uri for resource in plugin_resources):
                            plugin_name = p_name
                            break
                    except Exception as e:
                        self.logger.error(f"Failed to get resources from plugin {p_name}: {e}")
                        continue
                
                if plugin_name is None:
                    raise McpError(ErrorData(
                        code="INVALID_PARAMS",
                        message=f"Unknown resource: {uri}"
                    ))
                
                # Read the resource
                plugin = self.plugins[plugin_name]
                result = await plugin.read_resource(uri)
                
                # Create checkpoint
                execution_time = time.time() - start_time
                checkpoint = create_checkpoint(
                    plugin_name=plugin_name,
                    tool_name="read_resource",
                    input_state={"uri": uri},
                    output_state=result,
                    execution_time=execution_time,
                    thread_id=thread_id,
                    metadata={"server_name": self.name, "resource_uri": uri}
                )
                
                self.logger.debug(f"Resource read checkpoint: {checkpoint}")
                
                # Convert result to MCP format
                content = []
                for item in result:
                    if isinstance(item, dict):
                        if "type" in item and "text" in item:
                            content.append(TextContent(type=item["type"], text=item["text"]))
                        else:
                            content.append(TextContent(type="text", text=str(item)))
                    else:
                        content.append(TextContent(type="text", text=str(item)))
                
                self.logger.info(f"Read resource {uri} from plugin {plugin_name} in {execution_time:.3f}s")
                return content
                
            except McpError:
                raise
            except Exception as e:
                execution_time = time.time() - start_time
                self.logger.error(f"Resource read failed: {uri} - {e}")
                
                checkpoint = create_checkpoint(
                    plugin_name=plugin_name or "unknown",
                    tool_name="read_resource",
                    input_state={"uri": uri},
                    output_state={"error": str(e)},
                    execution_time=execution_time,
                    thread_id=thread_id,
                    metadata={"server_name": self.name, "error": True, "resource_uri": uri}
                )
                
                self.logger.debug(f"Error checkpoint: {checkpoint}")
                
                raise McpError(ErrorData(
                    code="INTERNAL_ERROR",
                    message=f"Resource read failed: {str(e)}"
                ))
        
        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
            """Get prompt content by name with optional arguments."""
            start_time = time.time()
            thread_id = self._get_thread_id()
            
            try:
                # Find which plugin provides this prompt
                plugin_name = None
                for p_name, plugin in self.plugins.items():
                    try:
                        plugin_prompts = await plugin.get_prompts()
                        if any(prompt.name == name for prompt in plugin_prompts):
                            plugin_name = p_name
                            break
                    except Exception as e:
                        self.logger.error(f"Failed to get prompts from plugin {p_name}: {e}")
                        continue
                
                if plugin_name is None:
                    raise McpError(ErrorData(
                        code="INVALID_PARAMS",
                        message=f"Unknown prompt: {name}"
                    ))
                
                # Get the prompt content
                plugin = self.plugins[plugin_name]
                result = await plugin.get_prompt_content(name, arguments)
                
                # Create checkpoint
                execution_time = time.time() - start_time
                checkpoint = create_checkpoint(
                    plugin_name=plugin_name,
                    tool_name="get_prompt",
                    input_state={"name": name, "arguments": arguments},
                    output_state=result,
                    execution_time=execution_time,
                    thread_id=thread_id,
                    metadata={"server_name": self.name, "prompt_name": name}
                )
                
                self.logger.debug(f"Prompt get checkpoint: {checkpoint}")
                
                self.logger.info(f"Got prompt {name} from plugin {plugin_name} in {execution_time:.3f}s")
                return result
                
            except McpError:
                raise
            except Exception as e:
                execution_time = time.time() - start_time
                self.logger.error(f"Prompt get failed: {name} - {e}")
                
                checkpoint = create_checkpoint(
                    plugin_name=plugin_name or "unknown",
                    tool_name="get_prompt",
                    input_state={"name": name, "arguments": arguments},
                    output_state={"error": str(e)},
                    execution_time=execution_time,
                    thread_id=thread_id,
                    metadata={"server_name": self.name, "error": True, "prompt_name": name}
                )
                
                self.logger.debug(f"Error checkpoint: {checkpoint}")
                
                raise McpError(ErrorData(
                    code="INTERNAL_ERROR",
                    message=f"Prompt retrieval failed: {str(e)}"
                ))
    
    def _get_thread_id(self) -> str:
        """Get current thread ID for checkpointing."""
        import threading
        return str(threading.get_ident())
    
    async def run(self) -> None:
        """Run the MCP server."""
        self.logger.info(f"Starting MCP Server: {self.name} v{self.version}")
        
        try:
            options = self.server.create_initialization_options()
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(read_stream, write_stream, options, raise_exceptions=True)
        except Exception as e:
            self.logger.error(f"MCP Server failed: {e}")
            raise
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information and statistics."""
        return {
            "name": self.name,
            "version": self.version,
            "plugins_count": len(self.plugins),
            "plugins": list(self.plugins.keys()),
            "registry_info": self.registry.get_registry_info()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the server and all plugins."""
        plugin_health = {}
        
        for plugin_name, plugin in self.plugins.items():
            try:
                health = await plugin.health_check()
                plugin_health[plugin_name] = health
            except Exception as e:
                plugin_health[plugin_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "server_status": "healthy",
            "server_name": self.name,
            "server_version": self.version,
            "plugins_count": len(self.plugins),
            "plugin_health": plugin_health
        } 