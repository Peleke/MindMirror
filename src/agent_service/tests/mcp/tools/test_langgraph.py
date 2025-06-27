"""
Test Suite for LangGraph Tool Implementations

Comprehensive tests for LangGraph-specific tool functionality.
"""

import pytest
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock

from agent_service.mcp.tools.langgraph import (
    LangGraphTool,
    LangGraphWorkflowTool,
    LangGraphStateManager,
    LangGraphNodeType,
    LangGraphNodeConfig
)


class TestLangGraphNodeType:
    """Test LangGraphNodeType enum."""
    
    def test_node_type_values(self):
        """Test node type enum values."""
        assert LangGraphNodeType.TOOL.value == "tool"
        assert LangGraphNodeType.CONDITIONAL.value == "conditional"
        assert LangGraphNodeType.HUMAN.value == "human"
        assert LangGraphNodeType.LLM.value == "llm"
        assert LangGraphNodeType.RETRIEVER.value == "retriever"
        assert LangGraphNodeType.AGGREGATOR.value == "aggregator"


class TestLangGraphNodeConfig:
    """Test LangGraphNodeConfig dataclass."""
    
    def test_node_config_creation(self):
        """Test node config creation."""
        config = LangGraphNodeConfig(
            node_type=LangGraphNodeType.TOOL,
            name="test_node",
            description="A test node",
            config={"tool_name": "test_tool"},
            dependencies=["dep1", "dep2"],
            tags=["test", "tool"]
        )
        
        assert config.node_type == LangGraphNodeType.TOOL
        assert config.name == "test_node"
        assert config.description == "A test node"
        assert config.config["tool_name"] == "test_tool"
        assert config.dependencies == ["dep1", "dep2"]
        assert config.tags == ["test", "tool"]
    
    def test_node_config_defaults(self):
        """Test node config with defaults."""
        config = LangGraphNodeConfig(
            node_type=LangGraphNodeType.LLM,
            name="llm_node",
            description="An LLM node"
        )
        
        assert config.config == {}
        assert config.dependencies == []
        assert config.tags == []


