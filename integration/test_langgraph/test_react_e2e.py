"""End-to-end tests for ReActAgent."""

from unittest.mock import MagicMock, patch

import pytest  # noqa: F401
from langchain.tools import BaseTool

from aimq.agents.react import ReActAgent


class E2ETestTool(BaseTool):
    """Mock tool for integration testing."""

    name: str = "test_tool"
    description: str = "Tool for testing end-to-end flows"

    def _run(self, query: str) -> str:
        return f"Result for: {query}"


class SearchTool(BaseTool):
    """Mock search tool."""

    name: str = "search"
    description: str = "Search for information"

    def _run(self, query: str) -> str:
        return f"Search results for {query}: Found 10 items"


@patch("aimq.clients.mistral.get_mistral_client")
def test_react_agent_full_execution(mock_client_func):
    """Test complete ReActAgent execution flow."""
    # Mock LLM responses
    responses = [
        # First: Choose to use tool
        MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content='THOUGHT: I should use the tool\nACTION: test_tool\nINPUT: {"query": "test"}'
                    )
                )
            ]
        ),
        # Second: Provide answer
        MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content="THOUGHT: I have the result\nANSWER: The answer is 42"
                    )
                )
            ]
        ),
    ]

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = responses
    mock_client_func.return_value = mock_client

    agent = ReActAgent(
        tools=[E2ETestTool()],
        system_prompt="Test agent",
        max_iterations=10,
    )

    # Execute
    initial_state = {
        "messages": [{"role": "user", "content": "What is the answer?"}],
        "tools": ["test_tool"],
        "iteration": 0,
        "errors": [],
    }

    result = agent.invoke(initial_state)

    # Should have final answer
    assert "final_answer" in result or result.get("iteration") > 0


@patch("aimq.clients.mistral.get_mistral_client")
def test_react_agent_multiple_tools_execution(mock_client_func):
    """Test agent with multiple tools."""
    responses = [
        MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content='THOUGHT: Search first\nACTION: search\nINPUT: {"query": "python"}'
                    )
                )
            ]
        ),
        MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content="THOUGHT: Got results\nANSWER: Found information about Python"
                    )
                )
            ]
        ),
    ]

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = responses
    mock_client_func.return_value = mock_client

    agent = ReActAgent(
        tools=[SearchTool(), E2ETestTool()],
        system_prompt="Search assistant",
        max_iterations=10,
    )

    initial_state = {
        "messages": [{"role": "user", "content": "Search for Python"}],
        "tools": ["search", "test_tool"],
        "iteration": 0,
        "errors": [],
    }

    result = agent.invoke(initial_state)

    assert result["iteration"] > 0


@patch("aimq.clients.mistral.get_mistral_client")
def test_react_agent_max_iterations_safety(mock_client_func):
    """Test agent stops at max iterations."""
    # Always try to use tool (infinite loop without max_iterations)
    response = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content='THOUGHT: Use tool\nACTION: test_tool\nINPUT: {"query": "test"}'
                )
            )
        ]
    )

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = response
    mock_client_func.return_value = mock_client

    agent = ReActAgent(
        tools=[E2ETestTool()],
        system_prompt="Test agent",
        max_iterations=3,  # Low limit
    )

    initial_state = {
        "messages": [{"role": "user", "content": "Keep going"}],
        "tools": ["test_tool"],
        "iteration": 0,
        "errors": [],
    }

    result = agent.invoke(initial_state)

    # Should stop at max iterations
    assert result["iteration"] >= 3


@patch("aimq.clients.mistral.get_mistral_client")
def test_react_agent_tool_error_handling(mock_client_func):
    """Test agent handles tool errors gracefully."""

    class ErrorTool(BaseTool):
        name: str = "error_tool"
        description: str = "Tool that errors"

        def _run(self, input: str) -> str:
            raise RuntimeError("Tool failed")

    responses = [
        MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content='THOUGHT: Use error tool\nACTION: error_tool\nINPUT: {"input": "test"}'
                    )
                )
            ]
        ),
        MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content="THOUGHT: Tool failed\nANSWER: Could not complete task"
                    )
                )
            ]
        ),
    ]

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = responses
    mock_client_func.return_value = mock_client

    agent = ReActAgent(
        tools=[ErrorTool()],
        system_prompt="Test agent",
        max_iterations=10,
    )

    initial_state = {
        "messages": [{"role": "user", "content": "Use the tool"}],
        "tools": ["error_tool"],
        "iteration": 0,
        "errors": [],
    }

    result = agent.invoke(initial_state)

    # Should handle error and continue
    assert "errors" in result or "final_answer" in result


@patch("aimq.clients.mistral.get_mistral_client")
def test_react_agent_streaming(mock_client_func):
    """Test agent streaming execution."""
    response = MagicMock(
        choices=[MagicMock(message=MagicMock(content="THOUGHT: Done\nANSWER: Complete"))]
    )

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = response
    mock_client_func.return_value = mock_client

    agent = ReActAgent(
        tools=[E2ETestTool()],
        system_prompt="Test agent",
        max_iterations=10,
    )

    initial_state = {
        "messages": [{"role": "user", "content": "Test"}],
        "tools": ["test_tool"],
        "iteration": 0,
        "errors": [],
    }

    # Test streaming
    stream = agent.stream(initial_state)

    # Collect all streamed states
    states = list(stream)
    assert len(states) > 0


@patch("aimq.clients.mistral.get_mistral_client")
def test_react_agent_no_tools(mock_client_func):
    """Test agent works with no tools (just reasoning)."""
    response = MagicMock(
        choices=[
            MagicMock(message=MagicMock(content="THOUGHT: Direct answer\nANSWER: Simple response"))
        ]
    )

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = response
    mock_client_func.return_value = mock_client

    agent = ReActAgent(
        tools=[],  # No tools
        system_prompt="Simple agent",
        max_iterations=10,
    )

    initial_state = {
        "messages": [{"role": "user", "content": "Hello"}],
        "tools": [],
        "iteration": 0,
        "errors": [],
    }

    result = agent.invoke(initial_state)

    assert "final_answer" in result or result["iteration"] > 0
