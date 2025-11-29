"""Tests for PlanExecuteAgent."""

from unittest.mock import MagicMock, patch

import pytest  # noqa: F401
from langchain.tools import BaseTool

from aimq.agents.plan_execute import PlanExecuteAgent, PlanExecuteState  # noqa: F401


class MockTool(BaseTool):
    """Mock tool for testing."""

    name: str = "mock_tool"
    description: str = "Mock tool for testing"

    def _run(self, input: str) -> str:
        return f"Mock result: {input}"


def test_plan_execute_agent_initialization():
    """Test PlanExecuteAgent can be initialized."""
    agent = PlanExecuteAgent(
        tools=[MockTool()],
        system_prompt="Test planner",
    )

    assert agent is not None
    assert len(agent.tools) == 1
    assert agent.system_prompt == "Test planner"


def test_plan_execute_agent_graph_compilation():
    """Test agent compiles graph successfully."""
    agent = PlanExecuteAgent(
        tools=[MockTool()],
        system_prompt="Test",
    )

    assert agent._compiled is not None
    assert agent._graph is not None


def test_plan_execute_agent_has_required_nodes():
    """Test graph has required nodes."""
    agent = PlanExecuteAgent(
        tools=[MockTool()],
        system_prompt="Test",
    )

    nodes = agent._graph.nodes
    assert "plan" in nodes
    assert "execute" in nodes
    assert "finalize" in nodes


@patch("aimq.clients.mistral.get_mistral_client")
def test_plan_node_creates_plan(mock_client_func):
    """Test plan node creates execution plan."""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content="""1. First step
2. Second step
3. Third step"""
            )
        )
    ]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_client_func.return_value = mock_client

    agent = PlanExecuteAgent(tools=[MockTool()], system_prompt="Test")

    state = {
        "input": "Test task",
        "plan": [],
        "current_step": 0,
        "step_results": [],
        "final_output": None,
        "needs_replan": False,
    }

    result = agent._plan_node(state)

    assert "plan" in result
    assert len(result["plan"]) == 3
    assert result["current_step"] == 0


def test_parse_plan_numbered_list():
    """Test plan parsing with numbered list."""
    agent = PlanExecuteAgent(tools=[MockTool()], system_prompt="Test")

    content = """1. First step
2. Second step
3. Third step"""

    plan = agent._parse_plan(content)

    assert len(plan) == 3
    assert plan[0] == "First step"
    assert plan[1] == "Second step"
    assert plan[2] == "Third step"


def test_parse_plan_bullet_list():
    """Test plan parsing with bullet points."""
    agent = PlanExecuteAgent(tools=[MockTool()], system_prompt="Test")

    content = """- First step
- Second step
* Third step"""

    plan = agent._parse_plan(content)

    assert len(plan) == 3


def test_execute_node():
    """Test execute node processes a step."""
    agent = PlanExecuteAgent(tools=[MockTool()], system_prompt="Test")

    state = {
        "input": "Test task",
        "plan": ["Step 1", "Step 2", "Step 3"],
        "current_step": 0,
        "step_results": [],
        "final_output": None,
        "needs_replan": False,
    }

    result = agent._execute_node(state)

    assert "step_results" in result
    assert len(result["step_results"]) == 1
    assert result["current_step"] == 1


def test_finalize_node():
    """Test finalize node compiles results."""
    agent = PlanExecuteAgent(tools=[MockTool()], system_prompt="Test")

    state = {
        "input": "Test task",
        "plan": ["Step 1", "Step 2"],
        "current_step": 2,
        "step_results": [
            {"step": "Step 1", "result": "Done 1", "step_number": 0},
            {"step": "Step 2", "result": "Done 2", "step_number": 1},
        ],
        "final_output": None,
        "needs_replan": False,
    }

    result = agent._finalize_node(state)

    assert "final_output" in result
    assert result["final_output"]["status"] == "completed"
    assert result["final_output"]["task"] == "Test task"
    assert len(result["final_output"]["results"]) == 2


def test_should_continue_continue_execution():
    """Test routing continues execution."""
    agent = PlanExecuteAgent(tools=[MockTool()], system_prompt="Test")

    state = {
        "input": "Test",
        "plan": ["Step 1", "Step 2", "Step 3"],
        "current_step": 1,
        "step_results": [],
        "final_output": None,
        "needs_replan": False,
    }

    result = agent._should_continue(state)
    assert result == "execute"


def test_should_continue_finalize():
    """Test routing finalizes when all steps complete."""
    agent = PlanExecuteAgent(tools=[MockTool()], system_prompt="Test")

    state = {
        "input": "Test",
        "plan": ["Step 1", "Step 2"],
        "current_step": 2,  # Beyond plan
        "step_results": [],
        "final_output": None,
        "needs_replan": False,
    }

    result = agent._should_continue(state)
    assert result == "finalize"


def test_should_continue_replan():
    """Test routing replans when needed."""
    agent = PlanExecuteAgent(tools=[MockTool()], system_prompt="Test")

    state = {
        "input": "Test",
        "plan": ["Step 1", "Step 2"],
        "current_step": 1,
        "step_results": [],
        "final_output": None,
        "needs_replan": True,
    }

    result = agent._should_continue(state)
    assert result == "replan"


def test_format_tools():
    """Test tool formatting for prompts."""
    tool1 = MockTool()

    class AnotherTool(BaseTool):
        name: str = "another_tool"
        description: str = "Another test tool"

        def _run(self, input: str) -> str:
            return "result"

    tool2 = AnotherTool()

    agent = PlanExecuteAgent(tools=[tool1, tool2], system_prompt="Test")

    formatted = agent._format_tools()

    assert "mock_tool" in formatted
    assert "another_tool" in formatted
    assert "Mock tool for testing" in formatted
    assert "Another test tool" in formatted


@patch("aimq.clients.mistral.get_mistral_client")
def test_plan_node_error_handling(mock_client_func):
    """Test plan node handles errors gracefully."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    mock_client_func.return_value = mock_client

    agent = PlanExecuteAgent(tools=[MockTool()], system_prompt="Test")

    state = {
        "input": "Test task",
        "plan": [],
        "current_step": 0,
        "step_results": [],
        "final_output": None,
        "needs_replan": False,
    }

    result = agent._plan_node(state)

    assert "plan" in result
    assert "Error" in result["plan"][0]


def test_execute_step_with_tools():
    """Test step execution with tools."""
    agent = PlanExecuteAgent(tools=[MockTool()], system_prompt="Test")

    result = agent._execute_step_with_tools("Test step")

    assert "Executed:" in result
    assert "Test step" in result


def test_parse_plan_empty():
    """Test plan parsing with empty content."""
    agent = PlanExecuteAgent(tools=[MockTool()], system_prompt="Test")

    content = ""
    plan = agent._parse_plan(content)

    assert len(plan) == 0


def test_parse_plan_mixed_format():
    """Test plan parsing with mixed formats."""
    agent = PlanExecuteAgent(tools=[MockTool()], system_prompt="Test")

    content = """1. First step
- Second step
3. Third step
Some text without numbering"""

    plan = agent._parse_plan(content)

    assert len(plan) >= 3  # At least the numbered/bulleted items