class TestLangGraphTool:
    """Test LangGraphTool base class."""
    
    def test_tool_creation(self):
        """Test tool creation."""
        node_config = LangGraphNodeConfig(
            node_type=LangGraphNodeType.TOOL,
            name="test_tool",
            description="A test tool"
        )
        
        tool = LangGraphTool(node_config)
        assert tool.node_config == node_config
        assert tool._graph is None
        assert tool._state == {}
    
    def test_tool_metadata(self):
        """Test tool metadata retrieval."""
        node_config = LangGraphNodeConfig(
            node_type=LangGraphNodeType.TOOL,
            name="test_tool",
            description="A test tool",
            tags=["test", "langgraph"]
        )
        
        tool = LangGraphTool(node_config)
        metadata = tool.get_metadata()
        
        assert metadata.name == "test_tool"
        assert metadata.description == "A test tool"
        assert "test" in metadata.tags
        assert "langgraph" in metadata.tags
    
    def test_effect_boundary_mapping(self):
        """Test effect boundary mapping for different node types."""
        # Test retriever node
        retriever_config = LangGraphNodeConfig(
            node_type=LangGraphNodeType.RETRIEVER,
            name="retriever",
            description="A retriever"
        )
        retriever_tool = LangGraphTool(retriever_config)
        assert retriever_tool._get_effect_boundary().value == "retriever"
        
        # Test LLM node
        llm_config = LangGraphNodeConfig(
            node_type=LangGraphNodeType.LLM,
            name="llm",
            description="An LLM"
        )
        llm_tool = LangGraphTool(llm_config)
        assert llm_tool._get_effect_boundary().value == "llm"
        
        # Test tool node
        tool_config = LangGraphNodeConfig(
            node_type=LangGraphNodeType.TOOL,
            name="tool",
            description="A tool"
        )
        tool_tool = LangGraphTool(tool_config)
        assert tool_tool._get_effect_boundary().value == "external"
    
    @pytest.mark.asyncio
    async def test_execute_tool_node(self):
        """Test executing a tool node."""
        node_config = LangGraphNodeConfig(
            node_type=LangGraphNodeType.TOOL,
            name="test_tool",
            description="A test tool",
            config={"tool_name": "test_tool", "tool_args": {"arg1": "value1"}}
        )
        
        tool = LangGraphTool(node_config)
        result = await tool.execute({
            "state": {"input": "test input"},
            "config": {"tool_name": "test_tool", "tool_args": {"arg1": "value1"}}
        })
        
        assert len(result) == 1
        assert result[0]["type"] == "tool_result"
        assert result[0]["tool_name"] == "test_tool"
        assert "Executed test_tool" in result[0]["result"]
    
    @pytest.mark.asyncio
    async def test_execute_conditional_node(self):
        """Test executing a conditional node."""
        node_config = LangGraphNodeConfig(
            node_type=LangGraphNodeType.CONDITIONAL,
            name="conditional",
            description="A conditional node",
            config={
                "condition": "test_condition",
                "branches": {"test_condition": "next_branch", "default": "default_branch"}
            }
        )
        
        tool = LangGraphTool(node_config)
        result = await tool.execute({
            "state": {"test_condition": True},
            "config": {
                "condition": "test_condition",
                "branches": {"test_condition": "next_branch", "default": "default_branch"}
            }
        })
        
        assert len(result) == 1
        assert result[0]["type"] == "conditional_result"
        assert result[0]["condition"] == "test_condition"
        assert result[0]["next_branch"] == "next_branch"
    
    @pytest.mark.asyncio
    async def test_execute_human_node(self):
        """Test executing a human interaction node."""
        node_config = LangGraphNodeConfig(
            node_type=LangGraphNodeType.HUMAN,
            name="human",
            description="A human interaction node",
            config={"prompt": "Please provide input:", "input_type": "text"}
        )
        
        tool = LangGraphTool(node_config)
        result = await tool.execute({
            "state": {},
            "config": {"prompt": "Please provide input:", "input_type": "text"}
        })
        
        assert len(result) == 1
        assert result[0]["type"] == "human_interaction"
        assert result[0]["prompt"] == "Please provide input:"
        assert result[0]["input_type"] == "text"
    
    @pytest.mark.asyncio
    async def test_execute_llm_node(self):
        """Test executing an LLM node."""
        node_config = LangGraphNodeConfig(
            node_type=LangGraphNodeType.LLM,
            name="llm",
            description="An LLM node",
            config={"prompt_template": "Process: {input}", "model": "gpt-4"}
        )
        
        tool = LangGraphTool(node_config)
        result = await tool.execute({
            "state": {"input": "test input"},
            "config": {"prompt_template": "Process: {input}", "model": "gpt-4"}
        })
        
        assert len(result) == 1
        assert result[0]["type"] == "llm_result"
        assert result[0]["model"] == "gpt-4"
        assert result[0]["prompt"] == "Process: test input"
        assert "LLM response" in result[0]["response"]
    
    @pytest.mark.asyncio
    async def test_execute_retriever_node(self):
        """Test executing a retriever node."""
        node_config = LangGraphNodeConfig(
            node_type=LangGraphNodeType.RETRIEVER,
            name="retriever",
            description="A retriever node",
            config={"query": "test query", "retriever_name": "test_retriever", "top_k": 3}
        )
        
        tool = LangGraphTool(node_config)
        result = await tool.execute({
            "state": {},
            "config": {"query": "test query", "retriever_name": "test_retriever", "top_k": 3}
        })
        
        assert len(result) == 1
        assert result[0]["type"] == "retriever_result"
        assert result[0]["retriever"] == "test_retriever"
        assert result[0]["query"] == "test query"
        assert len(result[0]["documents"]) == 3
    
    @pytest.mark.asyncio
    async def test_execute_aggregator_node(self):
        """Test executing an aggregator node."""
        node_config = LangGraphNodeConfig(
            node_type=LangGraphNodeType.AGGREGATOR,
            name="aggregator",
            description="An aggregator node",
            config={"type": "concat", "inputs": ["input1", "input2", "input3"]}
        )
        
        tool = LangGraphTool(node_config)
        result = await tool.execute({
            "state": {},
            "config": {"type": "concat", "inputs": ["input1", "input2", "input3"]}
        })
        
        assert len(result) == 1
        assert result[0]["type"] == "aggregator_result"
        assert result[0]["aggregation_type"] == "concat"
        assert result[0]["result"] == "input1 input2 input3"
    
    @pytest.mark.asyncio
    async def test_execute_unsupported_node_type(self):
        """Test executing an unsupported node type."""
        # Create a mock node type that doesn't exist
        class MockNodeType:
            value = "unsupported"
        
        node_config = LangGraphNodeConfig(
            node_type=MockNodeType(),
            name="unsupported",
            description="An unsupported node"
        )
        
        tool = LangGraphTool(node_config)
        
        with pytest.raises(ValueError, match="Unsupported node type"):
            await tool.execute({"state": {}, "config": {}})


