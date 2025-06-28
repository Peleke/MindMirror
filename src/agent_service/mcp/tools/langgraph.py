"""
LangGraph Tool Implementations

Specialized tool implementations for LangGraph backend integration.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .base import EffectBoundary, MCPTool, ToolBackend, ToolMetadata


class LangGraphNodeType(Enum):
    """Types of LangGraph nodes."""

    TOOL = "tool"
    CONDITIONAL = "conditional"
    HUMAN = "human"
    LLM = "llm"
    RETRIEVER = "retriever"
    AGGREGATOR = "aggregator"


@dataclass
class LangGraphNodeConfig:
    """Configuration for a LangGraph node."""

    node_type: LangGraphNodeType
    name: str
    description: str
    config: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


class LangGraphTool(MCPTool):
    """Base class for LangGraph-specific tools."""

    def __init__(self, node_config: LangGraphNodeConfig):
        self.node_config = node_config
        self._graph = None
        self._state = {}

    @property
    def owner_domain(self) -> str:
        """Get the owner domain for this tool."""
        return "langgraph"

    @property
    def version(self) -> str:
        """Get the tool version (semver)."""
        return "1.0.0"

    @property
    def output_schema(self) -> Dict[str, Any]:
        """Get the output schema for this tool."""
        return {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "result": {"type": "object"},
                    "state_update": {"type": "object"},
                },
                "required": ["type"],
            },
        }

    def get_metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        return ToolMetadata(
            name=self.node_config.name,
            description=self.node_config.description,
            input_schema=self._get_input_schema(),
            output_schema=self.output_schema,
            backend=ToolBackend.LANGGRAPH,
            owner_domain=self.owner_domain,
            version=self.version,
            tags=frozenset(self.node_config.tags),
            effect_boundary=self._get_effect_boundary(),
        )

    def _get_input_schema(self) -> Dict[str, Any]:
        """Get input schema for the tool."""
        return {
            "type": "object",
            "properties": {
                "state": {"type": "object", "description": "Current graph state"},
                "config": {
                    "type": "object",
                    "description": "Node-specific configuration",
                },
            },
            "required": ["state"],
        }

    def _get_effect_boundary(self) -> EffectBoundary:
        """Get effect boundary based on node type."""
        if self.node_config.node_type == LangGraphNodeType.RETRIEVER:
            return EffectBoundary.RETRIEVER
        elif self.node_config.node_type == LangGraphNodeType.LLM:
            return EffectBoundary.LLM
        elif self.node_config.node_type == LangGraphNodeType.TOOL:
            return EffectBoundary.EXTERNAL
        else:
            return EffectBoundary.PURE

    async def execute(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the LangGraph tool."""
        state = arguments.get("state", {})
        config = arguments.get("config", {})

        # Update internal state
        self._state = state

        # Execute based on node type
        if self.node_config.node_type == LangGraphNodeType.TOOL:
            return await self._execute_tool_node(config)
        elif self.node_config.node_type == LangGraphNodeType.CONDITIONAL:
            return await self._execute_conditional_node(config)
        elif self.node_config.node_type == LangGraphNodeType.HUMAN:
            return await self._execute_human_node(config)
        elif self.node_config.node_type == LangGraphNodeType.LLM:
            return await self._execute_llm_node(config)
        elif self.node_config.node_type == LangGraphNodeType.RETRIEVER:
            return await self._execute_retriever_node(config)
        elif self.node_config.node_type == LangGraphNodeType.AGGREGATOR:
            return await self._execute_aggregator_node(config)
        else:
            raise ValueError(f"Unsupported node type: {self.node_config.node_type}")

    async def _execute_tool_node(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute a tool node."""
        tool_name = config.get("tool_name", "unknown_tool")
        tool_args = config.get("tool_args", {})

        # Simulate tool execution
        result = {
            "type": "tool_result",
            "tool_name": tool_name,
            "result": f"Executed {tool_name} with args: {tool_args}",
            "state_update": {
                "last_tool": tool_name,
                "tool_result": f"Result from {tool_name}",
            },
        }

        return [result]

    async def _execute_conditional_node(
        self, config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute a conditional node."""
        condition = config.get("condition", "default")
        branches = config.get("branches", {})

        # Evaluate the condition
        condition_result = self._evaluate_condition(condition, self._state)

        # Map condition result to branch - support both boolean and string-based mapping
        if condition_result:
            # Try boolean mapping first, then condition name, then default
            next_branch = branches.get(
                "true", branches.get(condition, branches.get("default", "default"))
            )
        else:
            next_branch = branches.get("false", branches.get("default", "default"))

        result = {
            "type": "conditional_result",
            "condition": condition,
            "condition_result": condition_result,
            "next_branch": next_branch,
            "state_update": {
                "current_branch": next_branch,
                "condition_evaluated": condition,
                "condition_result": condition_result,
            },
        }

        return [result]

    async def _execute_human_node(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute a human interaction node."""
        prompt = config.get("prompt", "Please provide input:")
        input_type = config.get("input_type", "text")

        result = {
            "type": "human_interaction",
            "prompt": prompt,
            "input_type": input_type,
            "state_update": {"awaiting_human_input": True, "human_prompt": prompt},
        }

        return [result]

    async def _execute_llm_node(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute an LLM node."""
        prompt_template = config.get("prompt_template", "Process: {input}")
        model = config.get("model", "gpt-4")

        # Simulate LLM processing
        input_data = self._state.get("input", "default input")
        processed_prompt = prompt_template.format(input=input_data)

        result = {
            "type": "llm_result",
            "model": model,
            "prompt": processed_prompt,
            "response": f"LLM response for: {processed_prompt}",
            "state_update": {
                "llm_response": f"LLM response for: {processed_prompt}",
                "last_model": model,
            },
        }

        return [result]

    async def _execute_retriever_node(
        self, config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute a retriever node."""
        query = config.get("query", "")
        retriever_name = config.get("retriever_name", "default")
        top_k = config.get("top_k", 5)

        # Simulate retrieval
        retrieved_docs = [
            f"Document {i} for query: {query}" for i in range(min(top_k, 3))
        ]

        result = {
            "type": "retriever_result",
            "retriever": retriever_name,
            "query": query,
            "documents": retrieved_docs,
            "state_update": {
                "retrieved_documents": retrieved_docs,
                "last_query": query,
                "retriever_used": retriever_name,
            },
        }

        return [result]

    async def _execute_aggregator_node(
        self, config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute an aggregator node."""
        aggregation_type = config.get("type", "concat")
        inputs = config.get("inputs", [])

        # Simulate aggregation
        if aggregation_type == "concat":
            aggregated = " ".join(str(inp) for inp in inputs)
        elif aggregation_type == "sum":
            aggregated = sum(
                float(inp) for inp in inputs if str(inp).replace(".", "").isdigit()
            )
        else:
            aggregated = str(inputs)

        result = {
            "type": "aggregator_result",
            "aggregation_type": aggregation_type,
            "inputs": inputs,
            "result": aggregated,
            "state_update": {
                "aggregated_result": aggregated,
                "aggregation_type": aggregation_type,
            },
        }

        return [result]

    def _evaluate_condition(self, condition: str, state: Dict[str, Any]) -> bool:
        """Evaluate a workflow condition."""
        # Simple condition evaluation
        if condition == "always":
            return True
        elif condition == "never":
            return False
        elif condition.startswith("has_"):
            field_name = condition[4:]  # Remove "has_" prefix
            # Check for existence AND truthiness of the field (not the condition itself)
            return field_name in state and bool(state[field_name])
        else:
            # For other conditions, check if the condition field exists and is truthy
            # This handles both direct field checks and has_ conditions that are already in the state
            if condition in state:
                return bool(state[condition])
            else:
                # If the condition field doesn't exist, check if it's a has_ condition
                # that should check for a different field
                if condition.startswith("has_"):
                    field_name = condition[4:]
                    return field_name in state and bool(state[field_name])
                return False


class LangGraphWorkflowTool(LangGraphTool):
    """Tool for executing complete LangGraph workflows."""

    def __init__(self, workflow_config: Dict[str, Any]):
        self.workflow_config = workflow_config
        self.nodes = workflow_config.get("nodes", [])
        self.edges = workflow_config.get("edges", [])
        self.entry_point = workflow_config.get("entry_point", "start")

        super().__init__(
            LangGraphNodeConfig(
                node_type=LangGraphNodeType.TOOL,
                name=workflow_config.get("name", "workflow"),
                description=workflow_config.get("description", "A LangGraph workflow"),
                tags=["workflow", "langgraph"],
            )
        )

    def _get_input_schema(self) -> Dict[str, Any]:
        """Get input schema for workflow execution."""
        return {
            "type": "object",
            "properties": {
                "initial_state": {
                    "type": "object",
                    "description": "Initial state for the workflow",
                },
                "workflow_params": {
                    "type": "object",
                    "description": "Parameters for workflow execution",
                },
            },
            "required": ["initial_state"],
        }

    async def execute(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the complete workflow."""
        initial_state = arguments.get("initial_state", {})
        workflow_params = arguments.get("workflow_params", {})

        # Initialize workflow state
        current_state = initial_state.copy()
        current_state.update(
            {
                "workflow_started": True,
                "current_node": self.entry_point,
                "execution_path": [self.entry_point],
            }
        )

        # Execute workflow steps
        max_steps = workflow_params.get("max_steps", 10)
        step_count = 0

        while step_count < max_steps and current_state.get("current_node"):
            node_name = current_state["current_node"]
            node_config = self._find_node_config(node_name)

            if not node_config:
                break

            # Execute node
            node_tool = LangGraphTool(node_config)
            node_result = await node_tool.execute(
                {"state": current_state, "config": node_config.config}
            )

            # Update state
            for result in node_result:
                if "state_update" in result:
                    current_state.update(result["state_update"])

            # For conditional nodes, use the next_branch from the result
            if node_config.node_type == LangGraphNodeType.CONDITIONAL:
                for result in node_result:
                    if result.get("type") == "conditional_result":
                        next_node = result.get("next_branch")
                        if next_node:
                            current_state["current_node"] = next_node
                            current_state["execution_path"].append(next_node)
                        break
            else:
                # Determine next node for non-conditional nodes
                next_node = self._get_next_node(node_name, current_state)
                current_state["current_node"] = next_node
                if next_node:
                    current_state["execution_path"].append(next_node)

            step_count += 1

        # Finalize workflow
        current_state["workflow_completed"] = True
        current_state["total_steps"] = step_count

        return [
            {
                "type": "workflow_result",
                "final_state": current_state,
                "execution_path": current_state["execution_path"],
                "total_steps": step_count,
            }
        ]

    def _find_node_config(self, node_name: str) -> Optional[LangGraphNodeConfig]:
        """Find configuration for a specific node."""
        for node in self.nodes:
            if node.get("name") == node_name:
                return LangGraphNodeConfig(
                    node_type=LangGraphNodeType(node.get("type", "tool")),
                    name=node.get("name", ""),
                    description=node.get("description", ""),
                    config=node.get("config", {}),
                    dependencies=node.get("dependencies", []),
                    tags=node.get("tags", []),
                )
        return None

    def _get_next_node(self, current_node: str, state: Dict[str, Any]) -> Optional[str]:
        """Determine the next node in the workflow."""
        for edge in self.edges:
            if edge.get("from") == current_node:
                condition = edge.get("condition")
                if condition is None or self._evaluate_condition(condition, state):
                    return edge.get("to")
        return None


class LangGraphStateManager:
    """Manages state for LangGraph workflows."""

    def __init__(self):
        self.workflow_states = {}

    def create_workflow_state(
        self, workflow_id: str, initial_state: Dict[str, Any]
    ) -> str:
        """Create a new workflow state."""
        # Count existing states for this workflow
        existing_count = sum(
            1
            for state_data in self.workflow_states.values()
            if state_data["workflow_id"] == workflow_id
        )
        state_id = f"{workflow_id}_{existing_count}"

        self.workflow_states[state_id] = {
            "workflow_id": workflow_id,
            "state": initial_state.copy(),
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        return state_id

    def get_workflow_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow state by ID."""
        return self.workflow_states.get(state_id)

    def update_workflow_state(self, state_id: str, updates: Dict[str, Any]) -> bool:
        """Update workflow state."""
        if state_id not in self.workflow_states:
            return False

        self.workflow_states[state_id]["state"].update(updates)
        self.workflow_states[state_id]["updated_at"] = "2024-01-01T00:00:00Z"
        return True

    def delete_workflow_state(self, state_id: str) -> bool:
        """Delete workflow state."""
        if state_id in self.workflow_states:
            del self.workflow_states[state_id]
            return True
        return False

    def list_workflow_states(self, workflow_id: Optional[str] = None) -> List[str]:
        """List workflow state IDs."""
        if workflow_id:
            return [
                state_id
                for state_id, state_data in self.workflow_states.items()
                if state_data["workflow_id"] == workflow_id
            ]
        return list(self.workflow_states.keys())
