"""Tests for ReActAgent."""

from unittest.mock import MagicMock, patch

import pytest  # noqa: F401
from langchain.tools import BaseTool

from aimq.agents.react import ReActAgent
from aimq.langgraph.states import AgentState  # noqa: F401


class MockTool(BaseTool):
    """Mock tool for testing."""

    name: str = "mock_tool"
    description: str = "Mock tool for testing"

    def _run(self, input: str) -> str:
        return f"Mock result: {input}"


class CalculatorTool(BaseTool):
    """Calculator tool for testing."""

    name: str = "calculator"
    description: str = "Performs basic math"

    def _run(self, expression: str) -> str:
        try:
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Error: {e}"


def test_react_agent_initialization():
    """Test ReActAgent can be initialized."""
    agent = ReActAgent(
        tools=[MockTool()],
        system_prompt="Test agent",
        max_iterations=5,
    )

    assert agent is not None
    assert len(agent.tools) == 1
    assert agent.max_iterations == 5
    assert agent.system_prompt == "Test agent"


def test_react_agent_default_values():
    """Test ReActAgent uses default values."""
    agent = ReActAgent(tools=[MockTool()])

    assert agent.system_prompt == "You are a helpful AI assistant."
    assert agent.llm == "mistral-large-latest"
    assert agent.temperature == 0.1
    assert agent.memory is False
    assert agent.max_iterations == 10


def test_react_agent_graph_compilation():
    """Test agent compiles graph successfully."""
    agent = ReActAgent(
        tools=[MockTool()],
        system_prompt="Test",
    )

    assert agent._compiled is not None
    assert agent._graph is not None


def test_react_agent_has_required_nodes():
    """Test graph has required nodes."""
    agent = ReActAgent(
        tools=[MockTool()],
        system_prompt="Test",
    )

    # Check nodes exist
    nodes = agent._graph.nodes
    assert "reason" in nodes
    assert "act" in nodes


def test_react_agent_validator_initialized():
    """Test tool validator is initialized."""
    agent = ReActAgent(tools=[MockTool()], system_prompt="Test")

    assert agent.validator is not None


def test_react_agent_parse_action_with_action():
    """Test parsing ACTION/INPUT from LLM response."""
    agent = ReActAgent(tools=[MockTool()], system_prompt="Test")

    response = """THOUGHT: I need to use the tool
ACTION: mock_tool
INPUT: {"query": "test"}"""

    action = agent._parse_action(response)
    assert action.get("tool") == "mock_tool"
    assert action.get("input") == {"query": "test"}


def test_react_agent_parse_action_with_answer():
    """Test parsing ANSWER from LLM response."""
    agent = ReActAgent(tools=[MockTool()], system_prompt="Test")

    response = """THOUGHT: I have the answer
ANSWER: Final answer here"""

    action = agent._parse_action(response)
    assert action.get("answer") == "Final answer here"


def test_react_agent_parse_action_invalid_json():
    """Test parsing handles invalid JSON gracefully."""
    agent = ReActAgent(tools=[MockTool()], system_prompt="Test")

    response = """THOUGHT: Testing
ACTION: mock_tool
INPUT: not valid json"""

    action = agent._parse_action(response)
    assert action.get("tool") == "mock_tool"
    assert action.get("input") == {}  # Falls back to empty dict


def test_react_agent_should_continue_with_answer():
    """Test routing ends when final_answer is present."""
    agent = ReActAgent(tools=[MockTool()], system_prompt="Test", max_iterations=10)

    state = {
        "messages": [],
        "tools": ["mock_tool"],
        "iteration": 2,
        "errors": [],
        "final_answer": "Done",
    }

    result = agent._should_continue(state)
    assert result == "end"


def test_react_agent_should_continue_max_iterations():
    """Test routing ends at max iterations."""
    agent = ReActAgent(tools=[MockTool()], system_prompt="Test", max_iterations=3)

    state = {
        "messages": [],
        "tools": ["mock_tool"],
        "iteration": 3,  # At max
        "errors": [],
    }

    result = agent._should_continue(state)
    assert result == "end"


def test_react_agent_should_continue_with_tool():
    """Test routing goes to act when tool is selected."""
    agent = ReActAgent(tools=[MockTool()], system_prompt="Test", max_iterations=10)

    state = {
        "messages": [],
        "tools": ["mock_tool"],
        "iteration": 2,
        "errors": [],
        "current_tool": "mock_tool",
    }

    result = agent._should_continue(state)
    assert result == "act"


def test_react_agent_should_continue_keep_reasoning():
    """Test routing continues reasoning when no tool or answer."""
    agent = ReActAgent(tools=[MockTool()], system_prompt="Test", max_iterations=10)

    state = {
        "messages": [],
        "tools": ["mock_tool"],
        "iteration": 2,
        "errors": [],
    }

    result = agent._should_continue(state)
    assert result == "reason"