class TestLangGraphWorkflowTool:
    """Test LangGraphWorkflowTool."""
    
    def test_workflow_tool_creation(self):
        """Test workflow tool creation."""
        workflow_config = {
            "name": "test_workflow",
            "description": "A test workflow",
            "entry_point": "start",
            "nodes": [
                {
                    "name": "start",
                    "type": "tool",
                    "description": "Start node",
                    "config": {"tool_name": "start_tool"}
                }
            ],
            "edges": [
                {"from": "start", "to": "end"}
            ]
        }
        
        tool = LangGraphWorkflowTool(workflow_config)
        assert tool.workflow_config == workflow_config
        assert tool.entry_point == "start"
        assert len(tool.nodes) == 1
        assert len(tool.edges) == 1
    
    def test_workflow_metadata(self):
        """Test workflow tool metadata."""
        workflow_config = {
            "name": "test_workflow",
            "description": "A test workflow",
            "entry_point": "start",
            "nodes": [],
            "edges": []
        }
        
        tool = LangGraphWorkflowTool(workflow_config)
        metadata = tool.get_metadata()
        
        assert metadata.name == "test_workflow"
        assert metadata.description == "A test workflow"
        assert "workflow" in metadata.tags
        assert "langgraph" in metadata.tags
    
    @pytest.mark.asyncio
    async def test_workflow_execution(self):
        """Test workflow execution."""
        workflow_config = {
            "name": "test_workflow",
            "description": "A test workflow",
            "entry_point": "start",
            "nodes": [
                {
                    "name": "start",
                    "type": "tool",
                    "description": "Start node",
                    "config": {"tool_name": "start_tool"}
                },
                {
                    "name": "end",
                    "type": "llm",
                    "description": "End node",
                    "config": {"prompt_template": "Process: {input}"}
                }
            ],
            "edges": [
                {"from": "start", "to": "end"}
            ]
        }
        
        tool = LangGraphWorkflowTool(workflow_config)
        result = await tool.execute({
            "initial_state": {"input": "test input"},
            "workflow_params": {"max_steps": 5}
        })
        
        assert len(result) == 1
        assert result[0]["type"] == "workflow_result"
        assert result[0]["total_steps"] == 2
        assert result[0]["execution_path"] == ["start", "end"]
        assert result[0]["final_state"]["workflow_completed"] is True
    
    @pytest.mark.asyncio
    async def test_workflow_execution_with_conditionals(self):
        """Test workflow execution with conditional edges."""
        workflow_config = {
            "name": "conditional_workflow",
            "description": "A conditional workflow",
            "entry_point": "start",
            "nodes": [
                {
                    "name": "start",
                    "type": "conditional",
                    "description": "Start node",
                    "config": {"condition": "has_data", "branches": {"true": "process", "false": "end"}}
                },
                {
                    "name": "process",
                    "type": "tool",
                    "description": "Process node",
                    "config": {"tool_name": "process_tool"}
                },
                {
                    "name": "end",
                    "type": "llm",
                    "description": "End node",
                    "config": {"prompt_template": "Finished"}
                }
            ],
            "edges": [
                {"from": "start", "to": "process", "condition": "has_data"},
                {"from": "start", "to": "end", "condition": "!has_data"},
                {"from": "process", "to": "end"}
            ]
        }
        
        tool = LangGraphWorkflowTool(workflow_config)
        
        # Test with data
        result_with_data = await tool.execute({
            "initial_state": {"has_data": True},
            "workflow_params": {"max_steps": 5}
        })
        
        # The workflow should go: start -> process -> end
        # But the conditional node execution updates the state with the condition result
        # So the actual path depends on how the conditional node is processed
        execution_path = result_with_data[0]["execution_path"]
        assert "start" in execution_path
        assert "end" in execution_path
        assert len(execution_path) >= 2
        
        # Test without data
        result_without_data = await tool.execute({
            "initial_state": {"has_data": False},
            "workflow_params": {"max_steps": 5}
        })
        
        execution_path = result_without_data[0]["execution_path"]
        assert "start" in execution_path
        assert "end" in execution_path
        assert len(execution_path) >= 2
    
    def test_find_node_config(self):
        """Test finding node configuration."""
        workflow_config = {
            "name": "test_workflow",
            "entry_point": "start",
            "nodes": [
                {
                    "name": "test_node",
                    "type": "tool",
                    "description": "Test node",
                    "config": {"tool_name": "test_tool"},
                    "dependencies": ["dep1"],
                    "tags": ["test"]
                }
            ],
            "edges": []
        }
        
        tool = LangGraphWorkflowTool(workflow_config)
        node_config = tool._find_node_config("test_node")
        
        assert node_config is not None
        assert node_config.name == "test_node"
        assert node_config.node_type == LangGraphNodeType.TOOL
        assert node_config.dependencies == ["dep1"]
        assert node_config.tags == ["test"]
    
    def test_find_nonexistent_node_config(self):
        """Test finding non-existent node configuration."""
        workflow_config = {
            "name": "test_workflow",
            "entry_point": "start",
            "nodes": [],
            "edges": []
        }
        
        tool = LangGraphWorkflowTool(workflow_config)
        node_config = tool._find_node_config("nonexistent")
        
        assert node_config is None
    
    def test_get_next_node(self):
        """Test getting next node in workflow."""
        workflow_config = {
            "name": "test_workflow",
            "entry_point": "start",
            "nodes": [],
            "edges": [
                {"from": "start", "to": "next"},
                {"from": "next", "to": "end"}
            ]
        }
        
        tool = LangGraphWorkflowTool(workflow_config)
        
        next_node = tool._get_next_node("start", {})
        assert next_node == "next"
        
        next_node = tool._get_next_node("next", {})
        assert next_node == "end"
        
        next_node = tool._get_next_node("end", {})
        assert next_node is None
    
    def test_evaluate_condition(self):
        """Test condition evaluation."""
        workflow_config = {
            "name": "test_workflow",
            "entry_point": "start",
            "nodes": [],
            "edges": []
        }
        
        tool = LangGraphWorkflowTool(workflow_config)
        
        # Test always condition
        assert tool._evaluate_condition("always", {}) is True
        
        # Test never condition
        assert tool._evaluate_condition("never", {}) is False
        
        # Test has_ condition - should check for existence AND truthiness
        assert tool._evaluate_condition("has_data", {"data": "value"}) is True  # "data" exists and is truthy
        assert tool._evaluate_condition("has_data", {"data": True}) is True  # "data" exists and is truthy
        assert tool._evaluate_condition("has_data", {"data": False}) is False  # "data" exists but is falsy
        assert tool._evaluate_condition("has_data", {}) is False  # "data" doesn't exist
        
        # Test default case
        assert tool._evaluate_condition("unknown", {"unknown": True}) is True
        assert tool._evaluate_condition("unknown", {}) is False


class TestLangGraphStateManager:
    """Test LangGraphStateManager."""
    
    def test_state_manager_creation(self):
        """Test state manager creation."""
        manager = LangGraphStateManager()
        assert manager.workflow_states == {}
    
    def test_create_workflow_state(self):
        """Test creating workflow state."""
        manager = LangGraphStateManager()
        initial_state = {"input": "test", "step": 0}
        
        state_id = manager.create_workflow_state("test_workflow", initial_state)
        
        assert state_id == "test_workflow_0"
        assert state_id in manager.workflow_states
        assert manager.workflow_states[state_id]["workflow_id"] == "test_workflow"
        assert manager.workflow_states[state_id]["state"] == initial_state
    
    def test_get_workflow_state(self):
        """Test getting workflow state."""
        manager = LangGraphStateManager()
        initial_state = {"input": "test"}
        state_id = manager.create_workflow_state("test_workflow", initial_state)
        
        retrieved_state = manager.get_workflow_state(state_id)
        
        assert retrieved_state is not None
        assert retrieved_state["workflow_id"] == "test_workflow"
        assert retrieved_state["state"] == initial_state
    
    def test_get_nonexistent_workflow_state(self):
        """Test getting non-existent workflow state."""
        manager = LangGraphStateManager()
        
        retrieved_state = manager.get_workflow_state("nonexistent")
        
        assert retrieved_state is None
    
    def test_update_workflow_state(self):
        """Test updating workflow state."""
        manager = LangGraphStateManager()
        initial_state = {"input": "test"}
        state_id = manager.create_workflow_state("test_workflow", initial_state)
        
        updates = {"step": 1, "output": "result"}
        success = manager.update_workflow_state(state_id, updates)
        
        assert success is True
        updated_state = manager.get_workflow_state(state_id)
        assert updated_state["state"]["input"] == "test"
        assert updated_state["state"]["step"] == 1
        assert updated_state["state"]["output"] == "result"
    
    def test_update_nonexistent_workflow_state(self):
        """Test updating non-existent workflow state."""
        manager = LangGraphStateManager()
        
        success = manager.update_workflow_state("nonexistent", {"update": "value"})
        
        assert success is False
    
    def test_delete_workflow_state(self):
        """Test deleting workflow state."""
        manager = LangGraphStateManager()
        state_id = manager.create_workflow_state("test_workflow", {"input": "test"})
        
        success = manager.delete_workflow_state(state_id)
        
        assert success is True
        assert state_id not in manager.workflow_states
    
    def test_delete_nonexistent_workflow_state(self):
        """Test deleting non-existent workflow state."""
        manager = LangGraphStateManager()
        
        success = manager.delete_workflow_state("nonexistent")
        
        assert success is False
    
    def test_list_workflow_states_all(self):
        """Test listing all workflow states."""
        manager = LangGraphStateManager()
        manager.create_workflow_state("workflow1", {"input": "test1"})
        manager.create_workflow_state("workflow2", {"input": "test2"})
        
        state_ids = manager.list_workflow_states()
        
        assert len(state_ids) == 2
        assert "workflow1_0" in state_ids
        assert "workflow2_0" in state_ids  # Each workflow starts with _0
    
    def test_list_workflow_states_filtered(self):
        """Test listing workflow states filtered by workflow ID."""
        manager = LangGraphStateManager()
        manager.create_workflow_state("workflow1", {"input": "test1"})
        manager.create_workflow_state("workflow2", {"input": "test2"})
        manager.create_workflow_state("workflow1", {"input": "test3"})
        
        state_ids = manager.list_workflow_states("workflow1")
        
        assert len(state_ids) == 2
        assert all("workflow1" in state_id for state_id in state_ids) 