@patch("aimq.clients.mistral.get_mistral_client")
def test_react_agent_reasoning_node(mock_client_func):
    """Test reasoning node execution."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="THOUGHT: Test\nANSWER: Done"))]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_client_func.return_value = mock_client

    agent = ReActAgent(tools=[MockTool()], system_prompt="Test")

    state = {
        "messages": [],
        "tools": ["mock_tool"],
        "iteration": 0,
        "errors": [],
    }

    result = agent._reasoning_node(state)

    assert "final_answer" in result
    assert result["final_answer"] == "Done"
    assert result["iteration"] == 1


@patch("aimq.clients.mistral.get_mistral_client")
def test_react_agent_reasoning_node_with_tool(mock_client_func):
    """Test reasoning node selects tool."""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content='THOUGHT: Use tool\nACTION: mock_tool\nINPUT: {"query": "test"}'
            )
        )
    ]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_client_func.return_value = mock_client

    agent = ReActAgent(tools=[MockTool()], system_prompt="Test")

    state = {
        "messages": [],
        "tools": ["mock_tool"],
        "iteration": 0,
        "errors": [],
    }

    result = agent._reasoning_node(state)

    assert result["current_tool"] == "mock_tool"
    assert result["tool_input"] == {"query": "test"}


@patch("aimq.clients.mistral.get_mistral_client")
def test_react_agent_reasoning_node_error_handling(mock_client_func):
    """Test reasoning node handles errors."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    mock_client_func.return_value = mock_client

    agent = ReActAgent(tools=[MockTool()], system_prompt="Test")

    state = {
        "messages": [],
        "tools": ["mock_tool"],
        "iteration": 0,
        "errors": [],
    }

    result = agent._reasoning_node(state)

    assert "errors" in result
    assert len(result["errors"]) > 0
    assert "API Error" in result["errors"][0]


def test_react_agent_action_node_success():
    """Test action node executes tool successfully."""
    agent = ReActAgent(tools=[MockTool()], system_prompt="Test")

    state = {
        "messages": [],
        "tools": ["mock_tool"],
        "iteration": 1,
        "errors": [],
        "current_tool": "mock_tool",
        "tool_input": {"input": "test"},
    }

    result = agent._action_node(state)

    assert "tool_output" in result
    assert "Mock result" in result["tool_output"]


def test_react_agent_action_node_unknown_tool():
    """Test action node handles unknown tool."""
    agent = ReActAgent(tools=[MockTool()], system_prompt="Test")

    state = {
        "messages": [],
        "tools": ["mock_tool"],
        "iteration": 1,
        "errors": [],
        "current_tool": "unknown_tool",
        "tool_input": {},
    }

    result = agent._action_node(state)

    assert "errors" in result
    assert "Unknown tool" in result["errors"][0]


def test_react_agent_action_node_tool_error():
    """Test action node handles tool execution errors."""

    # Tool that raises an error
    class ErrorTool(BaseTool):
        name: str = "error_tool"
        description: str = "Tool that errors"

        def _run(self, input: str) -> str:
            raise RuntimeError("Tool error")

    agent = ReActAgent(tools=[ErrorTool()], system_prompt="Test")

    state = {
        "messages": [],
        "tools": ["error_tool"],
        "iteration": 1,
        "errors": [],
        "current_tool": "error_tool",
        "tool_input": {"input": "test"},
    }

    result = agent._action_node(state)

    assert "errors" in result
    assert len(result["errors"]) > 0


def test_react_agent_format_tools():
    """Test tool formatting for prompts."""
    tool1 = MockTool()
    tool2 = CalculatorTool()

    agent = ReActAgent(tools=[tool1, tool2], system_prompt="Test")

    formatted = agent._format_tools()

    assert "mock_tool" in formatted
    assert "calculator" in formatted
    assert "Mock tool for testing" in formatted
    assert "Performs basic math" in formatted


def test_react_agent_build_react_prompt():
    """Test ReAct prompt building."""
    agent = ReActAgent(tools=[MockTool()], system_prompt="Test system")

    state = {
        "messages": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ],
        "tools": ["mock_tool"],
        "iteration": 1,
        "errors": [],
    }

    prompt = agent._build_react_prompt(state)

    assert "Test system" in prompt
    assert "mock_tool" in prompt
    assert "THOUGHT:" in prompt
    assert "ACTION:" in prompt
    assert "ANSWER:" in prompt
    assert "Hello" in prompt
    assert "Hi there" in prompt


def test_react_agent_multiple_tools():
    """Test ReActAgent with multiple tools."""
    tools = [MockTool(), CalculatorTool()]
    agent = ReActAgent(tools=tools, system_prompt="Test")

    assert len(agent.tools) == 2
    assert agent._graph is not None


def test_react_agent_custom_llm_and_temperature():
    """Test ReActAgent with custom LLM and temperature."""
    agent = ReActAgent(
        tools=[MockTool()],
        llm="mistral-small-latest",
        temperature=0.7,
    )

    assert agent.llm == "mistral-small-latest"
    assert agent.temperature == 0.7


def test_react_agent_with_memory():
    """Test ReActAgent with memory enabled."""
    with patch("aimq.agents.base.get_checkpointer"):
        agent = ReActAgent(
            tools=[MockTool()],
            memory=True,
        )

        assert agent.memory is True
